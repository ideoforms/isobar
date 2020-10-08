from . import Pattern

class Globals:
    """
    The Globals class encapsulates a namespace of global variables that can be accessed
    throughout isobar. This is particularly useful to alter parameters shared across the
    composition, which can then be accessed in patterns using the PGlobals class.

    For example,
    """
    @classmethod
    def get(cls, key):
        """
        Returns the value stored in `key`.
        Args:
            key: The key to query.

        Returns:
            The value, which can be of any type.

        Raises:
            KeyError: If the key does not exist in the globals dict.
        """
        if key not in PGlobals.dict:
            raise KeyError("Global variable does not exist: %s" % key)
        value = PGlobals.dict[key]
        return Pattern.value(value)

    @classmethod
    def set(cls, key, value):
        PGlobals.dict[key] = value

class PGlobals (Pattern):
    """ PGlobals: Static global value identified by a string.
    """
    dict = {}

    def __init__(self, name):
        self.name = name

    def __next__(self):
        name = Pattern.value(self.name)
        value = Globals.get(name)
        return Pattern.value(value)

class PStaticPattern(Pattern):
    def __init__(self, pattern, element_duration):
        self.pattern = pattern
        self.value = None
        self.element_duration = element_duration
        self.current_element_start_time = None
        self.current_element_duration = None

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
