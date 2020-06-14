import sys
import math
import threading
import traceback

import isobar.io

from .track import Track
from .clock import Clock
from ..constants import DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO
from ..constants import EVENT_TIME, EVENT_FUNCTION
from ..exceptions import TrackLimitReachedException
import logging

log = logging.getLogger(__name__)

class Timeline(object):
    """
    A Timeline object represents a number of Tracks, each of which
    represents a sequence of note or control events.
    """

    def __init__(self,
                 tempo=DEFAULT_TEMPO,
                 output_device=None,
                 clock_source=None,
                 ticks_per_beat=DEFAULT_TICKS_PER_BEAT):
        """ Expect to receive one tick per beat, generate events at 120bpm """
        self.current_time = 0
        self.output_devices = [output_device] if output_device else []
        self.tracks = []
        self.max_tracks = 0

        self._clock_source = None
        self.thread = None
        self.stop_when_done = True

        self.events = []

        if clock_source is None:
            clock_source = Clock(self, tempo, ticks_per_beat)
        self.clock_source = clock_source

    def get_clock_source(self):
        return self._clock_source

    def set_clock_source(self, clock_source):
        clock_source.clock_target = self
        self._clock_source = clock_source

    clock_source = property(get_clock_source, set_clock_source)

    def get_ticks_per_beat(self):
        return self.clock_source.ticks_per_beat

    def set_ticks_per_beat(self, ticks_per_beat):
        self.clock_source.ticks_per_beat = ticks_per_beat

    ticks_per_beat = property(get_ticks_per_beat, set_ticks_per_beat)

    @property
    def tick_duration(self):
        """
        Tick duration, in beats.
        """
        return 1.0 / self.ticks_per_beat

    @property
    def tempo(self):
        """ Returns the tempo of this timeline's clock, or None if an external
        clock source is used (in which case the tempo is unknown).
        """
        return self.clock_source.tempo

    def tick(self):
        """
        Called once every tick to trigger new events.
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
                event[EVENT_FUNCTION]()
                self.events.remove(event)

        #--------------------------------------------------------------------------------
        # Copy self.tracks because removing from it whilst using it = bad idea
        #--------------------------------------------------------------------------------
        for track in self.tracks[:]:
            track.tick()
            if track.is_finished:
                self.tracks.remove(track)

        #--------------------------------------------------------------------------------
        # If we've run out of notes, raise a StopIteration.
        #--------------------------------------------------------------------------------
        if len(self.tracks) == 0 and len(self.events) == 0 and self.stop_when_done:
            raise StopIteration

        #--------------------------------------------------------------------------------
        # Tell our output devices to move forward a step.
        #--------------------------------------------------------------------------------
        for device in self.output_devices:
            device.tick(self.tick_duration)

        #--------------------------------------------------------------------------------
        # Increment beat count according to our current tick_length.
        #--------------------------------------------------------------------------------
        self.current_time += self.tick_duration

    def dump(self):
        """ Output a summary of this Timeline object
            """
        print("Timeline (clock: %s, tempo %s)" % (self.clock_source, self.clock_source.tempo if self.clock_source.tempo else "unknown"))

        print((" - %d devices" % len(self.output_devices)))
        for device in self.output_devices:
            print(("   - %s" % device))

        print((" - %d tracks" % len(self.tracks)))
        for tracks in self.tracks:
            print(("   - %s" % tracks))

    def reset_to_beat(self):
        """ Reset our timer to the last beat.
        Useful when a MIDI Stop/Reset message is received. """

        self.current_time = round(self.current_time)
        for tracks in self.tracks:
            tracks.reset_to_beat()

    def reset(self):
        """ Reset our timeline to t = 0. """
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
            self.clock_source.run()

        except StopIteration:
            #--------------------------------------------------------------------------------
            # This will be hit if every Pattern in a timeline is exhausted.
            #--------------------------------------------------------------------------------
            log.info("Timeline: Finished")

        except Exception as e:
            print((" *** Exception in background Timeline thread: %s" % e))
            traceback.print_exc(file=sys.stdout)

    def start(self):
        log.info("Timeline: Starting")

    def stop(self):
        log.info("Timeline: Stopping")
        for device in self.output_devices:
            device.all_notes_off()
            device.stop()

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

    def schedule(self, params, quantize=0, delay=0, output_device=None):
        """
        Schedule a new track within this Timeline.

        Args:
            params (dict): Event dictionary. Keys are generally EVENT_* values, defined in constants.py
            quantize (float): Quantize level, in beats. For example, 1.0 will begin executing the
                              events on the next whole beats.
            delay (float): Delay time, in beats, before events should be executed.
                           If `quantize` and `delay` are both specified, quantization is applied first,
                           and the event is scheduled `delay` beats after the quantization time.
            output_device: Output device to send events to. Uses the Timeline default if not specified.

        Returns:
            A new `Track` object if the track has been created immediately.
            If `quantize` or `delay` have been used, return value is None as the track creation is deferred.

        Raises:
            TrackLimitReachedException: If `max_tracks` has been reached.
        """
        if not output_device:
            #--------------------------------------------------------------------------------
            # If no output device exists, send to the system default MIDI output.
            #--------------------------------------------------------------------------------            
            if not self.output_devices:
                self.add_output_device(isobar.io.MidiOut())
            output_device = self.output_devices[0]

        if self.max_tracks and len(self.tracks) >= self.max_tracks:
            raise TrackLimitReachedException("Timeline: refusing to schedule track (hit limit of %d)" % self.max_tracks)

        def _add_track():
            #--------------------------------------------------------------------------------
            # Add a new track.
            #--------------------------------------------------------------------------------
            track = Track(params, self, output_device)
            self.tracks.append(track)
            return track

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
                EVENT_FUNCTION: _add_track
            })
        else:
            #--------------------------------------------------------------------------------
            # Begin events on this track right away.
            #--------------------------------------------------------------------------------
            return _add_track()

    #--------------------------------------------------------------------------------
    # Backwards-compatibility
    #--------------------------------------------------------------------------------
    sched = schedule
