import random
import time

from OSC import *

from isobar.note import *

MIDIIN_DEFAULT = "IAC Driver A"
MIDIOUT_DEFAULT = "IAC Driver A"

class OSCOut:
	def __init__(self, host = "localhost", port = 7000):
		self.osc = OSCClient()
		self.osc.connect((host, port))
		self.debug = False

	def tick(self, ticklen):
		pass

	def noteOn(self, note = 60, velocity = 64, channel = 0):
		if self.debug:
			print "channel %d, noteOn: %d" % (channel, note)
		msg = OSCMessage("/note", [ note, velocity, channel ])
		self.osc.send(msg)

	def noteOff(self, note = 60, channel = 0):
		if self.debug:
			print "channel %d, noteOff: %d" % (channel, note)
		msg = OSCMessage("/note", [ note, 0, channel ])
		self.osc.send(msg)

	def allNotesOff(self, channel = 0):
		if self.debug:
			print "channel %d, allNotesOff"
		for n in range(128):
			self.noteOff(n, channel)

	def control(self, control, value, channel = 0):
		# if self.debug:
		print "channel %d, control %d: %d" % (channel, control, value)
		msg = OSCMessage("/control", [ control, value, channel ])
		self.osc.send(msg)

	def __destroy__(self):
		self.osc.close()

	def send(self, address, params = None):
		msg = OSCMessage(address, params)
		print "osc: %s (%s)" % (address, params)
		self.osc.send(msg)


