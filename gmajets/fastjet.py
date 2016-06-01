import shelve
import math
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
        print p4.Theta(), p4.Phi(), p4.E()
        p4s.append(p4)
    return np.array(positions), p4s

sh = shelve.open('events.shv')

def process(ievent):
    plt.clf()
    plt.xlim(-math.pi/2., math.pi/2.)
    plt.ylim(-math.pi, math.pi)
    jet_clusterizer.clear()
    event = sh['events'][ievent]
    print event.keys()
    ptc_positions, ptc_p4s  = read_collection(event, 'particles')
    plt.plot(ptc_positions[:,0], ptc_positions[:,1], 'wo') 
    rec_positions, rec_p4s  = read_collection(event, 'rec')
    plt.plot(rec_positions[:,0], rec_positions[:,1], 'yo') 
    gen_positions, gen_p4s  = read_collection(event, 'gen')
    plt.plot(gen_positions[:,0], gen_positions[:,1], 'ro') 

    for p4 in ptc_p4s: 
        jet_clusterizer.add_p4(p4)
    jet_clusterizer.make_exclusive_jets(2)
    jets = []
    fj_positions = []
    for jeti in range(jet_clusterizer.n_jets()):
        jet = Jet(jet_clusterizer.jet(jeti))
        print jet
        jets.append(jet)
        fj_positions.append((jet.theta(), jet.phi()))
    fj_positions = np.array(fj_positions)
    plt.plot(fj_positions[:,0], fj_positions[:,1], 'b.')

    print ievent
    print gen_positions
    print rec_positions
    print fj_positions
    print jets

    print gen_p4s[0].E() + gen_p4s[1].E()
    print rec_p4s[0].E() + rec_p4s[1].E()
    print jets[0].e() + jets[1].e()

ievent = 0
process(ievent); ievent += 1

