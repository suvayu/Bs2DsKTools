#!/usr/bin/env python
# coding=utf-8
"""Scan classifier cuts and evaluate efficiencies and significance

Different classifier cuts are scanned, and depending on options
efficiency and significances are evaluated at these cuts.

Classifier range:
- rest: (-1,1)
- BDT w/ bagging: (-0.4,0.4)

Features:
- Can run on normal ntuples, or TMVA output.

- When running on MC ntuples, calculating significance doesn't make
  sense (since no background) hence it is disabled.  In this case, the
  MVA training config is used to replicate the original signal cuts.

- When running on data ntuples, a heuristic scheme is used to estimate
  the number of signal and background events.

  This is an approximation, e.g. it assumes there are no signal events
  in the upper mass sideband, the background shape is assumed to be
  linear and flat (fitting and estimating the slope could be an
  improvement).  Of course the best course of action is to do a full
  mass-fit.

@author: Suvayu Ali
@email:  Suvayu dot Ali at cern dot ch

"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('rfile', metavar='file',
                       help='Input ROOT file')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       help='Run in batch mode')
optparser.add_argument('-c', dest='classifier', default='BDTB',
                       help='Classifier to plot')
optparser.add_argument('-w', dest='what', choices=['eff', 'sig', 'both'], default='both',
                       help='What to plot: efficiency, significance, both')
optparser.add_argument('-T', dest='istmva', action='store_true',
                       help='Using TMVA output as input file')
optparser.add_argument('-n', dest='tree', default='',
                       help='Tree name to use')
optparser.add_argument('-s', dest='session',
                       help='Mandatory TMVA session config when using MC '
                       '(significance calc not possible)')
optparser.add_argument('--conf', default='TMVA.conf',
                       help='TMVA configuration file')
options = optparser.parse_args()
locals().update(_import_args(options))

# what to calculate
eff = what in ['eff', 'both']   # efficiency
sig = what in ['sig', 'both']   # significance
mc = bool(session)
cltitle = {
    'BDTB': 'BDT (w/ bagging) cuts',
    'BDTG': 'BDT (w/ gradient boost) cuts',
    'BDTGResponse_1': 'Old BDT (w/ gradient boost) cuts'
}

# option consistency checks
errmsg = 'Incompatible options: {}.'
import sys
if session:
    if what == 'both':
        print 'Cannot calculate significance with MC, will calc only eff.'
    elif what == 'sig':
        sys.exit(errmsg.format('session and significance'))
    else:
        eff, sig = True, False

from fixes import ROOT
ROOT.gROOT.SetBatch(batch)

tree = tree if tree else 'TestTree' if istmva else 'DecayTree'
if istmva:             # TMVA output
    rfile = ROOT.TFile.Open(rfile, 'read')
    tree = rfile.Get(tree)
else:
    rfile = ROOT.TFile.Open(rfile, 'read')
    tree = rfile.Get(tree)

## sig, bkg, and other cuts
if istmva:
    sig, bkg = 'classID=={}'.format(0), 'classID=={}'.format(1) # TMVA
    nbkg = float(tree.GetEntries(bkg))
    nsig = float(tree.GetEntries(sig))
elif mc:
    from tmvaconfig import ConfigFile
    conf = ConfigFile(conf)
    if conf.read() > 0:
        session = conf.get_session_config(session)
    else:
        sys.exit('No sesions found!')
    sig = session.cut_sig
    nsig = float(tree.GetEntries(sig))
else:
    ispion = 'lab1_PIDK<-5'                                       # data
    region1 = '5300<lab0_MM && lab0_MM<5445 && {}'.format(ispion) # ~ s + b(w/ π)
    region2 = '5445<lab0_MM && lab0_MM<5800'                      # ~ b
    region3 = '5445<lab0_MM && lab0_MM<5800 && {}'.format(ispion) # ~ b(w/ π)
    nregion1 = float(tree.GetEntries(region1))
    nregion2 = float(tree.GetEntries(region2))
    nregion3 = float(tree.GetEntries(region3))

# signal and background estimates from data
def get_bkg(nevts2, lo=5300, mid=5445, up=5800):
    """n2 = (5800-5445)/(5800-5300) * b"""
    return nevts2 * float(up-lo)/float(up-mid)

def get_sig(nevts1, nevts3, lo=5300, mid=5445, up=5800):
    """n1 = (5445-5300)/(5800-5300) * b(w/ π) + s
       b(w/ π) = get_bkg(n3)
       n3 = n2 w/ π
    """
    return nevts1 - float(mid-lo)/float(up-lo) * get_bkg(nevts3)

nevts_passed = []
if istmva:
    nevts_passed += [
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(sig, cut.greaterequal)),
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(bkg, cut.greaterequal))
    ]
elif mc:
    nevts_passed += [
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(sig, cut.greaterequal))
    ]
else:
    nevts_passed += [
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(region1, cut.greaterequal)),
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(region2, cut.greaterequal)),
        lambda tree, cut: tree.GetEntries('{}&&{}'.format(region3, cut.greaterequal))
    ]

from numpy import linspace, array
if classifier == 'BDTB':
    clrange = (-0.3, 0.3)
else:
    clrange = (-1.0, 1.0)
cuts = linspace(clrange[0], clrange[1], 101)

## significance, signal selection and background rejection efficiency
from utils import scan_range
res = array(scan_range(nevts_passed, cuts, classifier, tree))

from math import sqrt
if istmva:
    if eff:
        effs = [0, 1] + res / [nsig, -nbkg] # sel_s/tot_s, 1-sel_b/tot_s
        eff_s, eff_b = effs[:,0], effs[:,1]

    if sig:
        res /= [16.0, 1.0]                           # Dsπ/DsK ~ 16
        sigs = res[:,0] / map(sqrt, res.sum(axis=1)) # σ = s/sqrt(s+b)
elif mc:
    effs = res/nsig
else:
    # approximate signal and backround events
    res1 = res[:,0]
    res2 = res[:,1]
    res3 = res[:,2]
    evt_s = array(map(get_sig, res1, res3))
    evt_b = array(map(get_bkg, res2))

    if eff:
        eff_s = evt_s / get_sig(nregion1, nregion3)
        eff_b = 1 - evt_b / get_bkg(nregion2)

    if sig:
        evt_s /= 16.0
        sigs = evt_s / map(sqrt, evt_s + evt_b)
        # agns = eff_s * evt_s / (evt_s + evt_b) # FIXME: requires eff_s

from numpy import isnan                      # clean NaNs
sigs = map(lambda i: 0 if isnan(i) else i, sigs)
# agns = map(lambda i: 0 if isnan(i) else i, agns)

## plot
from ROOT import TH1D, TProfile
nbins = 40
bins = linspace(clrange[0], clrange[1], nbins + 1)
hist_s = TProfile('hist_s', 'Signal selection efficiency', nbins, bins)
hist_b = TProfile('hist_b', 'Background rejection efficiency', nbins, bins)
hsigma = TProfile('hsigma', 'Significance', nbins, bins)
# hagns  = TProfile('hagns', '#epsilon_{s}*purity = s/(s+b)', nbins, bins)

from utils import th1fill
map(th1fill(hist_s, 2), cuts, eff_s)
map(th1fill(hist_b, 2), cuts, eff_b)
map(th1fill(hsigma, 2), cuts, sigs)
# map(th1fill(hagns, 2), cuts, agns)

from ROOT import TCanvas, gPad, gStyle
from ROOT import kBlack, kViolet, kAzure, kRed
c1 = TCanvas('c1', '', 800, 500)
hist_s.SetLineColor(kAzure)
hist_b.SetLineColor(kRed)
hsigma.SetLineColor(kBlack)
# hagns.SetLineColor(kViolet)

gStyle.SetOptStat(0)
# hist_s.SetTitle('Significance') # FIXME: plot in correct order instead
hist_s.SetXTitle(cltitle[classifier])
hist_s.SetYTitle('Efficiency')
hist_s.Draw('e1')
hist_b.Draw('e1 same')
# print hist_s.GetYmax(), hagns.GetYmax()
# scale = hist_s.GetYmax()/hagns.GetYmax()
# hagns.Scale(scale)
# hagns.Draw('e1 same')
# print hist_s.GetYmax(), hsigma.GetYmax()
# scale = hist_s.GetYmax()/hsigma.GetYmax()
# hsigma.Scale(scale)
# hsigma.Draw('e1 same')

from ROOT import TGaxis
eaxis = TGaxis(hsigma.GetXaxis().GetXmin(), 0.962,
               hsigma.GetXaxis().GetXmax(), 0.962,
               0, 0, 0, 'U')
eaxis.Draw()

diff, idx = 1., None
for i, eff in enumerate(eff_s):
    diff_t = abs(eff-0.962)
    if diff > diff_t: diff, idx = diff_t, i

caxis = TGaxis(cuts[idx], 0, cuts[idx], 1.05, 0, 0, 0, 'U')
caxis.Draw()
c1.Update()

if doprint: c1.Print('significance_{}.pdf'.format(classifier))
