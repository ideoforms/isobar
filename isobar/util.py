import isobar
import random
import math
import sys

note_names = [
	[ "C" ],
	[ "C#", "Db" ],
	[ "D" ],
	[ "D#", "Eb" ],
	[ "E" ],
	[ "F" ],
	[ "F#", "Gb" ],
	[ "G" ],
	[ "G#", "Ab" ],
	[ "A" ],
	[ "A#", "Bb" ],
	[ "B" ]
]


isobar.debug = False

def log(message, *args):
	if isobar.debug:
		message = message % args
		sys.stderr.write("[isobar] %s\n" % message)

def normalize(array):
	""" Normalise an array to sum to 1.0. """
	if sum(array) == 0:
		return array
	return map(lambda n: float(n) / sum(array), array)

def windex(weights):
	""" Return a random index based on a list of weights, from 0..(len(weights) - 1).
	Assumes that weights is already normalised. """
	n = random.uniform(0, 1)
	for i in range(len(weights)):
		if n < weights[i]:
			return i
		n = n - weights[i]

def wnindex(weights):
	""" Returns a random index based on a list of weights. 
	Normalises list of weights before executing. """
	wnorm = normalize(weights)
	return windex(wnorm)

def wchoice(array, weights):
	""" Performs a weighted choice from a list of values (assumes pre-normalised weights) """
	index = windex(weights)
	return array[index]

def wnchoice(array, weights):
	""" Performs a weighted choice from a list of values
	(does not assume pre-normalised weights). """
	index = wnindex(weights)
	return array[index]

def nametomidi(name):
	""" Maps a MIDI note name (D3, C#6) to a value.
	Assumes that middle C is C4. """
	if name[-1].isdigit():
		octave = int(name[-1])
		name = name[:-1]
	else:
		octave = 0

	index = note_names.index(filter(lambda nameset: name in nameset, note_names)[0])
	return octave * 12 + index

def miditopitch(note):
	""" Maps a MIDI note index to a note name (independent of octave)
	miditopitch(0) -> "C"
	miditopitch(1) -> "C#" """
	degree = int(note) % len(note_names)
	return note_names[degree][0]

def miditoname(note):
	""" Maps a MIDI note index to a note name. """
	degree = int(note) % len(note_names)
	octave = int(note / len(note_names)) - 1
	str = "%s%d" % (note_names[degree][0], octave)
	frac = math.modf(note)[0]
	if frac > 0:
		str = (str + " + %2f" % frac)

	return str
	
