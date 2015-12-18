import sys 
import numpy as np
from cpyroot import *
from ROOT import TLine

officialStyle(gStyle)

rootfile = TFile(sys.argv[1])
tree = rootfile.Get('events')

class Fitter2D(object):
    
    def draw2D(self, *args):
        self.h2d.Draw(*args)
        self.hmean.Draw('psame')

            
    def fit(self, bin, opt='0'): 
        hslice = self.h2d.ProjectionY("", bin, bin, "")
        if not hslice.GetEntries(): 
            return 0., 0., 0., 0., 0., 0.
        hslice.Fit('gaus', opt)
        func = hslice.GetFunction('gaus')
        x = self.h2d.GetXaxis().GetBinCenter(bin)
        dx = self.h2d.GetXaxis().GetBinWidth(bin)
        mean = func.GetParameter(1)
        dmean = func.GetParError(1)
        sigma = func.GetParameter(2)
        dsigma = func.GetParError(2)
        return x, dx, mean, dmean, sigma, dsigma
    

class MetVsSumEt(Fitter2D): 
    def __init__(self, metname, tree, nx, xmin, xmax, ny, ymin, ymax):
        self.metname = metname
        cut = '{metname}_sumet>50.'.format(metname=metname)
        hname = '{metname}_h2d'.format(metname=metname)
        self.h2d = TH2F(hname, hname, 
                        nx, xmin, xmax, ny, ymin, ymax)
        tree.Project(self.h2d.GetName(), 
                      '{metname}_px:{metname}_sumet'.format(metname=metname),
                     cut )
        tree.Project(self.h2d.GetName(), 
                     '{metname}_py:{metname}_sumet'.format(metname=metname),
                     cut )
        self.h2d.FitSlicesY()
        self.hmean = gDirectory.Get( self.h2d.GetName() + '_1' )
        self.hsigma = gDirectory.Get( self.h2d.GetName() + '_2' )
        self.hsigma.SetYTitle('#sigma(MET_{x,y})')
        self.hchi2 = gDirectory.Get( self.h2d.GetName() + '_chi2' )

    def format(self, style):
        for hist in [self.hmean, self.hsigma, self.hchi2]: 
            style.format(hist)
            hist.SetTitle('')
            hist.SetXTitle('#SigmaE_{T} (GeV)')

        
class SumEtResponse(Fitter2D): 
    def __init__(self, metname, tree, nx, xmin, xmax, ny, ymin, ymax):
        self.metname = metname
        cut = 'genMetTrue_sumet>50.'.format(metname=metname)
        hname = '{metname}_SumEtResponse_h2d'.format(metname=metname)
        self.h2d = TH2F(hname, hname, 
                        nx, xmin, xmax, ny, ymin, ymax)
        tree.Project(self.h2d.GetName(), 
                      '{metname}_sumet/genMetTrue_sumet:genMetTrue_sumet'.format(metname=metname),
                     cut )
        self.h2d.FitSlicesY()
        self.hmean = gDirectory.Get( self.h2d.GetName() + '_1' )
        self.hmean.SetYTitle('#SigmaE_{T} response')
        self.hsigma = gDirectory.Get( self.h2d.GetName() + '_2' )
        self.hsigma.SetYTitle('#sigma(MET_{x,y})')
        self.hchi2 = gDirectory.Get( self.h2d.GetName() + '_chi2' )

    def format(self, style):
        for hist in [self.hmean, self.hsigma, self.hchi2]: 
            style.format(hist)
            hist.SetTitle('')
            hist.SetXTitle('true #SigmaE_{T} (GeV)')
 
        

c1 = TCanvas("c1","c1")
xmin, xmax = 0, 2000
args = (tree, 50, xmin, xmax, 100, -100, 100)

metcalo = MetVsSumEt('caloMetT1', *args) 
metcalo.format(traditional_style)
metcalo.hsigma.Draw()
# metcalo.hsigma.GetYaxis().SetRangeUser(0,30)
# metcalo.hsigma.GetXaxis().SetNdivisions(10)

metpf = MetVsSumEt('pfMetT1', *args) 
metpf.format(pf_style)
metpf.hsigma.Draw('same')

legend = TLegend(0.21,0.79, 0.49, 0.92)
legend.AddEntry(metcalo.hsigma, 'Calo MET', 'p')
legend.AddEntry(metpf.hsigma, 'PF MET', 'p')
legend.Draw('same')

c2 = TCanvas("c2","c2")
sumetresponse_args = (tree, 50, 0, 2000, 100, 0, 2)

sumetresponse_pf = SumEtResponse('pfMetT1', *sumetresponse_args) 
sumetresponse_pf.format(pf_style)
sumetresponse_pf.hmean.Draw()

sumetresponse_calo = SumEtResponse('caloMetT1', *sumetresponse_args) 
sumetresponse_calo.format(traditional_style)
sumetresponse_calo.hmean.Draw("same")

sumetresponse_pf.hmean.GetYaxis().SetRangeUser(0.5,1.2)

line = TLine(xmin,1.,xmax,1.)
line.Draw("same")

legend.Draw("same")
