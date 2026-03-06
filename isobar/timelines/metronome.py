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
    

class Metronome:
    def __init__(self,
                 timeline,
                 config: MetronomeConfig = MetronomeConfig()):
        self.timeline = timeline
        self.config = config
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
