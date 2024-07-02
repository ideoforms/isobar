# FluidSynth

isobar can be used to trigger notes in the free [FluidSynth](https://www.fluidsynth.org/) software synthesizer.

It requires the `pyfluidsynth` package:

```
pip install pyfluidsynth
```

## Example

```python
from isobar import *
from isobar.io.fluidsynth import FluidSynthOutputDevice

output_device = FluidSynthOutputDevice("soundfont.sf2")
timeline = Timeline(120, output_device=output_device)

timeline.schedule({
    "key": Key("C", "minor"),
    "octave": 5,
    "degree": PLoop(PSubsequence(PWhite(0, 12), 0, 8)),
    "duration": 0.25,
})

timeline.run()
```