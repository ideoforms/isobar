import logging
log = logging.getLogger(__name__)
from ..output import OutputDevice

try:
    import libsignal as sf
except:
    log.warning("No Signalflow support available")

class SignalflowOutputDevice (OutputDevice):
    def __init__(self):
        """
        Create an output device for the Signalflow audio DSP framework.

        Args:
            device_name (str): The name of the target device to use.
                               If not specified, uses the system default.
        """
        self.graph = sf.AudioGraph()
        self.graph.start()
        log.info("Opened Signalflow output")

    def create(self, patch_spec, patch_params):
        # TODO: patch = sf.Patch(patch_spec, patch_params)
        patch = sf.Patch(patch_spec)
        for key, value in patch_params.items():
            patch.set_input(key, value)
        patch.auto_free = True
        self.graph.add_output(patch)
