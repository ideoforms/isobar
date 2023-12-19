import math
import copy
import time
import logging
import threading
import traceback
from typing import Callable, Any, Optional
from dataclasses import dataclass

from .track import Track
from .clock import Clock
from .event import EventDefaults
from ..io import MidiOutputDevice
from ..constants import DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO
from ..constants import INTERPOLATION_NONE
from ..exceptions import TrackLimitReachedException, TrackNotFoundException
from ..util import make_clock_multiplier

log = logging.getLogger(__name__)

@dataclass
class Action:
    time: float
    function: Callable

class Timeline:
    """
    A Timeline object encapsulates a number of Tracks, each of which
    represents a sequence of note or control events.

    It has a `clock_source`, which can be a real-time Clock object, or an
    external source such as a MIDI clock (via `isobar.io.MidiInputDevice`).

    A Timeline typically runs until it is terminated by calling `stop()`.
    If you want the Timeline to terminate as soon as no more events are available,
    set `stop_when_done = True`.
    """

    def __init__(self,
                 tempo: float = DEFAULT_TEMPO,
                 output_device: Any = None,
                 clock_source: Any = None,
                 ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT):
        """ Expect to receive one tick per beat, generate events at 120bpm """
        self._clock_source = None
        if clock_source is None:
            clock_source = Clock(self, tempo, ticks_per_beat)
        self.set_clock_source(clock_source)

        self.output_devices = []
        self.clock_multipliers = {}
        if output_device:
            self.add_output_device(output_device)

        self.current_time = 0
        self.max_tracks = 0
        self.tracks = []

        self.thread = None
        self.stop_when_done = False
        self.actions = []
        self.running = False
        self.ignore_exceptions = False

        self.defaults = EventDefaults()

        #--------------------------------------------------------------------------------
        # Optional callback to trigger each time an event is performed.
        #--------------------------------------------------------------------------------
        self.on_event_callback = None

    def get_clock_source(self):
        return self._clock_source

    def set_clock_source(self, clock_source):
        clock_source.clock_target = self
        self._clock_source = clock_source

    clock_source = property(get_clock_source, set_clock_source)

    def get_ticks_per_beat(self):
        if self.clock_source:
            return self.clock_source.ticks_per_beat
        else:
            return None

    def set_ticks_per_beat(self, ticks_per_beat):
        self.clock_source.ticks_per_beat = ticks_per_beat

    ticks_per_beat = property(get_ticks_per_beat, set_ticks_per_beat)

    @property
    def tick_duration(self):
        """
        Tick duration, in beats.
        """
        return 1.0 / self.ticks_per_beat

    def get_tempo(self):
        """ Returns the tempo of this timeline's clock, or None if an external
        clock source is used (in which case the tempo is unknown).
        """
        return self.clock_source.tempo

    def set_tempo(self, tempo):
        """
        Set the tempo of this timeline's clock.
        If the timeline uses an external clock, this operation is invalid, and a
        RuntimeError is raised.

        Args:
            tempo (float): Tempo, in bpm
        """
        self.clock_source.tempo = tempo

    tempo = property(get_tempo, set_tempo)

    def seconds_to_beats(self, seconds):
        return seconds * self.tempo / 60.0

    def beats_to_seconds(self, beats):
        return beats * 60.0 / self.tempo

    def tick(self):
        """
        Called once every tick to trigger new events.

        Raises:
            StopIteration: If `stop_when_done` is true and no more events are scheduled.
        """
        #--------------------------------------------------------------------------------
        # Each time we arrive at precisely a new beat, generate a debug msg.
        # Round to several decimal places to avoid 7.999999999 syndrome.
        # http://docs.python.org/tutorial/floatingpoint.html
        #--------------------------------------------------------------------------------
        if round(self.current_time, 8) % 1 == 0:
            log.debug("--------------------------------------------------------------------------------")
            log.debug("Tick (%d active tracks, %d pending actions)" % (len(self.tracks), len(self.actions)))

        #--------------------------------------------------------------------------------
        # Copy self.actions because removing from it whilst using it = bad idea.
        # Perform actions before tracks are executed because an event might
        # include scheduling a quantized track, which should then be
        # immediately evaluated.
        #--------------------------------------------------------------------------------
        for action in self.actions[:]:
            #--------------------------------------------------------------------------------
            # The only event we currently get in a Timeline are add_track events
            #  -- which have a function object associated with them.
            #
            # Round to work around rounding errors.
            # http://docs.python.org/tutorial/floatingpoint.html
            #--------------------------------------------------------------------------------
            if round(action.time, 8) <= round(self.current_time, 8):
                action.function()
                self.actions.remove(action)

        #--------------------------------------------------------------------------------
        # Copy self.tracks because removing from it whilst using it = bad idea
        #--------------------------------------------------------------------------------
        for track in self.tracks[:]:
            try:
                track.tick()
            except Exception as e:
                if self.ignore_exceptions:
                    tb = traceback.format_exc()
                    log.warning("*** Exception in track: %s" % tb)
                    self.tracks.remove(track)
                else:
                    raise
            if track.is_finished and track.remove_when_done:
                self.tracks.remove(track)
                log.info("Timeline: Track finished, removing from scheduler (total tracks: %d)" % len(self.tracks))

        #--------------------------------------------------------------------------------
        # If we've run out of notes, raise a StopIteration.
        #--------------------------------------------------------------------------------
        if len(self.tracks) == 0 and len(self.actions) == 0 and self.stop_when_done:
            # TODO: Don't do this if we've never played any events, e.g.
            #       right after calling timeline.background(). Should at least
            #       wait for some events to happen first.
            raise StopIteration

        #--------------------------------------------------------------------------------
        # Tell our output devices to move forward a step.
        #--------------------------------------------------------------------------------
        for device in self.output_devices:
            clock_multiplier = self.clock_multipliers[device]
            ticks = next(clock_multiplier)

            for tick in range(ticks):
                device.tick()

        #--------------------------------------------------------------------------------
        # Increment beat count according to our current tick_length.
        #--------------------------------------------------------------------------------
        self.current_time += self.tick_duration

    def dump(self):
        """ Output a summary of this Timeline object
            """
        print("Timeline (clock: %s, tempo %s)" %
              (self.clock_source, self.clock_source.tempo if self.clock_source.tempo else "unknown"))

        print((" - %d devices" % len(self.output_devices)))
        for device in self.output_devices:
            print(("   - %s" % device))

        print((" - %d tracks" % len(self.tracks)))
        for tracks in self.tracks:
            print(("   - %s" % tracks))

    def reset_to_beat(self):
        """ Reset the timer to the last beat.
        Useful when a MIDI Stop/Reset message is received. """

        self.current_time = round(self.current_time)
        for tracks in self.tracks:
            tracks.reset_to_beat()

    def reset(self):
        """ Reset the timeline to t = 0. """
        self.current_time = 0.0
        for track in self.tracks:
            track.reset()

    def background(self):
        """ Run this Timeline in a background thread. """
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self, stop_when_done=None):
        """ Run this Timeline in the foreground.

        If stop_when_done is set, returns when no tracks are currently
        scheduled; otherwise, keeps running indefinitely. """

        self.start()

        if stop_when_done is not None:
            self.stop_when_done = stop_when_done

        try:
            #--------------------------------------------------------------------------------
            # Start the clock. This might internal (eg a Clock object, running on
            # an independent thread), or external (eg a MIDI clock).
            #--------------------------------------------------------------------------------
            for device in self.output_devices:
                device.start()
            self.running = True
            self.clock_source.run()

        except StopIteration:
            #--------------------------------------------------------------------------------
            # This will be hit if every Pattern in a timeline is exhausted.
            #--------------------------------------------------------------------------------
            log.info("Timeline: Finished")
            self.running = False

        except Exception as e:
            print((" *** Exception in Timeline thread: %s" % e))
            if not self.ignore_exceptions:
                raise e

    def start(self):
        log.info("Timeline: Starting")

    def stop(self):
        log.info("Timeline: Stopping")
        for device in self.output_devices:
            device.all_notes_off()
            device.stop()
        self.clock_source.stop()

    def warp(self, warper):
        """ Apply a PWarp object to warp our clock's timing. """
        self.clock_source.warp(warper)

    def unwarp(self, warper):
        """ Remove a PWarp object from our clock. """
        self.clock_source.warp(warper)

    def get_output_device(self):
        if len(self.output_devices) != 1:
            raise Exception("output_device is ambiguous for Timelines with multiple outputs")
        return self.output_devices[0]

    def set_output_device(self, output_device):
        """ Set a new device to send events to, removing any existing outputs. """
        self.output_devices = []
        self.add_output_device(output_device)

    output_device = property(get_output_device, set_output_device)

    def add_output_device(self, output_device):
        """ Append a new output device to our output list. """
        self.output_devices.append(output_device)
        self.clock_multipliers[output_device] = make_clock_multiplier(output_device.ticks_per_beat, self.ticks_per_beat)

    def schedule(self,
                 params: dict = None,
                 quantize: float = None,
                 delay: float = 0,
                 count: Optional[int] = None,
                 interpolate: str = INTERPOLATION_NONE,
                 output_device: Any = None,
                 remove_when_done: bool = True,
                 name: Optional[str] = None,
                 replace: bool = False,
                 track_index: Optional[int] = None) -> Track:
        """
        Schedule a new track within this Timeline.

        Args:
            params (dict):           Event dictionary. Keys are generally EVENT_* values, defined in constants.py.
                                     If params is None, a new empty Track will be scheduled and returned.
                                     This can be updated with Track.update().
                                     params can alternatively be a Pattern that generates a dict output.
            name (str):              Optional name for the track.
            quantize (float):        Quantize level, in beats. For example, 1.0 will begin executing the
                                     events on the next whole beats.
            delay (float):           Delay time, in beats, before events should be executed.
                                     If `quantize` and `delay` are both specified, quantization is applied,
                                     and the event is scheduled `delay` beats after the quantization time.
            count (int):             Number of events to process, or unlimited if not specified.
            interpolate (int):       Interpolation mode for control segments.
            output_device:           Output device to send events to. Uses the Timeline default if not specified.
            remove_when_done (bool): If True, removes the Track from the Timeline when it is finished.
                                     Otherwise, retains the Track, so update() can later be called to schedule
                                     additional events on it.
            name (str):              Optional name to identify the Track. If given, can be used to update the track's
                                     parameters in future calls to schedule() by specifying replace=True.
            replace (bool):          Must be used in conjunction with the `name` parameter. Instead of scheduling a
                                     new Track, this updates the parameters of an existing track with the same name.
            track_index (int):       When specified, inserts the Track at the given index.
                                     This can be used to set the priority of an event and ensure that it happens
                                     before another Track is evaluted, used in (e.g.) Track.update().

        Returns:
            The new `Track` object.

        Raises:
            TrackLimitReachedException: If `max_tracks` has been reached.
        """
        if not output_device:
            #--------------------------------------------------------------------------------
            # If no output device exists, send to the system default MIDI output.
            #--------------------------------------------------------------------------------
            if not self.output_devices:
                self.add_output_device(MidiOutputDevice())
            output_device = self.output_devices[0]

        #--------------------------------------------------------------------------------
        # If replace=True is specified, updated the params of any existing track
        # with the same name. If none exists, proceed to create it as usual.
        #--------------------------------------------------------------------------------
        if replace:
            if name is None:
                raise ValueError("Must specify a track name if `replace` is specified")
            for existing_track in self.tracks:
                if existing_track.name == name:
                    existing_track.update(params, quantize=quantize)
                    # TODO: Add unit test around this
                    return existing_track

        if self.max_tracks and len(self.tracks) >= self.max_tracks:
            raise TrackLimitReachedException("Timeline: Refusing to schedule track (hit limit of %d)" % self.max_tracks)

        def add_track(track):
            #--------------------------------------------------------------------------------
            # Add a new track.
            #--------------------------------------------------------------------------------
            if track_index is not None:
                self.tracks.insert(track_index, track)
            else:
                self.tracks.append(track)
            log.info("Timeline: Scheduled new track (total tracks: %d)" % len(self.tracks))

        if isinstance(params, Track):
            track = params
            track.reset()
        else:
            #--------------------------------------------------------------------------------
            # Take a copy of params to avoid modifying the original
            #--------------------------------------------------------------------------------
            track = Track(self,
                          events=copy.copy(params),
                          max_event_count=count,
                          interpolate=interpolate,
                          output_device=output_device,
                          remove_when_done=remove_when_done,
                          name=name)

        if quantize is None:
            quantize = self.defaults.quantize
        if quantize or delay:
            #--------------------------------------------------------------------------------
            # We don't want to begin events right away -- either wait till
            # the next beat boundary (quantize), or delay a number of beats.
            #--------------------------------------------------------------------------------
            self._schedule_action(function=lambda: add_track(track),
                                  quantize=quantize,
                                  delay=delay)
        else:
            #--------------------------------------------------------------------------------
            # Begin events on this track right away.
            #--------------------------------------------------------------------------------
            add_track(track)

        return track

    #--------------------------------------------------------------------------------
    # Backwards-compatibility
    #--------------------------------------------------------------------------------
    sched = schedule

    def unschedule(self, track):
        """
        Remove a track from playback.

        Args:
            track: The Track object.
            
        Raises:
            TrackNotFoundException: If the track is not playing.
        """
        if track not in self.tracks:
            raise TrackNotFoundException("Track is not currently scheduled")
        self.tracks.remove(track)

    def _schedule_action(self, function, quantize=0.0, delay=0.0):
        scheduled_time = self.current_time
        if quantize:
            scheduled_time = quantize * math.ceil(float(self.current_time) / quantize)
        scheduled_time += delay
        action = Action(scheduled_time, function)
        self.actions.append(action)

    def get_track(self, track_id):
        """
        Get the Track corresponding to the given track_id.
        track_id can be a numeric index, or the name corresponding to a track.

        Args:
            track_id: An index or name

        Returns:
            The Track object, or None if not found.
        """
        if isinstance(track_id, int):
            return self.tracks[track_id]
        elif isinstance(track_id, str):
            for track in self.tracks:
                if track.name == track_id:
                    return track
            return None
        else:
            raise TypeError("Invalid type for track_id (must be an int or str)")

    def clear(self):
        for track in self.tracks[:]:
            self.unschedule(track)

    def wait(self):
        while self.running:
            time.sleep(0.1)
