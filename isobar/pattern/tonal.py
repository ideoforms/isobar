from __future__ import annotations
from .core import Pattern
from ..scale import Scale
from ..util import midi_note_to_frequency, midi_semitones_to_frequency_ratio

import typing
from typing import Iterable

class PDegree(Pattern):
    """ PDegree: Map scale index <degree> to MIDI notes in <scale>.

        >>> p = PDegree(PSeries(0, 1), Scale.major)
        >>> p.nextn(16)
        [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26]
        """

    def __init__(self, degree, scale=Scale.major):
        dg_list = list(degree.copy())

        if dg_list != [None]:
            dg_list = self._replace_none_with_zero(dg_list)
            dg_list = [dg for dg in dg_list if dg is not None]
            scale_down = dg_list[0] > dg_list[-1]
        else:
            scale_down = False

        self.scale_down = scale_down
        self.degree = degree
        self.scale = scale

    def _replace_none_with_zero(self, lst):
        return [
            self._replace_none_with_zero(item) if isinstance(item, list) else 0 if item is None else item
            for item in lst
        ]

    def __repr__(self):
        return ("PDegree(%s, %s)" % (repr(self.degree), repr(self.scale)))

    def __next__(self):
        degree = Pattern.value(self.degree)
        scale = Pattern.value(self.scale)
        if degree is None:
            return None

        if isinstance(degree, typing.Iterable):
            return tuple(scale.get(degree, scale_down=self.scale_down) for degree in degree)
        else:
            return scale.get(degree,scale_down=self.scale_down)

class PFilterByKey(Pattern):
    """ PFilterByKey: Filter notes based on their presence in <key>.
        IF a note is not in <key>, None is returned instead.
        To compress the output and remove rests, use PCollapse.

        >>> p = PFilterByKey(PSeries(0, 1), Key("C", "major"))
        >>> p.nextn(16)
        [0, None, 2, None, 4, 5, None, 7, None, 9, None, 11, 12, None, 14, None]
        """

    def __init__(self, pattern: Pattern, key: Iterable):
        self.pattern = pattern
        self.key = key

    def __repr__(self):
        return ("PFilterByKey(%s, %s)" % (repr(self.pattern), repr(self.key)))

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

    abbreviation = "pnearestnote"
    
    def __init__(self, pattern: Pattern, key: Iterable):
        self.pattern = pattern
        self.key = key

    def __repr__(self):
        return ("PNearestNoteInKey(%s, %s)" % (repr(self.pattern), repr(self.key)))

    def __next__(self):
        note = Pattern.value(self.pattern)
        key = Pattern.value(self.key)
        return key.nearest_note(note)

class PMidiNoteToFrequency(Pattern):
    """ PMidiNoteToFrequency: Map MIDI note to frequency value.
        """
    
    abbreviation = "pnotetofreq"

    def __init__(self, input):
        self.input = input

    def __repr__(self):
        return ("PMidiNoteToFrequency(%s)" % repr(self.input))

    def __next__(self):
        note = Pattern.value(self.input)
        if note is None:
            return None
        return midi_note_to_frequency(note)

class PMidiSemitonesToFrequencyRatio(Pattern):
    """ PMidiSemitonesToFrequencyRatio: Map a MIDI offet in semitones to a frequency ratio.
        e.g. 0 -> 1.0
             12 -> 2.0
             7 -> 1.5
        """
    
    abbreviation = "psemistofreq"

    def __init__(self, input):
        self.input = input

    def __next__(self):
        note = Pattern.value(self.input)
        if note is None:
            return None
        return midi_semitones_to_frequency_ratio(note)