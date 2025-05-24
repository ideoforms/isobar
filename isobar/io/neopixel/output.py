from typing import Union
import numpy as np
try:
    import neopixel
    import board
except:
    pass

import time
import threading
from ..output import OutputDevice

# TODO
#  - Add support for IsobarProxyOutputDevice, that receives Events over a network and acts upon them 
#  - At the moment, PInterpolate on colour names does not work. Need a nice fix for this.
#    Really we want to interpolate between Event objects, which can do things like colour mappings?
# Support for different kinds of event:
#  - change colour
#  - fade/interpolate between colours
#  - flash
# This should all ideally be handled by the same LFO/automation mechanisms as normal isobar,
# which are themselves not very clearly defined yet.

class NeoPixelColour (np.ndarray):
    pass

class NeoPixelOutputDevice (OutputDevice):
    def __init__(self, num_pixels: int = 1):
        super().__init__()
        self.num_pixels = num_pixels
        self.colour_dict = {}
        self.pixels = neopixel.NeoPixel(board.D18, num_pixels)

        # TODO: support taking a tuple value
        self.set_all_pixels(np.array([0, 0, 0]))

    def define_colour(self, colour_name: str, rgb: tuple):
        if colour_name in self.colour_dict:
            raise ValueError(f"Colour '{colour_name}' is already defined.")
        self.colour_dict[colour_name] = np.array(rgb)
    
    def get_colour(self, colour_name: str):
        if colour_name not in self.colour_dict:
            raise ValueError("Colour name not found: %s" % colour_name)
        return self.colour_dict[colour_name]
    
    def set_pixel(self,
                  pixel: int,
                  colour: Union[str, tuple],
                  alpha: float = 1.0,
                  mode: str = "set"):
        if pixel < 0 or pixel >= self.num_pixels:
            raise ValueError("Invalid pixel index: %d" % pixel)
        if isinstance(colour, str):
            if colour not in self.colour_dict:
                raise ValueError("Colour name not found: %s" % colour)
            colour = self.colour_dict[colour]
        colour = tuple([int(alpha * round(c)) for c in colour])

        # TODO: actually set pixel value
        print("set_pixel: %d, %s" % (pixel, colour))
        current_colour = self.pixels[int(pixel)]
        print(current_colour)
        self.pixels[int(pixel)] = colour

        if mode == "flash":
            # this is a really hacky way to do this! TODO: fix
            def pixel_off(pixel, colour):
                time.sleep(0.05)
                print("set_pixel: %d, %s" % (pixel, colour))
                self.pixels[int(pixel)] = colour
            thread = threading.Thread(target=pixel_off, args=(pixel, current_colour), daemon=True)
            thread.start()
        elif mode == "solo":
            for n in range(self.num_pixels):
                if n != pixel:
                    self.pixels[n] = (0, 0, 0)

    def set_all_pixels(self, colour: Union[str, tuple], alpha: float = 1.0, mode: str = "set"):
        for pixel in range(self.num_pixels):
            self.set_pixel(pixel=pixel,colour=colour, alpha=alpha, mode=mode)