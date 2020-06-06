import sys

#------------------------------------------------------------------------
# Determines how fine-grained our clocking is -- events can't be
# scheduled any faster than this. 24 ticks per beat is identical
# to MIDI clocking.
#------------------------------------------------------------------------
TICKS_PER_BEAT = 24

FOREVER = sys.maxsize

EVENT_NOTE = "note"
EVENT_AMPLITUDE = "amp"
EVENT_DURATION = "dur"
EVENT_GATE = "gate"
EVENT_TRANSPOSE = "transpose"
EVENT_CHANNEL = "channel"
EVENT_OMIT = "omit"
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
EVENT_CONTROL = "control"
EVENT_ADDRESS = "address"
EVENT_VALUE = "value"
EVENT_OBJECT = "object"
EVENT_TIME = "time"
EVENT_FUNCTION = "function"