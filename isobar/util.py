import random
import math

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

def normalize(array):
	if sum(array) == 0:
		return array
	return map(lambda n: float(n) / sum(array), array)

def windex(weights):
	n = random.uniform(0, 1)
	for i in range(len(weights)):
		if n < weights[i]:
			return i
		n = n - weights[i]

def wnindex(weights):
	wnorm = normalize(weights)
	return windex(wnorm)

def wchoice(array, weights):
	index = windex(weights)
	return array[index]

def wnchoice(array, weights):
	index = wnindex(weights)
	return array[index]

def nametomidi(name):
	if name[-1].isdigit():
		octave = int(name[-1])
		name = name[:-1]
	else:
		octave = 0

	index = note_names.index(filter(lambda nameset: name in nameset, note_names)[0])
	return octave * 12 + index

def miditopitch(note):
	degree = int(note) % len(note_names)
	return note_names[degree][0]

def miditoname(note):
	degree = int(note) % len(note_names)
	octave = int(note / len(note_names)) - 1
	str = "%s%d" % (note_names[degree][0], octave)
	frac = math.modf(note)[0]
	if frac > 0:
		str = (str + " + %2f" % frac)

	return str
	
