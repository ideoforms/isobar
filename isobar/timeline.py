import sys
import time
import math
import copy
import _thread
import traceback
from isobar import *
from isobar.pattern import *

import isobar.io

import logging
log = logging.getLogger(__name__)

#------------------------------------------------------------------------
# Determines how fine-grained our clocking is -- events can't be
# scheduled any faster than this. 24 ticks per beat is identical
# to MIDI clocking.
#------------------------------------------------------------------------
TICKS_PER_BEAT = 24

class Timeline(object):
    """ A Timeline object represents a number of Channels, each of which
    represents a sequence of note or control events. """

    def __init__(self, clock=120, device=None):
        """ Expect to receive one tick per beat, generate events at 120bpm """
        self.tick_length = 1.0 / TICKS_PER_BEAT
        self.beats = 0
        self.devices = [ device ] if device else [] 
        self.channels = []
        self.automators = []
        self.max_channels = 0

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
        """ Returns the tempo of this timeline's clock (which may be internal
        or external). """
        if self.has_external.clock:
            return self.clock_source.bpm
        else:
            return self.clock.bpm

    @property
    def has_external_clock(self):
        """ Return True if we're using an external clock source. """
        return bool(self.clock_source)

    def tick(self):
        """ Called once every TICKS_PER_BEAT seconds (default 1/24s)
        to trigger new events. """

        #------------------------------------------------------------------------
        # Each time we arrive at precisely a new beat, generate a debug msg.
        # Round to several decimal places to avoid 7.999999999 syndrome.
        # http://docs.python.org/tutorial/floatingpoint.html
        #------------------------------------------------------------------------
        if round(self.beats, 8) % 1 == 0:
             log.debug("----------------------------------------------------------------")
             log.debug("Tick (%d active channels, %d pending events)" % (len(self.channels), len(self.events)))

        #------------------------------------------------------------------------
        # Copy self.events because removing from it whilst using it = bad idea.
        # Perform events before channels are executed because an event might
        # include scheduling a quantized channel, which should then be
        # immediately evaluated.
        #------------------------------------------------------------------------
        for event in self.events[:]:
            #------------------------------------------------------------------------
            # The only event we currently get in a Timeline are add_channel events
            #  -- which have a function object associated with them.
            # 
            # Round to work around rounding errors.
            # http://docs.python.org/tutorial/floatingpoint.html
            #------------------------------------------------------------------------
            if round(event["time"], 8) <= round(self.beats, 8):
                event["fn"]()
                self.events.remove(event)

        #------------------------------------------------------------------------
        # Tell our devices (ie, MidiFileOut) to move forward a step.
        #------------------------------------------------------------------------
        for device in self.devices:
            device.tick(self.tick_length)

        #------------------------------------------------------------------------
        # Copy self.channels because removing from it whilst using it = bad idea
        #------------------------------------------------------------------------
        for channel in self.channels[:]:
            channel.tick(self.tick_length)
            if channel.finished:
                self.channels.remove(channel)

        #------------------------------------------------------------------------
        # If we've run out of notes, throw a StopIteration.
        #------------------------------------------------------------------------
        if self.stop_when_done and len(self.channels) == 0:
            raise StopIteration

        #------------------------------------------------------------------------
        # TODO: should automator and channel inherit from a common superclass?
        #       One is continuous, one is discrete.
        #------------------------------------------------------------------------
        for automator in self.automators[:]:
            automator.tick(self.tick_length)
            if automator.finished:
                self.automators.remove(automator)

        #------------------------------------------------------------------------
        # Increment beats according to our current tick_length.
        #------------------------------------------------------------------------
        self.beats += self.tick_length

    def dump(self):
        """ Output a summary of this Timeline object
            """
        print(("Timeline (clock: %s)" % ("external" if self.has_external_clock else "%sbpm" % self.bpm)))

        print((" - %d devices" % len(self.devices)))
        for device in self.devices:
            print(("   - %s" % device))

        print((" - %d channels" % len(self.channels)))
        for channel in self.channels:
            print(("   - %s" % channel))

    def reset_to_beat(self):
        """ Reset our timer to the last beat.
        Useful when a MIDI Stop/Reset message is received. """

        self.beats = round(self.beats)
        for channel in self.channels:
            channel.reset_to_beat()

    def reset(self):
        """ Reset our timeline to t = 0. """
        self.beats = 0.0
        for channel in self.channels:
            channel.reset()

    def background(self):
        """ Run this Timeline in a background thread. """
        self.thread = _thread.start_new_thread(self.run, ())

    def run(self, high_priority=True, stop_when_done=True):
        """ Run this Timeline in the foreground.
        By default, attempts to run as a high-priority thread for more
        accurate timing (though requires being run as root to re-nice the
        process.)
        
        If stop_when_done is set, returns when no channels are currently
        scheduled; otherwise, keeps running indefinitely. """
        log.info("Timeline: Running")

        if stop_when_done is not None:
            self.stop_when_done = stop_when_done

        try:
            import os
            os.nice(-20)
            log.warn("Timeline: Running as high-priority thread")
        except:
            pass

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
            traceback.print_exc(file = sys.stdout)

    def warp(self, warper):
        """ Apply a PWarp object to warp our clock's timing. """
        self.clock.warp(warper)

    def unwarp(self, warper):
        """ Remove a PWarp object from our clock. """
        self.clock.warp(warper)

    def set_output(self, device):
        """ Set a new device to send events to, removing any existing outputs. """
        self.devices = []
        self.add_output(device)

    def add_output(self, device):
        """ Append a new output device to our output list. """
        self.devices.append(device)

    @property
    def default_output(self):
        if not self.devices:
            self.add_output(isobar.io.MidiOut())
        return self.devices[0]

    def sched(self, event, quantize = 0, delay = 0, count = 0, device = None):
        """ Schedule a new track within this Timeline. """
        if not device:
            device = self.default_output

        if self.max_channels and len(self.channels) >= self.max_channels:
            print("Timeline: refusing to schedule channel (hit limit of %d)" % self.max_channels)
            return

        def _add_channel():
            #----------------------------------------------------------------------
            # This isn't the best way to determine whether a device is an
            # automator or event generator. Should we have separate calls?
            #----------------------------------------------------------------------
            channel = Channel(event, count, self, device)
            self.channels.append(channel)

        if quantize or delay:
            #----------------------------------------------------------------------
            # We don't want to begin events right away -- either wait till
            # the next beat boundary (quantize), or delay a number of beats.
            #----------------------------------------------------------------------
            if quantize:
                scheduled_time = quantize * math.ceil(float(self.beats + delay) / quantize)
            else:
                scheduled_time = self.beats + delay
            self.events.append({ 'time' : scheduled_time, 'fn' : _add_channel })
        else:
            #----------------------------------------------------------------------
            # Begin events on this channel right away.
            #----------------------------------------------------------------------
            _add_channel()

class Channel:
    def __init__(self, events = {}, count = 0, timeline = None, device = None):
        #----------------------------------------------------------------------
        # evaluate in case we have a pattern which gives us an event
        # eg: PSeq([ { "note" : 20, "dur" : 0.5 }, { "note" : 50, "dur" : PWhite(0, 2) } ])
        # 
        # is this ever even necessary? 
        #----------------------------------------------------------------------
        # self.events = Pattern.pattern(events)
        self.events = events

        next(self)

        self.timeline = timeline
        self.device = device
        self.phase_now = next(self.event["phase"])

        #------------------------------------------------------------------------
        # Reset our play position.
        #------------------------------------------------------------------------
        self.reset()

        self.note_offs = []
        self.finished = False
        self.count_max = count
        self.count_now = 0

    def __str__(self):
        return "Channel(pos = %d, note = %s, dur = %s, dur_now = %d, channel = %s, control = %s)[count = %d/%d])" % (self.pos, self.event["note"], self.event["dur"], self.dur_now, self.event["channel"], self.event["control"] if "control" in self.event else "-", self.count_now, self.count_max)

    def __next__(self):
        #----------------------------------------------------------------------
        # event is a dictionary of patterns. anything which is not a pattern
        # (eg, constant values) are turned into PConsts.
        #----------------------------------------------------------------------
        event = Pattern.value(self.events)
    
        event.setdefault('note', 60)
        event.setdefault('transpose', 0)
        event.setdefault('dur', 1)
        event.setdefault('amp', 64)
        event.setdefault('channel', 0)
        event.setdefault('omit', 0)
        event.setdefault('gate', 1.0)
        event.setdefault('phase', 0.0)
        event.setdefault('octave', 0)

        if 'key' in event:
            pass
        elif 'scale' in event:
            event['key'] = Key(0, event['scale'])
        else:
            event['key'] = Key(0, Scale.default)

        #----------------------------------------------------------------------
        # this does the job of turning constant values into (PConst) patterns.
        #----------------------------------------------------------------------
        for key, value in list(event.items()):
            event[key] = Pattern.pattern(value)

        self.event = event

    def tick(self, time):
        #----------------------------------------------------------------------
        # process note_offs before we play the next note, else a repeated note
        # with gate = 1.0 will immediately be cancelled.
        #----------------------------------------------------------------------
        self.process_note_offs()

        try:
            if round(self.pos, 8) >= round(self.next_note + self.phase_now, 8):
                self.dur_now = next(self.event['dur'])
                self.phase_now = next(self.event['phase'])

                self.play()

                self.next_note += self.dur_now

                next(self)

                self.count_now += 1
                if self.count_max and self.count_now >= self.count_max:
                    raise StopIteration
        except StopIteration:
            self.finished = True

        self.pos += time

    def reset_to_beat(self):
        self.pos = round(self.pos)

    def reset(self):
        self.pos = 0
        self.dur_now = 0
        self.next_note = 0

    def play(self):
        values = {}
        for key, pattern in list(self.event.items()):
            # TODO: HACK!! to prevent stepping through dur twice (see 'tick' above')
            if key == "dur":
                value = self.dur_now
            elif key == "phase":
                value = self.phase_now
            else:
                value = next(pattern)
            values[key] = value

        #------------------------------------------------------------------------
        # print: Prints a value each time this event is triggered.
        #------------------------------------------------------------------------
        if "print" in values:
            print((values["print"]))
            return

        #------------------------------------------------------------------------
        # action: Carry out an action each time this event is triggered
        #------------------------------------------------------------------------
        if "action" in values:
            try:
                if "object" in values:
                    object = values["object"]
                    values["action"](object)
                else:
                    values["action"]()
            except Exception as e:
                print(("Exception when handling scheduled action: %s" % e))
                import traceback
                traceback.print_exc()
                pass

            return

        #------------------------------------------------------------------------
        # control: Send a control value
        #------------------------------------------------------------------------
        if "control" in values:
            value = values["value"]
            channel = values["channel"]
            log.debug("control (channel %d, control %d, value %d)", values["channel"], values["control"], values["value"]) 
            self.device.control(values["control"], values["value"], values["channel"])
            return 

        #------------------------------------------------------------------------
        # address: Send a value to an OSC endpoint
        #------------------------------------------------------------------------
        if "address" in values:
            self.device.send(values["address"], values["params"])
            return

        #------------------------------------------------------------------------
        # note/degree/etc: Send a MIDI note
        #------------------------------------------------------------------------
        note = None

        if "degree" in values:
            degree = values["degree"]
            key = values["key"]
            octave = values["octave"]
            if not degree is None:
                #----------------------------------------------------------------------
                # handle lists of notes (eg chords).
                # TODO: create a class which allows for scalars and arrays to handle
                # addition transparently
                #----------------------------------------------------------------------
                try:
                    values["note"] = [ key[n] + (octave * 12) for n in degree ]
                except:
                    values["note"] = key[degree] + (octave * 12)

        #----------------------------------------------------------------------
        # For cases in which we want to introduce a rest, simply set our 'amp'
        # value to zero. This means that we can still send rest events to
        # devices which receive all generic events (useful to display rests
        # when rendering a score).
        #----------------------------------------------------------------------
        if random.uniform(0, 1) < values['omit']:
            values["note"] = None

        if values["note"] is None:
            #----------------------------------------------------------------------
            # Rest.
            #----------------------------------------------------------------------
            values["note"] = 0
            values["amp"] = 0
        else:
            #----------------------------------------------------------------------
            # handle lists of notes (eg chords).
            # TODO: create a class which allows for scalars and arrays to handle
            # addition transparently.
            # 
            # the below does not allow for values["transpose"] to be an array,
            # for example.
            #----------------------------------------------------------------------
            try:
                values["note"] = [ note + values["transpose"] for note in values["note"] ]
            except:
                values["note"] += values["transpose"]


        #----------------------------------------------------------------------
        # event: Certain devices (eg Socket IO) handle generic events,
        #        rather than note_on/note_off. (Should probably have to 
        #        register for this behaviour rather than happening magically...)
        #----------------------------------------------------------------------
        if hasattr(self.device, "event") and callable(getattr(self.device, "event")):
            d = copy.copy(values)
            for key, value in list(d.items()):
                #------------------------------------------------------------------------
                # turn non-builtin objects into their string representations.
                # we don't want to call repr() on numbers as it turns them into strings,
                # which we don't want to happen in our resultant JSON.
                # TODO: there absolutely must be a way to do this for all objects which are
                #       non-builtins... ie, who are "class" instances rather than "type".
                #
                #       we could check dir(__builtins__), but for some reason, __builtins__ is
                #       different here than it is outside of a module!? 
                #
                #       instead, go with the lame option of listing "primitive" types.
                #------------------------------------------------------------------------
                if type(value) not in (int, float, bool, str, list, dict, tuple):
                    name = type(value).__name__
                    value = repr(value)
                    d[key] = value

            self.device.event(d)
            return

        #----------------------------------------------------------------------
        # note_on: Standard (MIDI) type of device
        #----------------------------------------------------------------------
        if values["amp"] > 0:
            # TODO: pythonic duck-typing approach might be better
            # TODO: doesn't handle arrays of amp, channel values, etc
            notes = values["note"] if hasattr(values["note"], '__iter__') else [ values["note"] ]

            #----------------------------------------------------------------------
            # Allow for arrays of amp, gate etc, to handle chords properly.
            # Caveat: Things will go horribly wrong for an array of amp/gate values
            # shorter than the number of notes.
            #----------------------------------------------------------------------
            for index, note in enumerate(notes):
                amp     = values["amp"][index] if isinstance(values["amp"], tuple) else values["amp"]
                channel = values["channel"][index] if isinstance(values["channel"], tuple) else values["channel"]
                gate    = values["gate"][index] if isinstance(values["gate"], tuple) else values["gate"]

                self.device.note_on(note, amp, channel)

                note_dur = self.dur_now * gate
                self.sched_note_off(self.next_note + note_dur + self.phase_now, note, channel)

    def sched_note_off(self, time, note, channel):
        self.note_offs.append([ time, note, channel ])

    def process_note_offs(self):
        for n, note in enumerate(self.note_offs):
            # TODO: create a Note object to represent these note_off events
            if note[0] <= self.pos:
                index = note[1]
                channel = note[2]
                self.device.note_off(index, channel)
                self.note_offs.pop(n)

#----------------------------------------------------------------------
# a clock is relied upon to generate accurate tick() events every
# fraction of a note. it should handle millisecond-level jitter
# internally - ticks should always be sent out on time!
#
# period, in seconds, corresponds to a 24th crotchet (1/96th of a bar),
# as per MIDI
#----------------------------------------------------------------------

class Clock:
    def __init__(self, tick_size = 1.0/24):
        self.tick_size_orig = tick_size
        self.tick_size = tick_size
        self.warpers = []
        self.accelerate = 1.0

    def run(self, timeline):
        clock0 = clock1 = time.time() * self.accelerate
        try:
            #------------------------------------------------------------------------
            # allow a tick to elapse before we call tick() for the first time
            # to keep Warp patterns in sync  
            #------------------------------------------------------------------------
            while True:
                if clock1 - clock0 >= self.tick_size:
                    # time for a tick
                    timeline.tick()
                    clock0 += self.tick_size
                    self.tick_size = self.tick_size_orig
                    for warper in self.warpers:
                        warp = next(warper)
                        #------------------------------------------------------------------------
                        # map [-1..1] to [0.5, 2]
                        #  - so -1 doubles our tempo, +1 halves it
                        #------------------------------------------------------------------------
                        warp = pow(2, warp)
                        self.tick_size *= warp

                time.sleep(0.002)
                clock1 = time.time() * self.accelerate
        except KeyboardInterrupt:
            print("interrupt caught, exiting")
            return

    def warp(self, warper):
        self.warpers.append(warper)

    def unwarp(self, warper):
        self.warpers.remove(warper)

