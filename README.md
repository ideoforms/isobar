## Introduction

isobar is a Python library for expressing and constructing musical patterns,
designed for use in algorithmic composition. It allows for concise construction,
manipulation and transposition of sequences, supporting scalar operations on
lazy patterns.

Most of the major parts of isobar are subclasses of Pattern, which implement's
Python's iterator protocol. The next() method is called to generate the
subsequent item in a pattern, with the StopIterator exception raised when a
pattern is exhausted. Builtins such as list() and sorted() can thus be used to
process the output of a Pattern.

## Usage

```python
from isobar import *
from isobar.io.midi import *

# create a repeating sequence with scalar transposition:
# [ 48, 50, 57, 60 ] ...
seqA = PSeq([ 0, 2, 7, 3 ]) + 48

# apply pattern-wise transposition
# [ 48, 62, 57, 72 ] ...
seqA = seqA + PSeq([ 0, 12 ])

# create a geometric chromatic series, repeated back and forth
seqB = PSeries(0, 1, 12) + 72
seqB = PPingPong(seqB)

# create an velocity series, with emphasis every 4th note,
# plus a random walk to create gradual dynamic changes
amp = PSeq([ 60, 40, 30, 40 ]) + PBrown(0, 1, -20, 20)

# a Timeline schedules events at a given BPM, sent over a specified output
timeline = Timeline(120)

midiout = MidiOut()
timeline.output(midiout)

# assign each of our Patterns to particular properties
timeline.sched({ 'note': seqA, 'dur': 1 })
timeline.sched({ 'note': seqB, 'dur': 0.25, 'amp': amp })

timeline.run()
```

## Examples

More examples are available in the 'examples' directory with this
distribution:

* [ex-basics.py](examples/ex-basics.py)
* [ex-lsystem-grapher.py](examples/ex-lsystem-grapher.py)

## Classes

Current class list:

    Chord
    Key
    Note
    Scale
    Timeline
    Clock

Pattern classes:


    CORE (core.py)
    Pattern          - Abstract superclass of all pattern generators.
    PConst           - Pattern returning a fixed value
    PRef             - Pattern containing a reference to another pattern
    PDict            - Dict of patterns
    PIndex           - Request a specified index from an array.
    PKey             - Request a specified key from a dictionary.
    PConcat          - Concatenate the output of multiple sequences.
    PAdd             - Add elements of two patterns (shorthand: patternA + patternB)
    PSub             - Subtract elements of two patterns (shorthand: patternA - patternB)
    PMul             - Multiply elements of two patterns (shorthand: patternA * patternB)
    PDiv             - Divide elements of two patterns (shorthand: patternA / patternB)
    PMod             - Modulo elements of two patterns (shorthand: patternA % patternB)
    PPow             - One pattern to the power of another (shorthand: patternA ** patternB)
    PLShift          - Binary left-shift (shorthand: patternA << patternB)
    PRShift          - Binary right-shift (shorthand: patternA << patternB)

    SEQUENCE (sequence.py)
    PSeq             - Sequence of values based on an array
    PSeries          - Arithmetic series, beginning at <start>, increment by <step>
    PRange           - Similar to PSeries, but specify a max/step value.
    PGeom            - Geometric series, beginning at <start>, multiplied by <step>
    PLoop            - Repeats a finite <pattern> for <n> repeats.
    PConcat          - Concatenate the output of multiple finite sequences
    PPingPong        - Ping-pong input pattern back and forth N times.
    PCreep           - Loop <length>-note segment, progressing <creep> notes after <count> repeats.
    PStutter         - Play each note of <pattern> <count> times.
    PWrap            - Wrap input note values within <min>, <max>.
    PPermut          - Generate every permutation of <count> input items.
    PDegree          - Map scale index <degree> to MIDI notes in <scale>.
    PSubsequence     - Returns a finite subsequence of an input pattern.
    PImpulse         - Outputs a 1 every <period> events, otherwise 0.
    PReset           - Resets <pattern> each time it receives a zero-crossing from
    PCounter         - Increments a counter by 1 for each zero-crossing in <trigger>.
    PArp             - Arpeggiator.
    PDecisionPoint   - Each time its pattern is exhausted, requests a new pattern by calling <fn>.

    CHANCE (chance.py)
    PWhite           - White noise between <min> and <max>.
    PBrown           - Brownian noise, beginning at <value>, step +/-<step>.
    PWalk            - Random walk around list.
    PChoice          - Random selection from <values>
    PWChoice         - Random selection from <values>, weighted by <weights>.
    PShuffle         - Shuffled list.
    PShuffleEvery    - Every <n> steps, take <n> values from <pattern> and reorder.
    PSkip            - Skip events with some probability, 1 - <play>.
    PFlipFlop        - flip a binary bit with some probability.
    PSwitchOne       - Capture <length> input values; repeat, switching two adjacent values <n> times.

    OPERATOR (operator.py)
    PChanged         - Outputs a 1 if the value of a pattern has changed.
    PDiff            - Outputs the difference between the current and previous values of an input pattern
    PAbs             - Absolute value of <input>
    PNorm            - Normalise <input> to [0..1].
    PCollapse        - Skip over any rests in <input>
    PNoRepeats       - Skip over repeated values in <input>
    PMap             - Apply an arbitrary function to an input pattern.
    PMapEnumerated   - Apply arbitrary function to input, passing a counter.
    PLinLin          - Map <input> from linear range [a,b] to linear range [c,d].
    PLinExp          - Map <input> from linear range [a,b] to exponential range [c,d].
    PRound           - Round <input> to N decimal places.
    PIndexOf         - Find index of items from <pattern> in <list>
    PPad             - Pad <pattern> with rests until it reaches length <length>.
    PPadToMultiple   - Pad <pattern> with rests until its length is divisible by <multiple>.

    STATIC (static.py)
    PStaticTimeline  - Returns the position (in beats) of the current timeline.
    PStaticGlobal    - Static global value identified by a string, with OSC listener

    FADE (fade.py)
    PFadeNotewise    - Fade a pattern in/out by introducing notes at a gradual rate.
    PFadeNotewise    - Fade a pattern in/out by gradually introducing random notes.

    MARKOV (markov.py)
    PMarkov          - Markov chain

    LSYSTEM (lsystem.py)
    PLSys            - integer sequence derived from Lindenmayer systems

    WARP (warp.py)
    PWInterpolate    - Requests a new target warp value from <pattern> every <length>
    PWRallantando    - Exponential deceleration to <amp> times the current tempo over <length> beats.


## BACKGROUND

isobar was first designed for the generative sound installation Variable 4:

    http://www.variable4.org.uk/

Many of the concepts behind Pattern and its subclasses are inspired by the
excellent pattern library of the SuperCollider synthesis language:

    http://supercollider.sf.net


