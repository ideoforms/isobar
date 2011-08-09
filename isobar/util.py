import random
import math

note_names = [ "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" ]

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
    try:
        return note_names.index(name)
    except:
        return None

def miditopitch(note):
    degree = int(note) % len(note_names)
    return note_names[degree]

def miditoname(note):
    degree = int(note) % len(note_names)
    octave = int(note / len(note_names)) - 1
    str = "%s%d" % (note_names[degree], octave)
    frac = math.modf(note)[0]
    if frac > 0:
        str = (str + " + %2f" % frac)

    return str
    
