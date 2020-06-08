import sys
import math
import _thread
import traceback

import isobar.io

from .track import Track
from .clock import Clock
from ..constants import TICKS_PER_BEAT
from ..constants import EVENT_TIME, EVENT_FUNCTION
from ..exceptions import TrackLimitReachedException
import logging

log = logging.getLogger(__name__)

class Timeline(object):
    """
    A Timeline object represents a number of Tracks, each of which
    represents a sequence of note or control events.
    """

    def __init__(self, clock=120, output_device=None):
        """ Expect to receive one tick per beat, generate events at 120bpm """
        self.tick_duration = 1.0 / TICKS_PER_BEAT
        self.beats = 0
        self.outputs = [output_device] if output_device else []
        self.tracks = []
        self.automators = []
        self.max_tracks = 0

        self.clock = None
        self.clock_source = None
        self.thread = None
        self.stop_when_done = True

        self.events = []

        if hasattr(clock, "clock_target"):
            #------------------------------------------------------------------------
            # Follow external clock.
            #------------------------------------------------------------------------
            clock.clock_target = self
            self.clock_source = clock
        else:
            #------------------------------------------------------------------------
            # Create internal clock for native timekeeping.
            #------------------------------------------------------------------------
            self.clock = Clock(60.0 / (clock * TICKS_PER_BEAT))

    @property
    def bpm(self):
        """ Returns the tempo of this timeline's clock, or None if an external
        clock source is used (in which case the bpm is unknown).
        """
        if self.has_external_clock:
            return None
        else:
            return self.clock.bpm

    @property
    def has_external_clock(self):
        """ Return True if we're using an external clock source. """
        return bool(self.clock_source)

    def tick(self):
        """
        Called once every tick to trigger new events.
        """
        #------------------------------------------------------------------------
        # Each time we arrive at precisely a new beat, generate a debug msg.
        # Round to several decimal places to avoid 7.999999999 syndrome.
        # http://docs.python.org/tutorial/floatingpoint.html
        #------------------------------------------------------------------------
        if round(self.beats, 8) % 1 == 0:
            log.debug("----------------------------------------------------------------")
            log.debug("Tick (%d active tracks, %d pending events)" % (len(self.tracks), len(self.events)))

        #------------------------------------------------------------------------
        # Copy self.events because removing from it whilst using it = bad idea.
        # Perform events before tracks are executed because an event might
        # include scheduling a quantized track, which should then be
        # immediately evaluated.
        #------------------------------------------------------------------------
        for event in self.events[:]:
            #------------------------------------------------------------------------
            # The only event we currently get in a Timeline are add_track events
            #  -- which have a function object associated with them.
            #
            # Round to work around rounding errors.
            # http://docs.python.org/tutorial/floatingpoint.html
            #------------------------------------------------------------------------
            if round(event[EVENT_TIME], 8) <= round(self.beats, 8):
                event[EVENT_FUNCTION]()
                self.events.remove(event)

        #------------------------------------------------------------------------
        # Copy self.tracks because removing from it whilst using it = bad idea
        #------------------------------------------------------------------------
        for track in self.tracks[:]:
            track.tick(self.tick_duration)
            if track.finished:
                self.tracks.remove(track)

        #------------------------------------------------------------------------
        # If we've run out of notes, raise a StopIteration.
        #------------------------------------------------------------------------
        if len(self.tracks) == 0 and self.stop_when_done:
            print("raising stop: %d" % self.stop_when_done)
            raise StopIteration

        #------------------------------------------------------------------------
        # TODO: should automator and track inherit from a common superclass?
        #       One is continuous, one is discrete.
        #------------------------------------------------------------------------
        for automator in self.automators[:]:
            automator.tick(self.tick_duration)
            if automator.finished:
                self.automators.remove(automator)

        #------------------------------------------------------------------------
        # Tell our devices (ie, MidiFileOut) to move forward a step.
        #------------------------------------------------------------------------
        for device in self.outputs:
            device.tick(self.tick_duration)

        #------------------------------------------------------------------------
        # Increment beat count according to our current tick_length.
        #------------------------------------------------------------------------
        self.beats += self.tick_duration

    def dump(self):
        """ Output a summary of this Timeline object
            """
        print(("Timeline (clock: %s)" % ("external" if self.has_external_clock else "%sbpm" % self.bpm)))

        print((" - %d devices" % len(self.outputs)))
        for device in self.outputs:
            print(("   - %s" % device))

        print((" - %d tracks" % len(self.tracks)))
        for tracks in self.tracks:
            print(("   - %s" % tracks))

    def reset_to_beat(self):
        """ Reset our timer to the last beat.
        Useful when a MIDI Stop/Reset message is received. """

        self.beats = round(self.beats)
        for tracks in self.tracks:
            tracks.reset_to_beat()

    def reset(self):
        """ Reset our timeline to t = 0. """
        self.beats = 0.0
        for track in self.tracks:
            track.reset()

    def background(self):
        """ Run this Timeline in a background thread. """
        self.thread = _thread.start_new_thread(self.run, ())

    def run(self, high_priority=True, stop_when_done=None):
        """ Run this Timeline in the foreground.
        By default, attempts to run as a high-priority thread for more
        accurate timing (though requires being run as root to re-nice the
        process.)

        If stop_when_done is set, returns when no tracks are currently
        scheduled; otherwise, keeps running indefinitely. """
        log.info("Timeline: Running")

        if stop_when_done is not None:
            self.stop_when_done = stop_when_done

        if high_priority:
            try:
                import os
                os.nice(-20)
                log.info("Timeline: Running as high-priority thread")
            except:
                log.info("Timeline: Standard thread priority (run with sudo for high-priority)")

        try:
            #------------------------------------------------------------------------
            # Start the clock. This might internal (eg a Clock object, running on
            # an independent thread), or external (eg a MIDI clock).
            #------------------------------------------------------------------------
            if self.has_external_clock:
                self.clock_source.run()
            else:
                self.clock.run(self)

        except StopIteration:
            #------------------------------------------------------------------------
            # This will be hit if every Pattern in a timeline is exhausted.
            #------------------------------------------------------------------------
            log.info("Timeline: Finished")

        except Exception as e:
            print((" *** Exception in background Timeline thread: %s" % e))
            traceback.print_exc(file=sys.stdout)

    def warp(self, warper):
        """ Apply a PWarp object to warp our clock's timing. """
        self.clock.warp(warper)

    def unwarp(self, warper):
        """ Remove a PWarp object from our clock. """
        self.clock.warp(warper)

    def set_output(self, device):
        """ Set a new device to send events to, removing any existing outputs. """
        self.outputs = []
        self.add_output(device)

    def add_output(self, device):
        """ Append a new output device to our output list. """
        self.outputs.append(device)

    @property
    def default_output(self):
        if not self.outputs:
            self.add_output(isobar.io.MidiOut())
        return self.outputs[0]

    def schedule(self, params, quantize=0, delay=0, output_device=None):
        """
        Schedule a new track within this Timeline.

        Args:
            params (dict): Event dictionary. Keys are generally EVENT_* values, defined in constants.py
            quantize (float): Quantize level, in beats. For example, 1.0 will begin executing the
                              events on the next whole beats
            delay (float): Delay time, in beats, before events should be executed
            output_device: Output device to send events to. Uses the Timeline default if not specified.

        Raises:
            TrackLimitReachedException: If `max_tracks` has been reached.
        """
        if not output_device:
            output_device = self.default_output

        if self.max_tracks and len(self.tracks) >= self.max_tracks:
            raise TrackLimitReachedException("Timeline: refusing to schedule track (hit limit of %d)" % self.max_tracks)

        def _add_track():
            #----------------------------------------------------------------------
            # This isn't the best way to determine whether a device is an
            # automator or event generator. Should we have separate calls?
            #----------------------------------------------------------------------
            track = Track(params, self, output_device)
            self.tracks.append(track)

        if quantize or delay:
            #----------------------------------------------------------------------
            # We don't want to begin events right away -- either wait till
            # the next beat boundary (quantize), or delay a number of beats.
            #----------------------------------------------------------------------
            if quantize:
                scheduled_time = quantize * math.ceil(float(self.beats + delay) / quantize)
            else:
                scheduled_time = self.beats + delay
            self.events.append({EVENT_TIME: scheduled_time, EVENT_FUNCTION: _add_track})
        else:
            #----------------------------------------------------------------------
            # Begin events on this track right away.
            #----------------------------------------------------------------------
            _add_track()

    #--------------------------------------------------------------------------------
    # Backwards-compatibility
    #--------------------------------------------------------------------------------
    sched = schedule
