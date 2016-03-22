import sys 
import numpy as np
from cpyroot import *

from ROOT import TLine

officialStyle(gStyle)

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

class MetVsSumEt(Fitter2D): 
    def __init__(self, metname, tree, nx, xmin, xmax, ny, ymin, ymax):
        self.metname = metname
        cut = '{metname}_sumet>50.'.format(metname=metname)
        hname = '{metname}_h2d'.format(metname=metname)
        super(MetVsSumEt,self).__init__( hname, hname, 
                                    nx, xmin, xmax, ny, ymin, ymax)
        tree.Project(self.h2d.GetName(), 
                      '{metname}_px:{metname}_sumet'.format(metname=metname),
                     cut )
        tree.Project(self.h2d.GetName(), 
                     '{metname}_py:{metname}_sumet'.format(metname=metname),
                     cut )
        self.fit_slices()
        self.hsigma.SetYTitle('#sigma(E_{T}^{miss}) (GeV)')
 
        
class SumEtResponse(Fitter2D): 
    def __init__(self, metname, tree, nx, xmin, xmax, ny, ymin, ymax):
        self.metname = metname
        cut = 'genMetTrue_sumet>50.'.format(metname=metname)
        hname = '{metname}_SumEtResponse_h2d'.format(metname=metname)
        super(SumEtResponse,self).__init__( hname, hname, 
                                    nx, xmin, xmax, ny, ymin, ymax)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_sumet/genMetTrue_sumet:genMetTrue_sumet'.format(metname=metname),
                     cut )
        self.fit_slices()
        self.hmean.SetYTitle('#SigmaE_{T} response')

 
        

c1 = TCanvas("c1","c1")
xmin, xmax = 0, 2000
args = (tree, 50, xmin, xmax, 100, -100, 100)

metcalo = MetVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style, '#SigmaE_{T} (GeV)')
metcalo.hsigma.Draw()
# metcalo.hsigma.GetYaxis().SetRangeUser(0,30)
# metcalo.hsigma.GetXaxis().SetNdivisions(10)

metpf = MetVsSumEt('pfMetT1', *args) 
metpf.format(pf_style, '#SigmaE_{T} (GeV)')
metpf.hsigma.Draw('same')

legend = TLegend(0.68,0.21, 0.87, 0.35)
legend.AddEntry(metcalo.hsigma, 'Calo', 'p')
legend.AddEntry(metpf.hsigma, 'PF', 'p')
legend.Draw('same')

cmsPrel(-1, 13, True)
c1.SaveAs('met_sigma_vs_sumet.pdf')

c2 = TCanvas("c2","c2")
sumetresponse_args = (tree, 50, 0, 2000, 100, 0, 2)

sumetresponse_pf = SumEtResponse('pfMetT1', *sumetresponse_args) 
sumetresponse_pf.format(pf_style, '#SigmaE_{T} (GeV)')
sumetresponse_pf.hmean.Draw()

sumetresponse_calo = SumEtResponse('caloMetT1', *sumetresponse_args) 
sumetresponse_calo.format(traditional_style, '#SigmaE_{T} (GeV)')
sumetresponse_calo.hmean.Draw("same")

sumetresponse_pf.hmean.GetYaxis().SetRangeUser(0.5,1.1)

line = TLine(xmin,1.,xmax,1.)
line.Draw("same")

legend.Draw("same")

cmsPrel(-1, 13, True)
c2.SaveAs('met_response_vs_sumet.pdf')
