from .core import Pattern
from ..scale import Scale
from ..util import midi_note_to_frequency

import typing

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

        if isinstance(degree, typing.Iterable):
            return tuple(scale[degree] for degree in degree)
        else:
            return scale[degree]

class PFilterByKey(Pattern):
    """ PFilterByKey: Filter notes based on their presence in <key>.
        IF a note is not in <key>, None is returned instead.
        To compress the output and remove rests, use PCollapse.

        >>> p = PFilterByKey(PSeries(0, 1), Key("C", "major"))
        >>> p.nextn(16)
        [0, None, 2, None, 4, 5, None, 7, None, 9, None, 11, 12, None, 14, None]
        """

    def __init__(self, pattern, key):
        self.pattern = pattern
        self.key = key

    def __next__(self):
        note = Pattern.value(self.pattern)
        key = Pattern.value(self.key)
        if note in key:
            return note
        else:
            return None

class PNearestNoteInKey(Pattern):
    """ PNearestNoteInKey: Return the nearest note in <key>.

        >>> p = PNearestNoteKey(PSeries(0, 1), Key("C", "major"))
        >>> p.nextn(16)
        [0, 0, 2, 2, 4, 5, 5, 7, 7, 9, 9, 11, 12, 12, 14, 14]
        """
    def __init__(self, pattern, key):
        self.pattern = pattern
        self.key = key

    def __next__(self):
        note = Pattern.value(self.pattern)
        key = Pattern.value(self.key)
        return key.nearest_note(note)

class PMidiNoteToFrequency(Pattern):
    """ PMidiNoteToFrequency: Map MIDI note to frequency value.
        """

    def __init__(self, input):
        self.input = input

    def __next__(self):
        note = Pattern.value(self.input)
        if note is None:
            return None
        return midi_note_to_frequency(note)
