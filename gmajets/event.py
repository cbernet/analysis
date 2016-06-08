import shelve
import copy
import math
import numpy as np
import matplotlib.pyplot as plt
from ROOT import TLorentzVector 

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


class Event(object): 
    
    def __init__(self, evdict, collection_names):
        self.evdict = copy.deepcopy(evdict) 
        self.collections = dict()
        map(self.process_collection, collection_names) 
        self.display_initialized = False
    
    def process_collection(self, collname): 
        p4s = []
        positions = []
        for theta, phi, energy in self.evdict[collname]:
            positions.append( (theta, phi, energy) )
            p4 = make_p4(theta, phi, energy)
            p4s.append(p4)
        positions = np.array(positions)
        self.collections[collname] = positions, p4s 
    
    def add_collection(self, collname, data):
        self.evdict[collname] = data
        self.process_collection(collname)

    def __getitem__(self, name):
        return self.collections[name]

    def display_collection(self, collname):
        positions = self.collections[collname][0]
        plt.plot(positions[:,0], positions[:,1], 'o')

    def display(self):
        if not self.display_initialized:
            plt.clf()
            plt.xlim(-math.pi/2., math.pi/2.)
            plt.ylim(-math.pi, math.pi)            
        colors = {
            'particles':'w',
            'rec':'b',
            'antikt':'y',
            'gen':'r'
            }
        for name, data in self.collections.iteritems():
            positions, p4s = data
            color = colors[name]
            plt.plot(positions[:,0], positions[:,1], color+'o')

 

