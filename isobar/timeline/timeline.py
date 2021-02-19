import math
import copy
import threading

from .track import Track
from .clock import Clock
from .event import EventDefaults
from ..key import Key
from ..io import MidiOutputDevice
from ..constants import DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO
from ..constants import EVENT_TIME, EVENT_ACTION, INTERPOLATION_NONE
from ..exceptions import TrackLimitReachedException, TrackNotFoundException
from ..util import make_clock_multiplier
import logging

log = logging.getLogger(__name__)

class Timeline(object):
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
                 tempo=DEFAULT_TEMPO,
                 output_device=None,
                 clock_source=None,
                 ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
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
        self.events = []
        self.running = False
        self.ignore_exceptions = False

        self.defaults = EventDefaults()

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
            log.debug("Tick (%d active tracks, %d pending events)" % (len(self.tracks), len(self.events)))

        #--------------------------------------------------------------------------------
        # Copy self.events because removing from it whilst using it = bad idea.
        # Perform events before tracks are executed because an event might
        # include scheduling a quantized track, which should then be
        # immediately evaluated.
        #--------------------------------------------------------------------------------
        for event in self.events[:]:
            #--------------------------------------------------------------------------------
            # The only event we currently get in a Timeline are add_track events
            #  -- which have a function object associated with them.
            #
            # Round to work around rounding errors.
            # http://docs.python.org/tutorial/floatingpoint.html
            #--------------------------------------------------------------------------------
            if round(event[EVENT_TIME], 8) <= round(self.current_time, 8):
                event[EVENT_ACTION]()
                self.events.remove(event)

        #--------------------------------------------------------------------------------
        # Copy self.tracks because removing from it whilst using it = bad idea
        #--------------------------------------------------------------------------------
        for track in self.tracks[:]:
            try:
                track.tick()
            except Exception as e:
                if self.ignore_exceptions:
                    print("*** Exception in track: %s" % e)
                else:
                    raise
            if track.is_finished and track.remove_when_done:
                self.tracks.remove(track)
                log.info("Timeline: Track finished, removing from scheduler (total tracks: %d)" % len(self.tracks))

        #--------------------------------------------------------------------------------
        # If we've run out of notes, raise a StopIteration.
        #--------------------------------------------------------------------------------
        if len(self.tracks) == 0 and len(self.events) == 0 and self.stop_when_done:
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

    def run(self, stop_when_done=None, background=False):
        """ Run this Timeline in the foreground.

        If stop_when_done is set, returns when no tracks are currently
        scheduled; otherwise, keeps running indefinitely. """

        if stop_when_done and background:
            raise Exception("Can't select both stop_when_done and background")

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
                 params=None,
                 quantize=None,
                 delay=0,
                 count=None,
                 interpolate=INTERPOLATION_NONE,
                 output_device=None,
                 remove_when_done=True):
        """
        Schedule a new track within this Timeline.

        Args:
            params (dict):           Event dictionary. Keys are generally EVENT_* values, defined in constants.py.
                                     If params is None, a new empty Track will be scheduled and returned.
                                     This can be updated with Track.update() to begin generating events.
                                     params can alternatively be a Pattern that generates a dict output.
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

        if self.max_tracks and len(self.tracks) >= self.max_tracks:
            raise TrackLimitReachedException("Timeline: Refusing to schedule track (hit limit of %d)" % self.max_tracks)

        def start_track(track):
            #--------------------------------------------------------------------------------
            # Add a new track.
            #--------------------------------------------------------------------------------
            self.tracks.append(track)
            log.info("Timeline: Scheduled new track (total tracks: %d)" % len(self.tracks))

        if isinstance(params, Track):
            track = params
            track.reset()
        else:
            #--------------------------------------------------------------------------------
            # Take a copy of params to avoid modifying the original
            #--------------------------------------------------------------------------------
            track = Track(self, copy.copy(params), max_event_count=count, interpolate=interpolate,
                          output_device=output_device, remove_when_done=remove_when_done)

        if quantize is None:
            quantize = self.defaults.quantize
        if quantize or delay:
            #--------------------------------------------------------------------------------
            # We don't want to begin events right away -- either wait till
            # the next beat boundary (quantize), or delay a number of beats.
            #--------------------------------------------------------------------------------
            scheduled_time = self.current_time
            if quantize:
                scheduled_time = quantize * math.ceil(float(self.current_time) / quantize)
            scheduled_time += delay

            self.events.append({
                EVENT_TIME: scheduled_time,
                EVENT_ACTION: lambda: start_track(track)
            })
        else:
            #--------------------------------------------------------------------------------
            # Begin events on this track right away.
            #--------------------------------------------------------------------------------
            start_track(track)

        return track

    #--------------------------------------------------------------------------------
    # Backwards-compatibility
    #--------------------------------------------------------------------------------
    sched = schedule

    def unschedule(self, track):
        if track not in self.tracks:
            raise TrackNotFoundException("Track is not currently scheduled")
        self.tracks.remove(track)

    def clear(self):
        for track in self.tracks[:]:
            self.unschedule(track)
