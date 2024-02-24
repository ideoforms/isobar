from abc import ABC, abstractmethod
import mido


class MetaMessageInterface(ABC):
    @abstractmethod
    def to_meta_message(self):
        return None


class MessageInterface(ABC):
    @abstractmethod
    def to_meta_message(self):
        return None


class MidiMessageControl:
    def __init__(self, channel, cc, value, location, time=0, track_idx=0):
        # channel = 0..15
        self.channel = channel
        # cc = 0..127
        self.cc = cc
        # value = 0..127
        self.value = value
        # location in time, beats
        self.location = location
        self.time = time
        self.track_idx = track_idx

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not isinstance(value, int) or not (0 <= value <= 15):
            raise ValueError("Invalid channel value. Channel must be an integer between 0 and 15.")
        self._channel = value

    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, value):
        if not isinstance(value, int) or not (0 <= value <= 127):
            raise ValueError("Invalid cc value. cc must be an integer between 0 and 127.")
        self._cc = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, int) or not (0 <= value <= 127):
            raise ValueError("Invalid value. Value must be an integer between 0 and 127.")
        self._value = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._time = value




class MidiMessageProgram:
    def __init__(self, channel, program, location, time=0, track_idx=0):
        # channel 0..15
        self.channel = channel
        # program 0..255
        self.program = program
        self.location = location
        # duration in time, beats
        self.time = time
        # track_idx >=0
        self.track_idx = track_idx
    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not isinstance(value, int) or not (0 <= value <= 15):
            raise ValueError("Invalid channel value. Must be an integer between 0 and 15.")
        self._channel = value

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, value):
        if not isinstance(value, int) or not (0 <= value <= 255):
            raise ValueError("Invalid program value. Must be an integer between 0 and 255.")
        self._program = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

class MidiMessagePitch:
    def __init__(self, channel, pitch, location, time=0, track_idx=0):
        self.channel = channel
        self.pitch = pitch
        self.location = location
        self.time = time
        self.track_idx = track_idx

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not isinstance(value, int) or not (0 <= value <= 15):
            raise ValueError("Invalid channel value. Must be an integer between 0 and 15.")
        self._channel = value

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        if not isinstance(value, int) or not (-8192 <= value <= 8192):
            raise ValueError("Invalid pitch value. Must be an integer between -8192 and 8192.")
        self._pitch = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

class MidiMessagePoly:
    def __init__(self, channel, note, value, location, time=0, track_idx=0):
        self.value = value
        self.channel = channel
        self.note = note
        self.location = location
        self.time = time
        self.track_idx = track_idx

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, int) or not (0 <= value <= 127):
            raise ValueError("Invalid value. Value must be an integer between 0 and 127.")
        self._value = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Invalid channel value. Channel must be between 0 and 15.")
        self._channel = value

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        if not 0 <= value <= 127:
            raise ValueError("Invalid note value. Pitch must be between 0 and 127.")
        self._note = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

class MidiMessageAfter:
    def __init__(self, channel, value, location, time=0, track_idx=0):
        self.channel = channel
        self.value = value
        self.location = location
        self.time = time
        self.track_idx = track_idx

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, int) or not (0 <= value <= 127):
            raise ValueError("Invalid value. Value must be an integer between 0 and 127.")
        self._value = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Invalid channel value. Channel must be between 0 and 15.")
        self._channel = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value


class MidiMetaMessageTempo(MetaMessageInterface):
    def __init__(self, tempo: int, location, type='set_tempo', time=0, track_idx=0):
        #   0..16777215

        self.tempo = tempo
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = 0

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        if not 0 <= value <= 16777215:
            raise ValueError("Invalid tempo value. Tempo must be between 0 and 16777215.")
        self._tempo = value

    def to_meta_message(self):
        return mido.MetaMessage(tempo=self.tempo, time=self.time, type='set_tempo')


class MidiMetaMessageKey(MetaMessageInterface):
    VALID_KEYS = [
        "A", "A#m", "Ab", "Abm", "Am", "B", "Bb", "Bbm", "Bm", "C", "C#", "C#m", "Cb", "Cm",
        "D", "D#m", "Db", "Dm", "E", "Eb", "Ebm", "Em", "F", "F#", "F#m", "Fm", "G", "G#m", "Gb", "Gm"
    ]

    def __init__(self, key: str, location, time=0, track_idx=0):
        self._key = None
        self.key = key
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = track_idx

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if value not in self.VALID_KEYS:
            raise ValueError("Invalid key value. Key must be one of the valid keys.")
        self._key = value

    def to_meta_message(self):
        return mido.MetaMessage(key=self.key, time=self.time, type='key_signature')


class MidiMetaMessageTimeSig(MetaMessageInterface):
    def __init__(self, numerator: int, denominator: int,
                 clocks_per_click: int, notated_32nd_notes_per_beat: int,
                 location, time=0, track_idx=0):
        # numerator 1..255
        self.numerator = numerator
        # denominator 1..2**255
        self.denominator = denominator
        # clocks_per_click 0..255
        self.clocks_per_click = clocks_per_click
        # notated_32nd_notes_per_beat 0..255
        self.notated_32nd_notes_per_beat = notated_32nd_notes_per_beat
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = 0

    @property
    def numerator(self):
        return self._numerator

    @numerator.setter
    def numerator(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Invalid numerator value. Numerator must be a positive integer.")
        self._numerator = value

    @property
    def denominator(self):
        return self._denominator

    @denominator.setter
    def denominator(self, value):
        if not isinstance(value, int) or value <= 0 or value & (value - 1) != 0 or value > 2**255:
            raise ValueError("Invalid denominator value. Denominator must be a power of 2"
                             "between 1 and 2**255")
        self._denominator = value

    @property
    def clocks_per_click(self):
        return self._clocks_per_click

    @clocks_per_click.setter
    def clocks_per_click(self, value):
        if not isinstance(value, int) or value <= 0 or value >255:
            raise ValueError("Invalid clocks_per_click value. Must be a integer between 1 and 255.")
        self._clocks_per_click = value

    @property
    def notated_32nd_notes_per_beat(self):
        return self._notated_32nd_notes_per_beat

    @notated_32nd_notes_per_beat.setter
    def notated_32nd_notes_per_beat(self, value):
        if not isinstance(value, int) or value <= 0 or value >255:
            raise ValueError("Invalid notated_32nd_notes_per_beat value. Must be a integer between 1 and 255.")
        self._notated_32nd_notes_per_beat = value

    def to_meta_message(self):
        return mido.MetaMessage(numerator=self.numerator, denominator=self.denominator,
                                clocks_per_click=self.clocks_per_click,
                                notated_32nd_notes_per_beat=self.notated_32nd_notes_per_beat,
                                time=self.time, type='time_signature')


class MidiMetaMessageTrackName(MetaMessageInterface):
    def __init__(self, name: str, location, time=0, track_idx=0):
        self.name = name
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = track_idx

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

    def to_meta_message(self):
        return mido.MetaMessage(name=self.name, time=self.time, type='track_name')


class MidiMetaMessageMidiPort(MetaMessageInterface):
    def __init__(self, port: int, location, time=0, track_idx=0):
        # port 00.255
        self.port = port
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = track_idx


    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, int) or not (0 <= value <= 255):
            raise ValueError("Invalid port value. Must be an integer between 0 and 255.")
        self._port = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

    def to_meta_message(self):
        return mido.MetaMessage(port=self.port, time=self.time, type='midi_port')


class MidiMetaMessageEndTrack(MetaMessageInterface):
    def __init__(self, location, time=0, track_idx=0):
        self.location = location
        self.is_meta = True
        self.time = time
        self.track_idx = track_idx

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        if value < 0:
            raise ValueError("Invalid time value. Must be a non-negative.")
        self._time = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value < 0:
            raise ValueError("Invalid location value. Must be a non-negative.")
        self._location = value

    @property
    def track_idx(self):
        return self._track_idx

    @track_idx.setter
    def track_idx(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid track_idx value. Must be a non-negative integer.")
        self._track_idx = value

    def to_meta_message(self):
        return mido.MetaMessage(time=self.time, type='end_of_track')
