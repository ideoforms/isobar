class DeviceNotFoundException (Exception):
    """
    I/O device could not be found.
    """
    pass

class TrackLimitReachedException (Exception):
    """
    No more tracks could be scheduled in this Timeline.
    """
    pass

class InvalidEventException (Exception):
    """
    Invalid event.
    """
    pass

class InvalidMIDIPitch (Exception):
    """
    MIDI pitch is invalid. Must range between 0..127
    """
    pass

class UnknownNoteName (Exception):
    """
    MIDI note name cannot be parsed.
    Note names must be upper/lowercase letter [abcdefg], optionally followed
    by b/#.
    """
    pass

class UnknownScaleName (Exception):
    """
    Scale name is not recognised.
    """
    pass