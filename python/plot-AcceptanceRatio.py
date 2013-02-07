#!/usr/bin/env python
# coding=utf-8
"""Plot acceptance ratio

"""

# Python modules
import os
import sys

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('file1', help='ROOT file with fit result')
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print plots to png/pdf files')

options = optparser.parse_args()
doPrint = options.doPrint

fname1 = options.file1

fname1tokens = fname1.split('-')
accfntype1 = fname1tokens[2]
mode1 = fname1tokens[1]
constoffset1 = fname1tokens[-1]

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
if doPrint: gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow, kCyan
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass, TLatex
from ROOT import TH1, TH1D, TH2D

# RooFit classes
from ROOT import RooPlot, RooWorkspace, RooFitResult, RooFit
from ROOT import RooArgSet, RooArgList

# my stuff
from factory import get_workspace, get_file, get_object, load_library

# Load custom ROOT classes
load_library('libacceptance.so')
from ROOT import PowLawAcceptance, AcceptanceRatio

# Files with fitresults:
# data/fitresult-DsK-ratio-*

# Get objects from workspace
workspace, ffile = get_workspace(fname1, 'workspace')
workspace.Print('v')

# variables
time = workspace.var('time')

# DsK acceptance function
ratio = workspace.function('ratio')
# acceptance_fn = workspace.function('acceptance_fn')
# DsK_acceptance = workspace.function('acceptance')
# DsK_acceptance.SetName('%s_%s' % ('DsK', DsK_acceptance.GetName()))

rturnon = workspace.var('rturnon')
roffset = workspace.var('roffset')
rbeta = workspace.var('rbeta')

fitresult = workspace.obj('fitresult_Model_dataset')

# ratio_hist = ratio.createHistogram('ratio_hist', time)
# ratio_hist.Draw()

tframe = time.frame(RooFit.Title('Time acceptance ratio'))

paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(tframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(tframe)

## Draw
# RooFit
tframe.Draw()

if doPrint:
    gPad.Print('plots/DsK_ratio.png')
    # gPad.Print('plots/DsK_ratio.pdf')

# NB: Do not close file, otherwise plot disappears
# ffile.Close()
