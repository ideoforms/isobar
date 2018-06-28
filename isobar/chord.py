import random
import copy

class Chord:
    """ Represents a chord made up of 1 or more note intervals.
    """

    dict = { }

    def __init__(self, intervals = [], root = 0, name = "unnamed chord"):
        self.intervals = intervals
        self.name = name
        self.root = root
        if name not in Chord.dict:
           Chord.dict[name] = self

    def __str__(self):
        return "%s %s%s" % (self.name, self.semitones(), (" + %d" % self.root) if self.root > 0 else "")

    @property
    def semitones(self):
        semitones = [0] + [sum(self.intervals[0:n+1]) for n in range(len(self.intervals))]
        return semitones

    @staticmethod
    def byname(name):
        return Chord.dict[name]

    @staticmethod
    def random():
        key = random.choice(list(Chord.dict.keys()))
        c = copy.deepcopy(Chord.dict[key])
        c.root = random.randint(0, 12)
        return c

    @staticmethod
    def arbitrary(name = "chord"):
        intervals_poss = [ 2, 3, 3, 4, 4, 5, 6 ]
        intervals = []
        top = random.randint(12, 18)
        n = 0
        while True:
            interval = random.choice(intervals_poss)
            n += interval
            if n > top:
                break
            intervals.append(interval)

        return Chord(intervals, 0, name if name else "chord", random.randint(0, 12))

Chord.major            = Chord([ 4, 3, 5 ], 0, "major")
Chord.minor            = Chord([ 3, 4, 5 ], 0, "minor")
Chord.diminished    = Chord([ 3, 3, 6 ], 0, "diminished")
Chord.augmented        = Chord([ 4, 4, 4 ], 0, "diminished")

Chord.sus4            = Chord([ 5, 2, 5 ], 0, "sus4")
Chord.sus2            = Chord([ 7, 2, 5 ], 0, "sus4")
