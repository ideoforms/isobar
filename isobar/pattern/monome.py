"""
Interfaces for the Monome controllers
"""

from .core import Pattern
from ..util import scale_lin_lin, scale_lin_exp, scale_exp_lin
import time

from typing import Callable

try:
    from monome import ArcUI, NoDevicesFoundError
except ModuleNotFoundError:
    pass

class IsobarMonomeManager:
    shared_manager = None

    def __init__(self, device_name: str = None):
        if IsobarMonomeManager.shared_manager is None:
            IsobarMonomeManager.shared_manager = self

        try:
            self.arc = ArcUI()
            self.arc_page = self.arc.add_page("unipolar")
            self.arc_page.add_handler(self._handle_arc_enc)
            self.ring_handlers = [[] for _ in range(self.arc.ring_count)]

        except NoDevicesFoundError:
            # No Arc found
            self.arc = None

    def add_ring_handler(self, ring: int, handler: Callable):
        if ring < 0 or ring >= self.arc.ring_count:
            raise ValueError("Invalid ring index: %d" % ring)
        self.ring_handlers[ring].append(handler)

    def _handle_arc_enc(self, ring, position, delta):
        for handler in self.ring_handlers[ring]:
            handler(ring, position, delta)

    @staticmethod
    def get_shared_manager():
        if IsobarMonomeManager.shared_manager is None:
            IsobarMonomeManager.shared_manager = IsobarMonomeManager()
        return IsobarMonomeManager.shared_manager


class PMonomeArcControl(Pattern):
    def __init__(self,
                 ring: int = 0,
                 mode: str = "unipolar",
                 min: float = 0,
                 max: float = 1.0,
                 initial: float = 0.0,
                 curve: str = "linear"):
        self.ring = ring
        self.mode = mode
        self.min = min
        self.max = max
        self.value = initial
        assert curve in ["linear", "exponential"]
        self.curve = curve

        manager = IsobarMonomeManager.get_shared_manager()
        if manager.arc is None:
            raise RuntimeError("No Arc was found")

        def ring_handler(_, pos, delta):
            self.on_change(pos / 64)
        manager.add_ring_handler(ring, ring_handler)

        if curve == "linear":
            initial_linear = scale_lin_lin(initial, min, max, 0, 64)
        elif curve == "exponential":
            initial_linear = scale_exp_lin(initial, min, max, 0, 64)

        # TODO - this is generally horrible syntax, improve the rings/control ranges API
        manager.arc_page.rings[ring].position = int(initial_linear)
        manager.arc_page.draw()

    def __str__(self):
        classname = str(self.pattern.__class__).split(".")[-1]
        return "%s(%s)" % (classname, str(self.pattern))

    def __next__(self):
        return self.value

    def on_change(self, value: float):
        if self.curve == "linear":
            value = scale_lin_lin(value, 0, 1, self.min, self.max)
        elif self.curve == "exponential":
            value = scale_lin_exp(value, 0, 1, self.min, self.max)
        else:
            raise ValueError("Invalid value for curve: %s" % self.curve)
        
        self.value = value

if __name__ == "__main__":
    pattern = PMonomeArcControl()
    while True:
        print(next(pattern))
        time.sleep(0.5)