from .core import Pattern
from ..scale import Scale


class PDegree(Pattern):
    """ PDegree: Map scale index <degree> to MIDI notes in <scale>.

        >>> p = PDegree(PSeries(0, 1), Scale.major)
        >>> p.nextn(16)
        [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26]
        """

    def __init__(self, degree, scale=Scale.major):
        self.degree = degree
        self.scale = scale

    def __next__(self):
        degree = Pattern.value(self.degree)
        scale = Pattern.value(self.scale)
        if degree is None:
            return None

        return scale[degree]

class PFilterByKey(Pattern):
    """ PFilterByKey: Filter notes based on their presence in <key>.

        >>>
        >>> p.nextn(16)
        []
        """

    def __init__(self, input, key):
        self.input = input
        self.key = key

    def __next__(self):
        note = next(self.input)
        key = Pattern.value(self.key)
        if note in key:
            return note
        else:
            return None

class PNearest(Pattern):
    """ PNearest: Return nearest note in <key>.

        >>>
        >>> p.nextn(16)
        []
        """
    def __init__(self, input, key):
        self.input = input
        self.key = key

    def __next__(self):
        note = next(self.input)
        key = Pattern.value(self.key)
        return key.nearest_note(note)

class PMidiToFrequency(Pattern):
    """ PMidiToFrequency: Map MIDI note to frequency value.
        """

    def __init__(self, note):
        self.note = note

    def __next__(self):
        note = Pattern.value(self.note)
        return midi_pitch_to_frequency(note)
