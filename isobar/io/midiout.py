import pypm
import random
import time


# MIDIOUT_DEFAULT = "MIDISPORT 2x2 Port A"
MIDIOUT_DEFAULT = "IAC Driver A"
# MIDIOUT_DEFAULT = "EDIROL FA-66 (3118) Plug 1"

class MidiOut:
    def __init__(self):
        pypm.Initialize()
        self.midi = None
        self.debug = False

        for n in range(pypm.CountDevices()):
            info = pypm.GetDeviceInfo(n)
            name = info[1]
            isOutput = info[3]
            if name == MIDIOUT_DEFAULT and isOutput == 1:
                self.midi = pypm.Output(n, 1)
                print "Found MIDI output (%s)" % name

    def noteOn(self, note = 60, velocity = 64, channel = 0):
        if self.debug:
            print "channel %d, noteOn: %d" % (channel, note)
        self.midi.WriteShort(0x90 + channel, int(note), int(velocity))
        # time.sleep(0.001)

    def noteOff(self, note = 60, channel = 0):
        if self.debug:
            print "channel %d, noteOff: %d" % (channel, note)
        self.midi.WriteShort(0x80 + channel, int(note), 0)
        # time.sleep(0.001)

    def allNotesOff(self, channel = 0):
        if self.debug:
            print "channel %d, allNotesOff"
        for n in range(128):
            self.noteOff(n, channel)

    def control(self, control = 0, value = 0, channel = 0):
        if self.debug:
            print "channel %d, control %d: %d" % (channel, control, value)
        self.midi.WriteShort(0xB0 + channel, int(control), int(value))

    def __destroy__(self):
        pypm.Terminate()
