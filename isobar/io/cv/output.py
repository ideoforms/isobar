import logging

from ..output import OutputDevice

logger = logging.getLogger("isobar")


def get_cv_output_devices():
    import sounddevice
    return list(sounddevice.query_devices())

class CVChannelMapping:
    def __init__(self,
                 channel_index: int,
                 property_name: str):

        if property_name not in ["note", "gate", "trigger", "envelope", "velocity", "clock"]:
            raise ValueError("Invalid property_name: %s" % property_name)

        self.channel_index = channel_index
        self.property_name = property_name

class CVChannelMappings:
    def __init__(self, mappings: list[CVChannelMapping] = []):
        self.mappings = mappings.copy()

        # Note stealing mode. Might consider: last, highest, lowest, random, none
        self.note_priority = "last"

        # Maximum number of simultaneous notes
        self.polyphony = 1

    def add_mapping(self, mapping: CVChannelMapping):
        self.mappings.append(mapping)

    def __iter__(self):
        return iter(self.mappings)

class CVOutputDevice(OutputDevice):
    """
    CVOutputDevice: Sends output to CV over an audio I/O device.
    """

    def __init__(self,
                 device_name: str = None,
                 sample_rate: int = 44100,
                 channel_mappings: CVChannelMappings = None,
                 graph: "AudioGraph" = None):
        """
        Create a control voltage output device.

        Control voltage signals require a DC-coupled audio interface, which Python
        sends audio signals to via the sounddevice library. 

        Args:
            device_name (str): Name of the audio output device to use.
                               To query possible names, call get_cv_output_devices().
            sample_rate (int): Audio sample rate to use.
            channel_mappings (CVChannelMappings): Mapping of CV channels to properties (note, gate, velocity, clock).
        """
        super().__init__()

        from signalflow import AudioGraph, Constant, ChannelArray, Impulse

        self.channel_mappings = channel_mappings
        if channel_mappings is None:
            self.channel_mappings = CVChannelMappings()

        if graph:
            self.graph = graph
        else:
            self.graph = AudioGraph.get_shared_graph()
            if self.graph is None:
                try:
                    self.graph = AudioGraph(start=True)
                except NameError:
                    raise Exception("Could not instantiate SignalFlowOutputDevice, signalflow not installed?")

        #--------------------------------------------------------------------------------
        # Lazily import sounddevice, to avoid the additional time cost of initializing
        # PortAudio when not needed
        #--------------------------------------------------------------------------------

        # Expert Sleepers ES-8 supports entire -10V to +10V range
        self.output_voltage_max = 3
        self.num_channels = self.graph.num_output_channels
        self.channel_outputs = [0] * self.num_channels
        for mapping in self.channel_mappings:
            if mapping.property_name == "note":
                self.channel_outputs[mapping.channel_index] = Constant(0)
            elif mapping.property_name == "trigger":
                self.channel_outputs[mapping.channel_index] = Impulse(0)
        self.note_slots = [None] * self.channel_mappings.polyphony
        self.channel_array = ChannelArray(self.channel_outputs)
        self.channel_array.play()
        self.midi_note_base = 60

        logger.info("Started CV output with %d channels" % self.num_channels)

    def _note_index_to_amplitude(self, note):
        note_float = (note - self.midi_note_base) / (12 * self.output_voltage_max)
        if note_float < -1.0 or note_float > 1.0:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)
        return note_float

    def _get_next_slot_index(self):
        for index, slot in enumerate(self.note_slots):
            if slot is None:
                return index
        return None

    def _clear_slot_for_note(self, note: int):
        for index, slot_note in enumerate(self.note_slots):
            if slot_note == note:
                self.note_slots[index] = None

    def note_on(self, note=60, velocity=64, channel=0):
        note_float = self._note_index_to_amplitude(note)
        slot_index = self._get_next_slot_index()
        if slot_index is not None:
            # Begin playing note through slot
            self.note_slots[slot_index] = note

            for mapping in self.channel_mappings:
                if mapping.property_name == "note":
                    self.channel_outputs[mapping.channel_index].set_value(note_float)
                elif mapping.property_name == "velocity":
                    self.channel_outputs[mapping.channel_index].set_value(velocity / 127.0)
                elif mapping.property_name == "trigger":
                    self.channel_outputs[mapping.channel_index].trigger()

        else:
            logger.warning("No free slots available for note %d" % note)

    def note_off(self, note=60, channel=0):
        self._clear_slot_for_note(note)

    def control(self, control, value, channel=0):
        pass


if __name__ == "__main__":
    import time
    mappings = CVChannelMappings([CVChannelMapping(0, "note"), CVChannelMapping(1, "trigger")])
    cv_output = CVOutputDevice(channel_mappings=mappings)
    while True:
        for note in [60, 62, 64, 67]:
            cv_output.note_on(note=note, velocity=64, channel=0)
            time.sleep(0.25)
            cv_output.note_off(note=note)
            time.sleep(0.25)
    
