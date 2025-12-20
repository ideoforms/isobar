from . import dummy_timeline

def test_track_mute(dummy_timeline):
    """
    Test basic mute functionality.
    """
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})

    # Neither track muted: both should play
    dummy_timeline.tick()
    assert dummy_timeline.output_device.events == [
        [0, 'note_on', 60, 64, 0], [0, 'note_on', 62, 64, 0]
    ]
    dummy_timeline.output_device.clear()

    # Mute track 1: only track 2 should play
    track1.mute()
    assert track1.is_muted
    assert not track2.is_muted

    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()
    
    assert dummy_timeline.output_device.events == [
        [1, 'note_off', 60, 0],
        [1, 'note_off', 62, 0],
        [1, 'note_on', 62, 64, 0]
    ]
    dummy_timeline.output_device.clear()

    # Unmute track 1: both should play
    track1.unmute()
    assert not track1.is_muted
    for n in range(dummy_timeline.ticks_per_beat):
        dummy_timeline.tick()
    
    assert dummy_timeline.output_device.events == [
        [2, 'note_on', 60, 64, 0],
        [2, 'note_off', 62, 0],
        [2, 'note_on', 62, 64, 0]
    ]

def test_track_mute_exclusive(dummy_timeline):
    """
    Test exclusive mute functionality.
    """
    track1 = dummy_timeline.schedule({"note": 60})
    track2 = dummy_timeline.schedule({"note": 62})
    track3 = dummy_timeline.schedule({"note": 64})

    # Mute track 1 and 3 normally
    track1.mute()
    track3.mute()
    assert track1.is_muted
    assert not track2.is_muted
    assert track3.is_muted

    # Exclusive mute track 2: should unmute others
    track2.mute(exclusive=True)
    
    # Track 2 should be muted
    assert track2.is_muted
    
    # Tracks 1 and 3 should be unmuted
    assert not track1.is_muted
    assert not track3.is_muted

    dummy_timeline.tick()
    # 60 and 64 should play, 62 should not
    events = dummy_timeline.output_device.events
    notes = sorted([e[2] for e in events if e[1] == 'note_on'])
    assert notes == [60, 64]
