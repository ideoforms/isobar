from typing import Union
import numpy as np

from ..output import OutputDevice

class NeoPixelColour (np.ndarray):
    pass

class NeoPixelOutputDevice (OutputDevice):
    def __init__(self, num_pixels: int = 1):
        super().__init__()
        self.num_pixels = num_pixels
        self.colour_dict = {}

    def define_colour(self, colour_name: str, rgb: tuple):
        if colour_name in self.colour_dict:
            raise ValueError(f"Colour '{colour_name}' is already defined.")
        self.colour_dict[colour_name] = np.array(rgb)
    
    def get_colour(self, colour_name: str):
        if colour_name not in self.colour_dict:
            raise ValueError("Colour name not found: %s" % colour_name)
        return self.colour_dict[colour_name]
    
    def set_pixel(self, pixel: int, colour: Union[str, tuple]):
        if pixel < 0 or pixel >= self.num_pixels:
            raise ValueError("Invalid pixel index: %d" % pixel)
        if isinstance(colour, str):
            if colour not in self.colour_dict:
                raise ValueError("Colour name not found: %s" % colour)
            colour = self.colour_dict[colour]
        colour = tuple([int(round(c)) for c in colour])

        # TODO: actually set pixel value
        print("set_pixel: %d, %s" % (pixel, colour))

    def set_all_pixels(self, colour: Union[str, tuple]):
        for pixel in range(self.num_pixels):
            self.set_pixel(pixel, colour)