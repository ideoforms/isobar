import time
import math
import copy
import thread
import traceback
from isobar import *
from isobar.pattern import *

import isobar.io

class Timeline:
	CLOCK_INTERNAL = 0
	CLOCK_EXTERNAL = 1

	def __init__(self, bpm = 120, device = None):
		"""expect to receive one tick per beat, generate events at 120bpm"""
		self.ticklen = 1/24.0
		self.beats = 0
		self.devices = [ device ] if device else [] 
		self.channels = []
		self.automators = []
		self.max_channels = 0

		self.debug = False
		self.bpm = None
		self.clock = None
		self.clocksource = None
		self.thread = None

		self.stop_when_done = False

		self.events = []

		if hasattr(bpm, "clocktarget"):
			bpm.clocktarget = self
			self.clocksource = bpm
			self.clockmode = self.CLOCK_EXTERNAL
		else:
			self.bpm = bpm
			self.clock = Clock(60.0 / self.bpm / 24.0)
			self.clockmode = self.CLOCK_INTERNAL

	def tick(self):
		# if round(self.beats, 5) % 8 == 0:
		#	print "tick (%d active channels, %d pending events)" % (len(self.channels), len(self.events))

		#------------------------------------------------------------------------
		# copy self.events because removing from it whilst using it = bad idea.
		# perform events before channels are executed because an event might
		# include scheduling a quantized channel, which should then be
		# immediately evaluated.
		#------------------------------------------------------------------------
		for event in self.events[:]:
			#------------------------------------------------------------------------
			# the only event we currently get in a Timeline are add_channel events
			#  -- which have a raw function associated with them.
			# 
			# round needed because we can sometimes end up with beats = 3.99999999...
			# http://docs.python.org/tutorial/floatingpoint.html
			#------------------------------------------------------------------------
			if round(event["time"], 8) <= round(self.beats, 8):
				event["fn"]()
				self.events.remove(event)

		#------------------------------------------------------------------------
		# some devices (ie, MidiFileOut) require being told to tick
		#------------------------------------------------------------------------
		for device in self.devices:
			device.tick(self.ticklen)

		#------------------------------------------------------------------------
		# copy self.channels because removing from it whilst using it = bad idea
		#------------------------------------------------------------------------
		for channel in self.channels[:]:
			channel.tick(self.ticklen)
			if channel.finished:
				self.channels.remove(channel)

		if self.stop_when_done and len(self.channels) == 0:
			raise StopIteration

		#------------------------------------------------------------------------
		# TODO: should automator and channel inherit from a common superclass?
		#       one is continuous, one is discrete.
		#------------------------------------------------------------------------
		for automator in self.automators[:]:
			automator.tick(self.ticklen)
			if automator.finished:
				self.automators.remove(automator)

		self.beats += self.ticklen

	def dump(self):
		print "Timeline (clock: %s)" % ("external" if self.clockmode == self.CLOCK_EXTERNAL else "%sbpm" % self.bpm)

		print " - %d devices" % len(self.devices)
		for device in self.devices:
			print "   - %s" % device

		print " - %d channels" % len(self.channels)
		for channel in self.channels:
			print"   - %s" % channel

	def reset_to_beat(self):
		self.beats = round(self.beats) # + 1/24.0
		for channel in self.channels:
			channel.reset_to_beat()

	def reset(self):
		# print "tl reset!"
		self.beats = -.0001
		# XXX probably shouldn't have to do this - should channels read the tl ticks value?
		for channel in self.channels:
			channel.reset()

	def background(self):
		self.thread = thread.start_new_thread(self.run, ())

	def run(self, high_priority = True):
		""" Create clock with 64th-beat granularity.
		By default, attempts to run as a high-priority thread
		(though requires being run as root to re-nice the process) """
		try:
			import os
			os.nice(-20)
			print "Timeline: Running as high-priority thread"
		except:
			pass

		try:
			if self.clockmode == self.CLOCK_INTERNAL:
				self.clock.run(self)
			else:
				self.clocksource.run()
		except StopIteration:
			print "timeline finished"
		except Exception, e:
			print " *** Exception in background Timeline thread: %s" % e
			traceback.print_exc(file = sys.stdout)

	def warp(self, warper):
		self.clock.warp(warper)

	def unwarp(self, warper):
		self.clock.warp(warper)

	def add_output(self, device):
		self.devices.append(device)

	def sched(self, event, quantize = 0, delay = 0, count = 0, device = None):
		if not device:
			if not self.devices:
				print "timeline: adding default MIDI output"
				self.add_output(isobar.io.MidiOut())
			device = self.devices[0]

		if self.max_channels and len(self.channels) >= self.max_channels:
			print "*** timeline: refusing to schedule channel (hit limit of %d)" % self.max_channels
			return

		# hmm - why do we need to copy this?
		# c = channel(copy.deepcopy(dict))
		# c = Channel(copy.copy(dict))
		def addchan():
			#----------------------------------------------------------------------
			# this isn't exactly the best way to determine whether a device is
			# an automator or event generator. should we have separate calls?
			#----------------------------------------------------------------------
			if type(event) == dict and event.has_key("control") and False:
				pass
			else:
				c = Channel(event, count)
				c.device = device
				self.channels.append(c)

		if quantize or delay:
			if quantize:
				schedtime = quantize * math.ceil(float(self.beats + delay) / quantize)
			else:
				schedtime = self.beats + delay
			self.events.append({ 'time' : schedtime, 'fn' : addchan })
		else:
			addchan()

class AutomatorChannel:
	def __init__(self, dict = {}):
		dict.setdefault('value', 0.5)
		dict.setdefault('control', 0)
		dict.setdefault('channel', 0)

		for k, value in dict.iteritems():
			if not isinstance(value, Pattern):
				dict[k] = PAConst(value)

		self.dick = dict

	def tick(self, ticklen):
		pass	

class Channel:
	def __init__(self, events = {}, count = 0):
		#----------------------------------------------------------------------
		# evaluate in case we have a pattern which gives us an event
		# eg: PSeq([ { "note" : 20, "dur" : 0.5 }, { "note" : 50, "dur" : PWhite(0, 2) } ])
		# 
		# is this ever even necessary? 
		#----------------------------------------------------------------------
		# self.events = Pattern.pattern(events)
		self.events = events
		# print "events is %s" % self.events

		self.next()

		self.pos = 0
		self.dur_now = 0
		self.phase_now = self.event["phase"].next()
		self.next_note = 0

		self.noteOffs = []
		self.finished = False
		self.count_max = count
		self.count_now = 0

	def __str__(self):
		return "Channel(pos = %d, note = %s, dur = %s, dur_now = %d, channel = %s, control = %s)[count = %d/%d])" % (self.pos, self.event["note"], self.event["dur"], self.dur_now, self.event["channel"], self.event["control"] if "control" in self.event else "-", self.count_now, self.count_max)

	def next(self):
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

		if event.has_key('key'):
			pass
		elif event.has_key('scale'):
			event['key'] = Key(0, event['scale'])
		else:
			event['key'] = Key(0, Scale.major)

		#----------------------------------------------------------------------
		# this does the job of turning constant values into (PConst) patterns.
		#----------------------------------------------------------------------
		for key, value in event.items():
			event[key] = Pattern.pattern(value)

		self.event = event

	def tick(self, time):
		#----------------------------------------------------------------------
		# process noteOffs before we play the next note, else a repeated note
		# with gate = 1.0 will immediately be cancelled.
		#----------------------------------------------------------------------
		self.processNoteOffs()

		try:
			if round(self.pos, 8) >= round(self.next_note + self.phase_now, 8):
				self.dur_now = self.event['dur'].next()
				self.phase_now = self.event['phase'].next()

				self.play()

				self.next_note += self.dur_now

				self.next()

				self.count_now += 1
				if self.count_max and self.count_now >= self.count_max:
					raise StopIteration
		except StopIteration:
			self.finished = True

		self.pos += time

	def reset_to_beat(self):
		self.pos = round(self.pos) # + 1/24.0

	def reset(self):
		self.pos = 0
		self.dur_now = 0
		self.next_note = 0

	def play(self):
		values = {}
		for key, pattern in self.event.items():
			# TODO: HACK!! to prevent stepping through dur twice (see 'tick' above')
			if key == "dur":
				value = self.dur_now
			elif key == "phase":
				value = self.phase_now
			else:
				value = pattern.next()
			values[key] = value

		if "print" in values:
			print values["print"]
			return

		if "action" in values:
			# might have passed a function (auto-wrapped in a pattern)
			try:
				# print "value is now %s" % value
				values["action"]()
			except Exception, e:
				print "ex: %s" % e
				import traceback
				traceback.print_exc()
				pass

			return

		if "control" in values:
			value = values["value"]
			channel = values["channel"]
			print "time line control: %d, %d [ch %d]" % (values["control"], values["value"], values["channel"])
			self.device.control(values["control"], values["value"], values["channel"])
			return 

		if "address" in values:
			self.device.send(values["address"], values["params"])
			return

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
			# print "(rest)"
			# return
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
		# 
		#----------------------------------------------------------------------
		if hasattr(self.device, "event") and callable(getattr(self.device, "event")):
			d = copy.copy(values)
			for key, value in d.items():
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

			print "sending event - %s" % d
			self.device.event(d)
			return

		if values["amp"] > 0:
			# print "note %d (%d)" % (values["note"], values["amp"])
			# TODO: pythonic duck-typing approach might be better
			# TODO: doesn't handle arrays of amp, channel values, etc
			notes = values["note"] if hasattr(values["note"], '__iter__') else [ values["note"] ]

			for note in notes:
				self.device.noteOn(note, values["amp"], values["channel"])

				gate = values["gate"]
				note_dur = self.dur_now * values["gate"]
				self.schedNoteOff(self.next_note + note_dur + self.phase_now, note, values["channel"])

	def schedNoteOff(self, time, note, channel):
		self.noteOffs.append([ time, note, channel ])

	def processNoteOffs(self):
		for n, note in enumerate(self.noteOffs):
			if note[0] <= self.pos:
				self.device.noteOff(note[1], note[2])
				self.noteOffs.pop(n)

#----------------------------------------------------------------------
# a clock is relied upon to generate accurate tick() events every
# fraction of a note. it should handle millisecond-level jitter
# internally - ticks should always be sent out on time!
#
# period, in seconds, corresponds to a 24th crotchet (1/96th of a bar),
# as per MIDI
#----------------------------------------------------------------------

class Clock:
	def __init__(self, ticksize = 1/24.0):
		self.ticksize_orig = ticksize
		self.ticksize = ticksize
		self.warpers = []
		self.accelerate = 1.0

	def run(self, timeline):
		clock0 = clock1 = time.time() * self.accelerate
		try:
			timeline.tick()
			while True:
				if clock1 - clock0 >= self.ticksize:
					# time for a tick
					timeline.tick()
					clock0 += self.ticksize
					self.ticksize = self.ticksize_orig
					for warper in self.warpers:
						warp = warper.next()
						if warp > 0:
							self.ticksize *= (1.0 + warp)
						elif warp < 0:
							self.ticksize /= (1.0 - warp)

				time.sleep(0.002)
				clock1 = time.time() * self.accelerate
		except KeyboardInterrupt:
			print "interrupt caught, exiting"
			return

	def warp(self, warper):
		self.warpers.append(warper)

	def unwarp(self, warper):
		self.warpers.remove(warper)

