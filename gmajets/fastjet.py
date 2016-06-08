import shelve
import math
import sys
import copy
import os 
# import numpy as np
# import matplotlib.pyplot as plt

from ROOT import gSystem
gSystem.Load("libfccphysics-tools")
from ROOT import JetClusterizer
jet_clusterizer = JetClusterizer(1)

from heppy.particles.tlv.jet import Jet
from event import Event 

infname = sys.argv[1]
path,base = os.path.split(infname)
outfname = '/'.join( [path, 'fastjet_'+base] )

print 'input:', infname
print 'output:', outfname

sh = shelve.open(infname)
outevents = list() 

def process(ievent, fastjet=False):
    jet_clusterizer.clear()
    event = Event(sh['events'][ievent], ['particles', 'rec', 'gen']) 
    if fastjet: 
        for p4 in event['particles'][1]: 
            jet_clusterizer.add_p4(p4)
        jet_clusterizer.make_exclusive_jets(2)
        jets = []
        fj_positions = []
        antikt = list()
        for jeti in range(jet_clusterizer.n_jets()):
            jet = Jet(jet_clusterizer.jet(jeti))
            jets.append(jet)
            fj_positions.append((jet.theta(), jet.phi()))
            antikt.append( (jet.theta(), jet.phi(), jet.e()) )
        fj_positions = np.array(fj_positions)
        event.add_collection('antikt', antikt)
    return event


def loop(outfname, nevents=None):
    outsh = shelve.open(outfname)
    if nevents is None: 
        nevents = len(sh['events'])
    events = []
    for ievent in range(nevents): 
        if ievent%100==0:
            print ievent
        events.append( process(ievent, True).evdict ) 
    outsh['events'] = events
    outsh.close()
    

ievent = 0
loop(outfname)

# event = process(0, False)
# event.display()




