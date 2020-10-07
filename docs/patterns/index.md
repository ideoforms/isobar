# Patterns

## About patterns

Patterns are the fundamental building blocks that are used to create melodies, rhythms and control sequences.
A pattern is a Python [iterator](https://wiki.python.org/moin/Iterator), which is to say it does two things:

 - generates and returns the next item in the sequence
 - when no more items are available in the sequence, raises a `StopIteration` exception

```python
>>> seq = iso.PSequence([ 1, 2, 3 ], 1)
>>> next(seq)
1
>>> next(seq)
2
>>> next(seq)
3
>>> next(seq)
Traceback (most recent call last):
  File "sequence.py", line 46, in __next__
    raise StopIteration
StopIteration
```

Note that this means that patterns can't seek backwards in time. Their only concern is generating the next event.

By assigning patterns to properties of [events](/events/), you can specify sequences of values to control any aspect of the control output: pitch, velocity, duration, etc.    

Patterns can be finite, such as the example above, or infinite, in which case they will keep generating new values forever.

Patterns can also typically generate different Python types. Some Pattern classes will seek to do the right thing based on whether they are passed them int or float arguments.

 - `PSequence([ "apple", "pear" ])` generates an alternating pair of strings
 - `PWhite(0, 10)` generates a stream of ints between `[0 .. 9]`
 - `PWhite(0.0, 10.0)` generates a stream of floats between `[0.0 .. 10.0]`
 - `PChoice([ Key("C", "major"), Key("A", "minor") ])` picks one of the specified [Key](../events/note.md)s at random
 
## Pattern resolution

When a pattern returns a pattern, the embedded pattern will also be resolved recursively. For example:

 - `PChoice([ PSequence([0, 2, 3]), PSequence([7, 5, 2 ]) ])` each step, picks one of the embedded patterns and returns its next value

## Pattern operators

Patterns can be combined and modified using standard Python arithmetic operators, with other patterns or with scalar values.

```python
>>> added = iso.PSequence([ 1, 2, 3 ]) + 10
>>> next(added)
11
>>> next(added)
12

>>> multiplied = iso.PSequence([ 1, 2, 3 ]) * 4
>>> next(added)
4
>>> next(added)
8

>>> inverted = 12 - iso.PSequence([ 1, 2, 3 ])
>>> next(inverted)
11
>>> next(inverted)
10

combined = iso.PSequence([ 1, 2, 3 ]) + iso.PSequence([ 12, 0, 12 ])
>>> next(combined)
13
>>> next(combined)
2
```

The operators are designed to do what you would expect:

 - binary operators (`+`, `-`, `*`, `/`, `%`, `<<`, `>>`) perform the operation on each item of the input patterns. Note that, for binary operators, if either of the inputs returns `None`, the output value becomes `None`.
 - equality operators (`<`, `>`, `==`, `!=`) can be used to do element-wise comparison on the input sequences, returning a pattern whose values are either `True`, `False` or `None`.
 - `abs()` can be used to generate the absolute values of a sequence
 - For finite sequences, `len()` will return the length of the sequence
 - A `float` pattern can be turned into an `int` pattern with `isobar.PInt(pattern)` 

## Duplicating patterns

It's often useful to be able to apply the same pattern to multiple properties or events.

However, this can result in unwanted behaviours as shown below:

```python
>>> a = iso.PSequence([ 1, 2, 3 ])
>>> d = iso.PDict({ "p1" : a, "p2" : a })
>>> next(d)
{'p1': 1, 'p2': 2}
```

Because the "p1" and "p2" properties both refer to the same instance, the `next()` method is called twice on `a`.

Instead, use `a.copy()` to create a duplicate with identical state:

```python
>>> a = iso.PSequence([ 1, 2, 3 ])
>>> d = iso.PDict({ "p1" : a.copy(), "p2" : a.copy() })
>>> next(d)
{'p1': 1, 'p2': 1}
```

## Resetting a pattern

To rewind a pattern to its initial state, call `pattern.reset()`. This restores all state variables to their original values.

## Stochastic patterns

Stochastic patterns each have their own independent random number generator state. This allows them to be seeded with a known value to create repeatable pseudo-random number sequences.

```python
>>> a = iso.PWhite(0, 10)
>>> a.seed(123)
>>> a.nextn(16)
[0, 0, 4, 1, 9, 0, 5, 3, 8, 1, 3, 3, 2, 0, 4, 0]
>>> a.seed(123)
>>> a.nextn(16)
[0, 0, 4, 1, 9, 0, 5, 3, 8, 1, 3, 3, 2, 0, 4, 0]
```

## Static patterns

The state of a regular pattern steps forward each time the `next()` method is called.

The state of a static pattern, conversely, is not modified by a call to `next()`. This means that `next()` may be called multiple times and return the same value each time.

Static pattern classes include:

 - `PStaticPattern`: When called as `PStaticPattern(pattern, duration)`, wraps a regular pattern and returns a new static pattern. Each new value of the inner pattern is returned for a specified duration in beats (see example below). The `duration` parameter may also be a pattern. 
 - `PCurrentTime`: Returns the current Timeline's time, in beats.
 - `PGlobals`: See [Globals](#globals).

Static patterns can be used to impose temporal structure on a piece. For example, to modulate over a set of keys:

```python
#--------------------------------------------------------------------------------
# Create a pattern which is an alternating pair of Keys.
#--------------------------------------------------------------------------------
key_sequence = iso.PSequence([
    iso.Key("C", "minor"),
    iso.Key("G", "major"),
])
#--------------------------------------------------------------------------------
# Create a static pattern embeds the key_sequence pattern.
# Each value will be held for 4 beats before progressing to the next value.
#--------------------------------------------------------------------------------
key_static = iso.PStaticPattern(key_sequence, 4)

#--------------------------------------------------------------------------------
# Schedule a pattern which plays notes following the given keys.
# A "C" note will be played for 4 notes, followed by a "G" for 4 notes,
# repeatedly. The same static pattern can be accessed by multiple different
# tracks or timelines to orchestrate changes across the composition. 
#--------------------------------------------------------------------------------
timeline = iso.Timeline(120)
timeline.schedule({
    "degree": 0,
    "octave": 5
    "key": key_static,
})
```

## Globals

The `Globals` class, and accompanying `PGlobals` pattern, can be used to share common variables across an isobar composition.

For example:

```python
#--------------------------------------------------------------------------------
# Create a stream of events that will skip each note based on a "density"
# global, with a key set by the "key" global.
#--------------------------------------------------------------------------------
iso.Globals.set("density", 0.5)
iso.Globals.set("key", iso.Key("A", "minor"))

p = iso.PDict({
    "degree": iso.PSkip(0, iso.PGlobals("density")),
    "key": iso.PGlobals("key")
})
```
