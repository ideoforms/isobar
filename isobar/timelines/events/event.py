from ...pattern import Pattern
from ...scale import Scale
from ...key import Key
from ...constants import *
from ...exceptions import InvalidEventException


class EventDefaults:
    default_values = {
        EVENT_ACTIVE: True,
        EVENT_CHANNEL: DEFAULT_EVENT_CHANNEL,
        EVENT_DURATION: DEFAULT_EVENT_DURATION,
        EVENT_GATE: DEFAULT_EVENT_GATE,
        EVENT_AMPLITUDE: DEFAULT_EVENT_AMPLITUDE,
        EVENT_OCTAVE: DEFAULT_EVENT_OCTAVE,
        EVENT_TRANSPOSE: DEFAULT_EVENT_TRANSPOSE,
        EVENT_KEY: Key("C", Scale.default),
        EVENT_QUANTIZE: DEFAULT_EVENT_QUANTIZE,
        EVENT_DELAY: DEFAULT_EVENT_DELAY,
        EVENT_PITCHBEND: None,
    }

    def __init__(self):
        for key, value in EventDefaults.default_values.items():
            setattr(self, key, value)

    def __setattr__(self, name, value):
        if name != "default_values" and name not in EventDefaults.default_values:
            raise ValueError("Invalid property for defaults: %s" % name)
        super().__setattr__(name, value)

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

        from . import MidiNoteEvent, ActionEvent, MidiControlChangeEvent, MidiProgramChangeEvent, GlobalsEvent, OscEvent, SuperColliderEvent, SignalFlowEvent

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
            event_values.setdefault(key, Pattern.value(value))

        #----------------------------------------------------------------------
        # Classify the event type.
        #----------------------------------------------------------------------
        if EVENT_NOTE in event_values or EVENT_DEGREE in event_values:
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