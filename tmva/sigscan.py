#!/usr/bin/env python
# coding=utf-8
"""Do a significance scan"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('rfile', metavar='file',
                       help='ROOT file with TMVA output')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       help='Run in batch mode')
optparser.add_argument('-c', dest='classifier', default='BDTB',
                       help='Classifier to plot')
options = optparser.parse_args()
locals().update(_import_args(options))

import sys
from fixes import ROOT
from ROOT import TFile
rfile = TFile.Open(rfile)
tree = rfile.Get('TestTree')

## significance, signal selection and background rejection efficiency
sig, bkg = 'classID=={}'.format(0), 'classID=={}'.format(1) # in TMVA
nbkg = float(tree.GetEntries(bkg))
nsig = float(tree.GetEntries(sig))

from utils import scan_range

nevts_passed = [
    lambda tree, cut: tree.GetEntries('{}&&{}'.format(sig, cut.greater)),
    lambda tree, cut: tree.GetEntries('{}&&{}'.format(bkg, cut.greater))
]

from numpy import linspace, array
cuts = linspace(-0.4, 0.4, 101)
res = array(scan_range(nevts_passed, cuts, 'BDTB', tree)) # sig, bkg

from math import sqrt
effs = [0, 1] + res / [nsig, -nbkg]
res /= [15.0, 1.0]              # FIXME: arbitrarily reduce signal / 15
sigs = res[:,0] / map(sqrt, res.sum(axis=1)) # σ = s/sqrt(s+b)
from numpy import isnan                      # clean NaNs
sigs = map(lambda i: 0 if isnan(i) else i, sigs)

## plot
from ROOT import TH1D, TProfile
nbins = 40
bins = linspace(-0.4, 0.4, nbins + 1)
hist_s = TProfile('hist_s', 'Signal selection efficiency', nbins, bins)
hist_b = TProfile('hist_b', 'Background rejection efficiency', nbins, bins)
hsigma = TProfile('hsigma', 'Significance', nbins, bins)

from utils import th1fill
eff_s, eff_b = effs[:,0], effs[:,1]
map(th1fill(hist_s, 2), cuts, eff_s)
map(th1fill(hist_b, 2), cuts, eff_b)
map(th1fill(hsigma, 2), cuts, sigs)

from ROOT import TCanvas, gPad, gStyle, kBlack, kAzure, kRed
c1 = TCanvas('c1', '', 800, 500)
hist_s.SetLineColor(kAzure)
hist_b.SetLineColor(kRed)
hsigma.SetLineColor(kBlack)

gStyle.SetOptStat(0)
hist_s.Draw('e1')
hist_b.Draw('e1 same')
rightmax = 1.1*hsigma.GetMaximum()
hsigma.Scale(gPad.GetUymax()/rightmax)
hsigma.Draw('e1 same')

from ROOT import TGaxis
axis = TGaxis(hsigma.GetXaxis().GetXmax(), hsigma.GetYaxis().GetXmin(),
              hsigma.GetXaxis().GetXmax(), hsigma.GetYaxis().GetXmax(),
              0, 19, 19 + 100*5, '+L')
axis.Draw()
c1.Update()
c1.Print('significance.pdf')
