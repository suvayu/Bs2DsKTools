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
timestamp = str(workspace.GetTitle())[19:]

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


## Dynamic bin merging
dspihist = TH1D('dspihist', 'Ds#pi decay time', nbins, tmin, tmax)
dskhist = TH1D('dskhist', 'DsK decay time', nbins, tmin, tmax)

for hist in (dspihist, dskhist):
    hist.Sumw2()

dspihist = dspi_data.fillHistogram(dspihist, RooArgList(time))
dskhist = dsk_data.fillHistogram(dskhist, RooArgList(time))

# old binning
obins = numpy.zeros(nbins, dtype=float)
dspihist.GetLowEdge(obins)

# bin content and bin error arrays
dspicons = numpy.zeros(nbins, dtype=float)
dspierrs = numpy.zeros(nbins, dtype=float)
dskcons = numpy.zeros(nbins, dtype=float)
dskerrs = numpy.zeros(nbins, dtype=float)

# fill arrays
for i in range(nbins):
    dspicons[i] = dspihist.GetBinContent(i + 1)
    dspierrs[i] = dspihist.GetBinContent(i + 1)
    dskcons[i] = dskhist.GetBinContent(i + 1)
    dskerrs[i] = dskhist.GetBinContent(i + 1)

# find new binning
newbinedges = [obins[0]]
# start from 2nd bin (i=1) because first bin is in the rising region
# and might have fewer entries
i = 1

## Bin merging algorithm:
# 1. if δ/n > 0.1
# 2. merge with next bin
# 3. recalculate δ(=√(n₁+n₂)) & n(=n₁+n₂)
# 4. if new δ/n > 0.1, repeat 2-3, else continue
while i < nbins:
    dspideln = dspierrs[i] / dspicons[i]
    dskdeln = dskerrs[i] / dskcons[i]
    if dspideln < 0.1 or dskdeln < 0.1:
        newbinedges += [obins[i]]
        i += 1
    else:
        dspicon = dspicons[i]
        dskcon = dskcons[i]
        n = 1                   # start merging bins
        while i + n < nbins:
            dspicon += dspicons[i + n]
            dskcon += dskcons[i + n]
            tdspideln = math.sqrt(dspicon) / dspicon
            tdskdeln = math.sqrt(dskcon) / dskcon
            if not (tdspideln < 0.1 or tdskdeln < 0.1):
                n += 1
            else:
                newbinedges += [obins[i + n]]
                break
        i += n

# new number of bins
oldnbins = nbins
nbins = len(newbinedges)

# add upper bin edge for last bin
newbinedges += [dspihist.GetBinLowEdge(oldnbins) + dspihist.GetBinWidth(oldnbins)]
newbins = numpy.array(newbinedges)
print '='*5, ' Dynamic bin merging summary ', '='*5
print '# of bins %d -> %d ' % (oldnbins, nbins)

# cleanup histograms for next step
dspihist.Delete()
dskhist.Delete()


## Get histogram from dataset
# instead of fiddling with TH1.Rebin(..) refill new histograms
dspihist = TH1D('dspihist', 'Ds#pi decay time', nbins, newbins)
dskhist = TH1D('dskhist', 'DsK decay time', nbins, newbins)
ratiohist = TH1D('ratiohist', 'DsK/Ds#pi ratio', nbins, newbins)

for hist in (dspihist, dskhist, ratiohist):
    hist.Sumw2()

dspihist = dspi_data.fillHistogram(dspihist, RooArgList(time))
dskhist = dsk_data.fillHistogram(dskhist, RooArgList(time))
ratiohist.Divide(dskhist, dspihist)

# relative normalisation
fintegral = ratio.createIntegral(RooArgSet(time), 'fullrange').getVal()
hintegral = ratiohist.Integral('width') # has weights, use width
norm = fintegral / hintegral
print '=' * 5, ' Integrals ', '=' * 5
print 'Function integral / histogram integral = %g / %g = %g' % (
    fintegral, hintegral, norm)
ratiohist.Scale(norm)

# make dataset from histogram
ratiodset = RooDataHist('ratiodset', '', RooArgList(time), ratiohist)
ratiodset.Print('v')


## Plot
tframe = time.frame(RooFit.Title('Time acceptance ratio'))
paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(tframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(tframe)
ratiodset.plotOn(tframe, RooFit.MarkerStyle(kFullDotMedium))

tframe.Draw()

# Print
if doPrint:
    print 'Plotting to file: plots/DsK_ratio_%s.{png,pdf}' % timestamp
    gPad.Print('plots/DsK_ratio_%s.png' % timestamp)
    gPad.Print('plots/DsK_ratio_%s.pdf' % timestamp)

# NB: Do not close file, otherwise plot disappears
# ffile.Close()
