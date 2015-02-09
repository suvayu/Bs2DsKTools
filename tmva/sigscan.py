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
    'BDTB': 'BDT cuts (w/ bagging)',
    'BDTG': 'BDT cuts (w/ gradient boost)',
    'BDTGResponse_1': 'Old BDT cuts (w/ gradient boost)'
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

from rplot.utils import th1fill
map(th1fill(hist_s, 2), cuts, eff_s)
map(th1fill(hist_b, 2), cuts, eff_b)
map(th1fill(hsigma, 2), cuts, sigs)
# map(th1fill(hagns, 2), cuts, agns)

import matplotlib as mpl
mpl.rc('font', family='Liberation Sans') # choose font
mpl.rc('mathtext', default='regular')    # use default font for math

if batch: mpl.use('pdf')    # plotting w/o X11
else: import matplotlib.pyplot as plt

# PDF backend
from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf
if doprint: pp = PdfPages('significance_{}.pdf'.format(classifier))

# use the API
from matplotlib.figure import Figure
from rplot.r2mpl import th12errorbar

fig = Figure()
canvas = FigureCanvasPdf(fig)
axes = fig.add_subplot(111)
if eff and sig:
    axes.set_title('Efficiency & significance')
else:
    axes.set_title('Efficiency' if eff else 'Significance')
axes.grid()
axes.set_xlabel(cltitle[classifier])
axes.set_xlim(clrange[0], clrange[1])
axes.set_ylabel('Efficiency' if eff else 'Significance')
if eff and sig:
    axes2 = axes.twinx()
    axes2.set_ylabel('Significance')

for hist in [hist_s, hist_b]:
    x, y, yerr = th12errorbar(hist, yerr=True)
    col = 'blue' if 'Signal' in hist.GetTitle() else 'red'
    axes.errorbar(x, y, yerr=yerr, xerr=None, fmt=None, ecolor=col,
                  label=hist.GetTitle())
x, y, yerr = th12errorbar(hsigma, yerr=True)
axes2.errorbar(x, y, yerr=yerr, xerr=None, fmt=None, ecolor='black',
               label=hist.GetTitle())

## annotations
if classifier == 'BDTGResponse_1':
    axes.plot([0.3, 0.3], [0, 1], color='black', linewidth=2)
    axes.text(0.35, 0.3, 'Old working pt ($\geq 0.3$)',
              bbox=dict(boxstyle='larrow', fc='white', ec='black'))
    oeff_s = hist_s.GetBinContent(hist_s.FindBin(0.3))
    axes.annotate('(0.3,{:.3f})'.format(oeff_s), xy=(0.3,oeff_s), xytext=(-0.1,0.75),
                  arrowprops=dict(facecolor='black', shrink=0.1, width=2,
                                  headwidth=5))
if classifier == 'BDTB':
    diff, idx = 1., None
    for i, eff in enumerate(eff_s):
        diff_t = abs(eff-0.842)     # eff_s @ old BDTG >= 0.3
        if diff > diff_t: diff, idx = diff_t, i
    axes.plot(clrange, [0.842, 0.842], color='black', linewidth=2)
    axes.annotate('Working pt @ old eff {}'.format((cuts[idx], 0.842)),
                  xy=(cuts[idx], 0.842), xytext=(0.0, 1.1), ha='right',
                  arrowprops=dict(facecolor='black', shrink=0.05,
                                  width=2, headwidth=5))

if doprint:
    pp.savefig(fig)
    pp.close()

if not batch:
    plt.show()
