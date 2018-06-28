from isobar.pattern.core import *

class PFilterByKey(Pattern):
    def __init__(self, input, key):
        self.input = input
        self.key = key

    def __next__(self):
        note = next(self.input)
        key = Pattern.value(self.key)
        if note in key:
            return note
        else:
            return None

class PNearest(Pattern):
    def __init__(self, input, key):
        self.input = input
        self.key = key

    def __next__(self):
        note = next(self.input)
        key = Pattern.value(self.key)
        return key.nearest_note(note)
