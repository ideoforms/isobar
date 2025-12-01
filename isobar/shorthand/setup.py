from ..io.midi import MidiOutputDevice, MidiInputDevice
from ..timelines import Timeline
from ..exceptions import DeviceNotFoundException
from ..globals import Globals
from .. import ALL_EVENT_PARAMETERS
import re

try:
    from signalflow import *
    from ..io.signalflow import SignalFlowOutputDevice
    from ..io.ableton import AbletonMidiOutputDevice

    # Don't need this for now
    # Globals.enable_interprocess_sync()

    midi_output_device = MidiOutputDevice("IAC Driver Bus 1")
    
    timeline = Timeline(midi_output_device, clock_source="link")
    timeline.defaults.quantize = 4
    timeline.ignore_exceptions = True

    graph = AudioGraph()
    signalflow_output_device = SignalFlowOutputDevice(graph)
    signalflow_output_device.added_latency_seconds = -0.04

    timeline.background()

except (ModuleNotFoundError, DeviceNotFoundException) as e:
    print("Warning: Could not set up shorthand mode: %s" % e)
    graph = None
    timeline = None

live_set = None
tempo = None

# Enable Ableton Link clock in current Live set
def enable_ableton_link():
    import live
    global live_set
    global tempo
    try:
        live_set = live.Set(scan=True)
        if not live_set.is_ableton_link_enabled:
            live_set.is_ableton_link_enabled = True
            # TODO use logger
            # print("Ableton Link enabled in current Live set.")

        # For some reasin, calling start_playing() here if Live is already playing with a Link clock
        # causes the playback to immediately rewind, which causes timing issues.
        if not live_set.is_playing:
            live_set.start_playing()

        tempo = timeline.automation(initial=live_set.tempo, default_duration=10)
        tempo.bind_to(live_set, "tempo")
    except (live.LiveConnectionError, OSError) as e:
        print(f"Error enabling Ableton Link: {e}")
enable_ableton_link()

def open_set(set_name):
    global live_set
    live_set.open(set_name)

def lfo(shape, frequency=1.0, min=0.0, max=1.0, **kwargs):
    from ..pattern import PLFO
    from ..timelines.lfo import LFO
    lfo = LFO(shape=shape, frequency=frequency, min=min, max=max, **kwargs)
    return PLFO(lfo)

def track(name, **kwargs):
    global timeline

    track_parameters = {
        "quantize": None,
        "count": None,
        "interpolate": None,
        "track_index": None,
        "output_device": None,
    }
    #--------------------------------------------------------------------------------
    # Unflatten the params list.
    # This has some perils (e.g. 'amp' is used as an Event keyword but is 
    # also often used as a Patch parameter).
    #--------------------------------------------------------------------------------
    params = {}
    for key in list(kwargs.keys()):
        if key in track_parameters:
            track_parameters[key] = kwargs[key]
            del kwargs[key]
        elif key in ALL_EVENT_PARAMETERS:
            pass
        else:
            params[key] = kwargs[key]
            del kwargs[key]
    
    if params:
        #--------------------------------------------------------------------------------
        # This caused the track to not generate any events when params was null,
        # not sure why
        #--------------------------------------------------------------------------------
        kwargs["params"] = params
    
    #--------------------------------------------------------------------------------
    # Automatically select the appropriate output device based on the event type.
    #--------------------------------------------------------------------------------
    if track_parameters["output_device"] is None:
        if "patch" in kwargs:
            track_parameters["output_device"] = signalflow_output_device
        else:
            track_parameters["output_device"] = timeline.output_device


    track = timeline.schedule(params=kwargs,
                              name=name,
                              replace=True,
                              **track_parameters)

    # TODO tidy this up
    from ..pattern import PLFO
    track.lfos = []
    if "params" in kwargs:
        for param in kwargs["params"]:
            if isinstance(kwargs["params"][param], PLFO):
                #--------------------------------------------------------------------------------
                # Register LFO with timeline
                #--------------------------------------------------------------------------------
                lfo = kwargs["params"][param].lfo
                lfo.track = track
                # TODO: Should this be a different formulation of add_lfo?
                track.lfos.append(lfo)

    #--------------------------------------------------------------------------------
    # Evaluating a cell with a track() command with mute() appended to it causes
    # the track to be silenced.
    #
    # Re-evaluating the cell without mute() should then unmute the track.
    #--------------------------------------------------------------------------------
    track.is_muted = False

    try:
        import signalflow_vscode
        cell_id = signalflow_vscode.get_this_cell_id()
        # print("Added flash callback for cell ID:", cell_id)
        if cell_id is not None:
            track.add_event_callback(lambda e: signalflow_vscode.flash_cell_id(cell_id, track.name))
    except (ModuleNotFoundError, ImportError):
        # no signalflow_vscode module available
        pass


    return track
