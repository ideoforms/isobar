import random
from .util import *

class Scale(object):
    dict = { }

    def __init__(self, semitones = [ 0, 2, 4, 5, 7, 9, 11 ], name = "unnamed scale", octave_size = 12):
        self.semitones = semitones
        """ For polymorphism with WeightedScale -- assume all notes equally weighted. """
        self.weights = [ 1.0 / len(self.semitones) for _ in range(len(self.semitones)) ]
        self.name = name
        self.octave_size = octave_size
        if name not in Scale.dict:
           Scale.dict[name] = self

    def __str__(self):
        return "%s %s" % (self.name, self.semitones)

    def __getitem__(self, key):
        return self.get(key)

    def __eq__(self, other):
        return self.semitones == other.semitones and self.octave_size == other.octave_size

    def __contains__(self, semitone):
        return (semitone % self.scale.octave_size) in self.semitones

    def get(self, n):
        """ Retrieve the n'th degree of this scale. """
        if n is None:
            return None

        octave = int(n / len(self.semitones))
        degree = n % len(self.semitones)
        note = (self.octave_size * octave) + self.semitones[degree]
        return note

    def copy(self):
        other = Scale(self.semitones, self.name)
        return other

    def change(self):
        """ Exchange two random elements of this scale. """
        i = random.randint(0, len(self.semitones) - 1)
        j = random.randint(0, len(self.semitones) - 1)
        if i != j:
            tmp = self.semitones[i]
            self.semitones[i] = self.semitones[j]
            self.semitones[j] = tmp
        return self

    def shuffle(self):
        random.shuffle(self.semitones)
        return self

    def indexOf(self, note):
        """ Return the index of the given note within this scale. """
        octave = int(note / self.octave_size)
        index = octave * len(self.semitones)
        note -= octave * self.octave_size
        degree = 0

        while note > self.semitones[degree] and degree < len(self.semitones) - 1:
            degree += 1

        index += degree
        return index

    @staticmethod
    def fromnotes(notes, name = "unnamed scale", octave_size = 12):
        notes = [ note % octave_size for note in notes ]
        notes = list(dict((k, k) for k in notes).keys())
        notes = sorted(notes)
        scale = Scale(notes, name = name, octave_size = octave_size)
        return scale

    @staticmethod
    def all():
        return list(Scale.dict.values())

    @staticmethod
    def byname(name):
        return Scale.dict[name]

    @staticmethod
    def random():
        key = random.choice(list(Scale.dict.keys()))
        return Scale.dict[key]

Scale.chromatic     = Scale([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ], "chromatic")
Scale.major         = Scale([ 0, 2, 4, 5, 7, 9, 11 ], "major")
Scale.maj7          = Scale([ 0, 2, 4, 5, 7, 9, 10 ], "maj7") ## XXX?
Scale.minor         = Scale([ 0, 2, 3, 5, 7, 8, 11 ], "minor")
Scale.pureminor     = Scale([ 0, 3, 7 ], "pureminor")
Scale.puremajor     = Scale([ 0, 4, 7 ], "puremajor")
Scale.minorPenta    = Scale([ 0, 3, 5, 7, 10 ], "minorPenta")
Scale.majorPenta    = Scale([ 0, 2, 4, 7, 9 ], "majorPenta")
Scale.ritusen       = Scale([ 0, 2, 5, 7, 9 ], "ritusen")
Scale.pelog         = Scale([ 0, 1, 3, 7, 8 ], "pelog")
Scale.augmented     = Scale([ 0, 3, 4, 7, 8, 11 ], "augmented")
Scale.augmented2    = Scale([ 0, 1, 4, 5, 8, 9 ], "augmented 2")
Scale.wholetone     = Scale([ 0, 2, 4, 6, 8, 10 ], "wholetone")

Scale.ionian        = Scale([ 0, 2, 4, 5, 7, 9, 11 ], "ionian")
Scale.dorian        = Scale([ 0, 2, 3, 5, 7, 9, 10 ], "dorian")
Scale.phrygian      = Scale([ 0, 1, 3, 5, 7, 8, 10 ], "phrygian")
Scale.lydian        = Scale([ 0, 2, 4, 6, 7, 9, 11 ], "lydian")
Scale.mixolydian    = Scale([ 0, 2, 4, 5, 7, 9, 10 ], "mixolydian")
Scale.aeolian       = Scale([ 0, 2, 3, 5, 7, 8, 10 ], "aeolian")
Scale.locrian       = Scale([ 0, 1, 3, 5, 6, 8, 10 ], "locrian")
Scale.fourths        = Scale([ 0, 2, 5, 7 ], "fourths")

#------------------------------------------------------------------------
# Use major scale as a global default. This can be overriden by user.
#------------------------------------------------------------------------
Scale.default        = Scale.major

class WeightedScale(Scale):
    def __init__(self, semitones = [ 0, 2, 4, 5, 7, 9, 11 ], weights = [ 1/7.0 ] * 7, name = "major", octave_size = 12):
        Scale.__init__(self, semitones, name = name, octave_size = octave_size)
        self.weights = weights
        if name not in Scale.dict:
           Scale.dict[name] = self

    def __str__(self):
        return "%s %s weights = %s" % (self.name, self.semitones, self.weights)

    @staticmethod
    def fromnotes(notes, name = "unnamed scale", octave_size = 12):
        note_sequence = [ note % octave_size for note in notes ]
        notes_dict = {}
        for note in note_sequence:
            if not note in notes_dict:
                notes_dict[note] = 0
            notes_dict[note] += 1.0 / len(note_sequence)

        notes_unique = list(dict((k, k) for k in note_sequence).keys())
        notes_unique = sorted(notes_unique)
        weights = []
        for note in notes_unique:
            weights.append(notes_dict[note])
        
        scale = WeightedScale(notes_unique, weights, name = name, octave_size = octave_size)
        return scale

    @staticmethod
    def fromorder(notes, name = "unnamed scale", octave_size = 12):
        notes = [ note % octave_size for note in notes ]
        weights = [ len(notes) - n for n in range(len(notes)) ]
        weights = normalize(weights)

        scale = WeightedScale(notes, weights, name = name, octave_size = octave_size)
        return scale
        
