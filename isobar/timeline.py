import time
import math
import copy
from isobar import *
from isobar.pattern import *

class Timeline:
	def __init__(self, bpm = 120, device = None):
		"""expect to receive one tick per beat, generate events at 120bpm"""
		self.bpm = bpm
		self.ticklen = 1/64.0
		self.beats = -.0001
		self.device = device
		self.channels = []
		self.warper = None
		self.automater = None 
		
	def tick(self):
		ticklen = self.ticklen
		if self.warper is not None:
			ticklen *= (1.0 + self.warper.next())
		if self.automater is not None:
			self.automater.play(self.device)

		beats_now = self.beats + ticklen
		if math.floor(beats_now) >= math.floor(self.beats):
			# we've gone over a new beat boundary
			self.beat()
			# self.beats = beats_now
			self.beats += 1
		
		# print "tick"
		for channel in self.channels:
			channel.tick(ticklen)

	def beat(self):
		pass 
		# print "beat %d" % self.beats

	def reset(self):
		# print "tl reset!"
		self.beats = -.0001
		# XXX probably shouldn't have to do this - should channels read the tl ticks value?
		for channel in self.channels:
			channel.reset()

	def run(self):
		# create clock with 64th-beat granularity
		c = Clock(60.0 / self.bpm / 64)
		c.run(self)

	def output(self, device):
		self.device = device

	def sched(self, dict):
		# hmm - why do we need to copy this?
		# c = channel(copy.deepcopy(dict))
		c = Channel(dict)
		# XXX hack!
		c.device = self.device
		self.channels.append(c)

	def automate(self, auto):
		self.automater = auto

	def warp(self, pattern):
		self.warper = pattern

class Channel:
	def __init__(self, dict = {}):
		dict.setdefault('note', 60)
		dict.setdefault('transpose', 0)
		dict.setdefault('dur', 1)
		dict.setdefault('amp', 32)
		dict.setdefault('channel', 0)
		dict.setdefault('omit', 0)
		dict.setdefault('gate', 1.0)

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
		dict['next_note'] = 0

		self.dict = dict

		self.noteOffs = []

	def tick(self, time):
		# print " - ch: pos = %.5f" % self.dict['pos']
		if self.dict['pos'] >= self.dict['next_note']:
			# self.dict['pos'] -= self.dict['dur_now']
			self.dict['dur_now'] = self.dict['dur'].next()
			self.play()
			self.dict['next_note'] += self.dict['dur_now']

		self.processNoteOffs()
		self.dict['pos'] += time

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

		note += self.dict['transpose'].next()

		amp = self.dict['amp'].next()

		channel = self.dict['channel'].next()
		# print "playing %d, %d" % (note, amp)
		if random.uniform(0, 1) < self.dict['omit'].next():
			return

		self.device.noteOn(note, amp, channel)

		gate = self.dict['gate'].next()
		note_dur = self.dict['dur_now'] * gate
		# print "gate %s, note_dur %s" % (gate, note_dur)
		self.schedNoteOff(self.dict['next_note'] + note_dur, note, channel)

	def schedNoteOff(self, time, note, channel):
		self.noteOffs.append([ time, note, channel ])

	def processNoteOffs(self):
		# print "- processing noteOffs"
		for n, note in enumerate(self.noteOffs):
			# print "looking at %.2f, pos %.2f" % (note[0], self.dict['pos'])
			if note[0] <= self.dict['pos']:
				self.device.noteOff(note[1], note[2])
				self.noteOffs.pop(n)

# a clock is relied upon to generate accurate tick() events every fraction of a note.
# it should handle millisecond-level jitter internally - ticks should always be sent out on time!
# period, in seconds, corresponds to a 64th crotchet (1/256th of a bar)
class Clock:
	def __init__(self, period = 1/64.0):
		self.period = period

	def run(self, timeline):
		clock0 = time.time() - self.period
		clock1 = time.time()
		while True:
			if clock1 - clock0 >= self.period:
				# time for a tick
				timeline.tick()
				clock0 += self.period
				# print "ticked at %f" % time.time()

			time.sleep(0.0001)
			clock1 = time.time()
