from cpyroot import officialStyle, Style, sBlack

from ROOT import TTree, TFile, TH2F, TH1F, TH1, TCanvas, TLegend, gStyle, gPad, gDirectory, TGraph, TMarker
import copy
import numpy as np

nev_qcd = int(1e5)
recptcut = 20.

qcd_file = TFile('QCD_d0df026/qcd/Colin.TauTuple.analyzers.TauTreeProducer.TauTreeProducer_pf/tau_tree.root')
qcd = qcd_file.Get('tau_tree')

dy_file = TFile('tau_tree_ztt.root')
dy = dy_file.Get('tau_tree')

officialStyle(gStyle)

def setAlias(tree):
    # fix old name in signal samples to match new name in qcd sample
    leaves = [leave.GetName() for leave in tree.GetListOfLeaves()]
    if leaves[0].startswith('gentau_'):
        for leave in leaves:
            tree.SetAlias(leave.replace('gentau','gen'), leave)
    tree.SetAlias('pfisocharged', 'gen_pf_hpsPFTauMVA3IsolationChargedIsoPtSum')
    tree.SetAlias('pfisoneutral', 'gen_pf_hpsPFTauMVA3IsolationNeutralIsoPtSum')
    tree.SetAlias('pfdecaymode', 'gen_pf_hpsPFTauDiscriminationByDecayModeFindingOldDMs>0.5')
    tree.SetAlias('pfisolation', 'gen_pf_isolation*(pfdecaymode) + 9999999*(!pfdecaymode)')
    
setAlias(dy)
setAlias(qcd)
          
sel_gen = '(gen_pt>20 && abs(gen_eta)<1.4 && gen_11_num==0 && gen_13_num==0)'

qcd.SetEventList(None)
dy.SetEventList(None)

qcd.Draw('>>qcd_gen_list', sel_gen, '', nev_qcd)
qcd_n_gen = qcd.GetSelectedRows()
qcd_gen_list = gDirectory.Get('qcd_gen_list')
qcd.SetEventList(qcd_gen_list)

dy.Draw('>>dy_gen_list', sel_gen)
dy_n_gen = dy.GetSelectedRows()
dy_gen_list = gDirectory.Get('dy_gen_list')
dy.SetEventList( dy_gen_list )

sel_pf = 'gen_pf_pt>{recptcut} && pfdecaymode'.format(recptcut=recptcut)

qcd.Draw('>>qcd_gen_pf_list', ' && '.join( [sel_gen, sel_pf]))
qcd_n_gen_pf = qcd.GetSelectedRows()
qcd.SetEventList(gDirectory.Get('qcd_gen_pf_list'))

dy.Draw('>>dy_gen_pf_list', sel_pf)
dy_n_gen_pf = dy.GetSelectedRows()
dy.SetEventList(gDirectory.Get('dy_gen_pf_list'))

sel_calo = 'gen_calo_caloRecoTauDiscriminationByLeadingTrackFinding>0.5 && gen_calo_caloRecoTauDiscriminationByLeadingTrackPtCut>0.5 && gen_calo_caloRecoTauDiscriminationByTrackIsolation>0.5 && gen_calo_caloRecoTauDiscriminationByECALIsolation>0.5 && (gen_calo_nsigcharged==1||gen_calo_nsigcharged==3) && abs(gen_calo_q)==1 && gen_calo_pt>{recptcut}'.format(recptcut=recptcut)

h_qcd = TH1F("h_qcd", "QCD", 5000, 0, 500)
h_dy = TH1F("h_dy", "Z#rightarrow#tau#tau", 5000, 0, 500)

# qcd.Draw('pfisolation>>h_qcd', '&&'.join([sel_gen, sel_pf]), '')
# dy.Draw('pfisolation>>h_dy', '&&'.join([sel_gen, sel_pf]), '')

qcd.Draw('pfisolation>>h_qcd')
dy.Draw('pfisolation>>h_dy')

h_qcd.Scale(1./qcd_n_gen)
h_dy.Scale(1./dy_n_gen)

h_dy.Draw()
h_qcd.Draw('same')

class ROC(object):
    def __init__(self, hx, hy):
        self.hx = hx
        self.hy = hy
        self.effx = np.array(self.efficiencies(self.hx))
        self.effy = np.array(self.efficiencies(self.hy))
        self.curve = TGraph(len(self.effx), self.effx, self.effy)
        self.h2d = TH2F('h2d', '', 10000, 0, 1, 100, 0, 1)
        self.h2d.GetXaxis().SetTitle(self.hx.GetTitle())
        self.h2d.GetYaxis().SetTitle(self.hy.GetTitle())
        sBlack.formatHisto(self.h2d)

    def efficiency(self, hist, ibin):
        if ibin<1 or ibin > hist.GetXaxis().GetNbins():
            assert(false)
        return hist.Integral(1, ibin)

    def efficiencies(self, hist):
        effs = []
        for ibin in range(1, hist.GetXaxis().GetNbins()):
            effs.append( self.efficiency(hist, ibin))
        return effs

    def draw(self):
        self.h2d.Draw()
        self.curve.Draw('same')
    
roc = ROC(h_qcd, h_dy)
roc.draw()
gPad.SetLogx()
        
qcd.SetEventList(qcd_gen_list)
dy.SetEventList(dy_gen_list)
qcd.Draw('>>qcd_gen_calo_list', sel_calo)
qcd_n_gen_calo = qcd.GetSelectedRows()
dy.Draw('>>dy_gen_calo_list', sel_calo)
dy_n_gen_calo = dy.GetSelectedRows()

marker = TMarker(
    float(qcd_n_gen_calo)/qcd_n_gen,
    float(dy_n_gen_calo)/dy_n_gen,
    21
    )
marker.Draw('same')

# read = True
# if read:
#     in_file = TFile('roc.root')
#     other_curve = in_file.Get('roc')
#     other_curve.SetLineColor(4)
#     other_curve.Draw('same')
#     other_marker = in_file.Get('calo')
#     other_marker.SetMarkerColor(4)
#     other_marker.Draw('same')
# else: 
#     out_file = TFile('roc.root', 'recreate')
#     roc.curve.Write('roc')
#     marker.Write('calo')
#     out_file.Close()
