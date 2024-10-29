from __future__ import annotations

from typing import Optional, Callable, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .timeline import Timeline
from ..constants import *
from ..util import scale_lin_lin

import logging
import numpy as np
import math

logger = logging.getLogger(__name__)

@dataclass
class Binding:
    object: Any
    property_name: str

class AutomationEnvelope:
    def __init__(self,
                 total_ticks: int,
                 envelope_ticks: int,
                 curve: str = "linear"):
        self.envelope = np.ones(total_ticks)
        self.total_ticks = total_ticks
        self.current_tick = 0
        self.is_finished = False
        if curve == "linear":
            self.envelope[0:envelope_ticks] = np.linspace(0, 1, envelope_ticks)
            self.envelope[-envelope_ticks:] = np.linspace(1, 0, envelope_ticks)
            # normalise envelope so that, when applied to a curve, the total
            # magnitude of the curve does not change.
            mean_value_per_tick = np.sum(self.envelope) / (len(self.envelope) if len(self.envelope) else 1)
            self.envelope /= mean_value_per_tick

    def tick(self):
        if self.is_finished:
            return 0
        elif len(self.envelope) == 0:
            return 1
        else:
            rv = self.envelope[self.current_tick]
            self.current_tick += 1
            if self.current_tick >= self.total_ticks:
                self.is_finished = True
            return rv

class AutomationModulation:
    def __init__(self,
                 delta_per_tick: float,
                 duration_ticks: int,
                 envelope_ticks: int,
                 envelope_curve: str = "linear"):
        self.delta_per_tick = delta_per_tick
        self.duration_ticks = duration_ticks
        self.current_tick = 0
        self.current_value = 0.0
        self.is_finished = False
        self.envelope = AutomationEnvelope(total_ticks=duration_ticks,
                                           envelope_ticks=envelope_ticks,
                                           curve=envelope_curve)

    def tick(self):
        self.current_tick += 1
        if self.current_tick >= self.duration_ticks:
            self.is_finished = True
        rv = self.envelope.tick()
        return self.delta_per_tick * rv


# class AutomationModulationLFO (AutomationModulation):


class Automation:
    def __init__(self,
                 timeline: Timeline,
                 range: Optional[tuple[float, float]] = None,
                 initial: Optional[float] = None,
                 ease: Optional[str] = None,
                 curve: Optional[str] = "linear",
                 boundaries: Optional[str] = "clip",
                 default_duration: Optional[float] = 0.0):
        """
        panner = timeline.automation(range=(0, 1), initial=0.5, ease="sine", curve="linear", boundaries="wrap")

        Args:
            timeline: The Timeline object that the track inhabits
        """
        self.timeline: Timeline = timeline
        self.range = range
        if initial is None:
            if self.range:
                initial = 0.5 * (self.range[0] + self.range[1])
            else:
                initial = 0.0

        self.current_value = initial

        self.ease = ease

        if curve not in ["linear", "exponential"]:
            raise ValueError("Invalid value for curve: %s" % curve)
        self.curve = curve

        if boundaries not in [None, "clip", "wrap", "fold"]:
            raise ValueError("Invalid value for boundaries: %s" % boundaries)
        self.boundaries = boundaries

        self.current_time: float = 0.0
        self.default_duration = default_duration

        self.value_changed_callbacks: list[Callable] = []
        self.bindings: list[Binding] = []
        self.modulations: list[AutomationModulation] = []

    def __str__(self):
        return "Automation (range=%s, curve=%.2f)" % (str(self.range), str(self.curve))
    
    @property
    def value(self) -> float:
        """
        The current value of the automation.

        Returns:
            float: The current value.
        """
        if self.range is None:
            return self.current_value
        elif self.boundaries == "clip":
            return max(self.range[0], min(self.range[1], self.current_value))
        elif self.boundaries == "wrap":
            return self.range[0] + (self.current_value % (self.range[1] - self.range[0]))
        elif self.boundaries == "fold":
            raise ValueError("Not yet implemented: fold")

    @property
    def tick_duration(self) -> float:
        """
        Tick duration, in beats.
        """
        return self.timeline.tick_duration

    def tick(self):
        """
        Step forward one tick.
        """
        
        previous_value = self.current_value
        self.current_time += self.tick_duration
        new_value = self.current_value
        for modulation in self.modulations[:]:
            delta = modulation.tick()
            new_value += delta
            if modulation.is_finished:
                self.modulations.remove(modulation)

        # Only send an update if the value has changed
        if new_value != previous_value:
            self.jump_to(new_value)

    def jump_to(self, value):
        self.current_value = value
        for binding in self.bindings:
            setattr(binding.object, binding.property_name, self.value)

    def stop(self):
        self.timeline.remove_automation(self)

    def move_to(self, value: float, duration: float = None, envelope: float = 0.5):
        # TODO: This`` prevents multiple move_bys, but is needed so that each Arc move_to
        # update action overwrites the previous. Need to think through this.
        self.modulations.clear()
        self.move_by(value - self.current_value, duration, envelope)
    
    def move_by(self, value: float, duration: float = None, envelope: float = 0.5):
        if duration is None:
            duration = self.default_duration

        duration_ticks = int(math.ceil(duration / self.tick_duration))
        delta_per_tick = value / (duration_ticks if duration_ticks > 0 else 1)
        envelope_ticks = int(envelope * duration_ticks)
        modulation = AutomationModulation(delta_per_tick=delta_per_tick,
                                          duration_ticks=duration_ticks,
                                          envelope_ticks=envelope_ticks)
        self.modulations.append(modulation)

    def add_value_changed_callback(self, callback: Callable):
        """
        Callback to trigger when a the automation value changes.
        Useful for displaying GUI changes.

        The callback receives a single arg containing the automation.
        """
        self.value_changed_callbacks.append(callback)

    def remove_value_changed_callback(self, callback: Callable):
        """
        Remove an event callback.

        Args:
            callback: The callback to remove.
        """
        self.value_changed_callbacks.remove(callback)

    def bind(self, object: Any, property_name: str):
        binding = Binding(object, property_name)
        self.bindings.append(binding)

        # Initialise each binding to the automation's initial value,
        # to prevent jumps if the source's property was previously set
        # to a different value
        setattr(binding.object, binding.property_name, self.value)
