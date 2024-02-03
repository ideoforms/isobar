from .scale import Scale
from .note import Note
from .util import midi_note_to_note_name, note_name_to_midi_note

import random


class Key:
    """Represents a harmonic structure, containing a tonic and scale."""

    def __init__(self, tonic=0, scale=Scale.major):
        if isinstance(tonic, str):
            # --------------------------------------------------------------------------------
            # Constructor specifies a note name and a scale name (e.g, "C# minor")
            # TODO unit test for this
            # --------------------------------------------------------------------------------
            if " " in tonic:
                tonic_str, scale_str = tuple(tonic.split(" "))
                tonic = note_name_to_midi_note(tonic_str)
                scale = Scale.byname(scale_str)
            else:
                tonic = note_name_to_midi_note(tonic)
        if isinstance(scale, str):
            scale = Scale.byname(scale)

        self.tonic = tonic
        self.scale = scale

    def __eq__(self, other):
        return self.tonic == other.tonic and self.scale == other.scale

    def __str__(self):
        return "Key: %s %s" % (midi_note_to_note_name(self.tonic)[:], self.scale.name)

    def __repr__(self):
        return 'Key(%s, "%s")' % (self.tonic, self.scale.name)

    def __hash__(self):
        return hash((self.tonic, hash(self.scale)))

    def get(self, *args, **kwargs):
        """Returns the <degree>th semitone within this key."""
        params = {"degree": None, "scale_down": False}
        for idx, arg in enumerate(args):
            params[list(params.keys())[idx]] = arg
        if kwargs is not None:
            params |= kwargs
        degree = params["degree"]
        scale_down = params["scale_down"]
        if degree is None:
            return None

        semitone = self.scale.get(degree, scale_down=scale_down)
        return semitone + self.tonic

    def __getitem__(self, degree):
        return self.get(degree)

    def __contains__(self, *args, **kwargs):
        """Return the index of the given note within this scale."""
        params = {"semitone": None, "scale_down": False}
        if hasattr(self, "scale_down"):
            params["scale_down"] = self.scale_down
        for idx, arg in enumerate(args):
            params[list(params.keys())[idx]] = arg
        if kwargs is not None:
            params |= kwargs

        semitone = params.get("semitone")
        # semitone -= self.tonic
        scale_down = params.get("scale_down")
        if (
            scale_down and
            hasattr(self.scale, "semitones_down") and
            self.scale.semitones_down
        ):
            semitones = self.semitones_down
        else:
            semitones = self.semitones
        # Always return true if None (rest) is queried.
        if semitone is None:
            return True
        return (semitone % self.scale.octave_size) in semitones

    @property
    def semitones(self):
        semitones = [
            (n + self.tonic) % self.scale.octave_size for n in self.scale.semitones
        ]
        semitones.sort()
        return semitones

    @property
    def semitones_down(self):
        semitones_down = [
            (n + self.tonic) % self.scale.octave_size for n in self.scale.semitones_down
        ]
        semitones_down.sort()
        return semitones_down

    def nearest_note(self, *args, **kwargs):
        """Return the index of the given note within this scale."""
        parms = {"note": None, "scale_down": False}
        if hasattr(self, "scale_down"):
            parms["scale_down"] = self.scale_down
        for idx, arg in enumerate(args):
            parms[list(parms.keys())[idx]] = arg
        if kwargs is not None:
            parms |= kwargs

        note = parms.get("note")

        scale_down = parms.get("scale_down")
        if (
            scale_down and
            hasattr(self.scale, "semitones_down") and
            self.scale.semitones_down
        ):
            semitones = self.scale.semitones_down
        else:
            semitones = self.scale.semitones
        if self.__contains__(semitone=note, scale_down=scale_down):
            return note
        else:
            return self._extracted_from_nearest_note(note, semitones)

    def _extracted_from_nearest_note(self, note, semitones):
        note_denominated = note - self.tonic
        octave, pitch = divmod(note_denominated, self.scale.octave_size)
        nearest_semi = None
        nearest_dist = None
        calc_octave = octave
        for semi in semitones:
            """
            0.1 is amendment allowing priority of selecting nearest note from
            below when 2 nearest notes are possible (from below and from above)
            """
            dist = min(
                abs(semi - pitch + 0.1),
                abs(abs(semi - pitch + 0.1) - self.scale.octave_size),
            )
            if nearest_dist is None or dist < nearest_dist:
                nearest_semi = semi
                nearest_dist = round(dist)
                calc_octave = (
                    octave + 1
                    if dist == abs(abs(semi - pitch + 0.1) - self.scale.octave_size)
                    else octave
                )
        octave = calc_octave
        return (octave * self.scale.octave_size) + nearest_semi + self.tonic

    def voiceleading(self, other):
        """Returns the most parsimonious voice leading between this key
        and <other>, as a list of N tuples (semiA, semiB) where N is the
        maximal length of (this, other), and semiA and semiB are members
        of each. May not be bijective."""

        if len(self.semitones) > len(other.semitones):
            semisA = self.semitones
            semisB = other.semitones
        else:
            semisA = other.semitones
            semisB = self.semitones
        semisB = list(reversed(semisB))

        leading = []
        for semiA in semisA:
            distances = []
            for semiB in semisB:
                distance = abs(semiA - semiB)
                if distance > self.scale.octave_size / 2:
                    distance = self.scale.octave_size - distance
                distances.append(distance)
            index = distances.index(min(distances))
            leading.append((semiA, semisB[index]))

        return leading

    def distance(self, other):
        leading = self.voiceleading(other)
        distance = sum([abs(a_b[0] - a_b[1]) for a_b in leading])
        return distance

    def fadeto(self, other, level):
        """level between 0..1"""
        semitones_a = self.semitones
        semitones_b = other.semitones
        semitones_shared = [n for n in semitones_b if n in semitones_a]
        semitones_a_only = [n for n in semitones_a if n not in semitones_b]
        semitones_b_only = [n for n in semitones_b if n not in semitones_a]

        if level < 0.5:
            # scale from 1..0
            level = 1.0 - (level * 2)
            count_from_a = int(round(level * len(semitones_a_only)))
            return semitones_shared + semitones_a_only[0:count_from_a]
        else:
            # scale from 0..1
            level = 2 * (level - 0.5)
            count_from_b = int(round(level * len(semitones_b_only)))
            return semitones_shared + semitones_b_only[0:count_from_b]

    @staticmethod
    def random():
        t = random.randint(0, 11)
        s = Scale.random()
        return Key(t, s)

    @staticmethod
    def all():
        return [Key(note, scale) for note in Note.all() for scale in Scale.all()]


Key.default = Key("C", "major")
