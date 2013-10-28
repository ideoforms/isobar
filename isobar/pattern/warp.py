from isobar.pattern import *
from isobar.timeline import *

import math

class PWarp(Pattern):
	pass

class PWInterpolate(PWarp):
	""" PWInterpolate: Requests a new target warp value from <pattern> every <length>
		beats, and applies linear interpolation to ramp between values. 

		To select a new target warp value every 8 beats, between [-0.5, 0.5]:

		>>> p = PWInterpolate(PWhite(-0.5, 0.5), 8)
		"""
	def __init__(self, pattern, length = 1):
		self.length = length
		self.pattern = pattern
		self.pos = self.length
		self.value = 0.0

	def next(self):
		rv = self.value

		#------------------------------------------------------------------------
		# keep ticking until we have reached our period (length, in beats)
		#------------------------------------------------------------------------
		self.pos += 1.0 / TICKS_PER_BEAT
		if self.pos >= self.length:
			self.pos = 0
			self.target = self.pattern.next()

			#------------------------------------------------------------------------
			# in case our length parameter is also a pattern: obtain a scalar value.
			# dv is used for linear interpolation until the next target reached.
			#------------------------------------------------------------------------
			length = Pattern.value(self.length)
			self.dv = (self.target - self.value) / (TICKS_PER_BEAT * length)

		self.value = self.value + self.dv

		return rv

class PWSine(PWarp):
	def __init__(self, length = 1, amp = 0.5):
		self.length = length
		self.amp = amp
		self.pos = 0.0

	def next(self):
		self.pos += 1.0 / TICKS_PER_BEAT
		if self.pos > self.length:
			self.pos -= self.length

		# normalize to [0, 1]
		pos_norm = self.pos / self.length
		warp = math.sin(2.0 * math.pi * pos_norm)
		warp = warp * self.amp

		return warp

