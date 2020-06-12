""" Unit tests for isobar """

import isobar as iso
import pytest
from isobar.io import DummyOutputDevice, MidiOut
from . import dummy_timeline

def test_timeline_tempo():
    timeline = iso.Timeline(100)
    assert timeline.clock.tempo == pytest.approx(100)

def test_timeline_default_output_device():
    timeline = iso.Timeline()
    try:
        track = timeline.schedule({})
        assert issubclass(type(track.output_device), MidiOut)
    except iso.DeviceNotFoundException:
        # Ignore exception on machines without a MIDI device
        pass
    except NameError:
        # Ignore exception on machines without a MIDI device
        pass

def test_timeline_output_device():
    dummy = DummyOutputDevice()
    timeline = iso.Timeline(output_device=dummy)
    track = timeline.schedule({})
    assert track.output_device == dummy

def test_timeline_stop_when_done():
    # When the Timeline ticks without any tracks, it should by default terminate.
    timeline = iso.Timeline()
    with pytest.raises(StopIteration):
        timeline.tick()
    assert timeline.beats == 0.0

    # When stop_when_done is False, ticking should run as normal
    timeline.stop_when_done = False
    timeline.tick()
    assert timeline.beats == pytest.approx(1.0 / iso.TICKS_PER_BEAT)

def test_timeline_schedule(dummy_timeline):
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    })
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [pytest.approx(0.0), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(1.0), "note_off", 1, 0]

def test_timeline_schedule_twice(dummy_timeline):
    pass

def test_timeline_schedule_real_clock():
    timeline = iso.Timeline(60, output_device=DummyOutputDevice())
    times = []
    import time
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
    initial_time = dummy_timeline.beats
    dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1)
    }, quantize=quantize, delay=delay)
    dummy_timeline.stop_when_done = True
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

def test_timeline_reset(dummy_timeline):
    track = dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([1], 1),
        iso.EVENT_DURATION: 1
    })
    for n in range(int(0.5 / dummy_timeline.tick_duration)):
        dummy_timeline.tick()
    assert dummy_timeline.beats == 0.5
    assert track.current_time == 0.5
    dummy_timeline.reset()
    assert dummy_timeline.beats == 0.0
    assert track.current_time == 0.0
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == 2
    assert dummy_timeline.output_device.events[0] == [pytest.approx(0.0), "note_on", 1, 64, 0]
    assert dummy_timeline.output_device.events[1] == [pytest.approx(1.5), "note_off", 1, 0]

def test_timeline_reset_to_beat(dummy_timeline):
    # TODO
    pass

def test_timeline_tick_events(dummy_timeline):
    dummy_timeline.done = False
    def callback():
        dummy_timeline.done = True
    event = {
        iso.EVENT_TIME: dummy_timeline.tick_duration,
        iso.EVENT_FUNCTION: callback
    }
    dummy_timeline.events.append(event)
    dummy_timeline.tick()
    with pytest.raises(StopIteration):
        dummy_timeline.tick()
    assert dummy_timeline.done