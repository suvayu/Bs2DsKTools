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


## Finer bins for small decay times (requested by Eduardo)
finebins = numpy.array([0.2 + i*0.05 for i in range(0, 17)])
z1dspihist = TH1D('z1dspihist', 'Ds#pi decay time', len(finebins) - 1, finebins)
z1dskhist = TH1D('z1dskhist', 'DsK decay time', len(finebins) - 1, finebins)
z1ratiohist = TH1D('z1ratiohist', 'DsK/Ds#pi ratio', len(finebins) - 1, finebins)

for hist in (z1dspihist, z1dskhist, z1ratiohist):
    hist.Sumw2()

z1dspihist = dspi_data.fillHistogram(z1dspihist, RooArgList(time))
z1dskhist = dsk_data.fillHistogram(z1dskhist, RooArgList(time))
z1ratiohist.Divide(z1dskhist, z1dspihist)

finebins = numpy.array([0.2 + i*0.025 for i in range(0, 33)])
z2dspihist = TH1D('z2dspihist', 'Ds#pi decay time', len(finebins) - 1, finebins)
z2dskhist = TH1D('z2dskhist', 'DsK decay time', len(finebins) - 1, finebins)
z2ratiohist = TH1D('z2ratiohist', 'DsK/Ds#pi ratio', len(finebins) - 1, finebins)

for hist in (z2dspihist, z2dskhist, z2ratiohist):
    hist.Sumw2()

z2dspihist = dspi_data.fillHistogram(z2dspihist, RooArgList(time))
z2dskhist = dsk_data.fillHistogram(z2dskhist, RooArgList(time))
z2ratiohist.Divide(z2dskhist, z2dspihist)

# # debug error calculation
# print
# print '=' * 5, ' Bin contents w/ errors for bins 1-3 ', '=' * 5
# print '|{0: >10s}|{1: >10s}|{2: >10s}|{3: >10s}|{4: >10s}|{5: >10s}|'.format(
#     'DsK', 'DsK err', 'DsPi', 'DsPi err', 'ratio', 'ratio err')
# print '|' + '+'.join(['-'*10 for i in range(6)]) + '|'
# for i in range(1,4):
#     print '|{0: > .3e}|{1: > .3e}|{2: > .3e}|{3: > .3e}|{4: > .3e}|{5: > .3e}|'.format(
#         z1dskhist.GetBinContent(i), z1dskhist.GetBinError(i),
#         z1dspihist.GetBinContent(i), z1dspihist.GetBinError(i),
#         z1ratiohist.GetBinContent(i), z1ratiohist.GetBinError(i))
# print

# relative normalisation
time.setRange('zoom', tmin, 1.0)
fintegral = ratio.createIntegral(RooArgSet(time), 'zoom').getVal()
hintegral = z1ratiohist.Integral('width') # has weights, use width
print hintegral
norm = fintegral / hintegral
print '=' * 5, ' Integrals (zoomed) ', '=' * 5
print 'Function integral / histogram integral = %g / %g = %g' % (
    fintegral, hintegral, norm)
z1ratiohist.Scale(norm)
hintegral = z2ratiohist.Integral('width') # has weights, use width
norm = fintegral / hintegral
z2ratiohist.Scale(norm)

# make dataset from histogram
z1ratiodset = RooDataHist('z1ratiodset', '', RooArgList(time), z1ratiohist)
z1ratiodset.Print('v')

z2ratiodset = RooDataHist('z2ratiodset', '', RooArgList(time), z2ratiohist)
z2ratiodset.Print('v')

z1tframe = time.frame(RooFit.Title('Time acceptance ratio 0.2-1.0 ps'),
                      RooFit.Range('zoom'))
paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(z1tframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(z1tframe)
z1ratiodset.plotOn(z1tframe, RooFit.MarkerStyle(kFullDotMedium))
z1tframe.Draw()
gPad.Update()

# Print
if doPrint:
    gPad.Print('plots/DsK_ratio_zoomed1.png')
    gPad.Print('plots/DsK_ratio_zoomed1.pdf')

z2tframe = time.frame(RooFit.Title('Time acceptance ratio 0.2-1.0 ps'),
                      RooFit.Range('zoom'))
paramset = RooArgSet(rturnon, roffset, rbeta)
ratio.plotOn(z2tframe, RooFit.VisualizeError(fitresult, paramset, 1, False))
ratio.plotOn(z2tframe)
z2ratiodset.plotOn(z2tframe, RooFit.MarkerStyle(kFullDotMedium))
z2tframe.Draw()
gPad.Update()

# Print
if doPrint:
    print 'Plotting to file: plots/DsK_ratio_%s.{png,pdf}' % timestamp
    gPad.Print('plots/DsK_ratio_%s.png' % timestamp)
    gPad.Print('plots/DsK_ratio_%s.pdf' % timestamp)

# NB: Do not close file, otherwise plot disappears
# ffile.Close()
