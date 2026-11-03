import pytest

signalflow = pytest.importorskip("signalflow")

from isobar.io.cv import CVOutputDevice, CVChannelMappings, CVChannelMapping
from isobar.io.cv.output import parse_clock_division, CV_CLOCK_TICKS_PER_BEAT


@pytest.fixture(scope="module")
def graph():
    graph = signalflow.AudioGraph.get_shared_graph()
    if graph is None:
        graph = signalflow.AudioGraph(output_device=signalflow.AudioOut_Dummy(8), start=False)
    return graph


def make_device(graph, mappings, **kwargs):
    return CVOutputDevice(channel_mappings=mappings, graph=graph, **kwargs)


def two_voice_mappings(note_priority="last"):
    return CVChannelMappings([CVChannelMapping(0, "note", 0),
                              CVChannelMapping(1, "gate", 0),
                              CVChannelMapping(2, "note", 1),
                              CVChannelMapping(3, "gate", 1)],
                             note_priority=note_priority)


def voice_notes(device):
    return [voice.note for voice in device.voices]


def test_polyphony_from_mappings(graph):
    device = make_device(graph, two_voice_mappings())
    assert len(device.voices) == 2


def test_gap_in_voices(graph):
    mappings = CVChannelMappings([CVChannelMapping(0, "note", 0), CVChannelMapping(1, "note", 2)])
    with pytest.raises(ValueError):
        make_device(graph, mappings)


def test_clock_only(graph):
    device = make_device(graph, CVChannelMappings([CVChannelMapping(0, "clock")]))
    assert device.voices == []
    device.note_on(60, 100)
    device.note_off(60)


def test_voices_and_gates(graph):
    device = make_device(graph, two_voice_mappings())
    device.note_on(60, 100)
    device.note_on(64, 100)
    assert voice_notes(device) == [60, 64]
    assert device.channel_outputs[1].value == 1.0
    assert device.channel_outputs[3].value == 1.0

    device.note_off(60)
    assert voice_notes(device) == [None, 64]
    assert device.channel_outputs[1].value == 0.0
    assert device.channel_outputs[3].value == 1.0

    # The next note goes to the voice that has rested longest
    device.note_off(64)
    device.note_on(67, 100)
    assert voice_notes(device) == [67, None]


def test_pitch_stays_after_note_off(graph):
    device = make_device(graph, two_voice_mappings(), output_voltage_range=(-10, 10))
    device.note_on(72, 100)
    device.note_off(72)
    assert device.channel_outputs[0].value == pytest.approx(0.1)


def test_zero_volt_note(graph):
    device = make_device(graph, two_voice_mappings(), output_voltage_range=(-10, 10), zero_volt_note=36)
    device.note_on(36, 100)
    device.note_on(48, 100)
    assert device.channel_outputs[0].value == pytest.approx(0.0)
    assert device.channel_outputs[2].value == pytest.approx(0.1)


def test_asymmetric_voltage_range(graph):
    device = make_device(graph, two_voice_mappings(), output_voltage_range=(0, 10), zero_volt_note=0)
    device.note_on(60, 100)
    assert device.channel_outputs[0].value == pytest.approx(0.0)


def test_note_out_of_range(graph):
    device = make_device(graph, two_voice_mappings(), output_voltage_range=(-3, 3))
    with pytest.raises(ValueError):
        device.note_on(100, 100)
    assert voice_notes(device) == [None, None]
    assert device.held_notes == []


def test_priority_last(graph):
    device = make_device(graph, two_voice_mappings("last"))
    device.note_on(60, 100)
    device.note_on(64, 100)
    device.note_on(67, 100)
    # The new note takes over the oldest note's voice
    assert voice_notes(device) == [67, 64]
    # Releasing a sounding note brings back the held note that was waiting
    device.note_off(67)
    assert voice_notes(device) == [60, 64]
    assert device.channel_outputs[1].value == 1.0


def test_priority_first(graph):
    device = make_device(graph, two_voice_mappings("first"))
    device.note_on(60, 100)
    device.note_on(64, 100)
    device.note_on(67, 100)
    assert voice_notes(device) == [60, 64]
    device.note_off(60)
    assert voice_notes(device) == [67, 64]


def test_priority_lowest(graph):
    device = make_device(graph, two_voice_mappings("lowest"))
    device.note_on(64, 100)
    device.note_on(67, 100)
    device.note_on(70, 100)
    assert voice_notes(device) == [64, 67]
    device.note_on(60, 100)
    assert voice_notes(device) == [64, 60]


def test_priority_highest(graph):
    device = make_device(graph, two_voice_mappings("highest"))
    device.note_on(64, 100)
    device.note_on(67, 100)
    device.note_on(60, 100)
    assert voice_notes(device) == [64, 67]
    device.note_on(70, 100)
    assert voice_notes(device) == [70, 67]


def test_invalid_priority():
    with pytest.raises(ValueError):
        CVChannelMappings(note_priority="loudest")


def test_mono_legato(graph):
    mappings = CVChannelMappings([CVChannelMapping(0, "note"), CVChannelMapping(1, "gate")])
    device = make_device(graph, mappings)
    device.note_on(60, 100)
    device.note_on(64, 100)
    assert voice_notes(device) == [64]
    device.note_off(64)
    assert voice_notes(device) == [60]
    assert device.channel_outputs[1].value == 1.0
    device.note_off(60)
    assert voice_notes(device) == [None]
    assert device.channel_outputs[1].value == 0.0


def test_repeated_note_on(graph):
    device = make_device(graph, two_voice_mappings())
    device.note_on(60, 100)
    device.note_on(60, 50)
    assert voice_notes(device) == [60, None]
    assert device.held_notes == [(60, 50)]
    device.note_off(60)
    assert voice_notes(device) == [None, None]


def test_note_on_zero_velocity(graph):
    device = make_device(graph, two_voice_mappings())
    device.note_on(60, 100)
    device.note_on(60, 0)
    assert voice_notes(device) == [None, None]


def test_all_notes_off(graph):
    device = make_device(graph, two_voice_mappings())
    device.note_on(60, 100)
    device.note_on(64, 100)
    device.all_notes_off()
    assert voice_notes(device) == [None, None]
    assert device.held_notes == []
    assert device.channel_outputs[1].value == 0.0


@pytest.mark.parametrize("division, beats", [
    ("4n", 1), ("8n", 0.5), ("16n", 0.25), ("1n", 4), ("8t", 1 / 3), ("4n.", 1.5), ("1m", 4), ("2m", 8), (2, 2),
])
def test_parse_clock_division(division, beats):
    assert parse_clock_division(division) == pytest.approx(beats)


def test_parse_clock_division_bars():
    assert parse_clock_division("1m", beats_per_bar=3) == 3


@pytest.mark.parametrize("division", ["4", "q", "0n", "4x", -1])
def test_parse_clock_division_invalid(division):
    with pytest.raises(ValueError):
        parse_clock_division(division)


def test_clock_division_too_fine(graph):
    with pytest.raises(ValueError):
        make_device(graph, CVChannelMappings([CVChannelMapping(0, "clock", division="64n")]))


class PulseRecorder:
    # Stands in for a channel's envelope node, recording the tick of each pulse
    def __init__(self, device):
        self.device = device
        self.ticks = []

    def trigger(self):
        self.ticks.append(self.device.tick_count)


def test_clock_subdivisions(graph):
    mappings = CVChannelMappings([CVChannelMapping(0, "clock", division="16n"),
                                  CVChannelMapping(1, "clock", division="1m"),
                                  CVChannelMapping(2, "clock")])
    device = make_device(graph, mappings)
    pulses = {}
    for channel in range(3):
        recorder = PulseRecorder(device)
        device.channel_outputs[channel] = recorder
        pulses[channel] = recorder.ticks

    for _ in range(CV_CLOCK_TICKS_PER_BEAT * 8):
        device.tick()
    assert pulses[0] == list(range(0, CV_CLOCK_TICKS_PER_BEAT * 8, CV_CLOCK_TICKS_PER_BEAT // 4))
    assert pulses[1] == [0, CV_CLOCK_TICKS_PER_BEAT * 4]
    assert pulses[2] == list(range(0, CV_CLOCK_TICKS_PER_BEAT * 8, CV_CLOCK_TICKS_PER_BEAT))

    device.tick()
    device.reset()
    pulses[1].clear()
    device.tick()
    assert pulses[1] == [0]


def test_clock_mapping_has_no_voice():
    with pytest.raises(ValueError):
        CVChannelMapping(0, "clock", voice_index=0)
