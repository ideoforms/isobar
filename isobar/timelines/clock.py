from ..constants import DEFAULT_TEMPO, DEFAULT_TICKS_PER_BEAT, MIN_CLOCK_DELAY_WARNING_TIME
from ..util import make_clock_multiplier

import time
import random
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

class Clock:
    def __init__(self,
                 clock_target: Any = None,
                 tempo: float = DEFAULT_TEMPO,
                 ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT):
        """
        A Clock generates tick events at a regular interval, defined by the `ticks_per_beat` property.
        The higher the number of ticks per beat, the finer the granularity events can be triggered.

        Different clocking systems vary in their granularity, typically specified in ticks per beat (crotchet),
        aka "pulses per quarter note", PPQN:
         - MIDI I/O has a resolution of 24 PPQN
         - MIDI files commonly have a resolution of 96 or 120 PPQN, but can vary by file

        isobar defaults to 480 PPQN, which equates to a tick per 1.04ms. This means that events can be
        scheduled in the Timeline with a ~1ms granularity.

        Clock division is needed to interact with other clocking systems, which is handled by
        `make_clock_multiplier`. Timeline contains logic to multiplex between multiple different clock outputs.

        Args:
            clock_target: Clock target, which must have a `tick()` method and `ticks_per_beat` property.
            tempo: Tempo, in BPM.
            ticks_per_beat: The number of tick events generated per quarter-note.
        """
        self.clock_target = clock_target
        self.tick_duration_seconds: float = None
        self.tick_duration_seconds_orig: float = None
        self._tempo: float = tempo
        self.ticks_per_beat: int = ticks_per_beat
        self.warpers = []
        self.accelerate: float = 1.0
        self.thread: threading.Thread = None
        self.running: bool = False
        self.jitter: float = 0.0

        target_ticks_per_beat = self.clock_target.ticks_per_beat if self.clock_target else ticks_per_beat
        self.clock_multiplier = make_clock_multiplier(target_ticks_per_beat, self.ticks_per_beat)

    def _calculate_tick_duration(self):
        self.tick_duration_seconds = 60.0 / (self.tempo * self.ticks_per_beat)
        self.tick_duration_seconds_orig = self.tick_duration_seconds

    def get_ticks_per_beat(self) -> int:
        return self._ticks_per_beat

    def set_ticks_per_beat(self, ticks_per_beat: int):
        self._ticks_per_beat = ticks_per_beat
        self._calculate_tick_duration()

    ticks_per_beat = property(get_ticks_per_beat, set_ticks_per_beat)
    """ Returns the number of ticks per beat. """

    def get_tempo(self):
        return self._tempo

    def set_tempo(self, tempo):
        self._tempo = tempo
        self._calculate_tick_duration()

    tempo = property(get_tempo, set_tempo)
    """ The tempo of this clock, in BPM. """

    def background(self):
        """ Run this Timeline in a background thread. """
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        clock0 = clock1 = time.time() * self.accelerate
        #------------------------------------------------------------------------
        # Allow a tick to elapse before we call tick() for the first time
        # to keep Warp patterns in sync
        #------------------------------------------------------------------------
        self.running = True
        while self.running:
            if clock1 - clock0 >= (2.0 * self.tick_duration_seconds):
                delay_time = (clock1 - clock0 - self.tick_duration_seconds * 2)
                if delay_time > MIN_CLOCK_DELAY_WARNING_TIME:
                    logger.info("Clock: Timer overflowed (late by %.3fs)" % delay_time)

            next_tick_duration = self.tick_duration_seconds
            if self.jitter > 0:
                next_tick_jitter = self.tick_duration_seconds * random.uniform(0, self.jitter)
                next_tick_duration += next_tick_jitter
            while clock1 - clock0 >= next_tick_duration:
                #------------------------------------------------------------------------
                # Time for a tick.
                # Use while() because multiple ticks might need to be processed if the
                # clock has overflowed.
                #------------------------------------------------------------------------
                ticks = next(self.clock_multiplier)
                for _ in range(ticks):
                    self.clock_target.tick()

                clock0 += self.tick_duration_seconds
                self.tick_duration_seconds = self.tick_duration_seconds_orig
                for warper in self.warpers:
                    warp = next(warper)
                    #------------------------------------------------------------------------
                    # map [-1..1] to [0.5, 2]
                    #  - so -1 doubles the tempo, +1 halves it
                    #------------------------------------------------------------------------
                    warp = pow(2, warp)
                    self.tick_duration_seconds *= warp

            time.sleep(0.0001)
            clock1 = time.time() * self.accelerate

    def stop(self):
        self.running = False

    def warp(self, warper):
        self.warpers.append(warper)

    def unwarp(self, warper):
        self.warpers.remove(warper)

    def rewind(self):
        self.clock_target.set_song_pos(0)

class DummyClock(Clock):
    """
    Clock subclass used in testing, which ticks at the highest rate possible.
    """

    def run(self):
        while True:
            self.clock_target.tick()
