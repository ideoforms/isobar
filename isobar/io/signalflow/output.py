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
            graph (str): An existing SignalFlow AudioGraph object to use.
                         If not specified, uses the current global AudioGraph,
                         creating one if it has not yet been instantiated.
        """
        super().__init__()
        if graph:
            self.graph = graph
        else:
            self.graph = sf.AudioGraph.get_shared_graph()
            if self.graph is None:
                try:
                    self.graph = sf.AudioGraph(start=True)
                except NameError:
                    raise Exception("Could not instantiate SignalFlowOutputDevice, signalflow not installed?")

        log.info("Opened SignalFlow output")

        self.patches = []

    def create(self, patch_spec, patch_params, output=None):
        #--------------------------------------------------------------------------------
        # Create a Patch, passing all params as keyword args
        #--------------------------------------------------------------------------------
        if inspect.isclass(patch_spec):
            patch = patch_spec(**patch_params)
        elif isinstance(patch_spec, sf.PatchSpec):
            patch = sf.Patch(patch_spec, patch_params)
        else:
            raise RuntimeError("patch property is of invalid type")

        patch.set_auto_free(True)

        if output:
            if patch.add_to_graph():
                #--------------------------------------------------------------------------------
                # Can fail if the graph exceeds its configured patch count limit
                #--------------------------------------------------------------------------------
                output.add_input(patch)
        else:
            self.graph.play(patch)

    def trigger(self, patch, trigger_name=None, trigger_value=None):
        if trigger_name is not None and trigger_value is not None:
            patch.trigger(trigger_name, trigger_value)
        elif trigger_name is not None:
            patch.trigger(trigger_name)
        else:
            patch.trigger()
