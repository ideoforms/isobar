# Changelog

## [v0.2.1](https://github.com/ideoforms/isobar/tree/v0.2.1) (2025-08-08)

- Added support for treating generator expressions in place of patterns
- Initial support for MPE
- Expanded `MidiInputDevice` with support for capturing aftertouch and polytouch events
- Added `globals` event type, to schedule changes to a global variable
- Added new scalar patterns: `PFloor`, `PCeil`, `PRoundToMultiple`
- Added `PKeyScale` pattern, to extract a Scale from a Key
- Added `Globals.enable_interprocess_sync()`, to synchronise global variables between multiple notebooks or Python processes on the same computer
- Fixed bug in quantization with Ableton Link Clock
- Refactor of Event handling, modularising handler logic for different event types
- Utils: Added `clip()`, `frequency_to_midi_note()`

## [v0.2.0](https://github.com/ideoforms/isobar/tree/v0.2.0) (2024-11-10)

- Globals: Added support for synchronising Globals state between isobar processes via `enable_interprocess_sync()`
- Added syntactical sugar around `PDict` `getattr`/`setattr`, so that a track's `params` property can be modified by (e.g.) `track.params.cutoff = 200` (requires `rpyc`)
- Added `PKeyScale` class, which returns the `Scale` corresponding to an input `Key`
- Added new `Automation` class for continuous parameter control
- Added new `Instrument` class for concise scheduling of multi-modal events
- `Timeline`: Added support for specifying a `clock_source` by name: either `midi`, `internal` or `link`
- `Timeline`: Added `start` constructor argument to immediately start the timeline

## [v0.1.4](https://github.com/ideoforms/isobar/tree/v0.1.4) (2024-08-11)

- Added support for LFOs for continuous parameter modulation, and `PLFO` pattern class
- Added `Track.nudge()` to nudge a track back/forward in time
- Added `FluidSynthOutputDevice` to interact with FluidSynth sound fonts
- Added initial support for monome devices
- Added `scale_exp_lin`

## [v0.1.3](https://github.com/ideoforms/isobar/tree/v0.1.3) (2024-07-01)

- Added support for Ableton Link clock sync (thanks to [Raphaël Forment](https://github.com/Bubobubobubobubo) for providing LinkPython-extern)
- Added shorthand syntax for more concise pattern expressions
- Added new pattern classes:
  - `PMIDIControl`: provides access to MIDI control change values
  - `PSaw`: sawtooth waveform
  - `PMidiSemitonesToFrequencyRatio`: map an interval in semitones to a frequency ratio
- Added `Pattern.poll()` for debugging pattern issues
- Auto-generated pattern library documentation (thanks to [Giacomo Loparco](https://github.com/loparcog))
- Improvements to type hinting, inline documentation and examples (thanks to [Giacomo Loparco](https://github.com/loparcog) and [Greg White](https://github.com/gregwht))
- Added event callbacks to Timeline and Track, to trigger a user-specified function when an event occurs
- Fixed bugs in `Key` and `Scale` handlers (thanks to [Piotr Sakowski](https://github.com/piotereks))

## [v0.1.2](https://github.com/ideoforms/isobar/tree/v0.1.2) (2023-05-28)

- Added `SignalFlowOutputDevice` and `CVOutputDevice`
- Added `NetworkClockSender` / `NetworkClockReceiver`, and `NetworkGlobalsSender` / `NetworkGlobalsReceiver`
- Added new stochastic patterns: `PCoin`, `PRandomImpulseSequence`, `PRandomExponential`, `PMetropolis`

## [v0.1.1](https://github.com/ideoforms/isobar/tree/v0.1.1) (2020-10-07)

Major overhaul and refactor.

- Unified and improved class names
- Added unit test suite and CI testing
- Added mkdocs documentation
- Added support for Control events with interpolation
- Added custom Exception classes
- Added examples covering MIDI I/O, MIDI files, live coding in iPython
- Added new Pattern classes: `PSample`, `PEqual`, `PNotEqual`, `PGreaterThan`, `PGreaterThanOrEqual`, `PLessThan`, `PLessThanOrEqual`, `PInterpolate`, `PReverse`, `PExplorer`, `PSequenceAction`, `PNearestNoteInKey`, `PFilterByKey`, `PMidiNoteToFrequency`

## [v0.0.1](https://github.com/ideoforms/isobar/tree/v0.0.1) (2019-10-03)

Initial PyPi release.
