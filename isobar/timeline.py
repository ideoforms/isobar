import time
import math
import copy
import thread
from isobar import *
from isobar.pattern import *

import isobar.io

class Timeline:
	CLOCK_INTERNAL = 0
	CLOCK_EXTERNAL = 1

	def __init__(self, bpm = 120, device = None):
		"""expect to receive one tick per beat, generate events at 120bpm"""
		self.ticklen = 1/24.0
		self.beats = -.0001
		self.device = device
		self.channels = []

		self.bpm = None
		self.clock = None
		self.clocksource = None

		if hasattr(bpm, "clocktarget"):
			bpm.clocktarget = self
			self.clocksource = bpm
			self.clockmode = self.CLOCK_EXTERNAL
		else:
			self.bpm = bpm
			self.clock = Clock(60.0 / self.bpm / 24.0)
			self.clockmode = self.CLOCK_INTERNAL
		
	def tick(self):
		for channel in self.channels:
			channel.tick(self.ticklen)
			if channel.finished:
				self.channels.remove(channel)

	def reset_to_beat(self):
		for channel in self.channels:
			channel.reset_to_beat()

	def beat(self):
		pass 

	def reset(self):
		# print "tl reset!"
		self.beats = -.0001
		# XXX probably shouldn't have to do this - should channels read the tl ticks value?
		for channel in self.channels:
			channel.reset()

	def background(self):
		t = thread.start_new_thread(self.run, ())

	def run(self):
		# create clock with 64th-beat granularity
		if self.clockmode == self.CLOCK_INTERNAL:
			self.clock.run(self)
		else:
			self.clocksource.run()

	def output(self, device):
		self.device = device

	def sched(self, dict, quantize = 0):
		if not self.device:
			self.device = isobar.io.MidiOut()

		# hmm - why do we need to copy this?
		# c = channel(copy.deepcopy(dict))
		# c = Channel(copy.copy(dict))
		c = Channel(dict)
		c.device = self.device
		self.channels.append(c)

class Channel:
	def __init__(self, dict = {}):
		dict.setdefault('note', 60)
		dict.setdefault('transpose', 0)
		dict.setdefault('dur', 1)
		dict.setdefault('amp', 32)
		dict.setdefault('channel', 0)
		dict.setdefault('omit', 0)
		dict.setdefault('gate', 1.0)
		dict.setdefault('phase', 0.0)
		dict.setdefault('jitter', 0.0)

		dict.setdefault('octave', 0)

		if dict.has_key('key'):
			pass
		elif dict.has_key('scale'):
			dict['key'] = Key(0, dict['scale'])
		else:
			dict['scale'] = Scale.major
			dict['key'] = Key(0, dict['scale'])

		# might be nice to create a dict subclass which automatically
		# creates pconsts when integer values are requested
		for k, value in dict.iteritems():
			if not isinstance(value, Pattern):
				# print "setting %s to pconst" % k
				dict[k] = PConst(value)

		dict['pos'] = 0
		dict['dur_now'] = 0
		dict['phase_now'] = dict['phase'].next()
		dict['next_note'] = 0

		self.dict = dict
		self.noteOffs = []
		self.finished = False

	def tick(self, time):
		# print " - ch: pos = %.5f" % self.dict['pos']

		#----------------------------------------------------------------------
		# process noteOffs before we play the next note, else notes
		# of gate = 1.0 will immediately be cancelled.
		#----------------------------------------------------------------------
		self.processNoteOffs()

		try:
			if self.dict['pos'] >= self.dict['next_note'] + self.dict['phase_now']:
				# self.dict['pos'] -= self.dict['dur_now']
				self.dict['dur_now'] = self.dict['dur'].next()
				self.dict['phase_now'] = self.dict['phase'].next()

				self.play()

				self.dict['next_note'] += self.dict['dur_now'] + self.dict['jitter'].next()
		except StopIteration:
			self.finished = True

		self.dict['pos'] += time

	def reset_to_beat(self):
		self.dict['pos'] = round(self.dict['pos']) + 1/24.0

	def reset(self):
		self.dict['pos'] = 0
		self.dict['dur_now'] = 0
		self.dict['next_note'] = 0

	def play(self):
		if self.dict.has_key("degree"):
			degree = self.dict['degree'].next()
			key = self.dict['key'].next()
			octave = self.dict['octave'].next()
			note = key[degree] + (octave * 12)
		else:
			note = self.dict['note'].next()

		if note is None:
			return

		note   += self.dict['transpose'].next()
		amp     = self.dict['amp'].next()
		channel = self.dict['channel'].next()

		if random.uniform(0, 1) < self.dict['omit'].next():
			return

		self.device.noteOn(note, amp, channel)

		gate = self.dict['gate'].next()
		note_dur = self.dict['dur_now'] * gate
		self.schedNoteOff(self.dict['next_note'] + note_dur + self.dict['phase_now'], note, channel)

	def schedNoteOff(self, time, note, channel):
		self.noteOffs.append([ time, note, channel ])

	def processNoteOffs(self):
		for n, note in enumerate(self.noteOffs):
			if note[0] <= self.dict['pos']:
				self.device.noteOff(note[1], note[2])
				self.noteOffs.pop(n)

# a clock is relied upon to generate accurate tick() events every fraction of a note.
# it should handle millisecond-level jitter internally - ticks should always be sent out on time!
# period, in seconds, corresponds to a 24th crotchet (1/96th of a bar), as per MIDI
class Clock:
	def __init__(self, ticksize = 1/24.0):
		self.ticksize_orig = ticksize
		self.ticksize = ticksize
		self.warpers = []

	def run(self, timeline):
		clock0 = time.time() - self.ticksize
		clock1 = time.time()
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

			time.sleep(0.0001)
			clock1 = time.time()

	def warp(self, warper):
		self.warpers.append(warper)

	def unwarp(self, warper):
		self.warpers.remove(warper)

