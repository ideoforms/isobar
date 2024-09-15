import random
import math
from typing import Any, Generator
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

def normalize(array: list[float]) -> list[float]:
    """
    Normalise an array to sum to 1.0.
    """
    if sum(array) == 0:
        return array
    return [float(n) / sum(array) for n in array]

def windex(weights: list[float], rng=random) -> float:
    """
    Return a random index based on a list of weights, from 0..(len(weights) - 1).
    Assumes that weights is already normalised.
    """
    n = rng.uniform(0, 1)
    for i in range(len(weights)):
        if n < weights[i]:
            return i
        n = n - weights[i]

def wnindex(weights: list[float], rng=random):
    """
    Returns a random index based on a list of weights.
    Normalises list of weights before executing.
    """
    wnorm = normalize(weights)
    return windex(wnorm, rng=rng)

def wchoice(array: list[Any], weights: list[float], rng=random):
    """
    Returns a weighted choice from a list of values (assumes pre-normalised weights)
    """
    index = windex(weights, rng=rng)
    return array[index]

def wnchoice(array, weights, rng=random):
    """ Performs a weighted choice from a list of values
    (does not assume pre-normalised weights). """
    index = wnindex(weights, rng=rng)
    return array[index]

def note_name_to_midi_note(name):
    """
    Maps a MIDI note name (D3, C#6) to a MIDI note value.
    Uses a convention of middle C (60) is represented as C4.

    If no octave is given, a note value between 0..11 is returned.
    """
    if name[-1].isdigit():
        sign = -1 if name[-2] == '-' else 1
        octave = sign * int(name[-1])
        if sign == 1:
            name = name[:-1]
        else:
            name = name[:-2]
    else:
        octave = -1

    try:
        index = note_names.index([nameset for nameset in note_names if name.capitalize() in nameset][0])
    except IndexError:
        raise UnknownNoteName("Unknown note name: %s" % name)

    return (octave + 1) * 12 + index

def midi_note_to_note_name(note: float) -> str:
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

def midi_note_to_frequency(note: float) -> float:
    """
    Maps a MIDI note index to a frequency.
    """
    if note is None:
        return None
    return 440.0 * pow(2, (note - 69.0) / 12)

def midi_note_to_frequency_just_intonation(note):
    note_ratios = [1/1, 256/243, 9/8, 32/27, 81/64, 4/3, 729/512, 3/2, 128/81, 27/16, 16/9, 243/128]
    octave = note // 12
    octave_note = note % 12
    octave_base_frequency = midi_note_to_frequency(octave * 12)
    octave_note_frequency = octave_base_frequency * note_ratios[octave_note]
    return octave_note_frequency

def note_name_to_frequency(note_name: str) -> float:
    """
    Returns the frequency corresponding to the given MIDI note name.

    Args:
        note_name: The note name

    Returns:
        float: The frequency
    """
    return midi_note_to_frequency(note_name_to_midi_note(note_name))

def midi_semitones_to_frequency_ratio(semitones: list[float]) -> float:
    """
    Map a MIDI semitone interval to a frequency ratio
    (e.g., input of 12 semitones -> output of 2.0)

    Args:
        semitones: The pitch difference, in semitones

    Returns:
        float: The frequency ratio corresponding to the semitone interval.
    """
    return pow(2, semitones / 12.0)

def frequency_ratio_to_midi_semitones(frequency_ratio) -> float:
    """
    Map a given frequency ratio to the corresponding interval, in semitones.

    Args:
        frequency_ratio: The frequency ratio.

    Returns:
        float: The ratio, in semitones
    """
    return math.log2(frequency_ratio) * 12

def scale_lin_exp(value: float,
                  from_min: float,
                  from_max: float,
                  to_min: float,
                  to_max: float) -> float:
    """
    Map a value on a linear scale to an exponential scale.

    Args:
        value: The value
        from_min: The lower bound of the input range
        from_max: The upper bound of the input range
        to_min: The lower bound of the output range (must be >0)
        to_max: The upper bound of the output range

    Returns:
        The scaled value.
    """
    if value < from_min:
        return to_min
    if value > from_max:
        return to_max
    return ((to_max / to_min) ** ((value - from_min) / (from_max - from_min))) * to_min

def scale_lin_lin(value: float,
                  from_min: float,
                  from_max: float,
                  to_min: float,
                  to_max: float) -> float:
    """
    Map a value on a linear scale to a linear scale.

    Args:
        value: The value
        from_min: The lower bound of the input range
        from_max: The upper bound of the input range
        to_min: The lower bound of the output range
        to_max: The upper bound of the output range

    Returns:
        The scaled value.
    """
    norm = (value - from_min) / (from_max - from_min)
    return norm * (to_max - to_min) + to_min

def scale_exp_lin(value: float,
                  from_min: float,
                  from_max: float,
                  to_min: float,
                  to_max: float) -> float:
    """
    Map a value on an exponential scale to a linear scale.

    Args:
        value: The value
        from_min: The lower bound of the input range
        from_max: The upper bound of the input range
        to_min: The lower bound of the output range
        to_max: The upper bound of the output range

    Returns:
        The scaled value.
    """
    norm = (math.log(value / from_min)) / (math.log(from_max / from_min))
    return norm * (to_max - to_min) + to_min

def bipolar_diverge(maximum: int) -> list[int]:
    """
    Returns [0, 1, -1, ...., maximum, -maximum ]
    """
    sequence = list(sum(list(zip(list(range(maximum + 1)), list(range(0, -maximum - 1, -1)))), ()))
    sequence.pop(0)
    return sequence

def filter_tone_row(source: list[int], target: list[int], bend_limit: int = 7) -> list[int]:
    """
    Filters the notes in <source> by the permitted notes in <target>.
    returns a tuple (<bool> acceptable, <int> pitch_bend)
    """
    bends = bipolar_diverge(bend_limit)
    for bend in bends:
        if all(((note + bend) % 12) in target for note in source):
            return (True, bend)
    return (False, 0)

def random_seed(seed: int) -> None:
    """
    Set the random number generator seed.

    Args:
        seed: An integer. Using the same seed will result in the same RNG output.
    """
    random.seed(seed)

def make_clock_multiplier(output_clock_rate: int, input_clock_rate: int) -> Generator:
    """
    Create a clock multiplier/divider to translate between different PPQN rates.

    Args:
        output_clock_rate: The desired output clock rate
        input_clock_rate: The input clock rate

    Returns:
        int: The multiplier
    """
    multiple = 1.0
    if output_clock_rate and input_clock_rate:
        multiple = output_clock_rate / input_clock_rate
    if (multiple > 1 and int(multiple) != multiple) or (multiple < 1 and 1 / multiple != int(1 / multiple)):
        raise ClockException("Cannot sync output device (clock rates must integer multiples of each other)")

    pos = 1
    while True:
        rv = 0
        pos += multiple
        while round(pos, 8) > 1:
            pos -= 1
            rv += 1
        yield rv
