import sys 
import numpy as np
from cpyroot import *

from tdrstyle import tdrstyle

from ROOT import TLine

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

NEVENTS=sys.maxint

class MetVsSumEt(Fitter2D): 
    def __init__(self, metname, tree, *args):        
        self.metname = metname
        cut = '{metname}_sumet>50. && {metname}_sumet<4000'.format(metname=metname)
        hname = '{metname}_h2d'.format(metname=metname)
        super(MetVsSumEt,self).__init__( hname, hname, *args)
        tree.Project(self.h2d.GetName(), 
                      '{metname}_px:{metname}_sumet'.format(metname=metname),
                     cut, '', NEVENTS)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_py:{metname}_sumet'.format(metname=metname),
                     cut, '', NEVENTS)
        self.fit_slices()
        self.hsigma.SetYTitle('#sigma(E_{T}^{miss}) (GeV)')
         
        
class SumEtResponse(Fitter2D): 
    def __init__(self, metname, tree, *args):
        self.metname = metname
        cut = 'genMetTrue_sumet>50.'.format(metname=metname)
        hname = '{metname}_SumEtResponse_h2d'.format(metname=metname)
        super(SumEtResponse,self).__init__( hname, hname, *args)
        tree.Project(self.h2d.GetName(), 
                     '{metname}_sumet/genMetTrue_sumet:genMetTrue_sumet'.format(metname=metname),
                     cut, '', NEVENTS)
        self.fit_slices()
        self.hmean.SetYTitle('#SigmaE_{T} response')


c1 = TCanvas("c1","c1")
xmin, xmax = 0, 4100

binsize_low = 100
xbins_low_max = 3000
xbins_low = np.linspace(xmin, xbins_low_max, (xbins_low_max-xmin)/binsize_low+1)
xbins_up = np.array([3200, 3400, 3600, 3800, 4000, xmax])
xbins = np.concatenate((xbins_low, xbins_up))
print xbins

# args = (tree, 50, xmin, xmax, 100, -100, 100)
args = (tree, len(xbins)-1, xbins, 100, -100, 100)

func = TF1("matthieu", "sqrt( [0]*[0]+ [1]**2 * (x-[2]) + ([3]*(x-[4]))**2 )")
func.SetLineColor(1)

metcalo = MetVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style, '#SigmaE_{T} (GeV)')
# metcalo.hsigma.Fit(func,'', '', 500, xmax)
metcalo.hsigma.Draw()
metcalo.hsigma.GetXaxis().SetNdivisions(5)
# metcalo.hsigma.GetXaxis().SetNdivisions(10)

func = TF1("matthieu", "sqrt( [0]*[0]+ ([1]*sqrt(x-[2]))**2 + ([3]*(x-[4]))**2 )")
func.SetLineColor(1)
metpf = MetVsSumEt('pfMetT1', *args) 
metpf.format(pf_style, '#SigmaE_{T} (GeV)')
metpf.hsigma.Draw('same')
# metpf.hsigma.Fit(func, '', 'same', 50, xmax)

metcalo.hsigma.SetStats(False)
metpf.hsigma.SetStats(False)

legend = TLegend(0.68,0.21, 0.87, 0.35)
legend.AddEntry(metcalo.hsigma, 'Calo', 'p')
legend.AddEntry(metpf.hsigma, 'PF', 'p')
legend.Draw('same')

tdrstyle.cmsPrel(-1, 13, True)
c1.SaveAs('met_sigma_vs_sumet.pdf')

c2 = TCanvas("c2","c2")
# sumetresponse_args = (tree, 50, xmin, xmax, 100, 0, 2)
sumetresponse_args = (tree, len(xbins)-1, xbins, 100, 0, 2)

sumetresponse_pf = SumEtResponse('pfMetT1', *sumetresponse_args) 
sumetresponse_pf.format(pf_style, '#SigmaE_{T} (GeV)')
sumetresponse_pf.hmean.Draw()
sumetresponse_pf.hmean.GetXaxis().SetNdivisions(5)

sumetresponse_calo = SumEtResponse('caloMetT1', *sumetresponse_args) 
sumetresponse_calo.format(traditional_style, '#SigmaE_{T} (GeV)')
sumetresponse_calo.hmean.Draw("same")

sumetresponse_pf.hmean.GetYaxis().SetRangeUser(0.5,1.1)

line = TLine(xmin,1.,xmax,1.)
line.Draw("same")

legend.Draw("same")

tdrstyle.cmsPrel(-1, 13, True)
c2.SaveAs('met_response_vs_sumet.pdf')

# metpf.write()
# metcalo.write()

gPad.Modified()
gPad.Update()
