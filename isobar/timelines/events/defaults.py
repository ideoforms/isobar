from ...scale import Scale
from ...key import Key
from ...constants import *


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

    def __init__(self, fallback_to: 'EventDefaults' = None):
        self.fallback_to = fallback_to
        if not fallback_to:
            for key, value in EventDefaults.default_values.items():
                setattr(self, key, value)

    def __setattr__(self, name, value):
        if name not in ["default_values", "fallback_to"] and name not in EventDefaults.default_values:
            raise ValueError("Invalid property for defaults: %s" % name)
        super().__setattr__(name, value)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if self.fallback_to:
                return getattr(self.fallback_to, name)
            else:
                raise