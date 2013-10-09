from __future__ import absolute_import 

from isobar.note import *
from isobar.pattern.core import *


import midi

class MidiFileIn:
	def __init__(self):
		pass

	def read(self, filename):
		reader = midi.FileReader()
		data = reader.read(file(filename))

		class Note:
			def __init__(self, pitch, velocity, location, duration = None):
				# pitch = MIDI 0..127
				self.pitch = pitch
				# velocity = MIDI 0..127
				self.velocity = velocity
				# location in time, beats
				self.location = location
				# duration in time, beats
				self.duration = duration

		notes = []
		for track in data:
			track.make_ticks_abs()
			for event in filter(lambda event: isinstance(event, midi.events.NoteEvent), track):
				location = event.tick / 96.0
				if isinstance(event, midi.events.NoteOnEvent):
					print "(%.2f beats) %s. \t(note = %d, velocity = %d)" % (location, miditoname(event.pitch), event.pitch, event.velocity)
					note = Note(event.pitch, event.velocity, location)
					notes.append(note)
				if isinstance(event, midi.events.NoteOffEvent):
					print "(%.2f beats) %s off \t(note = %d, velocity = %d)" % (location, miditoname(event.pitch), event.pitch, event.velocity)
					found = False
					for note in reversed(notes):
						if note.pitch == event.pitch:
							duration = location - note.location
							# print " -> duration = %.2f beats" % duration
							note.duration = duration
							found = True
							break
					if not found:
						print "*** NOTE-OFF FOUND WITHOUT NOTE-ON ***"
	
		d = {
			"note" : [ note.pitch for note in notes ],
			"amp" : [ note.velocity for note in notes ],
			"dur" : [ note.duration for note in notes ],
		}

		return d

class MidiFileOut:
	def __init__(self, numtracks = 16):
		from midiutil.MidiFile import MIDIFile

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
		try:
			for note in pattern:
				vdur = Pattern.value(dur)
				if note is not None and vdur is not None:
					self.score.addNote(tracknumber, self.channel, note, time, vdur, self.volume)
					time += vdur
				else:
					time += vdur
		except StopIteration:
			# a StopIteration exception means that an input pattern has been exhausted.
			# catch it and treat the track as completed.
			pass

	def addTimeline(self, timeline):
		# TODO: translate entire timeline into MIDI
		# difficulties: need to handle degree/transpose params
		#			   need to handle channels properly, and reset numtracks
		pass

	def writeFile(self, filename = "score.mid"):
		fd = open(filename, 'wb')
		self.score.writeFile(fd)
		fd.close()
