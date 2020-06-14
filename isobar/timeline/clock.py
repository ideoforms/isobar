from ..constants import DEFAULT_TEMPO, DEFAULT_TICKS_PER_BEAT

import time
import logging

log = logging.getLogger(__name__)

#----------------------------------------------------------------------
# A Clock is relied upon to generate accurate tick() events every
# fraction of a note. it should handle millisecond-level jitter
# internally - ticks should always be sent out on time!
#
# Period, in seconds, corresponds to a 24th crotchet (1/96th of a bar),
# as per MIDI
#----------------------------------------------------------------------

class Clock:
    def __init__(self,
                 clock_target=None,
                 tempo=DEFAULT_TEMPO,
                 ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
        self.clock_target = clock_target
        self.tick_duration_seconds = None
        self.tick_duration_seconds_orig = None
        self._tempo = tempo
        self.ticks_per_beat = ticks_per_beat
        self.warpers = []
        self.accelerate = 1.0

    def _calculate_tick_duration(self):
        self.tick_duration_seconds = 60.0 / (self.tempo * self.ticks_per_beat)
        self.tick_duration_seconds_orig = self.tick_duration_seconds

    def get_ticks_per_beat(self):
        return self._ticks_per_beat

    def set_ticks_per_beat(self, ticks_per_beat):
        self._ticks_per_beat = ticks_per_beat
        self._calculate_tick_duration()

    ticks_per_beat = property(get_ticks_per_beat, set_ticks_per_beat)

    def get_tempo(self):
        return self._tempo

    def set_tempo(self, tempo):
        self._tempo = tempo
        self._calculate_tick_duration()

    tempo = property(get_tempo, set_tempo)

    def run(self):
        clock0 = clock1 = time.time() * self.accelerate
        #------------------------------------------------------------------------
        # allow a tick to elapse before we call tick() for the first time
        # to keep Warp patterns in sync  
        #------------------------------------------------------------------------
        while True:
            if clock1 - clock0 >= (2.0 * self.tick_duration_seconds):
                log.warning("Clock overflowed!")

            if clock1 - clock0 >= self.tick_duration_seconds:
                # time for a tick
                self.clock_target.tick()
                clock0 += self.tick_duration_seconds
                self.tick_duration_seconds = self.tick_duration_seconds_orig
                for warper in self.warpers:
                    warp = next(warper)
                    #------------------------------------------------------------------------
                    # map [-1..1] to [0.5, 2]
                    #  - so -1 doubles our tempo, +1 halves it
                    #------------------------------------------------------------------------
                    warp = pow(2, warp)
                    self.tick_duration_seconds *= warp

            time.sleep(0.0001)
            clock1 = time.time() * self.accelerate

    def warp(self, warper):
        self.warpers.append(warper)

    def unwarp(self, warper):
        self.warpers.remove(warper)

class DummyClock (Clock):
    """
    Clock subclass used in testing, which ticks at the highest rate possible.
    """
    def run(self):
        while True:
            self.clock_target.tick()
