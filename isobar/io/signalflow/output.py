from ..output import OutputDevice

import logging
import inspect

log = logging.getLogger(__name__)

try:
    import signalflow as sf
except ModuleNotFoundError:
    # No SignalFlow support available
    pass

class SignalFlowOutputDevice(OutputDevice):
    def __init__(self, graph=None):
        """
        Create an output device for the SignalFlow audio DSP framework.

        Args:
            device_name (str): The name of the target device to use.
                               If not specified, uses the system default.
        """
        if graph:
            self.graph = graph
        else:
            try:
                self.graph = sf.AudioGraph()
            except NameError:
                raise Exception("Could not instantiate OutputDevice as libsignal not installed")
            except sf.GraphAlreadyCreatedException:
                raise Exception("SignalFlow graph has already been instantiated."
                                "Pass the AudioGraph object as an argument to SignalFlowOutputDevice.")

        self.graph.start()
        log.info("Opened SignalFlow output")

        self.patches = []

    def create(self, patch_spec, patch_params):
        # TODO: patch = sf.Patch(patch_spec, patch_params)
        if inspect.isclass(patch_spec):
            patch = patch_spec()
        elif isinstance(patch_spec, sf.PatchSpec):
            patch = sf.Patch(patch_spec)

        for key, value in patch_params.items():
            if value is None:
                return
            else:
                patch.set_input(key, value)
        patch.auto_free = True
        self.graph.play(patch)

    def trigger(self, patch, patch_params):
        patch.trigger()

