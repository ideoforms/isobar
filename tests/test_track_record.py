import isobar as iso
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
    dummy_timeline.tick()

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
    # The note on wasn't monitored, so no note off is sent for it
    input_device.note_off(60)
    assert len(dummy_timeline.output_device.events) == 0

    # Subsequent notes are monitored
    input_device.note_on(62, 64)
    input_device.note_off(62)
    assert [event[1] for event in dummy_timeline.output_device.events] == ['note_on', 'note_off']

def test_track_monitor_applies_note_effects(dummy_timeline):
    from isobar.effects import NoteEffectTranspose, NoteEffectScale
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({}, input_device=input_device)
    track.add_note_effect(NoteEffectTranspose(transpose=3))
    track.add_note_effect(NoteEffectScale(scale=0.5))
    track.start_recording()
    dummy_timeline.output_device.clear()

    input_device.note_on(60, 100)
    events = dummy_timeline.output_device.events
    assert [event[1:] for event in events] == [['note_on', 63, 50, 0]]

    # The note_off matches the transposed pitch that was played
    input_device.note_off(60)
    assert events[-1][1:] == ['note_off', 63, 0]
    track.stop_recording()

def test_track_monitor_note_off_after_effect_changes(dummy_timeline):
    from isobar.effects import NoteEffectTranspose
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({}, input_device=input_device)
    effect = NoteEffectTranspose(transpose=3)
    track.add_note_effect(effect)
    track.start_recording()
    dummy_timeline.output_device.clear()

    input_device.note_on(60, 100)
    effect.transpose = iso.PConstant(7)
    input_device.note_off(60)
    assert [event[1:3] for event in dummy_timeline.output_device.events] == [['note_on', 63], ['note_off', 63]]

def test_track_monitor_note_off_after_monitor_disabled(dummy_timeline):
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({}, input_device=input_device)
    track.start_recording()
    dummy_timeline.output_device.clear()

    input_device.note_on(60, 100)
    track.set_monitor(False)
    input_device.note_off(60)
    assert [event[1] for event in dummy_timeline.output_device.events] == ['note_on', 'note_off']

def test_track_recording_stores_notes_without_effects(dummy_timeline):
    from isobar.effects import NoteEffectTranspose
    input_device = DummyInputDevice()
    track = dummy_timeline.schedule({"note": 0, "amplitude": 0}, input_device=input_device)
    track.add_note_effect(NoteEffectTranspose(transpose=3))
    track.start_recording()

    input_device.note_on(60, 64)
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()
    input_device.note_off(60)

    # The recorded note is the raw input; effects are applied when it is played back
    assert [note.note for note in track.notes] == [60]
    track.stop_recording()

def test_track_note_on_method(dummy_timeline):
    from isobar.effects import NoteEffectTranspose
    track = dummy_timeline.schedule({})
    track.add_note_effect(NoteEffectTranspose(transpose=-2))
    dummy_timeline.output_device.clear()

    note = iso.MidiNoteInstance(timestamp=0, note=60, amplitude=80, channel=1)
    sounding = track.note_on(note)
    assert sounding.note == 58
    assert note.note == 60
    assert note.output_note is sounding
    track.note_off(note)
    assert note.sounding is None
    assert [event[1:] for event in dummy_timeline.output_device.events] == [['note_on', 58, 80, 1], ['note_off', 58, 1]]
