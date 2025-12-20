from . import dummy_timeline

def test_track_solo(dummy_timeline):
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})
    
    # Neither track soloed: both should play
    dummy_timeline.tick()
    assert dummy_timeline.output_device.events == [
        [0, 'note_on', 60, 64, 0], [0, 'note_on', 62, 64, 0]
    ]
    dummy_timeline.output_device.clear()

    # Track 1 soloed: only track 1 should play
    track1.solo()
    assert track1.is_soloed
    assert not track2.is_soloed
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()
    assert dummy_timeline.output_device.events == [
        [1, 'note_off', 60, 0],
        [1, 'note_on', 60, 64, 0],
        [1, 'note_off', 62, 0]
    ]
    dummy_timeline.output_device.clear()

    # Track 1 unsoloed: both should play
    track1.unsolo()
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()

    assert dummy_timeline.output_device.events == [
        [2, 'note_off', 60, 0],
        [2, 'note_on', 60, 64, 0], [2, 'note_on', 62, 64, 0]
    ]

def test_track_solo_multiple(dummy_timeline):
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})
    track3 = dummy_timeline.schedule({"note": 64})

    # Solo 1 and 2
    track1.solo()
    track2.solo()
    
    dummy_timeline.tick()
    # 60 and 62 should play, 64 should not
    events = dummy_timeline.output_device.events
    notes = sorted([e[2] for e in events if e[1] == 'note_on'])
    assert notes == [60, 62]

def test_track_solo_exclusive(dummy_timeline):
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})
    track3 = dummy_timeline.schedule({"note": 64})

    track1.solo()
    track2.solo(exclusive=True)

    assert not track1.is_soloed
    assert track2.is_soloed
    assert not track3.is_soloed

def test_track_mute_vs_solo(dummy_timeline):
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})

    # Verify initial state
    dummy_timeline.tick()
    assert len([e for e in dummy_timeline.output_device.events if e[1] == 'note_on']) == 2
    dummy_timeline.output_device.clear()

    # Solo track 1
    track1.solo()
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()

    # Note off events from previous tick + new note on
    note_ons = [e for e in dummy_timeline.output_device.events if e[1] == 'note_on']
    assert len(note_ons) == 1
    assert note_ons[0][2] == 60
    dummy_timeline.output_device.clear()

    # Mute track 1 (soloed)
    track1.mute()
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()

    # Should get no new notes
    assert len([e for e in dummy_timeline.output_device.events if e[1] == 'note_on']) == 0
