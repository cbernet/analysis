import shelve
import math
import sys
import copy

from heppy.particles.tlv.particle import Particle
from matching import matchObjectCollection2, deltaR
from event import Event 

from ROOT import TFile 
from heppy.statistics.tree import Tree 

infname = sys.argv[1]

sh = shelve.open(infname)
outevents = list() 

events = dict()

outfname = infname.replace('.shv', '.root')

print 'input:', infname
print 'output', outfname

f = TFile(outfname,'RECREATE')
tree = Tree('events', 'tree for gael')

tree.var('rec1_e')
tree.var('rec1_gen_e')
tree.var('rec1_dr')
tree.var('rec2_e')
tree.var('rec2_gen_e')
tree.var('rec2_dr')
tree.var('ak1_e')
tree.var('ak1_gen_e')
tree.var('ak1_dr')
tree.var('ak2_e')
tree.var('ak2_gen_e')
tree.var('ak2_dr')
tree.var('drgen')

def process_event(ievent):

    tree.reset()

    event = Event(sh['events'][ievent], ['particles', 'rec', 'gen', 'antikt']) 
    events[ievent] = event

    def make_jets(name):
        coll = event.collections[name][1]
        ptcs = []
        for ptc in coll:
            ptcs.append( Particle(0, 0, ptc ) )
        return ptcs

    gen_jets = make_jets('gen')
    rec_jets = make_jets('rec')
    ak_jets = make_jets('antikt')

    # compute dr between the two gens:                                                                         
    # drgen = deltaR(gen_jets[0].theta(), gen_jets[0].phi(), 
    #               gen_jets[1].theta(), gen_jets[1].phi())
    drgen = gen_jets[0].p3().Angle( gen_jets[1].p3() )

    # print 'event', ievent, drgen 

    # very large dR max 
    pairs = matchObjectCollection2(rec_jets, gen_jets, 10)

    for jet in rec_jets:
        gen_jet = pairs[jet]
        if not gen_jet:
            continue
        jet.dr = deltaR(jet.theta(), jet.phi(), gen_jet.theta(), gen_jet.phi())
        jet.gen = gen_jet
        # print 'rec', jet.e(), jet.gen.e(), jet.dr
        
    rec1, rec2 = rec_jets

    pairs = matchObjectCollection2(ak_jets, gen_jets, 10)

    for jet in ak_jets:
        gen_jet = pairs[jet]
        if not gen_jet:
            continue
        jet.dr = deltaR(jet.theta(), jet.phi(), gen_jet.theta(), gen_jet.phi())
        jet.gen = gen_jet
        # print 'ak', jet.e(), jet.gen.e(), jet.dr
        
    ak1, ak2 = ak_jets


    tree.fill('rec1_e', rec1.e())
    tree.fill('rec1_gen_e', rec1.gen.e())
    tree.fill('rec1_dr', rec1.dr)
    tree.fill('rec2_e', rec2.e())
    tree.fill('rec2_gen_e', rec2.gen.e())
    tree.fill('rec2_dr', rec2.dr)

    tree.fill('ak1_e', ak1.e())
    tree.fill('ak1_gen_e', ak1.gen.e())
    tree.fill('ak1_dr', ak1.dr)
    tree.fill('ak2_e', ak2.e())
    tree.fill('ak2_gen_e', ak2.gen.e())
    tree.fill('ak2_dr', ak2.dr)
 
    tree.fill('drgen', drgen)

    tree.tree.Fill()

for iev in range(len(sh['events'])):
# for iev in range(100):
    process_event(iev)

f.Write()
f.Close()
