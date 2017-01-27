import sys 
import numpy as np
from cpyroot import *

from tdrstyle import tdrstyle

from ROOT import TLine, TLatex

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

NEVENTS=sys.maxint
        
class MetVSTrue(Fitter2D): 
    def __init__(self, metname, tree, *args):
        self.metname = metname
        cut = 'genMetTrue_pt>50.'.format(metname=metname)
        # cut = '1'
        hname = '{metname}_MetVSTrue_h2d'.format(metname=metname)
        super(MetVSTrue,self).__init__( hname, hname, *args)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_pt/genMetTrue_pt:genMetTrue_pt'.format(metname=metname),
                     cut, '', NEVENTS)
        self.fit_slices()
        self.hmean.SetYTitle('p_{T}^{miss} response')

        
## binning 

calomet_name = 'caloMetT1'
pfmet_name = 'pfMetT1'
xmin = 0
xmax = 500
args = (tree, 50, xmin, xmax, 100, 0, 5)

## response

c2 = TCanvas("c2","c2")
metvstrue_args = (tree, 50, 0, 500, 100, 0, 5)

metvstrue_pf = MetVSTrue(pfmet_name, *metvstrue_args) 
metvstrue_pf.format(pf_style, 'Ref #Sigmap_{T} (GeV)')
metvstrue_pf.hmean.Draw()
metvstrue_pf.hmean.GetXaxis().SetNdivisions(5)

metvstrue_calo = MetVSTrue(calomet_name, *metvstrue_args) 
metvstrue_calo.format(traditional_style, 'Ref #Sigmap_{T} (GeV)')
metvstrue_calo.hmean.Draw("same")

metvstrue_pf.hmean.GetYaxis().SetRangeUser(0.5,1.1)

line = TLine(xmin,1.,xmax,1.)
line.Draw("same")

legend = TLegend(0.68,0.41, 0.87, 0.55)
legend.AddEntry(metvstrue_calo.hmean, 'Calo', 'p')
legend.AddEntry(metvstrue_pf.hmean, 'PF', 'p')

legend.Draw("same")

tdrstyle.cmsPrel(-1)
c2.SaveAs('met_response_vs_truemet.pdf')


## Resolution 


