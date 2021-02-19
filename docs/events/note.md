# Notes and MIDI events

## Notes and names

A common approach to composition in isobar is building up patterns of notes, which correspond to the standard MIDI note range (0..127, with 60 = middle C) and velocity range (0..127).

```python
timeline.schedule({
    "note": iso.PSequence([ 60, 64, 67, 72 ], 1),
    "amplitude": 64
})
```

To get a note from its string representation, use the `note_name_to_midi_note` utility function:

```python
>>> print(iso.note_name_to_midi_note("G#2"))
32
``` 

Note events support the following properties:

| property | type | description |
|-|-|-|
| note | int | MIDI note value |
| amplitude | int | MIDI note velocity |
| duration | float | Interval between notes (seconds) |
| gate | float | Proportion of note to sustain (where 1.0 = legato) |
| key | Key | Key for degree lookup |
| scale | Scale | Scale for degree lookup |
| degree | int | Degree within key/scale (cannot be used if note is specified) |
| transpose | int | MIDI note transpose |
| octave | int | MIDI note octave transpose |
| active | int | If false, skips the note |

## Duration and gate

The `duration` specifies the interval between one note and the next. The `gate` key specifies what proportion of this interval the note will be sustained for (and defaults to 1.0, for seamless legato).

For instance:

```python
#--------------------------------------------------------------------------------
# Play a note every beat, sustained for half a beat
#--------------------------------------------------------------------------------
timeline.schedule({
    "note": 60
    "duration": 1,
    "gate": 0.5
})
```

The `gate` can also be greater than 1, to hold a note down as the next note begins:

```python
#--------------------------------------------------------------------------------
# Play a sustained, overlapping chord, with each note lasting for 4 beats
#--------------------------------------------------------------------------------
timeline.schedule({
    "note": iso.PSequence([ 60, 64, 67, 72 ], 1),
    "duration": 0.5,
    "gate": 8
})
```

## Keys and Scales

isobar has builtin objects representing musical keys and scales.

- [Scale](https://github.com/ideoforms/isobar/blob/master/isobar/scale.py) encapsulates an ordered set of semitones. Named scales are [defined](https://github.com/ideoforms/isobar/blob/master/isobar/scale.py) corresponding to commonly-used scales (`major`, `minor`, `chromatic`, `aeolian`, etc).
- [Key](https://github.com/ideoforms/isobar/blob/master/isobar/key.py) encapsulates a Scale with a specified tonic.

!!! warning
    isobar currently only supports equal temperament tuning. 
    
    
Keys and scales can be used in events by using the `degree` key to look up a specific degree within the key/scale. `transpose` and `octave` can be used to transpose by semitones and octaves respectively.  

```python
#--------------------------------------------------------------------------------
# Play an F minor arpeggio
#--------------------------------------------------------------------------------
timeline.schedule({
    "degree": iso.PSequence([ 0, 2, 4, 7 ], 1),
    "key": iso.Key("F", "minor"),
    "octave": 4
})
```

## Chords

Chords can be specified by passing tuples of notes to the `note` or `degree` property.

```python
#--------------------------------------------------------------------------------
# Play a series of 3-note chords.
#--------------------------------------------------------------------------------
timeline.schedule({
    "degree": iso.PSequence([
        (0, 1, 4),
        (1, 4, 6),
        (3, 4, 7),
        (-1, 0, 4),
    ]),
    "octave": 4,
    "duration": 2
})
```

You can also specify different amplitudes or gates for notes of a chord by passing tuples of the same length:

```python
timeline.schedule({
    "note": iso.PSequence([
        (60, 62, 67),
    ]),
    "gate": iso.PSequence([
        (0.25, 0.5, 1)
    ]),
    "amplitude": iso.PSequence([
        (96, 64, 32),
        (64, 96, 32),
        (64, 32, 96),
    ]),
    "duration": 0.25
})
```

## Rests

Use `None` to specify a rest:

```python
timeline.schedule({
    "note": iso.PSequence([ 60, 60, None, 60, None, 60, 60, None ]),
    "duration": 0.25
})
```

Many Pattern classes can operate explicitly on rests, or introduce rests.

For example:

- `PCollapse` takes an input and steps past any rests to remove gaps
- `PSkipIf` replaces notes with rests given a conditional
- `PSkip` replaces notes with rests randomly given a probability
- `PPad` pads a sequence with rests until it reaches a specified length
