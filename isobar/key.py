from scale import *
from util import *

import random

class Key:
    def __init__(self, tonic = 0, scale = Scale.major):
        if type(tonic) == str:
            tonic = nametomidi(tonic)
        if type(scale) == str:
            scale = Scale.byname(scale)
            
        self.tonic = tonic
        self.scale = scale

    def __str__(self):
        return "key: %s %s" % (miditopitch(self.tonic), self.scale.name)

    def get(self, degree):
        semitone = self.scale[degree]
        return semitone + self.tonic

    def __getitem__(self, degree):
        return self.get(degree)

    def semitones(self):
        semitones = map(lambda n: n + self.tonic, self.scale.semitones)
        return semitones

    def fadeto(self, other, level):
        """level between 0..1"""
        semitones_a = self.semitones()
        semitones_b = other.semitones()
        semitones_shared = filter(lambda n: n in semitones_a, semitones_b)
        semitones_a_only = filter(lambda n: n not in semitones_b, semitones_a)
        semitones_b_only = filter(lambda n: n not in semitones_a, semitones_b)

        if level < 0.5:
            # scale from 1..0
            level = 1.0 - (level * 2)
            count_from_a = int(round(level * len(semitones_a_only)))
            return semitones_shared + semitones_a_only[0:count_from_a]
        else:
            # scale from 0..1
            level = 2 * (level - 0.5)
            count_from_b = int(round(level * len(semitones_b_only)))
            return semitones_shared + semitones_b_only[0:count_from_b]

    def random():
        t = random.randint(0, 11)
        s = Scale.random()
        return key(t, s)

    random = staticmethod(random)
