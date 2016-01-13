import sys 
from cpyroot import *

from ROOT import TLine

officialStyle(gStyle)

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

class MetPhiVsSumEt(Fitter2D):
    
    def __init__(self, metname, tree, nx, xmin, xmax, ny, ymin, ymax):
        self.metname = metname
        cut = 'genMetTrue_pt>50.'.format(metname=metname)
        hname = '{metname}_MetPhi_h2d'.format(metname=metname)
        super(MetPhiVsSumEt,self).__init__( hname, hname, 
                                            nx, xmin, xmax, ny, ymin, ymax)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_phi-genMetTrue_phi:genMetTrue_pt'.format(metname=metname),
                     cut )
        self.fit_slices()
        self.hsigma.SetYTitle('MET #phi resolution')

c1 = TCanvas("c1","c1")        
xmin, xmax = 50, 250
args = (tree, 20, xmin, xmax, 100, -1, 1)

metcalo = MetPhiVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style, 'True MET (GeV)')
metcalo.hsigma.Draw()

metpf = MetPhiVsSumEt('pfMetT1', *args) 
metpf.format(pf_style, 'True MET (GeV)')
metpf.hsigma.Draw('same')

legend = TLegend(0.62, 0.79, 0.90, 0.92)
legend.AddEntry(metcalo.hsigma, 'Calo MET', 'p')
legend.AddEntry(metpf.hsigma, 'PF MET', 'p')
legend.Draw('same')

c1.SaveAs('met_phi_vs_sumet.pdf')

 
