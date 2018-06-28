""" isobar.pattern.fade: Unary pattern operators to fade a pattern in or out.

    Rather than simply beginning a pattern, we may want to start by playing a
    single note, introducing the rest gradually.
    """

import sys
import random

from isobar.pattern.core import *

class PFade(Pattern):
    IN    = 1
    PEAK  = 0
    OUT   = -1

    def __init__(self):
        self.direction = 1

        self.fadestep = 0
        self.counter = 0
        self.rcounter = 0
        self.pattern = None

    def __str__(self):
        classname = str(p.__class__).split(".")[-1]
        return "%s(%s)" % (classname, str(self.pattern))

class PFadeNotewise(PFade):
    """ PFadeNotewise: Fade a pattern in/out by introducing notes at a gradual rate. """

    def __init__(self, pattern, rate_min = 1, rate_max = 1, repeats = 1, repeats_postfade = 1):
        PFade.__init__(self)

        self.notes = pattern.all()
        self.on = [ False ] * len(self.notes)
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.repeats = repeats
        self.repeats_postfade = repeats_postfade

        self.fadeindex = 0

    def fade_in(self):
        fade_count = random.randint(self.rate_min, self.rate_max)
        for n in range(fade_count):
            if self.fadeindex >= len(self.on):
                return
            self.on[self.fadeindex] = True
            self.fadeindex += 1
            self.fadestep += 1

    def fade_out(self):
        fade_count = random.randint(self.rate_min, self.rate_max)
        for n in range(fade_count):
            if self.fadeindex >= len(self.on):
                return
            self.on[self.fadeindex] = False
            self.fadeindex += 1
            self.fadestep -= 1

    def __next__(self):
        if self.counter >= len(self.notes):
            #----------------------------------------------------------------------
            # we've reached the end of the sequence.
            #----------------------------------------------------------------------
            self.rcounter += 1
            self.counter = 0
            if self.direction == PFade.IN and self.rcounter == self.repeats:
                #----------------------------------------------------------------------
                # we've finished fading in -- now play the complete sequence.
                #----------------------------------------------------------------------
                self.rcounter = 0
                self.fade_in()
                if self.fadestep == len(self.notes):
                    self.direction = PFade.PEAK
            elif self.direction == PFade.OUT and self.rcounter == self.repeats:
                #----------------------------------------------------------------------
                # finish fading out.
                #----------------------------------------------------------------------
                self.rcounter = 0
                self.fade_out()
                if self.fadestep == 0:
                    raise StopIteration
            elif self.direction == PFade.PEAK and self.rcounter == self.repeats_postfade:
                #----------------------------------------------------------------------
                # start fading out.
                #----------------------------------------------------------------------
                self.rcounter = 0
                self.direction = PFade.OUT
                self.fadeindex = 0
                self.fade_out()

        if type(self.notes[self.counter]) == dict:
            if self.on[self.counter]:
                rv = self.notes[self.counter]
            else:
                note = self.notes[self.counter].copy()
                note["note"] = None
                rv = note
        else:
            rv = self.notes[self.counter] if self.on[self.counter] else None
        
        self.counter += 1
            
        return rv

class PFadeNotewiseRandom(PFadeNotewise):
    """ PFadeNotewise: Fade a pattern in/out by gradually introducing random notes. """
    def __init__(self, *args, **kwargs):
        PFadeNotewise.__init__(self, *args, **kwargs)
        self.ordering = list(range(len(self.notes)))
        random.shuffle(self.ordering)

    def fade_in(self):
        fade_count = random.randint(self.rate_min, self.rate_max)
        if fade_count < 1: fade_count = 1
        for n in range(fade_count):
            if self.fadeindex >= len(self.on):
                return
            index = self.ordering[self.fadeindex]
            self.on[index] = True
            self.fadeindex += 1
            self.fadestep += 1

    def fade_out(self):
        fade_count = random.randint(self.rate_min, self.rate_max)
        if fade_count < 1: fade_count = 1
        for n in range(fade_count):
            if self.fadeindex >= len(self.on):
                return
            index = self.ordering[self.fadeindex]
            self.on[index] = False
            self.fadeindex += 1
            self.fadestep -= 1
