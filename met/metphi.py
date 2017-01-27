import sys 
from cpyroot import *
import numpy as np

from ROOT import TLine

from tdrstyle import tdrstyle

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

class MetPhiVsSumEt(Fitter2D):
    
    def __init__(self, metname, tree, *args):
        self.metname = metname
        cut = 'genMetTrue_pt>70.'.format(metname=metname)
        hname = '{metname}_MetPhi_h2d'.format(metname=metname)
        super(MetPhiVsSumEt,self).__init__( hname, hname, *args)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_phi-genMetTrue_phi:genMetTrue_pt'.format(metname=metname),
                     cut )
        self.fit_slices()
        self.hsigma.SetYTitle('p_{T}^{miss} #varphi resolution')

c1 = TCanvas("c1","c1")        

xmin, xmax = 50, 250

binsize_low = 10
xbins_low_max = 180
xbins_low = np.linspace(xmin, xbins_low_max, (xbins_low_max-xmin)/binsize_low+1)
xbins_up = np.array([180,200, 220, xmax])
# xbins_up = np.array([180, 190, 200, 210, 220, 230, 240, 250])
xbins = np.concatenate((xbins_low, xbins_up))
print xbins

args = (tree, len(xbins)-1, xbins, 100, -1, 1)

metcalo = MetPhiVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style, 'p_{T,Ref}^{miss} (GeV)')
metcalo.hsigma.Draw()
metcalo.hsigma.GetYaxis().SetRangeUser(0,0.5)

metpf = MetPhiVsSumEt('pfMetT1', *args) 
metpf.format(pf_style, 'Ref MET (GeV)')
metpf.hsigma.Draw('same')

legend = TLegend(0.69,0.76, 0.88, 0.90)
legend.AddEntry(metcalo.hsigma, 'Calo', 'p')
legend.AddEntry(metpf.hsigma, 'PF', 'p')
legend.Draw('same')

tdrstyle.cmsPrel(-1, None, True)

c1.SaveAs('met_phi_vs_truemet.pdf')

 
