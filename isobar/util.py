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


def normalize(array):
    """ Normalise an array to sum to 1.0. """
    if sum(array) == 0:
        return array
    return [float(n) / sum(array) for n in array]

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

    try:
        index = note_names.index([nameset for nameset in note_names if name in nameset][0])
        return octave * 12 + index
    except:
        return None

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

def miditofreq(note):
    return 440.0 * pow(2, (note - 69.0) / 12)

def bipolar_diverge(maximum):
    """ returns [0, 1, -1, ...., maximum, -maximum ] """
    sequence = list(sum(list(zip(list(range(maximum + 1)), list(range(0, -maximum - 1, -1)))), ()))
    sequence.pop(0)
    return sequence

def filter_tone_row(source, target, bend_limit = 7):
    """ filters the notes in <source> by the permitted notes in <target>.
    returns a tuple (<bool> acceptable, <int> pitch_bend) """
    bends = bipolar_diverge(bend_limit)
    for bend in bends:
        if all(((note + bend) % 12) in target for note in source):
            return (True, bend)
    return (False, 0)

