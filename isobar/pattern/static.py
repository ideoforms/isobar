from __future__ import annotations
from . import Pattern
from ..globals import Globals

from typing import Any


class PGlobals (Pattern):
    """ PGlobals: Static global value identified by a string.
    """

    def __init__(self, name: str, default: Any = None):
        self.name = name
        self.default = default

    def __repr__(self):
        return ("PGlobals(%s)" % repr(self.name))

    def __next__(self):
        name = Pattern.value(self.name)
        try:
            value = Globals.get(name)
            return Pattern.value(value)
        except KeyError:
            return self.default

class PStaticPattern(Pattern):
    def __init__(self, pattern: Pattern, element_duration: float):
        self.pattern = pattern
        self.value = None
        self.element_duration = element_duration
        self.current_element_start_time = None
        self.current_element_duration = None

    def __repr__(self):
        return ("PStaticPattern(%s, %s)" % (repr(self.pattern), repr(self.element_duration)))

    def __next__(self):
        timeline = self.timeline
        if timeline is None:
            raise Exception("Cannot query current timeline outside of a scheduled event context")
        current_time = round(timeline.current_time, 5)

        while self.current_element_start_time is None or \
                current_time - self.current_element_start_time >= self.current_element_duration:
            self.value = Pattern.value(self.pattern)
            self.current_element_start_time = round(timeline.current_time, 5)
            self.current_element_duration = Pattern.value(self.element_duration)

        return self.value

class PCurrentTime(Pattern):
    """ PCurrentTime: Returns the position (in beats) of the current timeline. """

    def __init__(self):
        pass

    def __repr__(self):
        return "PCurrentTime()"

    def __next__(self):
        beats = self.get_beats()
        return round(beats, 5)

    def get_beats(self):
        #------------------------------------------------------------------------
        # using the specified timeline (if given) or the currently-embedded
        # timeline (otherwise), return the current position in current_time.
        #------------------------------------------------------------------------
        timeline = self.timeline
        if timeline:
            return timeline.current_time

        return 0
