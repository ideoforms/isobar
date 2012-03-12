import random


class Scale:
	dict = { }

	def __init__(self, semitones = [ 0, 2, 4, 5, 7, 9, 11 ], name = "unnamed scale"):
		self.semitones = semitones
		self.name = name
		self.octave_size = 12
		if not Scale.dict.has_key(name):
		   Scale.dict[name] = self

	def __str__(self):
		return "%s %s" % (self.name, self.semitones)

	def __getitem__(self, key):
		return self.get(key)

	def __eq__(self, other):
		return self.semitones == other.semitones and self.octave_size == other.octave_size

	def get(self, n):
		if n is None:
			return None

		octave = int(n / len(self.semitones))
		degree = n % len(self.semitones)
		note = (self.octave_size * octave) + self.semitones[degree]
		return note

	def copy(self):
		other = Scale(self.semitones, self.name)
		return other

	def change(self):
		i = random.randint(0, len(self.semitones) - 1)
		j = random.randint(0, len(self.semitones) - 1)
		if i <> j:
			tmp = self.semitones[i]
			self.semitones[i] = self.semitones[j]
			self.semitones[j] = tmp
		return self

	def shuffle(self):
		random.shuffle(self.semitones)
		return self

	def indexOf(self, note):
		print "getting index of %d" % note
		octave = int(note / self.octave_size)
		index = octave * len(self.semitones)
		note -= octave * self.octave_size
		degree = 0

		while note > self.semitones[degree] and degree < len(self.semitones) - 1:
			degree += 1

		index += degree
		return index

	@staticmethod
	def all():
		return Scale.dict.values()

	@staticmethod
	def byname(name):
		return Scale.dict[name]

	@staticmethod
	def random():
		key = random.choice(Scale.dict.keys())
		return Scale.dict[key]

Scale.chromatic     = Scale([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ], "chromatic")
Scale.major         = Scale([ 0, 2, 4, 5, 7, 9, 11 ], "major")
Scale.minor         = Scale([ 0, 2, 3, 5, 7, 8, 11 ], "minor")
Scale.minor         = Scale([ 0, 2, 3, 5, 7, 8, 11 ], "minor")
Scale.minorPenta    = Scale([ 0, 3, 5, 7, 10 ], "minorPenta")
Scale.majorPenta    = Scale([ 0, 2, 4, 7, 9 ], "majorPenta")
Scale.ritusen       = Scale([ 0, 2, 5, 7, 9 ], "ritusen")
Scale.pelog         = Scale([ 0, 1, 3, 7, 8 ], "pelog")
Scale.augmented     = Scale([ 0, 3, 4, 7, 8, 11 ], "augmented")
Scale.augmented2    = Scale([ 0, 1, 4, 5, 8, 9 ], "augmented 2")

Scale.ionian        = Scale([ 0, 2, 4, 5, 7, 9, 11 ], "ionian")
Scale.dorian        = Scale([ 0, 2, 3, 5, 7, 9, 10 ], "dorian")
Scale.phrygian      = Scale([ 0, 1, 3, 5, 7, 8, 10 ], "phrygian")
Scale.lydian        = Scale([ 0, 2, 4, 6, 7, 9, 11 ], "lydian")
Scale.mixolydian    = Scale([ 0, 2, 4, 5, 7, 9, 10 ], "mixolydian")
Scale.aeolian       = Scale([ 0, 2, 3, 5, 7, 8, 10 ], "aeolian")
Scale.locrian       = Scale([ 0, 1, 3, 5, 6, 8, 10 ], "locrian")
Scale.fourths		= Scale([ 0, 2, 5, 7 ], "fourths")

