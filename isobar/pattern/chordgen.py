import sys
import random

from isobar import *
from isobar.pattern import *

class pchordgen(Pattern):

	notes_white = [ 0, 2, 4, 5, 7, 9, 11 ]
	notes_black = [ 1, 3, 6, 8, 10 ]

	def __init__(self, base = 60, note_count_min = 1, note_count_max = 6, note_interval_min = 0, note_interval_max = 3):
		self.base = base
		self.note_count_min = note_count_min
		self.note_count_max = note_count_max
		self.note_interval_min = note_interval_min
		self.note_interval_max = note_interval_max

		self.only_white = False
		self.only_black = False

		self.scale_white = Scale(self.notes_white)
		self.scale_black = Scale(self.notes_black)

	def __str__(self):
		return "chordgen"

	def next(self):
		print "min %d, max %d / %d, %d" % (self.note_count_min, self.note_count_max, self.note_interval_min, self.note_interval_max)
		base = self.value(self.base)
		note_count_min = self.value(self.note_count_min)
		note_count_max = self.value(self.note_count_max)
		note_interval_min = self.value(self.note_interval_min)
		note_interval_max = self.value(self.note_interval_max)

		chord = [] 
		note_count = random.randint(note_count_min, note_count_max)
		cur_white = bool(random.randint(0, 1))
		note_last = 0

		for n in range(note_count):
			scale = self.scale_white if cur_white else self.scale_black
			index = scale.indexOf(note_last)
			index = index + random.randint(note_interval_min, note_interval_max)
			note_last = scale[index]
			chord.append(note_last)

			cur_white = not cur_white

		return map(lambda n: n + self.base, chord)

