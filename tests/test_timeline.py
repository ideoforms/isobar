""" Unit tests for isobar """

import isobar as iso
import pytest
import time
from isobar.io import DummyOutputDevice, MidiOutputDevice
from . import dummy_timeline
from isobar.exceptions import InvalidEventException

def test_timeline_tempo():
    timeline = iso.Timeline(100)
    assert timeline.clock_source.tempo == pytest.approx(100)

def test_timeline_default_output_device():
    timeline = iso.Timeline()
    try:
        track = timeline.schedule({ "note": 0 })
        assert issubclass(type(track.output_device), MidiOutputDevice)
    except iso.DeviceNotFoundException:
        # Ignore exception on machines without a MIDI device
        pass

def test_timeline_output_device():
    dummy = DummyOutputDevice()
    timeline = iso.Timeline(output_device=dummy)
    track = timeline.schedule({ "note" : 0 })
    assert track.output_device == dummy

def test_timeline_stop_when_done():
    # When the Timeline ticks without any tracks, it should by default keep running
    timeline = iso.Timeline(output_device=DummyOutputDevice())
    timeline.tick()
    assert timeline.current_time == pytest.approx(1.0 / iso.DEFAULT_TICKS_PER_BEAT)

    # When stop_when_done is True, the timeline should stop as soon as it runs on empty
    timeline.stop_when_done = True
    with pytest.raises(StopIteration):
        timeline.tick()

def test_timeline_schedule(dummy_timeline):
    events = {
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }
    dummy_timeline.schedule(events)
    assert len(events.keys()) == 1
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [pytest.approx(0.0), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(1.0), "note_off", 1, 0]

def test_timeline_schedule_update(dummy_timeline):
    """
    Schedule an empty Track, and subsequently update it with events.
    Useful for live coding.
    """
    dummy_timeline.stop_when_done = False
    dummy_timeline.tick()
    dummy_timeline.stop_when_done = True

    #--------------------------------------------------------------------------------
    # Note that, because the Track has its own current_time which is relative
    # to the moment it is created, the track creation and the update() call
    # both need to have quantize=1.
    #--------------------------------------------------------------------------------
    track = dummy_timeline.schedule(quantize=1)
    track.update({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }, quantize=1)

    dummy_timeline.run()
    assert dummy_timeline.output_device.events == [[1.0, 'note_on', 1, 64, 0], [2.0, 'note_off', 1, 0]]

def test_timeline_schedule_update_after_period(dummy_timeline):
    """
    Check that, if we update the contents of a Track after a long period has elapsed,
    it does not play through the whole history of past events that would have been played.
    """
    dummy_timeline.stop_when_done = False
    track = dummy_timeline.schedule(remove_when_done=False)
    for n in range(int(dummy_timeline.ticks_per_beat * 2.5)):
        dummy_timeline.tick()
    track.update({
        iso.EVENT_NOTE: iso.PSequence([1, 2], 1)
    }, quantize=1)
    for n in range(int(dummy_timeline.ticks_per_beat * 2.5) + 1):
        dummy_timeline.tick()
    assert dummy_timeline.output_device.events == [
        [3.0, 'note_on', 1, 64, 0], [4.0, 'note_off', 1, 0],
        [4.0, 'note_on', 2, 64, 0], [5.0, 'note_off', 2, 0],
    ]

def test_timeline_schedule_twice(dummy_timeline):
    # TODO
    pass

def test_timeline_unschedule(dummy_timeline):
    events = {
        iso.EVENT_NOTE: iso.PSequence([1]),
        iso.EVENT_GATE: 0.5
    }
    track = dummy_timeline.schedule(events)
    ticks = 2 * dummy_timeline.ticks_per_beat
    dummy_timeline.stop_when_done = False
    for n in range(ticks):
        dummy_timeline.tick()

    assert len(dummy_timeline.tracks) == 1
    assert len(dummy_timeline.output_device.events) == 4
    dummy_timeline.unschedule(track)
    assert len(dummy_timeline.tracks) == 0
    for n in range(ticks):
        dummy_timeline.tick()

    assert len(dummy_timeline.output_device.events) == 4

def test_timeline_schedule_real_clock():
    timeline = iso.Timeline(60, output_device=DummyOutputDevice())
    times = []
    timeline.stop_when_done = True
    def record_time():
        times.append(time.time())
    timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1, 1], 1),
        iso.EVENT_ACTION: record_time,
        iso.EVENT_DURATION: 0.1
    }, delay=0.1)
    t0 = time.time()
    timeline.run()
    diff = times[1] - times[0]
    assert diff == pytest.approx(0.1, abs=timeline.tick_duration)

@pytest.mark.parametrize("quantize", [0.0, 0.1, 0.5, 1.0])
@pytest.mark.parametrize("delay", [0.0, 0.1, 0.5, 1.0])
def test_timeline_schedule_quantize_delay(dummy_timeline, quantize, delay):
    dummy_timeline.stop_when_done = False
    dummy_timeline.tick()
    dummy_timeline.stop_when_done = True
    initial_time = dummy_timeline.current_time
    stream = dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }, quantize=quantize, delay=delay)
    assert stream.timeline == dummy_timeline
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    #--------------------------------------------------------------------------------
    # Scheduling can only be as precise as the duration of a tick,
    # so use this as the bounds for approximation.
    #--------------------------------------------------------------------------------
    if quantize == 0.0:
        assert dummy_timeline.output_device.events[0] == [pytest.approx(initial_time + delay, abs=dummy_timeline.tick_duration), "note_on", 1, 64, 0]
        assert dummy_timeline.output_device.events[1] == [pytest.approx(initial_time + delay + 1.0, abs=dummy_timeline.tick_duration), "note_off", 1, 0]
    else:
        assert dummy_timeline.output_device.events[0] == [pytest.approx(quantize + delay, abs=dummy_timeline.tick_duration), "note_on", 1, 64, 0]
        assert dummy_timeline.output_device.events[1] == [pytest.approx(quantize + delay + 1.0, abs=dummy_timeline.tick_duration), "note_off", 1, 0]

@pytest.mark.parametrize("quantize", [0.0, 0.1, 0.5, 1.0])
def test_timeline_schedule_quantize_on_beat(dummy_timeline, quantize):
    # Check that quantized notes are played immediately when scheduled on the beat.
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }, quantize=quantize)
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [0, "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(1.0, abs=dummy_timeline.tick_duration), "note_off", 1, 0]

def test_timeline_schedule_default_quantize(dummy_timeline):
    dummy_timeline.defaults.quantize = 1
    dummy_timeline.stop_when_done = False
    dummy_timeline.tick()
    dummy_timeline.stop_when_done = True

    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    })
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [1, "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(2, abs=dummy_timeline.tick_duration), "note_off", 1, 0]

def test_timeline_schedule_default_quantize_override(dummy_timeline):
    dummy_timeline.defaults.quantize = 1
    dummy_timeline.stop_when_done = False
    dummy_timeline.tick()
    dummy_timeline.stop_when_done = True
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }, quantize=0)
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [pytest.approx(dummy_timeline.tick_duration, abs=dummy_timeline.tick_duration), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(1 + dummy_timeline.tick_duration, abs=dummy_timeline.tick_duration), "note_off", 1, 0]

@pytest.mark.skip
def test_timeline_schedule_time(dummy_timeline):
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1),
        iso.EVENT_DURATION: 1
    }, time=1.25)
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [pytest.approx(1.25, abs=dummy_timeline.tick_duration), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(2.25, abs=dummy_timeline.tick_duration), "note_off", 1, 0]

@pytest.mark.skip
def test_timeline_schedule_count(dummy_timeline):
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSeries(0, 1),
        iso.EVENT_DURATION: 1
    }, count=4)
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 8
    assert dummy_timeline.output_device.events == [
        [0, "note_on", 0, 64, 0], [1, "note_off", 0, 0],
        [1, "note_on", 1, 64, 0], [2, "note_off", 1, 0],
        [2, "note_on", 2, 64, 0], [3, "note_off", 2, 0],
        [3, "note_on", 3, 64, 0], [4, "note_off", 3, 0]
    ]

def test_timeline_reset(dummy_timeline):
    track = dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1, 2], 1),
        iso.EVENT_DURATION: 1.0,
        iso.EVENT_GATE: 0.5
    })

    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()
    assert dummy_timeline.current_time == pytest.approx(1.0)
    assert track.current_time == pytest.approx(1.0)
    dummy_timeline.reset()
    assert dummy_timeline.current_time == 0.0
    assert track.current_time == 0.0

    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 6
    assert dummy_timeline.output_device.events[0] == [pytest.approx(0.0), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(0.5), "note_off", 1, 0]
    assert dummy_timeline.output_device.events[2] == [pytest.approx(1.0), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[3] == [pytest.approx(1.5), "note_off", 1, 0]
    assert dummy_timeline.output_device.events[4] == [pytest.approx(2.0), "note_on", 2, 64, 0]
    assert dummy_timeline.output_device.events[5] == [pytest.approx(2.5), "note_off", 2, 0]

def test_timeline_reset_to_beat(dummy_timeline):
    # TODO
    pass

def test_timeline_background():
    timeline = iso.Timeline(60, output_device=iso.io.DummyOutputDevice())
    timeline.ticks_per_beat = 100
    executed = 0
    def set_executed():
        nonlocal executed
        executed += 1
    timeline.background()
    timeline.schedule({
        "action": set_executed,
        "duration": 0.05
    }, delay=0.01)
    time.sleep(0.2)
    timeline.stop()
    assert executed == 4

def test_timeline_running(dummy_timeline):
    # TODO
    pass

def test_timeline_tick_events(dummy_timeline):
    dummy_timeline.done = False
    def callback():
        dummy_timeline.done = True
    event = {
        iso.EVENT_TIME: dummy_timeline.tick_duration,
        iso.EVENT_ACTION: callback
    }
    dummy_timeline.events.append(event)
    dummy_timeline.tick()
    with pytest.raises(StopIteration):
        dummy_timeline.tick()
    assert dummy_timeline.done

def test_timeline_beats_to_seconds(dummy_timeline):
    timeline = iso.Timeline(120)
    assert timeline.beats_to_seconds(1) == pytest.approx(0.5)
    assert timeline.beats_to_seconds(0) == pytest.approx(0.0)
    timeline.tempo = 180
    assert timeline.beats_to_seconds(1) == pytest.approx(1/3)

def test_timeline_seconds_to_beats(dummy_timeline):
    timeline = iso.Timeline(120)
    assert timeline.seconds_to_beats(1) == pytest.approx(2)
    assert timeline.seconds_to_beats(0) == pytest.approx(0.0)
    timeline.tempo = 180
    assert timeline.seconds_to_beats(1) == pytest.approx(3)

def test_timeline_tempo(dummy_timeline):
    # Set tempo of internal clock
    dummy_timeline.clock_source = iso.Clock(dummy_timeline, 120)
    dummy_timeline.tempo = 180
    assert dummy_timeline.clock_source.tempo == 180

    # Set tempo of external clock (raise exception)
    try:
        dummy_timeline.clock_source = iso.MidiInputDevice("Virtual Device", virtual=True)
        assert dummy_timeline.tempo is None
        with pytest.raises(RuntimeError):
            dummy_timeline.tempo = 180
    except iso.DeviceNotFoundException:
        # Fail quietly on machines that don't support MIDI
        pass