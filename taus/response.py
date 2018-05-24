from cpyroot import *

f = TFile('forColin/tau_tree_ztt.root')
t = f.Get('tau_tree')

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


setAlias(t)

sel_gen = '(gen_pt>20 && abs(gen_eta)<1.4 && gen_11_num==0 && gen_13_num==0)'
sel_pf = 'pfdecaymode && gen_211_num==1'

t.SetMarkerStyle(8)
t.SetLineColor(2)
t.Draw('gen_pfjet_pt/gen_pt>>h(100,0,2)', sel_gen + ' && pfisolation<2. && ' + sel_pf, 'histnorm')
t.SetLineColor(4)
t.Draw('gen_pfjet_pt/gen_pt', sel_gen, 'histnormsame')
t.Draw('gen_pfjet_pt/gen_pt', sel_gen, 'histnormsame')
