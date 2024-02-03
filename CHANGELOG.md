# Changelog
# isobar-ext exclusive releases
## [0.5.1](https://github.com/piotereks/isobar-ext/tree/v0.5.1) (2024-02-03)

- Added numerous of exotic scales and their definition extracted to `scales.json`
- Added support for scales that are different when melody inclines and different when declines: `minorc melodic`, `japanese yoyo`, `enigmatic`
- Numerous fixes
  - nearest note calculation (in case of tie lower note taken when melody goes up, and higher when melody goes down)
  - for 'Scale', 'Key' - correction for considering tonic in re-calculations 
  - midi to notename fix
  - warning when EVENT_ACTION is used together with EVENT_NOTE or EVENT_DEGREE. EVENT_ACTION absorbs EVENT_NOTE or EVENT_DEGREE.
  - problem with detection rests and proper detection of note_offs
  
# Original isobar releases
## [v0.1.2](https://github.com/ideoforms/isobar/tree/v0.1.1) (2023-05-28)

- Added `SignalFlowOutputDevice` and `CVOutputDevice`
- Added `NetworkClockSender` / `NetworkClockReceiver`, and `NetworkGlobalsSender` / `NetworkGlobalsReceiver`
- Added new stochastic patterns: `PCoin`, `PRandomImpulseSequence`, `PRandomExponential`, `PMetropolis`

## [v0.1.1](https://github.com/ideoforms/isobar/tree/v0.1.0) (2020-10-07)

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
