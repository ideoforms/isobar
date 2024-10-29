from __future__ import annotations

from typing import Optional, Callable, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .timeline import Timeline
from ..constants import *
from ..util import scale_lin_lin

import logging
import math

logger = logging.getLogger(__name__)

@dataclass
class Binding:
    object: Any
    property_name: str

class LFO:
    def __init__(self,
                 timeline: Timeline,
                 shape: str,
                 frequency: float,
                 min: float = 0.0,
                 max: float = 1.0,
                 name: Optional[str] = None):
        """
        Args:
            timeline: The Timeline object that the track inhabits
            shape: The shape of the LFO
            frequency: The frequency of the LFO
            min: The minimum value to generate
            max: The maximum value to generate
            name: Optional name for the LFO. If specified, can be used to update LFOs in place by specifying \
                  its name when scheduling events on the Timeline.
        """
        self.timeline: Timeline = timeline
        self.name: str = name
        self.shape = shape
        self.frequency = frequency
        self.min = min
        self.max = max

        self.is_started: bool = True
        self.is_paused: bool = False
        self.current_value: float = 0.0
        self.current_time: float = 0.0

        self.value_changed_callbacks: list[Callable] = []
        self.bindings: list[Binding] = []

    def __str__(self):
        return "LFO (%s, shape=%s, frequency=%.2f)" % (self.name if self.name else "unnamed", self.shape, self.frequency)
    
    @property
    def value(self) -> float:
        """
        The current value of the LFO.

        Returns:
            float: The current value.
        """
        return self.current_value

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

        if not self.is_started:
            return

        self.current_time += self.tick_duration
        
        if self.shape == "sine":
            value_unscaled = math.sin(math.pi * 2 * self.current_time * self.frequency)
            value_scaled = scale_lin_lin(value_unscaled, -1, 1, self.min, self.max)
            self.current_value = value_scaled
        else:
            raise ValueError("Invalid LFO shape: %s" % self.shape)
        
        for binding in self.bindings:
            setattr(binding.object, binding.property_name, self.current_value)
        
    def update(self,
               properties: dict):
        """
        Update the properties of this LFO.

        Args:
            properties: A dict of properties.
        """
        for key, value in properties.items():
            setattr(self, key, value)

    def reset(self):
        """
        Rewind to the beginning of the LFO.
        """
        self.current_time = 0

    def stop(self):
        self.timeline.remove_lfo(self)

    def pause(self) -> None:
        """
        Pauses the LFO. 
        """
        self.is_paused = True

    def unpause(self) -> None:
        """
        Unpauses the LFO.
        """
        self.is_paused = False

    def add_value_changed_callback(self, callback: Callable):
        """
        Callback to trigger when a the LFO value changes.
        Useful for displaying GUI changes to reflect underlying LFO changes.

        The callback received a single arg containing the LFO.
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
