# Changelog

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
