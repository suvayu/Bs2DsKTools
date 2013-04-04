#!/usr/bin/env python
# coding=utf-8
"""Plot acceptance ratio

"""

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('file', help='ROOT file with fit result')
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print plots to png/pdf files')
options = optparser.parse_args()
doPrint = options.doPrint
fname = options.file

# Python modules
import os
import sys
import math
import numpy

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
if doPrint: gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow, kCyan
from ROOT import kFullTriangleUp, kOpenTriangleDown, kFullDotMedium

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


## Read everything from file
# Get objects from workspace
workspace, ffile = get_workspace(fname, 'workspace')
workspace.Print('v')

# Variables
time = workspace.var('time')
# time range
tmin = time.getMin()
tmax = time.getMax()
time.setRange('fullrange', tmin, tmax)
nbins = time.getBins()

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


## Finer bins for small decay times (requested by Eduardo)
finebins = numpy.array([0.2 + i*0.05 for i in range(0, 17)])
zdspihist = TH1D('zdspihist', 'Ds#pi decay time', len(finebins) - 1, finebins)
zdskhist = TH1D('zdskhist', 'DsK decay time', len(finebins) - 1, finebins)
zratiohist = TH1D('zratiohist', 'DsK/Ds#pi ratio', len(finebins) - 1, finebins)

for hist in (zdspihist, zdskhist, zratiohist):
    hist.Sumw2()

zdspihist = dspi_data.fillHistogram(zdspihist, RooArgList(time))
zdskhist = dsk_data.fillHistogram(zdskhist, RooArgList(time))
zratiohist.Divide(zdskhist, zdspihist)

print
print '=' * 5, ' Bin contents w/ errors for bins 1-3 ', '=' * 5
print '|{0: >10s}|{1: >10s}|{2: >10s}|{3: >10s}|{4: >10s}|{5: >10s}|'.format(
    'DsK', 'DsK err', 'DsPi', 'DsPi err', 'ratio', 'ratio err')
print '|' + '+'.join(['-'*10 for i in range(6)]) + '|'
for i in range(1,4):
    print '|{0: > .3e}|{1: > .3e}|{2: > .3e}|{3: > .3e}|{4: > .3e}|{5: > .3e}|'.format(
        zdskhist.GetBinContent(i), zdskhist.GetBinError(i),
        zdspihist.GetBinContent(i), zdspihist.GetBinError(i),
        zratiohist.GetBinContent(i), zratiohist.GetBinError(i))
print

# relative normalisation
time.setRange('zoom', tmin, 1.0)
fintegral = ratio.createIntegral(RooArgSet(time), 'zoom').getVal()
hintegral = zratiohist.Integral('width') # has weights, use width
print hintegral
norm = fintegral / hintegral
print '=' * 5, ' Integrals (zoomed) ', '=' * 5
print 'Function integral / histogram integral = %g / %g = %g' % (
    fintegral, hintegral, norm)
zratiohist.Scale(norm)

# make dataset from histogram
zratiodset = RooDataHist('zratiodset', '', RooArgList(time), zratiohist)
zratiodset.Print('v')

ztframe = time.frame(RooFit.Title('Time acceptance ratio 0.2-1.0 ps'),
                    RooFit.Range('zoom'))
paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(ztframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(ztframe)
zratiodset.plotOn(ztframe, RooFit.MarkerStyle(kFullDotMedium))
ztframe.Draw()
gPad.Update()

# Print
if doPrint:
    gPad.Print('plots/DsK_ratio_zoomed.png')

# NB: Do not close file, otherwise plot disappears
# ffile.Close()
