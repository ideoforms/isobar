""" Unit tests for Track """

import isobar as iso
import pytest
from . import dummy_timeline

@pytest.fixture()
def dummy_track():
    return iso.Track(output_device=iso.io.DummyOutputDevice())

def test_track(dummy_timeline):
    track = iso.Track(dummy_timeline)
    track.update({
        "note": iso.PSequence([], 0)
    })
    track.tick()
    assert track.is_finished

def test_track_replace(dummy_timeline):
    track1 = dummy_timeline.schedule({"note": 60}, name="foo")
    track2 = dummy_timeline.schedule({"note": 61}, name="bar")
    track3 = dummy_timeline.schedule({"note": 62}, name="foo")
    track4 = dummy_timeline.schedule({"note": 63}, name="foo", replace=False)

    assert track1 == track3
    assert track1.note.constant == 62
    assert track1 != track2
    assert track1 != track4
    assert len(dummy_timeline.tracks) == 3

def test_track_update(dummy_timeline):
    #--------------------------------------------------------------------------------
    # Test that a track can be updated properly.
    #  - Track should continue playing its current events until precisely the
    #    quantized time of the update.
    #  - Should also catch the case in which the current event stream finishes
    #    at exactly the scheduled time, to ensure that the track does not mistakenly
    #    set its `is_finished` flag and terminate.
    #  - Should also catch the case in which two updates are scheduled for the same
    #    tick, in which the last update takes precedence
    #--------------------------------------------------------------------------------
    assert len(dummy_timeline.tracks) == 0
    track = dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([50], 4),
    }, count=20)
    assert len(dummy_timeline.tracks) == 1
    dummy_timeline.tick()

    # This update is later obsoleted
    track.update({
        iso.EVENT_NOTE: iso.PSequence([70], 4),
    }, quantize=4)
    dummy_timeline.tick()

    # This update takes precedence over the previous update
    track.update({
        iso.EVENT_NOTE: iso.PSequence([60], 4),
    }, quantize=4)

    dummy_timeline.run()
    assert dummy_timeline.output_device.events == [
        [0, 'note_on', 50, 64, 0], [1, 'note_off', 50, 0],
        [1, 'note_on', 50, 64, 0], [2, 'note_off', 50, 0],
        [2, 'note_on', 50, 64, 0], [3, 'note_off', 50, 0],
        [3, 'note_on', 50, 64, 0], [4, 'note_off', 50, 0],
        [4, 'note_on', 60, 64, 0], [5, 'note_off', 60, 0],
        [5, 'note_on', 60, 64, 0], [6, 'note_off', 60, 0],
        [6, 'note_on', 60, 64, 0], [7, 'note_off', 60, 0],
        [7, 'note_on', 60, 64, 0], [8, 'note_off', 60, 0],

    ]
    assert track.is_finished
    assert len(dummy_timeline.tracks) == 0

def test_track_callbacks(dummy_timeline):
    track_events = []
    timeline_events = []

    def track_callback(event):
        track_events.append(event)
        assert event.output_device == dummy_timeline.output_device
        assert event.track == track

    def timeline_callback(event):
        timeline_events.append(event)
        assert event.output_device == dummy_timeline.output_device
        assert event.track == track

    track = dummy_timeline.schedule({"note": 60}, count=2)
    track.on_event_callbacks.append(track_callback)

    dummy_timeline.on_event_callback = timeline_callback
    dummy_timeline.run()
    assert len(track_events) == 2
    assert len(timeline_events) == 2

def wait_for_callbacks(track, timeout: float = 1.0):
    # Callbacks are called on the track's callback thread
    import time
    end = time.monotonic() + timeout
    while not track.callback_queue.empty() and time.monotonic() < end:
        time.sleep(0.001)
    time.sleep(0.01)


def test_track_callbacks_report_note_list_notes(dummy_timeline):
    track = dummy_timeline.schedule(name="notes")
    track.add_note(iso.MidiNoteInstance(note=60, amplitude=100, channel=0, timestamp=0, duration=0.5))
    track.add_note(iso.MidiNoteInstance(note=64, amplitude=50, channel=0, timestamp=1, duration=0.5))
    events = []
    track.add_event_callback(events.append)
    # A track of notes never finishes, so the timeline is ticked through the notes rather than run
    for _ in range(int(1.5 / dummy_timeline.tick_duration)):
        dummy_timeline.tick()
    wait_for_callbacks(track)
    assert [(event.type, event.note, event.amplitude) for event in events] == \
           [(iso.EVENT_TYPE_NOTE, 60, 100), (iso.EVENT_TYPE_NOTE, 64, 50)]
    assert all(event.track is track for event in events)


def test_track_callbacks_report_each_note_of_a_chord(dummy_timeline):
    track = dummy_timeline.schedule({"note": (60, 64, 67)}, count=1)
    events = []
    track.add_event_callback(events.append)
    dummy_timeline.run()
    assert sorted(event.note for event in events) == [60, 64, 67]


def test_track_callbacks_report_other_events(dummy_timeline):
    track = dummy_timeline.schedule({"control": 1, "value": 64}, count=2)
    events = []
    track.add_event_callback(events.append)
    dummy_timeline.run()
    assert [event.type for event in events] == [iso.EVENT_TYPE_CONTROL] * 2


def test_several_track_callbacks_each_called(dummy_timeline):
    track = dummy_timeline.schedule({"note": 60}, count=1)
    first, second = [], []
    track.add_event_callback(first.append)
    track.add_event_callback(second.append)
    dummy_timeline.run()
    assert len(first) == 1 and len(second) == 1


def test_track_add_remove_note(dummy_timeline):
    track = dummy_timeline.schedule(name="test_track")

    notes = []
    for index, n in enumerate([60, 62, 64, 65, 67]):
        note = iso.MidiNoteInstance(note=n,
                                    amplitude=32,
                                    channel=0,
                                    timestamp=index,
                                    duration=1.0)
        notes.append(note)
        track.add_note(note)

    assert len(track.notes) == 5

    # Remove a note
    track.remove_note(notes[0])
    assert len(track.notes) == 4
    assert notes[0] not in track.notes
    with pytest.raises(ValueError):
        track.remove_note(notes[0])
    for note in track.notes[:]:
        track.remove_note(note)
    assert len(track.notes) == 0

def test_track_is_finished_after_last_note(dummy_timeline):
    track = dummy_timeline.add_track(name="test_track", remove_when_done=False)

    note1 = iso.MidiNoteInstance(note=60, timestamp=0.0, duration=1)
    note2 = iso.MidiNoteInstance(note=62, timestamp=1.0, duration=1)
    track.add_note(note1)
    track.add_note(note2)

    for tick_count in range(dummy_timeline.time_to_ticks_int(2.0)):
        dummy_timeline.tick()
    
    assert track.is_finished is False
    with pytest.raises(StopIteration):
        dummy_timeline.tick()
    assert track.is_finished

def test_track_defaults(dummy_timeline):
    track = dummy_timeline.schedule(name="test_track")

    track.add_note(iso.MidiNoteInstance(timestamp=0.0, note=60))
    track.add_note(iso.MidiNoteInstance(timestamp=1.0, note=62))
    assert track.notes[0].has_amplitude() is False
    assert track.notes[0].amplitude == iso.DEFAULT_EVENT_AMPLITUDE

    dummy_timeline.defaults.amplitude = 32
    assert track.notes[0].amplitude == 32

    track.defaults.amplitude = 48
    assert track.notes[0].amplitude == 48

    track.notes[0].amplitude = 97
    assert track.notes[0].has_amplitude() is True
    assert track.notes[0].amplitude == 97

    assert track.notes[1].amplitude == 48