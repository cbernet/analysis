import shelve
import math
import sys
import copy
# import numpy as np
# import matplotlib.pyplot as plt
from ROOT import TLorentzVector 

from ROOT import gSystem
gSystem.Load("libfccphysics-tools")
from ROOT import JetClusterizer
jet_clusterizer = JetClusterizer(1)

from heppy.particles.tlv.jet import Jet

def make_p4(theta, phi, energy):
    theta = math.pi/2. - theta
    cost = math.cos(theta)
    sint = math.sin(theta)
    cosp = math.cos(phi)
    sinp = math.sin(phi)
    x = sint*cosp
    y = sint*sinp
    z = cost 
    t = 1.
    p4 = TLorentzVector(x, y, z, t)
    p4 *= energy
    return p4 

def read_collection(event, name):
    p4s = []
    positions = []
    for theta, phi, energy in event[name]:
        positions.append( (theta, phi) )
        p4 = make_p4(theta, phi, energy)
        # print p4.Theta(), p4.Phi(), p4.E()
        p4s.append(p4)
    return np.array(positions), p4s

infname = sys.argv[1]
sh = shelve.open(infname)
outevents = list() 

def process(ievent, display=True):
    jet_clusterizer.clear()
    event = sh['events'][ievent]
    outevent = copy.deepcopy(event)
    ptc_positions, ptc_p4s  = read_collection(event, 'particles')
    rec_positions, rec_p4s  = read_collection(event, 'rec')
    gen_positions, gen_p4s  = read_collection(event, 'gen')

    for p4 in ptc_p4s: 
        jet_clusterizer.add_p4(p4)
    jet_clusterizer.make_exclusive_jets(2)
    jets = []
    fj_positions = []
    for jeti in range(jet_clusterizer.n_jets()):
        jet = Jet(jet_clusterizer.jet(jeti))
        jets.append(jet)
        fj_positions.append((jet.theta(), jet.phi()))
        outevent.setdefault('antikt', []).append((jet.theta(), jet.phi(), jet.e()))
    fj_positions = np.array(fj_positions)
    outevents.append(outevent)

    if display:
        plt.clf()
        plt.xlim(-math.pi/2., math.pi/2.)
        plt.ylim(-math.pi, math.pi)    
        plt.plot(ptc_positions[:,0], ptc_positions[:,1], 'wo') 
        plt.plot(rec_positions[:,0], rec_positions[:,1], 'yo') 
        plt.plot(gen_positions[:,0], gen_positions[:,1], 'ro') 
        plt.plot(fj_positions[:,0], fj_positions[:,1], 'b.')
        print event.keys()
        print ievent
        print gen_positions
        print rec_positions
        print fj_positions
        print jets
        print gen_p4s[0].E() + gen_p4s[1].E()
        print rec_p4s[0].E() + rec_p4s[1].E()
        print jets[0].e() + jets[1].e()


def loop(nevents=None):
    if nevents is None: 
        nevents = len(sh['events'])
    for ievent in range(nevents): 
        print ievent
        process(ievent, display=False)

ievent = 0

loop(1000)

# process(ievent); ievent += 1

sh.close()

outfname = 'fastjet_' + infname
outsh = shelve.open(outfname)
outsh['events'] = outevents
outsh.close()
