from isobar.pattern.core import *

import threading
import inspect
import math

import pythonosc

class PStaticViaOSC (Pattern):
    listening = False
    
    def __init__(self, default = 0, address = "/value", port = 9900):
        if not PStaticViaOSC.initialised:
            server = OSC.OSCServer(("localhost", port))
            server.addMsgHandler(prefix, self.recv)
            self.thread = threading.Thread(target = server.serve_forever)
            self.thread.setDaemon(True)
            self.thread.start()

            PStaticGlobal.listening = True

            osc_server = OSC.OSCServer(("0.0.0.0", port))

            osc_server.serve_forever()

        self.value = default
        self.address = address
        osc.bind(self.recv, address)

    def recv(self, msg, source = None):
        address = msg[0]
        signature = msg[1][1:]
        print("(%s) %s" % (address, signature))
        self.value = msg[2]

    def __next__(self):
        return self.value

class PStaticTimeline (Pattern):
    """ PStaticTimeline: Returns the position (in beats) of the current timeline. """

    def __init__(self, timeline = None):
        self.given_timeline = timeline

    def __next__(self):
        beats = self.get_beats()
        return round(beats, 5)

    def get_beats(self):
        #------------------------------------------------------------------------
        # using the specified timeline (if given) or the currently-embedded
        # timeline (otherwise), return the current position in beats.
        #------------------------------------------------------------------------
        timeline = self.given_timeline if self.given_timeline else self.timeline
        if timeline:
            return timeline.beats

        return 0

class PStaticGlobal(Pattern):
    """ PStaticGlobal: Static global value identified by a string, with OSC listener """
    dict = {}
    listening = False

    def __init__(self, name, value = None):
        self.name = name
        if value is not None:
            PStaticGlobal.set(name, value)

    def __next__(self):
        name = Pattern.value(self.name)
        value = PStaticGlobal.dict[name]
        return Pattern.value(value)

    # BROKEN: not sure why
    @classmethod
    def _get(self, key):
        value = PStaticGlobal.dict[key]
        return Pattern.value(value)

    @classmethod
    def set(self, key, value):
        PStaticGlobal.dict[key] = value

    @classmethod
    def listen(self, prefix = "/global", port = 9900):
        if not PStaticGlobal.listening:
            server = OSC.OSCServer(("localhost", port))
            server.addMsgHandler(prefix, self.recv)
            self.thread = threading.Thread(target = server.serve_forever)
            self.thread.setDaemon(True)
            self.thread.start()

            PStaticGlobal.listening = True

        self.prefix = prefix

    @classmethod
    def recv(self, addr, tags, data, client_address):
        # print "GOT MSG"
        key = data[0]
        value = data[1]
        print("(%s) %s = %.1f" % (addr, key, value))
        PStaticGlobal.set(key, value)

class PStaticTimelineSine(PStaticTimeline):
    def __init__(self, period):
        PStaticTimeline.__init__(self)
        self.period = period

    def __next__(self):
        period = Pattern.value(self.period)
        # self.phase += math.pi * 2.0 / period

        beats = self.get_beats()
        rv = math.sin(2 * math.pi * beats / self.period)
        return rv


class PStaticSeq(Pattern):
    def __init__(self, sequence, duration):
        #------------------------------------------------------------------------
        # take a copy of the list to avoid changing the original
        #------------------------------------------------------------------------
        self.sequence = copy.copy(sequence)
        self.duration = duration
        self.start = None
    
    def __next__(self):
        timeline = self.timeline
        if self.start is None:
            self.start = round(timeline.beats, 5)

        now = round(timeline.beats, 5)
        if now - self.start >= self.duration:
            self.sequence.pop(0)
            self.start = now
            if len(self.sequence) == 0:
                raise StopIteration
        return self.sequence[0]

