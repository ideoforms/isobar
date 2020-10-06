# isobar

isobar is a Python library for creating and manipulating musical patterns, designed for use in algorithmic composition, generative music and sonification. It makes it quick and easy to express complex musical ideas, and can send and receive events from various different sources: MIDI, OSC, SocketIO, and .mid files.

### What isobar does

The core objective of isobar is to provide a framework for sequencing and triggering events, which may be MIDI messages, OSC triggers, triggers for third-party DSP engines such as SuperCollider, or even Python functions. ([What types of event are supported?](events/index.md#event-types)) 

It can be used to trigger events in real time, or to generate patterns that can be serialised as MIDI files and loaded into a DAW.

It can sync to external clocks, or act as a clock source to external devices.  

It can also load patterns serialised in MIDI files for processing.

### What isobar doesn't do

isobar does not generate any audio on its own. It must be configured to send events to an output device which is responsible for sound synthesis.

## Basic concepts

There are a few key components in isobar.

- The **[Timeline](timelines/index.md)** handles timing and scheduling, triggering events at the correct moment. It is made up of multiple Tracks, which normally . It can maintain its own clock with millisecond accuracy, or sync to an external clock.  
- **[Events](events/index.md)** correspond to triggers that are typically sent to output devices or received from input devices. These may be MIDI notes, control changes, OSC triggers, and other general types. An event is typically described by a dict with a number of properties. For example: `{ "note" : 60, "amplitude": 127 }`
- **[Patterns](patterns/index.md)**: Each of the properties of an event can be specified by a Pattern, which generates a sequence of return values. Simple pattern types generate fixed sequences, random values, or values based on statistical models. Patterns can be passed other patterns as parameters, so they can operate on each other -- for example, causing an input pattern to loop N times, or skipping the input values with some probability.  
- **[Devices](devices/index.md)**: Events are sent to output devices, over interfaces such as MIDI or OSC. Events can also be received and processed. 

### Flow diagram

![Flow Diagram](diagrams/Isobar Flow Diagram.png)

## Documentation

- [Getting started](getting-started.md)
- [Code examples](https://github.com/ideoforms/isobar/tree/master/examples)
- [Pattern library reference](patterns/library.md)
