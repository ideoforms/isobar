#!/usr/bin/env python3

#------------------------------------------------------------------------
# isobar: ex-static-pattern
#
# Bind a chord sequence to a static sequence, which is then referenced
# in other patterns.
#------------------------------------------------------------------------

import isobar as iso

key_sequence = iso.PSequence([
    iso.Key("C", "minor"),
    iso.Key("G", "minor"),
    iso.Key("Bb", "major"),
    iso.Key("F", "major"),
])
key = iso.PStaticPattern(key_sequence, 4)
timeline = iso.Timeline(120)
timeline.schedule({
    "degree": 0,
    "key": key,
    "octave": 3
})
timeline.schedule({
    "degree": iso.PCreep(iso.PWhite(0, 6), 2, 2, 3),
    "key": key,
    "octave": 6,
    "duration": 0.25
})
timeline.run()
