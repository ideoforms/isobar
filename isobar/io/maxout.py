class MaxOut:
    def __init__(self, maxObject):
        self.maxObject = maxObject
        self.debug = False
        print "Created Max/MSP output device"

    def noteOn(self, note = 60, velocity = 64, channel = 0):
        if self.debug:
            print "channel %d, noteOn: %d" % (channel, note)

        print "note! %s" % self.maxObject
        self.maxObject.outlet(0, note)
        self.maxObject.outlet(1, velocity)

    def noteOff(self, note = 60, channel = 0):
        if self.debug:
            print "channel %d, noteOff: %d" % (channel, note)

        # time.sleep(0.001)
        # maxObject.outlet(0, note)
        # maxObject.outlet(1, velocity)

    def allNotesOff(self, channel = 0):
        pass

    def control(self, control = 0, value = 0, channel = 0):
        pass

    def __destroy__(self):
        pass
