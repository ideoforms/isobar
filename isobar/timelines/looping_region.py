from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..timelines.track import Track

class LoopingRegion:
    def __init__(self,
                 track: Track,
                 start_time: float,
                 end_time: float):
        self.track = track
        self.start_time = start_time
        self.end_time = end_time
        self.loop = True