from ..pattern import Pattern
from ..key import Key
from ..scale import Scale
from ..constants import EVENT_NOTE, EVENT_AMPLITUDE, EVENT_DURATION, EVENT_TRANSPOSE, \
    EVENT_CHANNEL, EVENT_GATE, EVENT_DEGREE, EVENT_PROGRAM_CHANGE, \
    EVENT_OCTAVE, EVENT_KEY, EVENT_SCALE, EVENT_VALUE, EVENT_ACTION_ARGS, EVENT_CONTROL, \
    EVENT_ACTION, EVENT_OSC_ADDRESS, EVENT_PATCH
from ..constants import DEFAULT_EVENT_TRANSPOSE, DEFAULT_EVENT_AMPLITUDE, \
    DEFAULT_EVENT_CHANNEL, DEFAULT_EVENT_DURATION, DEFAULT_EVENT_GATE, DEFAULT_EVENT_OCTAVE
from ..constants import EVENT_TYPE_NOTE, EVENT_TYPE_ACTION, EVENT_TYPE_OSC, EVENT_TYPE_CONTROL, \
    EVENT_TYPE_PATCH, EVENT_TYPE_PROGRAM_CHANGE
from ..exceptions import InvalidEventException
import logging

log = logging.getLogger(__name__)

class Event:
    def __init__(self, event_values):
        event_values.setdefault(EVENT_CHANNEL, DEFAULT_EVENT_CHANNEL)
        event_values.setdefault(EVENT_DURATION, DEFAULT_EVENT_DURATION)
        event_values.setdefault(EVENT_GATE, DEFAULT_EVENT_GATE)
        event_values.setdefault(EVENT_AMPLITUDE, DEFAULT_EVENT_AMPLITUDE)
        event_values.setdefault(EVENT_OCTAVE, DEFAULT_EVENT_OCTAVE)
        event_values.setdefault(EVENT_TRANSPOSE, DEFAULT_EVENT_TRANSPOSE)
        event_values.setdefault(EVENT_SCALE, Scale.default)

        if EVENT_NOTE in event_values and EVENT_DEGREE in event_values:
            raise InvalidEventException("Cannot specify both note and degree")

        #------------------------------------------------------------------------
        # Note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        if EVENT_DEGREE in event_values:
            degree = event_values[EVENT_DEGREE]
            if degree is None:
                event_values[EVENT_NOTE] = None
            else:
                if EVENT_KEY in event_values:
                    key = event_values[EVENT_KEY]
                else:
                    key = Key(0, event_values[EVENT_SCALE])

                #----------------------------------------------------------------------
                # handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                # addition transparently
                #----------------------------------------------------------------------
                try:
                    event_values[EVENT_NOTE] = [key[n] for n in degree]
                except:
                    event_values[EVENT_NOTE] = key[degree]

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, set amplitude
        # to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
        if EVENT_NOTE in event_values:
            if event_values[EVENT_NOTE] is None:
                #----------------------------------------------------------------------
                # Rest.
                #----------------------------------------------------------------------
                event_values[EVENT_NOTE] = 0
                event_values[EVENT_AMPLITUDE] = 0
                event_values[EVENT_GATE] = 0
            else:
                #----------------------------------------------------------------------
                # Handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                #       addition transparently.
                #
                # The below does not allow for event_values[EVENT_TRANSPOSE] to be an array,
                # for example.
                #----------------------------------------------------------------------
                try:
                    event_values[EVENT_NOTE] = [note + event_values[EVENT_OCTAVE] * 12 + event_values[EVENT_TRANSPOSE] for note in event_values[EVENT_NOTE]]
                except:
                    event_values[EVENT_NOTE] += event_values[EVENT_OCTAVE] * 12 + event_values[EVENT_TRANSPOSE]

        #----------------------------------------------------------------------
        # Classify the event type.
        #----------------------------------------------------------------------
        if EVENT_ACTION in event_values:
            self.type = EVENT_TYPE_ACTION
            self.action = event_values[EVENT_ACTION]
            self.args = []
            if EVENT_ACTION_ARGS in event_values:
                self.args = [Pattern.value(value) for value in event_values[EVENT_ACTION_ARGS]]

        elif EVENT_PATCH in event_values:
            self.type = EVENT_TYPE_PATCH
            
        elif EVENT_CONTROL in event_values:
            self.type = EVENT_TYPE_CONTROL
            self.control = event_values[EVENT_CONTROL]
            self.value = event_values[EVENT_VALUE]
            self.channel = event_values[EVENT_CHANNEL]
            
        elif EVENT_PROGRAM_CHANGE in event_values:
            self.type = EVENT_TYPE_PROGRAM_CHANGE
            
        elif EVENT_OSC_ADDRESS in event_values:
            self.type = EVENT_TYPE_OSC
            
        elif EVENT_NOTE in event_values or EVENT_DEGREE in event_values:
            self.type = EVENT_TYPE_NOTE
            self.note = event_values[EVENT_NOTE]
            self.amplitude = event_values[EVENT_AMPLITUDE]
            self.gate = event_values[EVENT_GATE]
            self.channel = event_values[EVENT_CHANNEL]
            
        else:
            possible_event_types = [EVENT_NOTE, EVENT_DEGREE, EVENT_ACTION, EVENT_PATCH, EVENT_CONTROL, EVENT_PROGRAM_CHANGE, EVENT_OSC_ADDRESS]
            raise InvalidEventException("No event type specified (must provide one of %s)" % possible_event_types)
        
        self.duration = event_values[EVENT_DURATION]
        
        self.fields = event_values
