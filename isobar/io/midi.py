import pypm
import random
import time

from isobar.note import *

MIDIIN_DEFAULT = "IAC Driver A"
MIDIOUT_DEFAULT = "IAC Driver A"


class MidiIn:
	def __init__(self, target = MIDIIN_DEFAULT):
		pypm.Initialize()
		self.midi = None
		self.clocktarget = None

		for n in range(pypm.CountDevices()):
			info = pypm.GetDeviceInfo(n)
			name = info[1]
			print "[%d] %s %s" % (n, name, info)
			isInput = info[2]
			if name == target and isInput == 1:
				self.midi = pypm.Input(n)
				print "xx found target input: %s" % target

		if self.midi is None:
			raise Exception, "Could not find MIDI source: %s" % target

	def run(self):
		while True:
			if not self.midi.Poll():
				continue
			data = self.midi.Read(1)
			data_type = data[0][0][0]
			data_note = data[0][0][1]
			data_vel = data[0][0][2]
			if data_type == 248:
				if self.clocktarget is not None:
					self.clocktarget.tick()
			elif data_type == 144:
				# TODO: is this the right midi code?
				if self.clocktarget is not None:
					self.clocktarget.reset_to_beat()
			elif data_type & 0x90:
				# note on
				# print "%d (%d)" % (data_note, data_vel)
				pass 
			# print "%d %d (%d)" % (data_type, data_note, data_vel)

			time.sleep(0.001)

	def poll(self):
		""" used in markov-learner -- can we refactor? """
		if not self.midi.Poll():
			return

		data = self.midi.Read(1)
		data_type = data[0][0][0]
		data_note = data[0][0][1]
		data_vel = data[0][0][2]

		if (data_type & 0x90) > 0 and data_vel > 0:
			# note on
			return note(data_note, data_vel)

	def __destroy__(self):
		pypm.Terminate()


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
