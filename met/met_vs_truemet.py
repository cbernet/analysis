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
        self.hsigma.SetYTitle('Relative p_{T}^{miss} resolution')

        
## binning 

calomet_name = 'caloMetT1'
pfmet_name = 'pfMetT1'

xmin, xmax = 50, 250

binsize_low = 10
xbins_low_max = 180
xbins_low = np.linspace(xmin, xbins_low_max, (xbins_low_max-xmin)/binsize_low+1)
xbins_up = np.array([180,200, 220, xmax])
# xbins_up = np.array([180, 190, 200, 210, 220, 230, 240, 250])
xbins = np.concatenate((xbins_low, xbins_up))
print xbins

args = (tree, len(xbins)-1, xbins, 100, 0, 5)

## response

c1 = TCanvas("c1","c1")
# metvstrue_args = (tree, 50, 0, 500, 100, 0, 5)

metvstrue_pf = MetVSTrue(pfmet_name, *args) 
metvstrue_pf.format(pf_style, 'p_{T,Ref}^{miss} (GeV)')
metvstrue_pf.hmean.Draw()
metvstrue_pf.hmean.GetXaxis().SetNdivisions(5)

metvstrue_calo = MetVSTrue(calomet_name, *args) 
metvstrue_calo.format(traditional_style, 'p_{T,Ref}^{miss} (GeV)')
metvstrue_calo.hmean.Draw("same")

metvstrue_pf.hmean.GetYaxis().SetRangeUser(0.5,1.1)

line = TLine(xmin,1.,xmax,1.)
line.Draw("same")

legend = TLegend(0.69,0.76, 0.88, 0.90)

legend.AddEntry(metvstrue_calo.hmean, 'Calo', 'p')
legend.AddEntry(metvstrue_pf.hmean, 'PF', 'p')

legend.Draw("same")

tdrstyle.cmsPrel(-1)
c1.SaveAs('met_response_vs_truemet.pdf')


## Resolution 

c2 = TCanvas("c2","c2")

metvstrue_calo.hsigma.Draw()
metvstrue_calo.hsigma.GetXaxis().SetNdivisions(5)
metvstrue_calo.hsigma.GetYaxis().SetRangeUser(0, 0.5)
metvstrue_pf.hsigma.Draw('same')

legend.Draw("same")

tdrstyle.cmsPrel(-1)
c2.SaveAs('met_relsigma_vs_truemet.pdf')

