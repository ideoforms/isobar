from ..output import OutputDevice

import logging

log = logging.getLogger(__name__)

try:
    import fluidsynth
except ModuleNotFoundError:
    pass

class FluidSynthOutputDevice (OutputDevice):
    """
    FluidSynthOutputDevice: Sends events to the FluidSynth soundfont host.
    """

    def __init__(self, soundfont_path: str, presets: list[int] = [0]):
        """
        Args:
            soundfont_path: Path to an .sf2 sound font file.
            presets: Optionally, a list of one or more General MIDI sounds to use, one per channel.
                     By default, initialises one channel set to Piano.
                     
                     Full list of General MIDI presets:
                     https://en.wikipedia.org/wiki/General_MIDI

        """
        super().__init__()
        try:
            self.synth = fluidsynth.Synth()
            self.synth.start()

            self.sfid = self.synth.sfload(soundfont_path)
            if presets:
                for index, preset in enumerate(presets):
                    self.synth.program_select(chan=index,
                                              sfid=self.sfid,
                                              bank=0,
                                              preset=preset)

        except NameError:
            raise Exception("The pyfluidsynth package must be installed: pip3 install pyfluidsynth")

    def note_on(self, note: int = 60, velocity: int = 64, channel: int = 0):
        self.synth.noteon(channel, note, velocity)

    def note_off(self, note: int = 60, channel: int = 0):
        self.synth.noteoff(channel, note)

    def control(self, control, value, channel=0):
        pass
