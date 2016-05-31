import sys 
from cpyroot import *

from ROOT import TLine

from tdrstyle import tdrstyle

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
        self.hsigma.SetYTitle('E_{T}^{miss} #phi resolution')

c1 = TCanvas("c1","c1")        
xmin, xmax = 50, 250
args = (tree, 20, xmin, xmax, 100, -1, 1)

metcalo = MetPhiVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style, 'True E_{T}^{miss} (GeV)')
metcalo.hsigma.Draw()
metcalo.hsigma.GetYaxis().SetRangeUser(0,0.5)

metpf = MetPhiVsSumEt('pfMetT1', *args) 
metpf.format(pf_style, 'True MET (GeV)')
metpf.hsigma.Draw('same')

legend = TLegend(0.69,0.76, 0.88, 0.90)
legend.AddEntry(metcalo.hsigma, 'Calo', 'p')
legend.AddEntry(metpf.hsigma, 'PF', 'p')
legend.Draw('same')

tdrstyle.cmsPrel(-1, 13, True)

c1.SaveAs('met_phi_vs_truemet.pdf')

 
