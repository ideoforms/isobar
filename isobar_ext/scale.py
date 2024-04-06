import json
import random
from pathlib import Path

from .exceptions import UnknownScaleName
from .util import normalize


class Scale(object):
    dict = {}
    # _scales = []

    def __init__(
        self, semitones=None, name="unnamed scale", octave_size=12, semitones_down=None
    ):
        self.scale_down = False

        if semitones is None:
            semitones = [0, 2, 4, 5, 7, 9, 11]
        self.semitones = semitones
        self.semitones_down = semitones_down
        """ For polymorphism with WeightedScale -- assume all notes equally weighted. """
        self.weights = [1.0 / len(self.semitones) for _ in range(len(self.semitones))]
        self.name = name
        self.octave_size = octave_size
        if name not in Scale.dict:
            Scale.dict[name] = self

    @classmethod
    def create_scale(cls, semitones, name, octave_size=12, semitones_down=None):
        scale_instance = cls(semitones=semitones, name=name, octave_size=octave_size, semitones_down=semitones_down)
        # cls._scales.append(scale_instance)
        setattr(cls, name, scale_instance)
        cls.dict[name] = scale_instance
        return scale_instance

    def __str__(self):
        return "%s %s" % (self.name, self.semitones)

    def __getitem__(self, key):
        return self.get(key)

    def __eq__(self, other):
        return (
            self.semitones == other.semitones and self.octave_size == other.octave_size
        )

    def __contains__(self, semitone):
        return (semitone % self.scale.octave_size) in self.semitones

    def __hash__(self):
        return hash(
            tuple(
                (
                    tuple(self.semitones),
                    tuple(self.weights),
                    self.name,
                    self.octave_size,
                )
            )
        )

    def get(self, *args, **kwargs):
        """Retrieve the n'th degree of this scale."""
        parameters = {"n": None, "scale_down": False}
        if hasattr(self, "scale_down"):
            parameters["scale_down"] = self.scale_down
        for idx, arg in enumerate(args):
            parameters[list(parameters.keys())[idx]] = arg
        if kwargs is not None:
            parameters |= kwargs
        n = parameters["n"]
        scale_down = parameters["scale_down"]
        if n is None:
            return None
        semitones_down = None
        if hasattr(self, "semitones_down"):
            semitones_down = self.semitones_down

        semitones = (
            semitones_down
            if scale_down and semitones_down is not None
            else self.semitones
        )
        octave = n // len(semitones)
        degree = n % len(semitones)
        semitone = semitones[degree]
        return (self.octave_size * octave) + semitone

    def copy(self):
        other = Scale(self.semitones, self.name)
        return other

    def change(self):
        """Exchange two random elements of this scale."""
        i = random.randint(0, len(self.semitones) - 1)
        j = random.randint(0, len(self.semitones) - 1)
        if i != j:
            tmp = self.semitones[i]
            self.semitones[i] = self.semitones[j]
            self.semitones[j] = tmp
        return self

    def shuffle(self):
        random.shuffle(self.semitones)
        return self

    def indexOf(self, *args, **kwargs):
        """Return the index of the given note within this scale."""
        parameters = {"note": None, "scale_down": False}
        if hasattr(self, "scale_down"):
            parameters["scale_down"] = self.scale_down
        for idx, arg in enumerate(args):
            parameters[list(parameters.keys())[idx]] = arg
        if kwargs is not None:
            parameters |= kwargs
        scale_down = parameters.get("scale_down")
        if scale_down and hasattr(self, "semitones_down") and self.semitones_down:
            semitones = self.semitones_down
        else:
            semitones = self.semitones

        note = parameters.get("note")
        # octave = int(note / self.octave_size)
        octave = note // self.octave_size
        index = octave * len(semitones)
        # note -= octave * self.octave_size
        note %= self.octave_size
        degree = 0

        while note > semitones[degree] and degree < len(semitones) - 1:
            degree += 1

        index += degree
        return index

    @staticmethod
    def fromnotes(notes, name="unnamed scale", octave_size=12):
        notes = [note % octave_size for note in notes]
        notes = list(dict((k, k) for k in notes).keys())
        notes = sorted(notes)
        scale = Scale(notes, name=name, octave_size=octave_size)
        return scale

    @staticmethod
    def all():
        return list(Scale.dict.values())

    @staticmethod
    def byname(name):
        if name in Scale.dict:
            return Scale.dict[name]
        else:
            raise UnknownScaleName()

    @staticmethod
    def random():
        key = random.choice(list(Scale.dict.keys()))
        return Scale.dict[key]

# ------------------------------------------------------------------------
current_directory = Path(__file__).resolve().parent
config_file = current_directory / "scales.json"

with open(config_file, "r") as file:
    scales = json.load(file)

    for scale in scales["scales"]:
        for name in scale["name"]:
            Scale.create_scale(
                semitones=scale["semitones"],
                name=name,
                octave_size=scale.get("octave_size", 12),
            )

# ------------------------------------------------------------------------
# Use major scale as a global default. This can be overriden by user.
# ------------------------------------------------------------------------
Scale.chromatic = Scale([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "chromatic")
Scale.major = Scale([0, 2, 4, 5, 7, 9, 11], "major")
Scale.default = Scale.major


class WeightedScale(Scale):
    def __init__(
        self,
        semitones=[0, 2, 4, 5, 7, 9, 11],
        weights=[1 / 7.0] * 7,
        name="major",
        octave_size=12,
    ):
        Scale.__init__(self, semitones, name=name, octave_size=octave_size)
        self.weights = weights
        if name not in Scale.dict:
            Scale.dict[name] = self

    def __str__(self):
        return "%s %s weights = %s" % (self.name, self.semitones, self.weights)

    @staticmethod
    def fromnotes(notes, name="unnamed scale", octave_size=12):
        note_sequence = [note % octave_size for note in notes]
        notes_dict = {}
        for note in note_sequence:
            if note not in notes_dict:
                notes_dict[note] = 0
            notes_dict[note] += 1.0 / len(note_sequence)

        notes_unique = list(dict((k, k) for k in note_sequence).keys())
        notes_unique = sorted(notes_unique)
        weights = []
        for note in notes_unique:
            weights.append(notes_dict[note])

        scale = WeightedScale(notes_unique, weights, name=name, octave_size=octave_size)
        return scale

    @staticmethod
    def fromorder(notes, name="unnamed scale", octave_size=12):
        notes = [note % octave_size for note in notes]
        weights = [len(notes) - n for n in range(len(notes))]
        weights = normalize(weights)

        scale = WeightedScale(notes, weights, name=name, octave_size=octave_size)
        return scale
