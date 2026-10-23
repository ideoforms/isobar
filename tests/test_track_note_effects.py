""" Unit tests for note effects applied to a Track's notes """

import isobar as iso
from isobar.effects import NoteEffectEcho, NoteEffectScale, NoteEffectSnapToKey, NoteEffectTranspose
from . import dummy_timeline


def make_looping_track(timeline, note: int = 60, amplitude: int = 64, loop_length: float = 1.0):
    # A track that loops one note, starting at time 0. The timeline keeps running after the note, as it loops.
    timeline.stop_when_done = False
    track = timeline.add_track(name="test_track", remove_when_done=False)
    track.add_note(iso.MidiNoteInstance(note=note, amplitude=amplitude, channel=0, timestamp=0.0, duration=0.5))
    track.add_looping_region(0, loop_length)
    return track


def run(timeline, beats: float):
    for _ in range(timeline.time_to_ticks_int(beats)):
        timeline.tick()


def events_of_type(timeline, event_type: str) -> list:
    return [event[1:] for event in timeline.output_device.events if event[1] == event_type]


def test_transpose_is_not_reapplied_each_loop(dummy_timeline):
    track = make_looping_track(dummy_timeline)
    track.add_note_effect(NoteEffectTranspose(transpose=3))
    run(dummy_timeline, 3)

    assert [event[1] for event in events_of_type(dummy_timeline, "note_on")] == [63, 63, 63]
    # The stored note is unchanged
    assert [note.note for note in track.notes] == [60]


def test_note_off_matches_played_pitch(dummy_timeline):
    track = make_looping_track(dummy_timeline)
    track.add_note_effect(NoteEffectTranspose(transpose=3))
    run(dummy_timeline, 2)

    assert [event[1] for event in events_of_type(dummy_timeline, "note_off")] == [63, 63]


def test_changing_transpose_affects_next_play(dummy_timeline):
    track = make_looping_track(dummy_timeline)
    effect = NoteEffectTranspose(transpose=3)
    track.add_note_effect(effect)
    run(dummy_timeline, 0.25)
    # Changing the transpose while the note is playing still sends the note_off for what was played
    effect.transpose = iso.PConstant(5)
    run(dummy_timeline, 1)

    assert [event[1] for event in events_of_type(dummy_timeline, "note_on")] == [63, 65]
    assert [event[1] for event in events_of_type(dummy_timeline, "note_off")] == [63]


def test_scale_is_not_reapplied_each_loop(dummy_timeline):
    track = make_looping_track(dummy_timeline, amplitude=100)
    track.add_note_effect(NoteEffectScale(scale=0.5))
    run(dummy_timeline, 3)

    assert [event[2] for event in events_of_type(dummy_timeline, "note_on")] == [50, 50, 50]
    assert [note.amplitude for note in track.notes] == [100]


def test_snap_to_key_is_not_saved_into_note(dummy_timeline):
    track = make_looping_track(dummy_timeline, note=61)
    track.add_note_effect(NoteEffectSnapToKey(scale=iso.Scale.major, tonic=0))
    run(dummy_timeline, 1)

    assert [event[1] for event in events_of_type(dummy_timeline, "note_on")] == [60]
    assert track.to_dict()["notes"][0]["note"] == 61


def test_echoes_do_not_accumulate(dummy_timeline):
    track = make_looping_track(dummy_timeline, loop_length=2.0)
    track.add_note_effect(NoteEffectEcho(delay=0.5, count=1))
    run(dummy_timeline, 5)

    # Three passes, each playing the note and one echo
    assert len(events_of_type(dummy_timeline, "note_on")) == 6
    # Echoes are removed once played, and not saved
    assert len(track.notes) == 1
    assert len(track.to_dict()["notes"]) == 1


def test_stop_all_notes_sends_played_pitch(dummy_timeline):
    track = make_looping_track(dummy_timeline)
    track.add_note_effect(NoteEffectTranspose(transpose=3))
    run(dummy_timeline, 0.25)
    track.stop_all_notes()

    assert [event[1] for event in events_of_type(dummy_timeline, "note_off")] == [63]
    assert track.notes[0].sounding is None
