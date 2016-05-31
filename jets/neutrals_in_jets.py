from cpyroot import *
from tdrstyle import tdrstyle
from ROOT import TFile, TH1F, TPaveText, TLine
import sys
import copy

infos = []

def print_jet_info(add_line1=None, add_line2=None, left=False):
    xmin = 0.62
    ymin = 0.58
    if left:
        xmin = 0.22
        ymin = 0.48
    xmax = xmin+0.288
    ymax = ymin+0.331
    jetinfo = TPaveText(xmin,ymin,xmax,ymax, 'ndc')
    jetinfo.AddText('Anti-k_{T}, R=0.4')
    jetinfo.AddText('|#eta^{Ref}|<1.3')
    # jetinfo.AddText('')
    if add_line1:
        jetinfo.AddText(add_line1)
    else:
        jetinfo.AddText('')
    if add_line2:
        jetinfo.AddText(add_line2)
    else:
        jetinfo.AddText('')        
    jetinfo.SetTextSizePixels(28)
    jetinfo.SetBorderSize(0)
    jetinfo.SetFillColor(0)
    jetinfo.SetFillStyle(0)
    jetinfo.Draw()
    infos.append(jetinfo) # necessary to save the pavetext... 

# setTDRStyle()

rootfile = TFile(sys.argv[1])
events = rootfile.Get('events')

gen_sel = '(jet1_gen_pt>50 && jet1_gen_pt<500 && abs(jet1_gen_eta)<1.3)'

n_for_frac = 10000

textScale = 1.2

nbins, xmin, xmax = 50, 0, 2.5

def make_residuals(pdgid, xtitle, jetline):
    hname = 'res_{pdgid}'.format(pdgid=pdgid)
    res = TH1F(hname, '', nbins, xmin, xmax)
    var = 'jet1_{pdgid}_pt/jet1_gen_{pdgid}_pt'.format(pdgid=pdgid)
    minfrac_sel = '(jet1_gen_{pdgid}_pt/jet1_gen_pt > 0.1)'.format(pdgid=pdgid)
    sel = ' && '.join([gen_sel, minfrac_sel])
    print 'var\t', var
    print 'sel\t', sel
    events.Project(hname, var, sel, "", n_for_frac)
    res.Draw()
    res.Scale(1/res.GetEntries())
    res.SetXTitle(xtitle)
    tdrstyle.cmsPrel(-1, 13., True, textScale=textScale)
    print_jet_info(jetline)
    gPad.Update()
    gPad.SaveAs(hname + '.pdf')
    return res 

residuals = dict()

c211 = TCanvas('c211')
residuals[211] = make_residuals(211,
                                '#Sigma p_{T,h^{#pm}} / #Sigma p_{T,h^{#pm}}^{Ref}',
                                '#Sigma p_{T,h^{#pm}}^{Ref}/ p_{T}^{Ref} > 0.1')

c130 = TCanvas('c130')
residuals[130] = make_residuals(130,
                                '#Sigma p_{T,h^{0}} / #Sigma p_{T,h^{0}}^{Ref}',
                                '#Sigma p_{T,h^{0}}^{Ref}/ p_{T}^{Ref} > 0.1')
    
c22 = TCanvas('c22')
residuals[22] = make_residuals( 22,
                                '#Sigma p_{T,#gamma} / #Sigma p_{T,#gamma}^{Ref}',
                                '#Sigma p_{T,#gamma}^{Ref}/ p_{T}^{Ref} > 0.1')


cneutral = TCanvas('cneutral')
hname = 'res_neutrals'
res = TH1F(hname, '', nbins, xmin, xmax)
var = '(jet1_22_pt+jet1_130_pt)/jet1_gen_130_pt'
minfrac_sel = '(jet1_gen_130_pt/jet1_gen_pt > 0.1)'
sel = ' && '.join([gen_sel, minfrac_sel])
print 'var\t', var
print 'sel\t', sel
events.Draw('>>nophotons', 'jet1_gen_22_num == 0.')
events.SetEventList(gDirectory.Get('nophotons'))
events.Project(hname, var, sel)
res.Draw()
res.Scale(1/res.GetEntries())
res.SetXTitle('(#Sigma p_{T,#gamma} + #Sigma p_{T,h^{0}}) / #Sigma p_{T,h^{0}}^{Ref}')
tdrstyle.cmsPrel(-1, 13., True, textScale=textScale)
print_jet_info('#Sigma p_{T,h^{0}}^{Ref}/ p_{T}^{Ref} > 0.1', '#Sigma p_{T, #gamma}^{Ref} = 0')
gPad.Update()
gPad.SaveAs(hname + '.pdf')

# cneutralprof = TCanvas('cneutralprof')
# neutralprof = TProfile('neutralprof','', 50, 0, 1)
# events.Project(neutralprof.GetName(), '(jet1_22_pt+jet1_130_pt)/jet1_pt:jet1_gen_130_pt/jet1_gen_pt', gen_sel, 'prof')
# neutralprof.SetXTitle('p_{T,h^{0}}^{Ref}/p_{T}^{Ref}')
# neutralprof.SetYTitle('(p_{T,#gamma} + p_{T,h^{0}}) / p_{T}')
# neutralprof.SetMarkerSize(1)
# neutralprof.Draw()
# line = TLine(0,0,1,1)
# line.SetLineStyle(7)
# line.Draw()
# tdrstyle.cmsPrel(-1, 13., True, textScale=textScale)
# print_jet_info('p_{T, #gamma}^{Ref} = 0', left=True)
# gPad.Update()
# gPad.SaveAs(neutralprof.GetName() + '.pdf')
