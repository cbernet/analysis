from cpyroot import * 
from ROOT import gPad
import time

chain = Chain('Events/fastjet*root')

c1 = TCanvas()

class Plots(dict):

    def add_jet(self, jet):
        self[jet] = dict()
    
    def add_plot(self, jet, plotname, plot):
        plot.SetStats(False)
        if plotname.startswith('res'):
            plot.GetYaxis().SetRangeUser(0.7, 1.3)
        if jet.startswith('ak'):
            plot.SetMarkerColor(1)
        elif jet.startswith('rec'):
            plot.SetMarkerColor(4)
        if '1' in jet: 
            plot.SetMarkerStyle(21)
        elif '2' in jet: 
            plot.SetMarkerStyle(8)
        self[jet][plotname] = plot.Clone( '_'.join([jet, plotname]) )

    def draw_profiles(self):
        self['ak1']['res_vs_dr_profile'].Draw()
        self['ak2']['res_vs_dr_profile'].Draw('same')
        self['rec1']['res_vs_dr_profile'].Draw('same')
        self['rec2']['res_vs_dr_profile'].Draw('same')
        
plots = Plots()

def shs(name):
    gPad.Update()
    time.sleep(1)
    gPad.SaveAs(name)

def draw(jet):
    plots.add_jet(jet)
    chain.Draw('{jet}_e/{jet}_gen_e:drgen>>h(12,0,3,50, 0, 3)'.format(jet=jet), 
               '', 'colz')
    plots.add_plot(jet, 'res_vs_dr', gDirectory.Get('h'))
    shs('res_vs_dr_{jet}.png'.format(jet=jet))
    chain.Draw('{jet}_e/{jet}_gen_e:drgen>>h(12,0,3)'.format(jet=jet), 
               '', 'prof')
    plots.add_plot(jet, 'res_vs_dr_profile', gDirectory.Get('h'))
    shs('res_vs_dr_profile_{jet}.png'.format(jet=jet))

draw('rec1')
draw('rec2')
draw('ak1')
draw('ak2')
plots.draw_profiles()
