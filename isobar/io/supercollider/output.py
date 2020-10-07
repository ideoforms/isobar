from ..output import OutputDevice

import logging

log = logging.getLogger(__name__)

try:
    import supercollider
except ModuleNotFoundError:
    pass

class SuperColliderOutputDevice (OutputDevice):
    """
    SuperColliderOutputDevice: Wraps MIDI messages in OSC.
    /note [ note, velocity, channel ]
    /control [ control, value, channel ]
    """

    def __init__(self, host="127.0.0.1", port=57110):
        """
        Args:
            host: Hostname to send OSC messages to
            port: =Port number to send OSC messages to
        """
        try:
            self.server = supercollider.Server()

        except NameError:
            raise Exception("The supercollider package must be installed: pip3 install supercollider")

        self.default_synth_name = "sine"
        self.synths = {}

    def note_on(self, note=60, velocity=64, channel=0):
        synth_params = {
            "note": note,
            "velocity": velocity
        }
        synth = supercollider.Synth(self.server, self.default_synth_name, synth_params)
        self.synths[note] = synth

    def note_off(self, note=60, channel=0):
        pass

    def control(self, control, value, channel=0):
        pass

    def create(self, name, params=None):
        log.debug("Creating SuperCollider Synth: %s, %s" % (name, params))
        supercollider.Synth(self.server, name, params)
