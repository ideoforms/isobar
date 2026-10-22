import isobar as iso
from isobar.io.midi import MidiInputDevice, MidiOutputDevice
import pytest
import mido
import time
from . import dummy_timeline

VIRTUAL_DEVICE_NAME = "Virtual Device"

no_midi = False
try:
    midi_out = iso.MidiOutputDevice()
except iso.DeviceNotFoundException:
    no_midi = True

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi():
    """
    Send a MIDI message through a virtual loopback device.
    Note that virtual=True is not needed for subsequent calls, as it has already been
    created so is visible to rtmidi as an existing device.
    """
    events = []
    def log_event(message):
        nonlocal events
        events.append(message)
    midi_in = iso.MidiInputDevice(VIRTUAL_DEVICE_NAME, virtual=True)
    midi_in.callback = log_event
    midi_out = iso.MidiOutputDevice(VIRTUAL_DEVICE_NAME)

    timeline = iso.Timeline(120, midi_out)
    timeline.stop_when_done = True
    timeline.schedule({
        "note": 60,
        "duration" : 0.1
    }, count=1)
    timeline.run()
    # Allow time for the MIDI virtual device to process the message
    time.sleep(0.01)
    # A note_on and note_off message should have been sent
    assert len(events) == 2

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_sync():
    tempo = 150
    midi_out = iso.MidiOutputDevice(VIRTUAL_DEVICE_NAME, virtual=True, send_clock=True)
    clock = iso.Clock(tempo=tempo, clock_target=midi_out)

    midi_in = iso.MidiInputDevice(VIRTUAL_DEVICE_NAME)

    clock.background()
    time.sleep(0.1)
    clock.stop()
    assert midi_in.tempo == pytest.approx(tempo, rel=0.03)


#--------------------------------------------------------------------------------
# event_filter tests
#--------------------------------------------------------------------------------
FILTER_DEVICE_NAME = "Virtual Filter Device"

def channel_filter(channel):
    return lambda message: message.channel == channel

@pytest.fixture
def make_midi_in():
    devices = []
    def _make(**kwargs):
        midi_in = iso.MidiInputDevice(FILTER_DEVICE_NAME, virtual=True, **kwargs)
        devices.append(midi_in)
        return midi_in
    yield _make
    for device in devices:
        device.close()

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_note_channel(make_midi_in):
    midi_in = make_midi_in(event_filter=channel_filter(1))
    notes_on = []
    notes_off = []
    midi_in.add_note_on_handler(notes_on.append)
    midi_in.add_note_off_handler(notes_off.append)

    # Notes on other channels are ignored
    midi_in._mido_callback(mido.Message("note_on", channel=0, note=60, velocity=100))
    midi_in._mido_callback(mido.Message("note_on", channel=2, note=62, velocity=100))
    assert notes_on == []
    assert midi_in.notes_down == []
    assert midi_in.poll() is None

    # Notes on the selected channel are processed
    midi_in._mido_callback(mido.Message("note_on", channel=1, note=64, velocity=100))
    assert len(notes_on) == 1
    assert notes_on[0].pitch == 64
    assert notes_on[0].channel == 1
    assert [note.pitch for note in midi_in.notes_down] == [64]
    message = midi_in.poll()
    assert message.type == "note_on" and message.channel == 1
    assert midi_in.poll() is None

    # A note off for the same pitch on another channel must not release the note
    midi_in._mido_callback(mido.Message("note_off", channel=0, note=64))
    assert notes_off == []
    assert [note.pitch for note in midi_in.notes_down] == [64]

    # Note off on the selected channel releases it
    midi_in._mido_callback(mido.Message("note_off", channel=1, note=64))
    assert len(notes_off) == 1
    assert midi_in.notes_down == []

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_note_on_zero_velocity(make_midi_in):
    # note_on with velocity 0 is treated as note off, and should be filtered too
    midi_in = make_midi_in(event_filter=channel_filter(1))
    notes_off = []
    midi_in.add_note_off_handler(notes_off.append)
    midi_in._mido_callback(mido.Message("note_on", channel=1, note=60, velocity=100))
    midi_in._mido_callback(mido.Message("note_on", channel=0, note=60, velocity=0))
    assert notes_off == []
    assert len(midi_in.notes_down) == 1
    midi_in._mido_callback(mido.Message("note_on", channel=1, note=60, velocity=0))
    assert len(notes_off) == 1
    assert midi_in.notes_down == []

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_control_messages(make_midi_in):
    midi_in = make_midi_in(event_filter=channel_filter(3))
    control_changes = []
    pitchbends = []
    aftertouches = []
    midi_in.add_control_change_handler(control_changes.append)
    midi_in.on_pitchbend_handlers.append(pitchbends.append)
    midi_in.add_aftertouch_handler(aftertouches.append)

    for channel in range(16):
        midi_in._mido_callback(mido.Message("control_change", channel=channel, control=1, value=channel))
        midi_in._mido_callback(mido.Message("pitchwheel", channel=channel, pitch=channel))
        midi_in._mido_callback(mido.Message("aftertouch", channel=channel, value=channel))

    assert [m.channel for m in control_changes] == [3]
    assert [m.channel for m in pitchbends] == [3]
    assert [m.channel for m in aftertouches] == [3]

    received = []
    while (message := midi_in.poll()) is not None:
        received.append(message)
    assert len(received) == 3
    assert all(message.channel == 3 for message in received)

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_multiple_channels(make_midi_in):
    midi_in = make_midi_in(event_filter=lambda message: message.channel in (0, 9))
    notes_on = []
    midi_in.add_note_on_handler(notes_on.append)
    for channel in range(16):
        midi_in._mido_callback(mido.Message("note_on", channel=channel, note=channel, velocity=100))
    assert [note.channel for note in notes_on] == [0, 9]

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_none(make_midi_in):
    # With no filter, messages on all channels are processed
    midi_in = make_midi_in()
    notes_on = []
    midi_in.add_note_on_handler(notes_on.append)
    for channel in range(16):
        midi_in._mido_callback(mido.Message("note_on", channel=channel, note=channel, velocity=100))
    assert [note.channel for note in notes_on] == list(range(16))

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_ignores_system_messages(make_midi_in):
    # System messages have no channel, so should bypass the filter entirely
    filtered_messages = []
    def reject_all(message):
        filtered_messages.append(message)
        return False

    midi_in = make_midi_in(event_filter=reject_all)
    midi_in._mido_callback(mido.Message("start"))
    assert midi_in.is_midi_transport_started
    midi_in._mido_callback(mido.Message("clock"))
    midi_in._mido_callback(mido.Message("stop"))
    assert not midi_in.is_midi_transport_started
    assert filtered_messages == []

    # Channel messages are passed to the filter
    midi_in._mido_callback(mido.Message("note_on", channel=0, note=60, velocity=100))
    assert len(filtered_messages) == 1
    assert midi_in.notes_down == []

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_event_filter_loopback(make_midi_in):
    """
    Send messages on several channels through a virtual loopback device,
    and check that only those on the selected channel are received.
    """
    midi_in = make_midi_in(event_filter=channel_filter(5))
    midi_out = mido.open_output(FILTER_DEVICE_NAME)
    try:
        for channel in range(16):
            midi_out.send(mido.Message("note_on", channel=channel, note=60 + channel, velocity=100))
            midi_out.send(mido.Message("control_change", channel=channel, control=7, value=channel))
        # Allow time for the MIDI virtual device to process the messages
        time.sleep(0.05)
    finally:
        midi_out.close()

    received = []
    while (message := midi_in.poll()) is not None:
        received.append(message)
    assert [message.type for message in received] == ["note_on", "control_change"]
    assert all(message.channel == 5 for message in received)
    assert [note.pitch for note in midi_in.notes_down] == [65]

@pytest.mark.skipif(no_midi, reason="Device does not have MIDI support")
def test_io_midi_polytouch_without_held_note(make_midi_in):
    # Polyphonic aftertouch for a note that isn't held should not raise
    midi_in = make_midi_in()
    polytouches = []
    midi_in.add_polytouch_handler(polytouches.append)
    midi_in._mido_callback(mido.Message("polytouch", channel=0, note=60, value=64))
    assert len(polytouches) == 1

    midi_in._mido_callback(mido.Message("note_on", channel=0, note=60, velocity=100))
    midi_in._mido_callback(mido.Message("polytouch", channel=0, note=60, value=32))
    assert midi_in.notes_down[0].aftertouch == 32
