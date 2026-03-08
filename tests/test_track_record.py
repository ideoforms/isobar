from . import dummy_timeline
from isobar.io.dummy.input import DummyInputDevice
from isobar.io.midinote import MidiNote
import pytest



def test_track_recording_state(dummy_timeline):
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({}, input_device=input_device)
    assert not track.is_recording
    
    track.start_recording()
    assert track.is_recording
    
    track.stop_recording()
    assert not track.is_recording

def test_track_recording_notes(dummy_timeline):
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({"note": 0, "amplitude": 0}, input_device=input_device)
    track.start_recording()
    
    # Send note on at t=0
    input_device.note_on(60, 64)
    
    # Advance time to t=1
    for n in range(dummy_timeline.ticks_per_beat):
    	dummy_timeline.tick()
    
    # Send note off at t=1
    input_device.note_off(60)
    
    # Check if note was recorded
    assert len(track.notes) == 1
    note = track.notes[0]
    assert note.note == 60
    assert note.amplitude == 64
    assert note.timestamp == 0.0
    assert note.duration == pytest.approx(1.0, abs=0.01)
    
    track.stop_recording()

def test_track_recording_monitor(dummy_timeline):
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({}, input_device=input_device)
    
    # Monitor enabled by default
    track.start_recording()
    
    # Clear output device events
    dummy_timeline.output_device.clear()
    
    input_device.note_on(60, 64)
    assert len(dummy_timeline.output_device.events) == 1
    assert dummy_timeline.output_device.events[0][1] == 'note_on'
    assert dummy_timeline.output_device.events[0][2] == 60
    
    input_device.note_off(60)
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[1][1] == 'note_off'
    
    track.stop_recording()
    
    # Test monitor disabled
    dummy_timeline.output_device.clear()
    track.start_recording(monitor=False)
    input_device.note_on(62, 64)
    assert len(dummy_timeline.output_device.events) == 0
    input_device.note_off(62)
    assert len(dummy_timeline.output_device.events) == 0
    
    track.stop_recording()

def test_track_set_monitor(dummy_timeline):
    track = dummy_timeline.schedule({})
    # Check default? It's private _monitor.
    # But we can check behavior or property if exposed?
    # We didn't expose 'monitor' property, only set_monitor method and init param in start_recording
    
    # Track needs input_device to record
    input_device = DummyInputDevice()
    track.input_device = input_device
    
    track.start_recording(monitor=False)
    input_device.note_on(60, 64)
    assert len(dummy_timeline.output_device.events) == 0
    
    track.set_monitor(True)
    input_device.note_off(60) # Note off should be monitored now
    assert len(dummy_timeline.output_device.events) == 1
    assert dummy_timeline.output_device.events[0][1] == 'note_off'
