import logging
import re
from typing import Optional, Union

from ..output import OutputDevice

logger = logging.getLogger("isobar")

# Resolution of the CV clock, in ticks per beat. 24 matches MIDI clock, and divides evenly into all
# whole, half, quarter, eighth, sixteenth and thirty-second notes and their triplets.
CV_CLOCK_TICKS_PER_BEAT = 24

# Length of trigger and clock pulses, in seconds
CV_TRIGGER_DURATION = 0.02

# Attack and release of envelope outputs, in seconds. Envelopes rise from 0V to the top of the output voltage range,
# and sustain for the note's duration.
CV_ENVELOPE_ATTACK = 0.01
CV_ENVELOPE_RELEASE = 0.1

# Properties that belong to a single voice, and so take a voice_index
CV_VOICE_PROPERTIES = ["note", "gate", "trigger", "envelope", "velocity"]
CV_PROPERTIES = CV_VOICE_PROPERTIES + ["clock", "control"]

# Which notes keep sounding when more notes are held than there are voices
CV_NOTE_PRIORITIES = ["last", "first", "lowest", "highest"]


def get_cv_output_devices():
    import sounddevice
    return list(sounddevice.query_devices())


def parse_clock_division(division: Union[str, float, int], beats_per_bar: float = 4) -> float:
    """
    Returns the length of a clock division in beats. The division can be a number of beats, or a note length:
    "4n" is a quarter note, "16n" a sixteenth note, "8t" an eighth-note triplet, "4n." a dotted quarter note,
    and "1m" one bar (of beats_per_bar beats).
    """
    if isinstance(division, (int, float)):
        beats = float(division)
    else:
        match = re.fullmatch(r"(\d+)(n\.?|t|m)", division.strip())
        if match is None:
            raise ValueError("Invalid clock division: %s (expected e.g. 4n, 8t, 4n. or 1m)" % division)
        count, kind = int(match.group(1)), match.group(2)
        if count == 0:
            raise ValueError("Invalid clock division: %s" % division)
        if kind == "m":
            beats = count * beats_per_bar
        else:
            beats = 4.0 / count
            if kind == "t":
                beats *= 2 / 3
            elif kind == "n.":
                beats *= 1.5
    if beats <= 0:
        raise ValueError("Invalid clock division: %s" % division)
    return beats


class CVChannelMapping:
    def __init__(self,
                 channel_index: int,
                 property_name: str,
                 voice_index: int = None,
                 division: Union[str, float, int] = "4n",
                 control_index: int = None,
                 voltage_range: tuple[float, float] = None):
        """
        Maps one output channel to a property.

        Args:
            channel_index (int): The output channel, from 0.
            property_name (str): One of: note (pitch), gate, trigger, envelope, velocity, clock, control.
            voice_index (int): For note, gate, trigger, envelope and velocity: the voice whose property is sent.
                               Defaults to 0.
            division: For clock: how often to send a pulse, as a number of beats or a note length such as "16n"
                      (see parse_clock_division). Defaults to once per beat.
            control_index (int): For control: the control whose continuous value is sent, set with
                                 CVOutputDevice.set_control. Defaults to 0.
            voltage_range: For control: the voltages sent at the control's minimum and maximum values.
                           Defaults to the device's whole output voltage range.
        """
        if property_name not in CV_PROPERTIES:
            raise ValueError("Invalid property_name: %s" % property_name)

        if property_name in CV_VOICE_PROPERTIES:
            if voice_index is None:
                voice_index = 0
            if voice_index < 0:
                raise ValueError("Invalid voice_index: %d" % voice_index)
        elif voice_index is not None:
            raise ValueError("%s outputs do not belong to a voice" % property_name)

        if property_name == "control":
            if control_index is None:
                control_index = 0
            if control_index < 0:
                raise ValueError("Invalid control_index: %d" % control_index)
            if voltage_range is not None:
                voltage_range = (float(voltage_range[0]), float(voltage_range[1]))
                if voltage_range[1] <= voltage_range[0]:
                    raise ValueError("Invalid voltage_range: %s" % (voltage_range,))
        elif control_index is not None or voltage_range is not None:
            raise ValueError("Only control outputs take a control_index or voltage_range")

        self.channel_index = channel_index
        self.property_name = property_name
        self.voice_index = voice_index
        self.division = division if property_name == "clock" else None
        self.control_index = control_index
        self.voltage_range = voltage_range


class CVChannelMappings:
    def __init__(self,
                 mappings: list[CVChannelMapping] = None,
                 note_priority: str = "last"):
        """
        The set of channel mappings for a CV output device.

        Args:
            mappings: The channel mappings. The number of notes that can sound at once is the number of voices
                      that they use, numbered from 0.
            note_priority: Which notes sound when more are held than there are voices:
                            - last: the most recent notes (a new note takes over the oldest voice)
                            - first: the earliest notes (a new note waits until a voice is free)
                            - lowest: the lowest notes
                            - highest: the highest notes
                           When a sounding note is released, a held note that was waiting takes over its voice.
        """
        self.mappings = list(mappings) if mappings else []
        self.note_priority = note_priority

    def get_note_priority(self) -> str:
        return self._note_priority

    def set_note_priority(self, note_priority: str):
        if note_priority not in CV_NOTE_PRIORITIES:
            raise ValueError("Invalid note_priority: %s (expected one of: %s)"
                             % (note_priority, ", ".join(CV_NOTE_PRIORITIES)))
        self._note_priority = note_priority

    note_priority = property(get_note_priority, set_note_priority)

    @property
    def num_voices(self) -> int:
        """
        The number of voices that the mappings use, which is the number of notes that can sound at once.
        Raises a ValueError if the voice numbers have a gap, as that voice would have no outputs.
        """
        voice_indices = set(mapping.voice_index for mapping in self.mappings if mapping.voice_index is not None)
        missing_indices = set(range(len(voice_indices))) - voice_indices
        if missing_indices:
            raise ValueError("Voices must be numbered from 0 with no gaps, but voice %d has no outputs"
                             % min(missing_indices))
        return len(voice_indices)

    @property
    def num_controls(self) -> int:
        """
        The number of controls that the mappings send. Several channels can send the same control.
        Raises a ValueError if the control numbers have a gap.
        """
        control_indices = set(mapping.control_index for mapping in self.mappings
                              if mapping.property_name == "control")
        missing_indices = set(range(len(control_indices))) - control_indices
        if missing_indices:
            raise ValueError("Controls must be numbered from 0 with no gaps, but control %d has no outputs"
                             % min(missing_indices))
        return len(control_indices)

    def add_mapping(self, mapping: CVChannelMapping):
        self.mappings.append(mapping)

    def __iter__(self):
        return iter(self.mappings)


class CVVoice:
    """
    One voice of a CV output device, and the channels that send its properties.
    """
    def __init__(self, index: int):
        self.index = index
        self.note: Optional[int] = None
        self.velocity: int = 0
        self.last_used: int = 0
        """ When the voice last started or stopped a note, used to pick the free voice that has rested longest. """
        self.mappings: list[CVChannelMapping] = []

    @property
    def is_free(self) -> bool:
        return self.note is None


class CVOutputDevice(OutputDevice):
    """
    CVOutputDevice: Sends output to CV over an audio I/O device.
    """

    def __init__(self,
                 device_name: str = None,
                 sample_rate: int = 44100,
                 channel_mappings: CVChannelMappings = None,
                 graph: "AudioGraph" = None,
                 output_voltage_range: tuple[float, float] = (-3, 3),
                 zero_volt_note: float = 60,
                 beats_per_bar: float = 4,
                 name: str = "CV"):
        """
        Create a control voltage output device.

        Control voltage signals require a DC-coupled audio interface, which Python
        sends audio signals to via the sounddevice library.

        Args:
            device_name (str): Name of the audio output device to use, or None for the system default.
                               To query possible names, call get_cv_output_devices(). Ignored if graph is given,
                               or if another device has already started the shared graph.
            sample_rate (int): Audio sample rate to use, when starting the graph.
            channel_mappings (CVChannelMappings): Mapping of CV channels to properties (note, gate, velocity, clock).
            output_voltage_range: The voltages that the interface outputs at sample values -1 and 1.
            zero_volt_note: The MIDI note that is sent as 0V on note channels, at 1V per octave.
            beats_per_bar: The number of beats in a bar, for clock divisions in bars such as "1m".
            name: The device's name, e.g. as saved with a track.
        """
        super().__init__()
        self.name = name

        from signalflow import AudioGraph, AudioGraphConfig, Constant, ChannelArray, RectangularEnvelope, ASREnvelope

        self.channel_mappings = channel_mappings
        if channel_mappings is None:
            self.channel_mappings = CVChannelMappings()

        if graph:
            self.graph = graph
        else:
            self.graph = AudioGraph.get_shared_graph()
            if self.graph is None:
                config = AudioGraphConfig()
                config.sample_rate = sample_rate
                if device_name is not None:
                    config.output_device_name = device_name
                self.graph = AudioGraph(config=config, start=True)
            elif device_name is not None and self.graph.output_device_name != device_name:
                logger.warning("CV output is using the shared audio graph's device, not %s" % device_name)

        # Expert Sleepers ES-8 supports entire -10V to +10V range
        self.output_voltage_min, self.output_voltage_max = output_voltage_range
        if self.output_voltage_max <= self.output_voltage_min:
            raise ValueError("Invalid output_voltage_range: %s" % (output_voltage_range,))
        self.zero_volt_note = zero_volt_note
        self.beats_per_bar = beats_per_bar

        self.num_channels = self.graph.num_output_channels
        self.channel_outputs = [0] * self.num_channels
        self.voices = [CVVoice(index) for index in range(self.channel_mappings.num_voices)]
        self.num_controls = self.channel_mappings.num_controls
        self.clock_mappings: list[tuple[CVChannelMapping, int]] = []
        """ Each clock mapping, with its division in ticks. """

        for mapping in self.channel_mappings:
            if mapping.channel_index < 0 or mapping.channel_index >= self.num_channels:
                raise ValueError("Channel %d is outside the device's %d output channels"
                                 % (mapping.channel_index, self.num_channels))

            if mapping.property_name in ("note", "velocity", "gate"):
                self.channel_outputs[mapping.channel_index] = Constant(0)
            elif mapping.property_name in ("trigger", "clock"):
                self.channel_outputs[mapping.channel_index] = RectangularEnvelope(CV_TRIGGER_DURATION)
            elif mapping.property_name == "envelope":
                self.channel_outputs[mapping.channel_index] = ASREnvelope(CV_ENVELOPE_ATTACK, 0, CV_ENVELOPE_RELEASE)
            elif mapping.property_name == "control":
                if mapping.voltage_range is not None:
                    low, high = mapping.voltage_range
                    if low < self.output_voltage_min or high > self.output_voltage_max:
                        raise ValueError("Channel %d's voltage range (%gV to %gV) is outside the device's (%gV to %gV)"
                                         % (mapping.channel_index, low, high,
                                            self.output_voltage_min, self.output_voltage_max))
                # Starts at the bottom of its range, the control's minimum value
                self.channel_outputs[mapping.channel_index] = Constant(
                    self._voltage_to_amplitude(self._control_voltage(mapping, 0.0)))

            if mapping.voice_index is not None:
                self.voices[mapping.voice_index].mappings.append(mapping)

            if mapping.property_name == "clock":
                self.clock_mappings.append((mapping, self._division_to_ticks(mapping.division)))

        self.held_notes: list[tuple[int, int]] = []
        """ The (note, velocity) of each note that is held down, in the order they started. """
        self.voice_counter = 0
        self.tick_count = 0

        self.channel_array = ChannelArray(self.channel_outputs)
        self.channel_array.play()

        logger.info("Started CV output with %d channels, %d voices" % (self.num_channels, len(self.voices)))

    @property
    def ticks_per_beat(self):
        # CV devices are sent CV_CLOCK_TICKS_PER_BEAT ticks per beat, at the specified tempo,
        # which are divided down to send clock signals.
        return CV_CLOCK_TICKS_PER_BEAT

    def _division_to_ticks(self, division) -> int:
        ticks = parse_clock_division(division, self.beats_per_bar) * CV_CLOCK_TICKS_PER_BEAT
        if abs(ticks - round(ticks)) > 1e-6 or round(ticks) < 1:
            raise ValueError("Clock division %s is too fine: the CV clock has %d ticks per beat"
                             % (division, CV_CLOCK_TICKS_PER_BEAT))
        return int(round(ticks))

    def _voltage_to_amplitude(self, voltage: float) -> float:
        if voltage < self.output_voltage_min or voltage > self.output_voltage_max:
            raise ValueError("%.3fV is outside the voltage range supported by this device (%.3fV to %.3fV)"
                             % (voltage, self.output_voltage_min, self.output_voltage_max))
        return 2.0 * (voltage - self.output_voltage_min) / (self.output_voltage_max - self.output_voltage_min) - 1.0

    def _control_voltage(self, mapping: CVChannelMapping, value: float) -> float:
        # The voltage of a control's value, from 0 (the bottom of its range) to 1 (the top)
        low, high = mapping.voltage_range or (self.output_voltage_min, self.output_voltage_max)
        return low + max(0.0, min(1.0, value)) * (high - low)

    def set_control(self, index: int, value: float):
        """
        Sets a control's continuous value, from 0 (the bottom of its voltage range) to 1 (the top), on every
        channel that sends it. Values outside 0 to 1 are clamped.
        """
        if not 0 <= index < self.num_controls:
            raise ValueError("Invalid control index: %d (the device has %d controls)" % (index, self.num_controls))
        for mapping in self.channel_mappings:
            if mapping.property_name == "control" and mapping.control_index == index:
                voltage = self._control_voltage(mapping, value)
                self.channel_outputs[mapping.channel_index].set_value(self._voltage_to_amplitude(voltage))

    def _note_index_to_amplitude(self, note):
        try:
            return self._voltage_to_amplitude((note - self.zero_volt_note) / 12)
        except ValueError:
            raise ValueError("Note index %d is outside the voltage range supported by this device" % note)

    #--------------------------------------------------------------------------------
    # Voice allocation
    #--------------------------------------------------------------------------------

    def _get_sounding_notes(self) -> list[int]:
        """
        Returns the held notes that should sound, according to the note priority.
        """
        notes = [note for note, _ in self.held_notes]
        num_voices = len(self.voices)
        if num_voices == 0:
            return []
        priority = self.channel_mappings.note_priority
        if priority == "last":
            return notes[-num_voices:]
        elif priority == "first":
            return notes[:num_voices]
        elif priority == "lowest":
            return sorted(notes)[:num_voices]
        else:
            return sorted(notes, reverse=True)[:num_voices]

    def _update_voices(self, new_note: int = None):
        """
        Assigns the notes that should sound to voices, after a note starts or stops.

        A voice whose note should no longer sound hands over to a note that should (a new note stealing it, or
        a held note returning when another is released), keeping its gate high. Otherwise, notes go to the free
        voice that has rested longest, and voices with nothing to play are stopped. new_note, if given, is the
        note that has just started, which fires its voice's trigger.
        """
        sounding_notes = self._get_sounding_notes()
        velocities = dict(self.held_notes)

        released_voices = [voice for voice in self.voices if not voice.is_free and voice.note not in sounding_notes]
        for voice in released_voices:
            voice.note = None

        assigned_notes = [voice.note for voice in self.voices if not voice.is_free]
        for note in sounding_notes:
            if note in assigned_notes:
                continue
            candidates = released_voices or [voice for voice in self.voices if voice.is_free]
            voice = min(candidates, key=lambda voice: voice.last_used)
            if voice in released_voices:
                released_voices.remove(voice)
            self._start_voice(voice, note, velocities[note], retrigger=(note == new_note))

        for voice in released_voices:
            self._stop_voice(voice)

    def _start_voice(self, voice: CVVoice, note: int, velocity: int, retrigger: bool):
        voice.note = note
        voice.velocity = velocity
        self.voice_counter += 1
        voice.last_used = self.voice_counter

        for mapping in voice.mappings:
            output = self.channel_outputs[mapping.channel_index]
            if mapping.property_name == "note":
                output.set_value(self._note_index_to_amplitude(note))
            elif mapping.property_name == "velocity":
                output.set_value(2.0 * (velocity / 127.0) - 1.0)
            elif mapping.property_name == "gate":
                output.set_value(1.0)
            elif mapping.property_name == "trigger" and retrigger:
                output.trigger()

    def _stop_voice(self, voice: CVVoice):
        # The pitch is left where it is, so that the note's release sounds at the right pitch
        voice.note = None
        self.voice_counter += 1
        voice.last_used = self.voice_counter
        for mapping in voice.mappings:
            if mapping.property_name == "gate":
                self.channel_outputs[mapping.channel_index].set_value(0.0)

    #--------------------------------------------------------------------------------
    # OutputDevice
    #--------------------------------------------------------------------------------

    def perform(self, note) -> None:
        """
        Plays a MidiNoteInstance, passing its duration (in seconds, at the timeline's tempo) to note_on, so that
        envelope outputs sustain for as long as the note.
        """
        duration = None
        if note.duration is not None and note.track is not None and note.track.timeline is not None:
            duration = note.duration * 60.0 / note.track.timeline.tempo
        self.note_on(note.note, note.amplitude, note.channel, duration=duration)

    def note_on(self, note=60, velocity=64, channel=0, duration: Optional[float] = None):
        """
        Starts a note. duration, in seconds, is how long envelope outputs sustain: without one, they keep the
        sustain of the last note that had one.
        """
        if velocity == 0:
            self.note_off(note, channel)
            return

        # Checked first, so that a note that can't be played doesn't take over a voice
        self._note_index_to_amplitude(note)

        # A note that is already sounding is retriggered on its own voice
        voice = next((voice for voice in self.voices if voice.note == note), None)
        if voice is not None:
            self.held_notes = [(held, velocity if held == note else held_velocity)
                               for held, held_velocity in self.held_notes]
            self._start_voice(voice, note, velocity, retrigger=True)
        else:
            self.held_notes = [held for held in self.held_notes if held[0] != note]
            self.held_notes.append((note, velocity))
            self._update_voices(new_note=note)
            voice = next((voice for voice in self.voices if voice.note == note), None)
            if voice is None:
                logger.debug("No voice available for note %d" % note)
                return

        for mapping in voice.mappings:
            if mapping.property_name == "envelope":
                envelope = self.channel_outputs[mapping.channel_index]
                if duration is not None:
                    envelope.set_input("sustain", duration)
                envelope.trigger()

    def note_off(self, note=60, channel=0):
        if all(held_note != note for held_note, _ in self.held_notes):
            return
        self.held_notes = [held for held in self.held_notes if held[0] != note]
        self._update_voices()

    def all_notes_off(self):
        self.held_notes = []
        for voice in self.voices:
            if not voice.is_free:
                self._stop_voice(voice)

    def control(self, control, value, channel=0):
        pass

    def tick(self):
        for mapping, division_ticks in self.clock_mappings:
            if self.tick_count % division_ticks == 0:
                self.channel_outputs[mapping.channel_index].trigger()
        self.tick_count += 1

    def reset(self):
        # Clock pulses restart from the first beat of the bar
        self.tick_count = 0


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
