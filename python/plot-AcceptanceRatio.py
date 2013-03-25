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
optparser.add_argument('file', help='ROOT file with fit result')
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print plots to png/pdf files')
options = optparser.parse_args()
doPrint = options.doPrint
fname = options.file

epsilon = 0.2

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
from ROOT import RooArgSet, RooArgList, RooDataHist

# my stuff
from factory import get_workspace, get_file, get_object, load_library

# Load custom ROOT classes
load_library('libacceptance.so')
from ROOT import PowLawAcceptance, AcceptanceRatio


# Get objects from workspace
workspace, ffile = get_workspace(fname, 'workspace')
workspace.Print('v')

# Variables
time = workspace.var('time')

# DsK acceptance function
rturnon = workspace.var('rturnon')
roffset = workspace.var('roffset')
rbeta = workspace.var('rbeta')
ratio = workspace.function('ratio')
fitresult = workspace.obj('fitresult_PDF_dataset')

# Dataset
argset = RooArgSet(time)
decaycat = workspace.cat('decaycat')
decaycat.setRange('onlydspi', 'DsPi')
decaycat.setRange('onlydsk', 'DsK')

dataset = workspace.data('dataset')
# RooFit limits entry selection to variables specified in the argset
# passed to SelectVars.  Hence RooFit.SelectVars(argset) needs to be
# called separately on reduced dataset
dspi_data = dataset.reduce(RooFit.Name('dspi_data'),
                           RooFit.CutRange('onlydspi')).reduce(
                               RooFit.SelectVars(argset))
dsk_data = dataset.reduce(RooFit.Name('dsk_data'),
                          RooFit.CutRange('onlydsk')).reduce(
                              RooFit.SelectVars(argset))

print '=' * 5, ' Datasets retrieved ', '=' * 5
for dset in (dataset, dspi_data, dsk_data):
    dset.Print('v')

# histogram from dataset (FIXME:)
dspihist = TH1D('dspihist', 'Ds#pi decay time', 150, epsilon, 15.0)
dskhist = TH1D('dskhist', 'DsK decay time', 150, epsilon, 15.0)
ratiohist = TH1D('ratiohist', 'DsK/Ds#pi ratio', 150, epsilon, 15.0)

for hist in (dspihist, dskhist, ratiohist):
    hist.Sumw2()

dspihist = dspi_data.fillHistogram(dspihist, RooArgList(time))
dskhist = dsk_data.fillHistogram(dskhist, RooArgList(time))
ratiohist.Divide(dskhist, dspihist)

# FIXME: relative normalisation
time.setRange('fullrange', epsilon, 15.0)
fintegral = ratio.createIntegral(RooArgSet(time), 'fullrange').getVal()
hintegral = ratiohist.Integral()
norm = fintegral / hintegral
print '=' * 5, ' Integrals ', '=' * 5
print 'Function integral / histogram integral = %g / %g = %g' % (
    fintegral, hintegral, norm)
ratiohist.Scale(norm)

ratiodset = RooDataHist('ratiodset', '', RooArgList(time), ratiohist)
ratiodset.Print('v')

# TODO: variable binning (dynamic merge beyond 5ps) for long decay times

## Plot
tframe = time.frame(RooFit.Title('Time acceptance ratio'))
paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(tframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(tframe)
ratiodset.plotOn(tframe)

## Draw
tframe.Draw()

if doPrint:
    gPad.Print('plots/DsK_ratio.png')
    gPad.Print('plots/DsK_ratio.pdf')

# NB: Do not close file, otherwise plot disappears
# ffile.Close()
