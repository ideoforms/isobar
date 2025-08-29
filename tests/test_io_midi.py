import isobar as iso
from isobar.io.midi import MidiInputDevice, MidiOutputDevice
import pytest
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

