# Virtual MIDI Devices

To send MIDI events to audio software running on the same computer (for example, to use isobar to trigger events in your DAW), you will generally need to set up a *virtual MIDI driver*. This lets you send MIDI messages between different applications. This can be done natively on MacOS and most Linux distributions, but will require additional software for Windows.

After any of these guides, please refer to the [isobar MIDI documentation](midi.md) to link the newly created virtual MIDI bus to your isobar setup.

## Mac

MacOS has a built-in inter-application driver (or IAC driver) which can be used to make any number of virtual MIDI buses:

1. Launch "Audio Midi Setup" and go to "Window > Show MIDI Studio" in the top menu
2. Double-click the IAC Driver and check the box beside "Device is online"
3. (Optionally) add, adjust, or rename any ports

## Linux

Any linux distribution with [ALSA](https://www.alsa-project.org/wiki/Main_Page) available has access to virtual midi ports. This will be a quick setup guide, but any further details can be found in the document [HOWTO Use MIDI Sequencers With Softsynths](https://tldp.org/HOWTO/MIDI-HOWTO-10.html) or in the [ALSA MIDI documentation](https://alsa.opensrc.org/AlsaMidi).

## Windows

Windows does not have any virtual MIDI bus native to it, but it does have freeware available, most notably, [loopMIDI](http://www.tobias-erichsen.de/software/loopmidi.html). This program comes with it's own guide and instructions, 
