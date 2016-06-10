from cpyroot import * 
from ROOT import gPad
import time

from tdrstyle import tdrstyle

chain = Chain('Events/fastjet*root')

c1 = TCanvas()

def draw_hists(hists):
    max_h = []
    for hist in hists:
        max_h.append( [hist.GetMaximum(), hist] )
    same = ''
    first = None
    for maximum, hist in sorted(max_h, reverse=True):
        hist.Draw(same)
        if first is None:
            same = 'same'
            first = hist
    return first
    

class Plots(dict):

    def add_jet(self, jet):
        self.setdefault(jet, dict())
    
    def add_plot(self, jet, plotname, plot):
        plot.SetStats(False)
        plot.GetXaxis().SetTitle('#theta_{gen} (rad)')
        if plotname.startswith('res'):
            plot.GetYaxis().SetRangeUser(0.7, 1.3)
            plot.GetYaxis().SetTitle('E_{rec}/E_{gen}')
        if jet.startswith('ak'):
            plot.SetTitle('anti-k_{T}')
            plot.SetMarkerColor(1)
        elif jet.startswith('rec'):
            plot.SetTitle('GMA')
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
        gPad.SaveAs('means.png')


        
    def draw_residuals(self, imin, imax, rebin, xmin, xmax):
        resmin, resmax = 0, 3
        jets = dict( ak1 = (1,'anti-kT jet 1'),
                     ak2 = (2, 'anti-kT jet 2'),
                     rec1 = (3, 'gma jet 1'),
                     rec2 = (4, 'gma jet 2' ))
        self.residual_projs = dict()
        projname = 'res_{imin}_{imax}'.format(imin=imin, imax=imax)
        same = ''
        ymax = 0
        legend = TLegend(0.6,0.5,0.89,0.89, '', 'NDC')
        hists = []
        for jet, params in sorted(jets.iteritems()):
            color, legtitle = params
            hist = self[jet]['res_vs_dr']
            hist.GetYaxis().SetRangeUser(resmin, resmax)
            proj = hist.ProjectionY('', imin, imax, '').Clone()
            proj.Rebin(rebin)
            self[jet][projname] = proj
            proj.SetLineColor(color)
            proj.Draw(same)
            legend.AddEntry(proj, legtitle, 'l')
            if proj.GetMaximum()>ymax:
                ymax = proj.GetMaximum()
            hists.append(proj)
            if same == '':
                same = 'same'
        def add_total(tot_name, to_be_added):
            self.add_jet(tot_name)
            self[tot_name][projname] = None
            for addname in to_be_added:
                # import pdb; pdb.set_trace()
                if not self[tot_name][projname]:               
                    self[tot_name][projname] = self[addname][projname].Clone()
                else: 
                    self[tot_name][projname].Add(self[addname][projname])
            # self[tot_name][projname].Draw('same')
            return self[tot_name][projname]
        ak12 = add_total('ak12', ['ak1','ak2'])
        rec12 = add_total('rec12', ['rec1','rec2'])
        # ak12.SetLineWidth(3)
        # rec12.SetLineWidth(3)
        hist = draw_hists(hists)
        hist.GetXaxis().SetRangeUser(xmin, xmax)
        hist.legend = legend
        legend.Draw('same')
        gPad.SaveAs('residuals_{imin}_{imax}.png'.format(imin=imin, imax=imax))

    def draw_residuals_sum(self, imin, imax, xmin, xmax):
        #import pdb; pdb.set_trace()
        projname = 'res_{imin}_{imax}'.format(imin=imin, imax=imax)
        ak12 = self['ak12'][projname]
        rec12 = self['rec12'][projname]
        ak12.SetLineColor(1)
        rec12.SetLineColor(4)
        hist = draw_hists([ak12, rec12])
        hist.GetXaxis().SetRangeUser(xmin, xmax)
        hist.legend = TLegend(0.55,0.7,0.89,0.89, '', 'NDC')
        hist.legend.AddEntry(ak12, 'antikt, both jets', 'l')
        hist.legend.AddEntry(rec12, 'gma, both jets', 'l')
        hist.legend.Draw('same')
        gPad.SaveAs('residuals_sum_{imin}_{imax}.png'.format(imin=imin, imax=imax))
        
        
plots = Plots()

def shs(name):
    gPad.Update()
    time.sleep( tsleep )
    gPad.SaveAs(name)

def draw(jet):
    plots.add_jet(jet)
    chain.Draw('{jet}_e/{jet}_gen_e:drgen>>h(12,0,3,200, 0, 3)'.format(jet=jet), 
               '', 'colz', nevents)
    plots.add_plot(jet, 'res_vs_dr', gDirectory.Get('h'))
    shs('res_vs_dr_{jet}.png'.format(jet=jet))
    chain.Draw('{jet}_e/{jet}_gen_e:drgen>>h(12,0,3)'.format(jet=jet), 
               '', 'prof', nevents)
    plots.add_plot(jet, 'res_vs_dr_profile', gDirectory.Get('h'))
    shs('res_vs_dr_profile_{jet}.png'.format(jet=jet))

nevents = 999999
tsleep = 0.1
    
draw('rec1')
draw('rec2')
draw('ak1')
draw('ak2')
plots.draw_profiles()
plots.draw_residuals(1,4,2,0,3)
plots.draw_residuals(9,12,1,0.7,1.4)
plots.draw_residuals_sum(1,4,0,3)
plots.draw_residuals_sum(9,12,0.7,1.4)
