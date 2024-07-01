from ..constants import DEFAULT_TEMPO, DEFAULT_TICKS_PER_BEAT
from .clock import Clock
from typing import Any
import logging
import time

logger = logging.getLogger(__name__)

try:
    import link
except ModuleNotFoundError as e:
    pass

class AbletonLinkClock (Clock):
    def __init__(self,
                 clock_target: Any = None,
                 tempo: float = DEFAULT_TEMPO,
                 ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT):
        self.link_client = link.Link(120)
        self.link_client.enabled = True
        self.link_client.startStopSyncEnabled = True
        self.link_client.setTempoCallback(self.tempo_changed_callback)

        super().__init__(clock_target,
                         tempo,
                         ticks_per_beat)

    def tempo_changed_callback(self, tempo):
        logger.debug("Link: Tempo changed: %.1f" % tempo)

    def run(self):
        ticks_previous = None
        got_sync = False

        while True:
            link_state = self.link_client.captureSessionState()
            link_time = self.link_client.clock().micros()
            #--------------------------------------------------------------------------------
            # Start clock at next 4-beat boundary (next bar, assuming 4/4)
            #--------------------------------------------------------------------------------
            beats = link_state.beatAtTime(link_time, 4)

            ticks_current = int(beats * self.ticks_per_beat)
            if not got_sync:
                if ticks_current % self.ticks_per_beat == 0:
                    got_sync = True
            if ticks_previous is None or ticks_current > ticks_previous:
                if ticks_previous is None:
                    delta_ticks = 1
                else:
                    #--------------------------------------------------------------------------------
                    # Under system load, multiple ticks may have passed since our last timestamp was
                    # received. In this case, send multiple ticks to the timeline to compensate.
                    #--------------------------------------------------------------------------------
                    delta_ticks = ticks_current - ticks_previous
                ticks_previous = ticks_current

                if not got_sync:
                    continue
                for n in range(delta_ticks):
                    self.clock_target.tick()
            time.sleep(0.0001)

    def get_tempo(self):
        link_state = self.link_client.captureSessionState()
        return link_state.tempo()

    def set_tempo(self, tempo):
        link_state = self.link_client.captureSessionState()
        now = self.link_client.clock().micros()
        link_state.setTempo(tempo, now)
        self.link_client.commitSessionState(link_state)

    tempo = property(get_tempo, set_tempo)
