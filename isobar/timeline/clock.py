import time
from ..constants import TICKS_PER_BEAT

#----------------------------------------------------------------------
# A Clock is relied upon to generate accurate tick() events every
# fraction of a note. it should handle millisecond-level jitter
# internally - ticks should always be sent out on time!
#
# Period, in seconds, corresponds to a 24th crotchet (1/96th of a bar),
# as per MIDI
#----------------------------------------------------------------------

class DummyClock:
    def __init__(self):
        self.clock_target = None

    @property
    def bpm(self):
        return 0.0

    def run(self):
        while True:
            self.clock_target.tick()

class Clock:
    def __init__(self, clock_target, tick_size=(1.0 / TICKS_PER_BEAT)):
        self.clock_target = clock_target
        self.tick_size_orig = tick_size
        self.tick_size = tick_size
        self.warpers = []
        self.accelerate = 1.0

    @property
    def bpm(self):
        return 60.0 / (self.tick_size * TICKS_PER_BEAT)

    def run(self):
        clock0 = clock1 = time.time() * self.accelerate
        #------------------------------------------------------------------------
        # allow a tick to elapse before we call tick() for the first time
        # to keep Warp patterns in sync  
        #------------------------------------------------------------------------
        while True:
            if clock1 - clock0 >= self.tick_size:
                # time for a tick
                self.clock_target.tick()
                clock0 += self.tick_size
                self.tick_size = self.tick_size_orig
                for warper in self.warpers:
                    warp = next(warper)
                    #------------------------------------------------------------------------
                    # map [-1..1] to [0.5, 2]
                    #  - so -1 doubles our tempo, +1 halves it
                    #------------------------------------------------------------------------
                    warp = pow(2, warp)
                    self.tick_size *= warp

            time.sleep(0.001)
            clock1 = time.time() * self.accelerate

    def warp(self, warper):
        self.warpers.append(warper)

    def unwarp(self, warper):
        self.warpers.remove(warper)
