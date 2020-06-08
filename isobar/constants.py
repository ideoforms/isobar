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
MAX_CLOCK_RATE = 12000

#------------------------------------------------------------------------
# Keys used in Timeline event dictionaries.
#------------------------------------------------------------------------
EVENT_NOTE = "note"
EVENT_AMPLITUDE = "amp"
EVENT_DURATION = "dur"
EVENT_GATE = "gate"
EVENT_TRANSPOSE = "transpose"
EVENT_CHANNEL = "channel"
EVENT_GATE = "gate"
EVENT_PHASE = "phase"
EVENT_OCTAVE = "octave"
EVENT_EVENT = "event"
EVENT_DEGREE = "degree"
EVENT_PHASE = "phase"
EVENT_KEY = "key"
EVENT_SCALE = "scale"
EVENT_PRINT = "print"
EVENT_ACTION = "action"
EVENT_ACTION_OBJECT = "object"
EVENT_CONTROL = "control"
EVENT_ADDRESS = "address"
EVENT_VALUE = "value"
EVENT_TIME = "time"
EVENT_FUNCTION = "function"