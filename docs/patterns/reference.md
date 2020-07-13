# Patterns

## About patterns

Patterns are the fundamental building blocks that are used to create melodies, rhythms and control sequences.
In Python terms, a pattern is an [iterator](https://wiki.python.org/moin/Iterator), which is to say it does two things:

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

By assigning patterns to properties of [events](events/index.md), you can specify sequences of values to control any aspect of the control output: pitch, velocity, duration, etc.    

Patterns can be finite, such as the example above, or infinite, in which case they will keep generating new values forever.

Patterns can also typically generate different Python types. Some Pattern classes will seek to do the right thing based on the type of their input.

 - `iso.PSequence([ "apple", "pear" ])` generates an alternating pair of strings
 - `iso.PWhite(0, 10)` generates a stream of ints between `[0 .. 9]`
 - `iso.PWhite(0.0, 10.0)` generates a stream of floats between `[0.0 .. 10.0]`

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

## Duplicating patterns

It's often useful to be able to apply the same pattern to multiple outputs.  

## Pattern resolution

The class method `Pattern.value` can be used to resolve a pattern. 

## Resetting a pattern

## Stochastic patterns

## Static patterns

## Globals

