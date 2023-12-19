from .. import *
from signalflow import *
import numpy as np
import random
import os

graph = AudioGraph()
output_device = SignalFlowOutputDevice(graph)
timeline = Timeline(120, output_device)
timeline.background()

def track(name, **kwargs):
    global timeline
    params = {}
    for key in list(kwargs.keys()):
        if key not in ALL_EVENT_PARAMETERS:
            params[key] = kwargs[key]
            del kwargs[key]
    kwargs["params"] = params
    return timeline.schedule(kwargs, name=name, replace=True, quantize=1)

class SegmentPlayerPatch (Patch):
    def __init__(self, buf, onsets, pan=0.0, index=0, rate=1.0):
        super().__init__()
        index = self.add_input("index", index)
        rate = self.add_input("rate", rate)
        pan = self.add_input("pan", pan)
        player = SegmentPlayer(buf, onsets, rate=rate, index=index)
        pan = StereoBalance(player, pan)
        self.set_trigger_node(player)
        self.set_output(pan)

def segmenter(filename):
    buf = Buffer(filename)
    prefix, extension = os.path.splitext(filename)
    metadata_file = "%s.csv" % prefix
    onsets = list(np.loadtxt(metadata_file))
    patch = SegmentPlayerPatch(buf, onsets)
    patch.play()
    return patch

abs = PAbs
add = PAdd
pand = PAnd
arpeggiator = PArpeggiator
arrayindex = PArrayIndex
binop = PBinOp
brown = PBrown
changed = PChanged
choice = PChoice
coin = PCoin
collapse = PCollapse
concatenate = PConcatenate
constant = PConstant
counter = PCounter
creep = PCreep
currenttime = PCurrentTime
degree = PDegree
dict = PDict
dictkey = PDictKey
diff = PDiff
div = PDiv
equal = PEqual
euclidean = PEuclidean
explorer = PExplorer
fade = PFade
fadenotewise = PFadeNotewise
fadenotewiserandom = PFadeNotewiseRandom
filterbykey = PFilterByKey
flipflop = PFlipFlop
floordiv = PFloorDiv
func = PFunc
geom = PGeom
globals  = PGlobals
greaterthan = PGreaterThan
greaterthanorequal = PGreaterThanOrEqual
impulse = PImpulse
indexof = PIndexOf
int = PInt
interpolate = PInterpolate
lshift = PLShift
lsystem = PLSystem
lessthan = PLessThan
lessthanorequal = PLessThanOrEqual
loop = PLoop
midicontrol = PMIDIControl
map = PMap
mapenumerated = PMapEnumerated
markov = PMarkov
metropolis = PMetropolis
midinotetofrequency = PMidiNoteToFrequency
mod = PMod
mul = PMul
nearestnoteinkey = PNearestNoteInKey
norepeats = PNoRepeats
normalise = PNormalise
notequal = PNotEqual
pad = PPad
padtomultiple = PPadToMultiple
patterngeneratoraction = PPatternGeneratorAction
permut = PPermut
pingpong = PPingPong
pow = PPow
rshift = PRShift
randomexponential = PRandomExponential
randomimpulsesequence = PRandomImpulseSequence
randimpseq = PRandomImpulseSequence
randomwalk = PRandomWalk
range = PRange
ref = PRef
reset = PReset
reverse = PReverse
round = PRound
sample = PSample
scalar = PScalar
scalelinexp = PScaleLinExp
scalelinlin = PScaleLinLin
sequence = PSequence
seq = PSequence
sequenceaction = PSequenceAction
series = PSeries
shuffle = PShuffle
shuffleinput = PShuffleInput
skip = PSkip
skipif = PSkipIf
staticpattern = PStaticPattern
stochasticpattern = PStochasticPattern
stutter = PStutter
sub = PSub
subsequence = PSubsequence
switchone = PSwitchOne
tri = PTri
winterpolate = PWInterpolate
wrallantando = PWRallantando
wsine = PWSine
warp = PWarp
white = PWhite
wrap = PWrap