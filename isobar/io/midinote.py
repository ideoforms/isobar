from dataclasses import dataclass
from typing import Optional

@dataclass
class MidiNote:
    #--------------------------------------------------------------------------------
    # Pitch = MIDI 0..127
    #--------------------------------------------------------------------------------
    pitch: int

    #--------------------------------------------------------------------------------
    # Velocity = MIDI 0..127
    #--------------------------------------------------------------------------------
    velocity: int

    #--------------------------------------------------------------------------------
    # Aftertouch = MIDI 0..127
    # If present, this value may be updated dynamically during the note's lifetime.
    #--------------------------------------------------------------------------------
    aftertouch: Optional[int] = None

    #--------------------------------------------------------------------------------
    # Channel = MIDI 0..15
    #--------------------------------------------------------------------------------
    channel: Optional[int] = None

    #--------------------------------------------------------------------------------
    # For notes that are located in a time sequence:
    #  - Location on the timeline, in beats
    #  - Duration, in beats
    #--------------------------------------------------------------------------------
    location: Optional[float] = None
    duration: Optional[float] = None
