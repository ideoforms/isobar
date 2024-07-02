# SuperCollider

isobar can be used to create and interact with [SuperCollider](https://supercollider.github.io/) synths. The [python-supercollider](https://github.com/ideoforms/python-supercollider/) module is required, which can be installed with:

```
pip install supercollider
```

## Example

```python
import supercollider as sc
import isobar as iso
import logging

server = sc.Server()
buf = sc.Buffer.read(server, "apollo.wav")

output = iso.SuperColliderOutputDevice()
timeline = iso.Timeline(120, output)

timeline.schedule({
    "synth": "playbuf",
    "params": {
        "buffer": buf,
        "rate": iso.PSequence([ 1, 2, 0.5 ])
    },
    "duration": 1
})

timeline.run()
```