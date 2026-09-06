from __future__ import annotations

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..timelines.track import Track

class LoopingRegion:
    def __init__(self,
                 track: Track,
                 start_time: float,
                 end_time: float,
                 loop: Optional[bool] = True):
        self.track = track
        self.start_time = start_time
        self.end_time = end_time
        self.loop = loop

    def to_dict(self):
        return {
            "track": self.track,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "loop": self.loop
        }

    @classmethod
    def from_dict(cls, data: dict) -> LoopingRegion:
        return cls(track=data["track"],
                   start_time=data["start_time"],
                   end_time=data["end_time"],
                   loop=data.get("loop", True))