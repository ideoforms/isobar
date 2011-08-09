import random
import copy

class Chord:
	""" Represents a chord made up of 1 or more note intervals.
	"""

	dict = { }

	def __init__(self, intervals = [], name = "unnamed chord", root = 0):
		self.intervals = intervals
		self.name = name
		self.root = root
		if not Chord.dict.has_key(name):
		   Chord.dict[name] = self

	def __str__(self):
		return "%s %s%s" % (self.name, self.semitones(), (" + %d" % self.root) if self.root > 0 else "")

	def semitones(self):
		semitones = [0] + map(lambda n: sum(self.intervals[0:n+1]), range(len(self.intervals)))
		return semitones

	@staticmethod
	def byname(name):
		return Chord.dict[name]

	def random():
		key = random.choice(Chord.dict.keys())
		c = copy.deepcopy(Chord.dict[key])
		c.root = random.randint(0, 12)
		return c

	def arbitrary(name = "chord"):
		intervals_poss = [ 3, 3, 4, 4, 5, 6 ]
		intervals = []
		top = random.randint(12, 18)
		n = 0
		while True:
			interval = random.choice(intervals_poss)
			n += interval
			if n > top:
				break
			intervals.append(interval)

		return Chord(intervals, name if name else "chord", random.randint(0, 12))

	byname = staticmethod(byname)
	random = staticmethod(random)
	arbitrary = staticmethod(arbitrary)

Chord.major			= Chord([ 4, 3, 5 ], "major")
Chord.minor			= Chord([ 3, 4, 5 ], "minor")
Chord.diminished	= Chord([ 3, 3, 6 ], "diminished")
Chord.augmented		= Chord([ 4, 4, 4 ], "diminished")

Chord.sus4			= Chord([ 5, 2, 5 ], "sus4")
Chord.sus2			= Chord([ 7, 2, 5 ], "sus4")
