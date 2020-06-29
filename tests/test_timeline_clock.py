""" Unit tests for isobar """

import isobar as iso
import pytest
import time

def test_timeline_clock_accuracy():
    #--------------------------------------------------------------------------------
    # 480 ticks per beat @ 125bpm = 1 tick per 1ms
    #--------------------------------------------------------------------------------
    timeline = iso.Timeline(125, output_device=iso.DummyOutputDevice())
    timeline.stop_when_done = True
    timeline.ticks_per_beat = 480
    timeline.event_times = []
    timeline.schedule({
        iso.EVENT_ACTION: lambda: timeline.event_times.append(time.time()),
        iso.EVENT_DURATION: iso.PSequence([ 0.001 ], 50)
    })
    timeline.run()
    #--------------------------------------------------------------------------------
    # Check that timing is accurate to +/- 1ms
    #--------------------------------------------------------------------------------
    for index, t in enumerate(timeline.event_times[:-1]):
        dt = timeline.event_times[index + 1] - t
        assert 0.0002 < dt < 0.002

@pytest.mark.parametrize("ticks_per_beat", [ 24, 96, 480 ])
def test_timeline_ticks_per_beat(ticks_per_beat):
    #--------------------------------------------------------------------------------
    # Schedule a single event
    #--------------------------------------------------------------------------------
    delay_time = 0.1
    timeline = iso.Timeline(120, output_device=iso.DummyOutputDevice())
    timeline.stop_when_done = True
    timeline.ticks_per_beat = ticks_per_beat
    timeline.event_times = []
    timeline.schedule({
        iso.EVENT_ACTION: lambda: timeline.event_times.append(time.time()),
        iso.EVENT_DURATION: iso.PSequence([ timeline.seconds_to_beats(delay_time) ], 2)
    })
    timeline.run()
    for index, t in enumerate(timeline.event_times[:-1]):
        dt = timeline.event_times[index + 1] - t
        assert (delay_time * 0.95) < dt < (delay_time * 1.05)

def test_timeline_clock_midi_sync_out():
    pass

def test_timeline_clock_midi_sync_in():
    pass
