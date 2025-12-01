from ...pattern import Pattern
from ...constants import *
from ...exceptions import InvalidEventException
from .defaults import EventDefaults

class Event:
    def __init__(self, event_values, track):
        self.duration = event_values[EVENT_DURATION]
        self.active = event_values[EVENT_ACTIVE]
        self.fields = event_values
        self.track = track

    @classmethod
    def from_dict(self,
                  event_values,
                  defaults=EventDefaults(),
                  track=None) -> 'Event':
        
        if len(event_values) == 0:
            # Empty event, return a dummy event
            return None

        from . import MidiNoteEvent, ActionEvent, MidiControlChangeEvent, MidiProgramChangeEvent, GlobalsEvent, OscEvent, SuperColliderEvent, SignalFlowEvent, AbletonMidiNoteEvent

        for key in event_values.keys():
            if key not in ALL_EVENT_PARAMETERS:
                raise ValueError("Invalid key for event: %s" % (key))

        # Shorthand and synonym keys
        for synonym, key in EVENT_KEY_SYNONYMS.items():
            if synonym in event_values:
                event_values[key] = event_values[synonym]
                del event_values[synonym]

        for key, value in defaults.__dict__.items():
            # Defaults can be patterns too
            if key == "fallback_to":
                continue
            event_values.setdefault(key, Pattern.value(value))

        #----------------------------------------------------------------------
        # Classify the event type.
        #----------------------------------------------------------------------
        if EVENT_NOTE in event_values or EVENT_DEGREE in event_values:
            from ...io.ableton.output import AbletonMidiOutputDevice
            if isinstance(track, AbletonMidiOutputDevice):
                event = AbletonMidiNoteEvent(event_values, track)
            else:
                event = MidiNoteEvent(event_values, track)
        elif EVENT_CONTROL in event_values:
            event = MidiControlChangeEvent(event_values, track)
        elif EVENT_PROGRAM_CHANGE in event_values:
            event = MidiProgramChangeEvent(event_values, track)
        elif EVENT_ACTION in event_values:
            event = ActionEvent(event_values, track)
        elif EVENT_GLOBAL in event_values:
            event = GlobalsEvent(event_values, track)
        elif EVENT_OSC_ADDRESS in event_values:
            event = OscEvent(event_values, track)
        elif EVENT_SUPERCOLLIDER_SYNTH in event_values:
            event = SuperColliderEvent(event_values, track)
        elif EVENT_PATCH in event_values:
            event = SignalFlowEvent(event_values, track)
        else:
            possible_event_types = [EVENT_NOTE, EVENT_DEGREE, EVENT_ACTION, EVENT_PATCH, EVENT_CONTROL,
                                    EVENT_PROGRAM_CHANGE, EVENT_OSC_ADDRESS, EVENT_GLOBAL]
            raise InvalidEventException("No event type specified (must provide one of %s)" % possible_event_types)

        return event

    def __str__(self):
        return "Event (%s)" % self.fields

    @property
    def output_device(self):
        return self.track.output_device