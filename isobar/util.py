import random
import math
from .exceptions import InvalidMIDIPitch, UnknownNoteName, ClockException

note_names = [
    ["C"],
    ["C#", "Db"],
    ["D"],
    ["D#", "Eb"],
    ["E"],
    ["F"],
    ["F#", "Gb"],
    ["G"],
    ["G#", "Ab"],
    ["A"],
    ["A#", "Bb"],
    ["B"]
]

def normalize(array):
    """ Normalise an array to sum to 1.0. """
    if sum(array) == 0:
        return array
    return [float(n) / sum(array) for n in array]

def windex(weights, rng=random):
    """ Return a random index based on a list of weights, from 0..(len(weights) - 1).
    Assumes that weights is already normalised. """
    n = rng.uniform(0, 1)
    for i in range(len(weights)):
        if n < weights[i]:
            return i
        n = n - weights[i]

def wnindex(weights, rng=random):
    """ Returns a random index based on a list of weights.
    Normalises list of weights before executing. """
    wnorm = normalize(weights)
    return windex(wnorm, rng=rng)

def wchoice(array, weights, rng=random):
    """ Performs a weighted choice from a list of values (assumes pre-normalised weights) """
    index = windex(weights, rng=rng)
    return array[index]

def wnchoice(array, weights, rng=random):
    """ Performs a weighted choice from a list of values
    (does not assume pre-normalised weights). """
    index = wnindex(weights, rng=rng)
    return array[index]

def note_name_to_midi_note(name):
    """ Maps a MIDI note name (D3, C#6) to a value.
    Assumes that middle C is C4. """
    if name[-1].isdigit():
        octave = int(name[-1])
        name = name[:-1]
    else:
        octave = 0

    try:
        index = note_names.index([nameset for nameset in note_names if name in nameset][0])
    except IndexError:
        raise UnknownNoteName("Unknown note name: %s" % name)

    return octave * 12 + index

def midi_note_to_note_name(note):
    """
    Maps a MIDI note index to a note name.
    Supports fractional pitches.
    """
    if (type(note) is not int and type(note) is not float) or (note < 0 or note > 127):
        raise InvalidMIDIPitch()

    degree = int(note) % len(note_names)
    octave = int(note / len(note_names)) - 1
    str = "%s%d" % (note_names[degree][0], octave)
    frac = math.modf(note)[0]
    if frac > 0:
        str = (str + " + %2f" % frac)

    return str

def midi_note_to_frequency(note):
    """ Maps a MIDI note index to a frequency. """
    if note is None:
        return None
    return 440.0 * pow(2, (note - 69.0) / 12)

def bipolar_diverge(maximum):
    """ Returns [0, 1, -1, ...., maximum, -maximum ] """
    sequence = list(sum(list(zip(list(range(maximum + 1)), list(range(0, -maximum - 1, -1)))), ()))
    sequence.pop(0)
    return sequence

def filter_tone_row(source, target, bend_limit=7):
    """ Filters the notes in <source> by the permitted notes in <target>.
    returns a tuple (<bool> acceptable, <int> pitch_bend) """
    bends = bipolar_diverge(bend_limit)
    for bend in bends:
        if all(((note + bend) % 12) in target for note in source):
            return (True, bend)
    return (False, 0)

def random_seed(seed):
    random.seed(seed)

def make_clock_multiplier(output_clock_rate, input_clock_rate):
    multiple = 1.0
    if output_clock_rate and input_clock_rate:
        multiple = output_clock_rate / input_clock_rate
    if (multiple > 1 and int(multiple) != multiple) or (multiple < 1 and 1/multiple != int(1/multiple)):
        raise ClockException("Cannot sync output device (clock rates must integer multiples of each other)")

    pos = 1
    while True:
        rv = 0
        pos += multiple
        while round(pos, 8) > 1:
            pos -= 1
            rv += 1
        yield rv
