from dataclasses import dataclass
from typing import Any

@dataclass
class MetronomeConfig:
    bar_length: int = 4
    interval: float = 1
    
    type: str = "midi"

    midi_output_device: Any = None
    midi_channel: int = 0
    midi_note_major: int = 72
    midi_note_minor: int = 60
    midi_velocity_major: int = 64
    midi_velocity_minor: int = 48
    midi_note_duration: float = 0.1

    def to_dict(self) -> dict:
        # The output device is saved by name: it is opened again when loaded, by the caller of from_dict
        return {
            "bar_length": self.bar_length,
            "interval": self.interval,
            "type": self.type,
            "midi_output_device": getattr(self.midi_output_device, "name", None),
            "midi_channel": self.midi_channel,
            "midi_note_major": self.midi_note_major,
            "midi_note_minor": self.midi_note_minor,
            "midi_velocity_major": self.midi_velocity_major,
            "midi_velocity_minor": self.midi_velocity_minor,
            "midi_note_duration": self.midi_note_duration,
        }

    @classmethod
    def from_dict(cls, data: dict, midi_output_device: Any = None) -> "MetronomeConfig":
        """
        Deserialize a MetronomeConfig from a dictionary made by to_dict.

        The dictionary holds only the output device's name (as data["midi_output_device"]), so the open device
        is passed in as midi_output_device. If it is None, the metronome plays on the timeline's output device.
        """
        defaults = cls()
        return cls(bar_length=data.get("bar_length", defaults.bar_length),
                   interval=data.get("interval", defaults.interval),
                   type=data.get("type", defaults.type),
                   midi_output_device=midi_output_device,
                   midi_channel=data.get("midi_channel", defaults.midi_channel),
                   midi_note_major=data.get("midi_note_major", defaults.midi_note_major),
                   midi_note_minor=data.get("midi_note_minor", defaults.midi_note_minor),
                   midi_velocity_major=data.get("midi_velocity_major", defaults.midi_velocity_major),
                   midi_velocity_minor=data.get("midi_velocity_minor", defaults.midi_velocity_minor),
                   midi_note_duration=data.get("midi_note_duration", defaults.midi_note_duration))
    

class Metronome:
    def __init__(self,
                 timeline,
                 config: MetronomeConfig = None):
        self.timeline = timeline
        self.config = config if config is not None else MetronomeConfig()
        self.current_tick = 0

    @property
    def output_device(self):
        if self.config.midi_output_device is not None:
            return self.config.midi_output_device
        else:
            return self.timeline.output_device
        
    def tick(self):
        # print("metronome tick: current_tick = %d" % self.current_tick)
        note = None
        velocity = None
        if self.current_tick % (self.timeline.ticks_per_beat * self.config.bar_length) == 0:
            # Major beat
            note = self.config.midi_note_major
            velocity = self.config.midi_velocity_major
        elif self.current_tick % (self.timeline.ticks_per_beat * self.config.interval) == 0:
            # Minor beat
            note = self.config.midi_note_minor
            velocity = self.config.midi_velocity_minor
            
        if note is not None:
            self.output_device.note_on(note=note,
                                       velocity=velocity,
                                       channel=self.config.midi_channel)
            def note_off_callback():
                self.output_device.note_off(note=note,
                                            channel=self.config.midi_channel)
            self.timeline._schedule_action(note_off_callback, delay=self.config.midi_note_duration)
        
        self.current_tick += 1
    
    def reset(self):
        self.current_tick = 0
