from isobar.note import *

from midiutil.MidiFile import MIDIFile

class MidiFileOut:
	def __init__(self, numtracks = 16):
		self.score = MIDIFile(numtracks)
		self.track = 0
		self.channel = 0
		self.volume = 64
		self.time = 0

	def tick(self, ticklen):
		self.time += ticklen

	def noteOn(self, note = 60, velocity = 64, channel = 0, duration = 1):
		#------------------------------------------------------------------------
		# avoid rounding errors
		#------------------------------------------------------------------------
		time = round(self.time, 5)
		self.score.addNote(channel, channel, note, time, duration, velocity)

	def noteOff(self, note = 60, channel = 0):
		pass

	def writeFile(self, filename = "score.mid"):
		fd = open(filename, 'wb')
		self.score.writeFile(fd)
		fd.close()

class PatternWriterMIDI:
	def __init__(self, numtracks = 1):
		self.score = MIDIFile(numtracks)
		self.track = 0
		self.channel = 0
		self.volume = 64

	def addTrack(self, pattern, tracknumber = 0, trackname = "track", dur = 1.0):
		time = 0
		# naive approach: assume every duration is 1
		# TODO: accept dicts or PDicts
		for note in pattern:
			if note is not None:
				self.score.addNote(tracknumber, self.channel, note, time, dur, self.volume)
				time += dur
			else:
				time += dur

	def addTimeline(self, timeline):
		# TODO: translate entire timeline into MIDI
		# difficulties: need to handle degree/transpose params
		#			   need to handle channels properly, and reset numtracks
		pass

	def writeFile(self, filename = "score.mid"):
		fd = open(filename, 'wb')
		self.score.writeFile(fd)
		fd.close()
