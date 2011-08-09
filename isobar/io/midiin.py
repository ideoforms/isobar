import pypm
import random
import time

from isobar.note import *

MIDIIN_DEFAULT = "MIDISPORT 2x2 Port B"
# MIDIIN_DEFAULT = "EDIROL FA-66 (3118) Plug 1"
# MIDIIN_DEFAULT = "Hua Xing"
# MIDIIN_DEFAULT = "Remote SL Port 1"

class MidiIn:
    def __init__(self, target = MIDIIN_DEFAULT):
        pypm.Initialize()
        self.midi = None

        for n in range(pypm.CountDevices()):
            info = pypm.GetDeviceInfo(n)
            name = info[1]
            print "[%d] %s %s" % (n, name, info)
            isInput = info[2]
            if name == target and isInput == 1:
                self.midi = pypm.Input(n)
                print "found target input: %s" % target

        if self.midi is None:
            raise Exception, "Could not find MIDI source: %s" % target

    def run(self):
        while True:
            if not self.midi.Poll(): continue
            data = self.midi.Read(1)
            data_type = data[0][0][0]
            data_note = data[0][0][1]
            data_vel = data[0][0][2]
            time.sleep(0.001)
            if data_type & 0x90:
                # note on
                print "%d (%d)" % (data_note, data_vel)

    def poll(self):
        if not self.midi.Poll(): return
        data = self.midi.Read(1)
        data_type = data[0][0][0]
        data_note = data[0][0][1]
        data_vel = data[0][0][2]
        print "data %s, %d" % (data, data_type & 0x90)
        if (data_type & 0x90) > 0 and data_vel > 0:
            # note on
            return note(data_note, data_vel)

    def __destroy__(self):
        pypm.Terminate()
