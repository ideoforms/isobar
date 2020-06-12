import sys

#------------------------------------------------------------------------
# Determines how fine-grained our clocking is -- events can't be
# scheduled any faster than this. 24 ticks per beat is identical
# to MIDI clocking.
#------------------------------------------------------------------------
TICKS_PER_BEAT = 24

#------------------------------------------------------------------------
# Used when scheduling neverending events.
#------------------------------------------------------------------------
FOREVER = sys.maxsize

#------------------------------------------------------------------------
# Default BPM
#------------------------------------------------------------------------
DEFAULT_CLOCK_RATE = 120

#------------------------------------------------------------------------
# Very fast clock rate, used for quickly running through a timeline.
#------------------------------------------------------------------------
MAX_CLOCK_RATE = 1e6

#------------------------------------------------------------------------
# Parameters used in Timeline event dictionaries.
#------------------------------------------------------------------------
EVENT_TYPE = "type"
EVENT_CHANNEL = "channel"
EVENT_AMPLITUDE = "amp"
EVENT_DURATION = "dur"
EVENT_GATE = "gate"
EVENT_NOTE = "note"
EVENT_DEGREE = "degree"
EVENT_KEY = "key"
EVENT_SCALE = "scale"
EVENT_OCTAVE = "octave"
EVENT_TRANSPOSE = "transpose"
EVENT_EVENT = "event"
EVENT_ACTION = "action"
EVENT_ACTION_OBJECT = "object"
EVENT_CONTROL = "control"
EVENT_OSC_ADDRESS = "address"
EVENT_OSC_PARAMS = "params"
EVENT_VALUE = "value"
EVENT_TIME = "time"
EVENT_FUNCTION = "function"

#------------------------------------------------------------------------
# Event types
#------------------------------------------------------------------------
EVENT_TYPE_UNKNOWN = 0
EVENT_TYPE_NOTE = 1
EVENT_TYPE_CONTROL = 2
EVENT_TYPE_OSC = 3
EVENT_TYPE_ACTION = 4

#------------------------------------------------------------------------
# Default parameter values
#------------------------------------------------------------------------
DEFAULT_EVENT_CHANNEL = 0
DEFAULT_EVENT_DURATION = 1
DEFAULT_EVENT_GATE = 1.0
DEFAULT_EVENT_AMPLITUDE = 64
DEFAULT_EVENT_OCTAVE = 0
DEFAULT_EVENT_TRANSPOSE = 0