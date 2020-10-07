""" Unit tests for events """

import isobar as iso
import pytest
import math
from . import dummy_timeline

def test_event_control_no_interpolation(dummy_timeline):
    """
    Simple case: schedule a series of regularly-spaced control points.
    Output device should receive discrete control events.
    """
    control_series = iso.PSeries(start=1, step=2, length=3)
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: control_series,
        iso.EVENT_DURATION: 1,
        iso.EVENT_CHANNEL: 9
    })
    dummy_timeline.run()
    assert dummy_timeline.output_device.events == [
        [0, "control", 0, 1, 9],
        [1, "control", 0, 3, 9],
        [2, "control", 0, 5, 9]
    ]

def test_event_control_linear_interpolation(dummy_timeline):
    """
    Linear interpolation between control points.
    """
    control_series = iso.PSequence([1, 3, 2], 1)
    dummy_timeline.ticks_per_beat = 10
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: control_series,
        iso.EVENT_DURATION: iso.PSequence([1, 0.5]),
        iso.EVENT_CHANNEL: 9
    }, interpolate=iso.INTERPOLATION_LINEAR)
    dummy_timeline.run()

    expected_series = [1 + 2 * n / dummy_timeline.ticks_per_beat for n in range(dummy_timeline.ticks_per_beat)] + \
                      [3 - 1 * n / (dummy_timeline.ticks_per_beat // 2) for n in range(dummy_timeline.ticks_per_beat // 2)] + \
                      [2]
    values = [event[3] for event in dummy_timeline.output_device.events]

    assert len(dummy_timeline.output_device.events) == (dummy_timeline.ticks_per_beat * 1.5) + 1
    assert expected_series == pytest.approx(values, rel=0.01)

def test_event_control_linear_interpolation_zero_duration(dummy_timeline):
    control_series = iso.PSequence([0, 1])
    duration_series = iso.PSequence([1, 0])
    dummy_timeline.ticks_per_beat = 10
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: control_series,
        iso.EVENT_DURATION: duration_series,
        iso.EVENT_CHANNEL: 9
    }, interpolate=iso.INTERPOLATION_LINEAR, count=4)
    dummy_timeline.run()
    expected_series = [0.1 * n for n in range(0, 11)] + [0.1 * n for n in range(1, 11)]
    values = [event[3] for event in dummy_timeline.output_device.events]
    assert expected_series == pytest.approx(values, rel=0.0000001)

def test_event_control_cosine_interpolation(dummy_timeline):
    """
    Linear interpolation between control points.
    """
    alternator = iso.PSequence([0, 1])
    dummy_timeline.ticks_per_beat = 10
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: alternator,
        iso.EVENT_CHANNEL: 9
    }, interpolate=iso.INTERPOLATION_COSINE, count=3)
    dummy_timeline.run()

    expected_series = [
        0.5 * (1.0 - math.cos(math.pi * n / dummy_timeline.ticks_per_beat))
        for n in range(2 * dummy_timeline.ticks_per_beat + 1)
    ]
    values = [event[3] for event in dummy_timeline.output_device.events]
    assert expected_series == pytest.approx(values, rel=0.000001)