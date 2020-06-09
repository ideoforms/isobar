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