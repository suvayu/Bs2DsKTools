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
tree = rfile.Get('DecayTree')

## significance, signal selection and background rejection efficiency
# sig, bkg = 'classID=={}'.format(0), 'classID=={}'.format(1) # TMVA
# nbkg = float(tree.GetEntries(bkg))
# nsig = float(tree.GetEntries(sig))

ispion = 'lab1_PIDK<-5'                                       # data
region1 = '5300<lab0_MM && lab0_MM<5445 && {}'.format(ispion) # ~ s + b(w/ π)
region2 = '5445<lab0_MM && lab0_MM<5800'                                      # ~ b
region3 = '5445<lab0_MM && lab0_MM<5800 && {}'.format(ispion)                 # ~ b(w/ π)
nregion1 = float(tree.GetEntries(region1))
nregion2 = float(tree.GetEntries(region2))
nregion3 = float(tree.GetEntries(region3))

def get_bkg(nevts2, lo=5300, mid=5445, up=5800):
    """n2 = (5800-5445)/(5800-5300) * b"""
    return nevts2 * float(up-lo)/float(up-mid)

def get_sig(nevts1, nevts3, lo=5300, mid=5445, up=5800):
    """n1 = (5445-5300)/(5800-5300) * b(w/ π) + s
       b(w/ π) = get_bkg(n3)
       n3 = n2 w/ π
    """
    return nevts1 - float(mid-lo)/float(up-lo) * get_bkg(nevts3)

from utils import scan_range

nevts_passed = [
    # lambda tree, cut: tree.GetEntries('{}&&{}'.format(sig, cut.greater)), # TMVA
    # lambda tree, cut: tree.GetEntries('{}&&{}'.format(bkg, cut.greater))
    lambda tree, cut: tree.GetEntries('{}&&{}'.format(region1, cut.greater)), # TMVA
    lambda tree, cut: tree.GetEntries('{}&&{}'.format(region2, cut.greater)),
    lambda tree, cut: tree.GetEntries('{}&&{}'.format(region3, cut.greater))
]

from numpy import linspace, array
cuts = linspace(-0.4, 0.4, 101)
res = array(scan_range(nevts_passed, cuts, 'BDTB', tree)) # sig, bkg
res1 = res[:,0]
res2 = res[:,1]
res3 = res[:,2]
evt_s = array(map(get_sig, res1, res3))
evt_b = array(map(get_bkg, res2))

from math import sqrt
from numpy import isnan                      # clean NaNs
# effs = [0, 1] + res / [nsig, -nbkg]
# res /= [15.0, 1.0]              # FIXME: arbitrarily reduce signal / 15
# sigs = res[:,0] / map(sqrt, res.sum(axis=1)) # σ = s/sqrt(s+b)
# sigs = map(lambda i: 0 if isnan(i) else i, sigs)
eff_s = evt_s / get_sig(nregion1, nregion3)
eff_b = 1 - evt_b / get_bkg(nregion2)
evt_s /= 16.0
sigs = evt_s / map(sqrt, evt_s + evt_b)
sigs = map(lambda i: 0 if isnan(i) else i, sigs)

## plot
from ROOT import TH1D, TProfile
nbins = 40
bins = linspace(-0.4, 0.4, nbins + 1)
hist_s = TProfile('hist_s', 'Signal selection efficiency', nbins, bins)
hist_b = TProfile('hist_b', 'Background rejection efficiency', nbins, bins)
hsigma = TProfile('hsigma', 'Significance', nbins, bins)

from utils import th1fill
# eff_s, eff_b = effs[:,0], effs[:,1]
map(th1fill(hist_s, 2), cuts, eff_s)
map(th1fill(hist_b, 2), cuts, eff_b)
map(th1fill(hsigma, 2), cuts, sigs)

from ROOT import TCanvas, gPad, gStyle, kBlack, kAzure, kRed
c1 = TCanvas('c1', '', 800, 500)
hist_s.SetLineColor(kAzure)
hist_b.SetLineColor(kRed)
hsigma.SetLineColor(kBlack)

gStyle.SetOptStat(0)
hist_s.SetTitle('Significance') # FIXME: plot in correct order instead
hist_s.SetXTitle('BDTB cuts')
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
