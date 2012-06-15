#!/usr/bin/env python
# coding=utf-8
"""
Fit it for lifetime acceptance in Monte Carlo.

@author Suvayu Ali

"""

## Python modules
import os
import sys
import argparse

# option parsing
optparser = argparse.ArgumentParser(description='Lifetime acceptance')
optparser.add_argument('--accfn', default='powerlaw',
                       help='Acceptance funtion to use (default: powerlaw)')
optparser.add_argument('--print', dest='doPrint', type=bool, default=False)
optparser.add_argument('--toy', dest='isToy', type=bool, default=False)

options = optparser.parse_args()
accfn = options.accfn
doPrint = options.doPrint
isToy = options.isToy

# Math
from math import *
import numpy

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
# gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem
# gStyle.SetOptStat(0)

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass, TH1F

# RooFit classes
from ROOT import RooFit, RooGlobalFunc, RooFitResult
from ROOT import RooPlot, RooWorkspace, RooBinning
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian, RooUniform
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel

# my stuff
from factory import *

set_integrator_config()

# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this
epsilon = 2E-4

# Observables
time = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01+epsilon)
time.setRange('fullrange', epsilon, 0.01+epsilon)
# Limits determined from tree
dt = RooRealVar('dt', 'Error in lifetime measurement (ns)', 1E-5, 9E-5)
dt.setBins(100)

# Temporary RooArgSet to circumvent scoping issues for nested
# temporary objects.
timeargset = RooArgSet(time)
dtargset = RooArgSet(dt)

# Parameters
if accfn == 'powerlaw':
    turnon = RooRealVar('turnon', 'turnon', 1500., 500., 5000.)
    offset = RooRealVar('offset', 'offset', 0., -1E-3, 1E-3)
elif accfn == 'arctan':
    # turnon has a different range as it is in the denominator
    turnon = RooRealVar('turnon', 'turnon', 1., 1E-3, 1.)
    offset = RooRealVar('offset', 'offset', 1E-3, 0, 5E-3)
elif accfn == 'erf':
    # turnon has a different range as it is in the denominator
    turnon = RooRealVar('turnon', 'turnon', 1., 1E-4, 10.)
    offset = RooRealVar('offset', 'offset', 0., -1E-3, 1E-3)
else:
    print 'Unknown acceptance type. Aborting'
    assert(False)

# Resolution model
mean = RooRealVar('mean', 'Mean', 0.)
scale = RooRealVar('scale', 'Per-event time error scale factor', 1.)
resmodel = RooGaussModel('resmodel', 'Time resolution model', time,
                         mean, scale, dt)

# Decay model
decayH = RooDecay('decayH', 'Decay function for the B_{s,H}',
                  time, RooRealConstant.value(1.536875/1E3),
                  resmodel, RooDecay.SingleSided)
decayL = RooDecay('decayL', 'Decay function for the B_{s,L}',
                  time, RooRealConstant.value(1.407125/1E3),
                  resmodel, RooDecay.SingleSided)
decay = RooAddPdf('decay', 'Decay function for the B_{s}',
                  decayH, decayL, RooRealConstant.value(0.5))
decayargset = RooArgSet(decay)

# Get tree
rfile = get_file('data/smalltree-new-MC.root', 'read')
ftree = get_object('ftree', rfile)

# dt dataset for denom
trigger = 'HLT2Topo3BodyTOS'
triggerVar = RooRealVar(trigger, trigger, 0, 2)
cut = trigger+'>0'
tmpdtdataset = RooDataSet('dtdataset', 'dt dataset', RooArgSet(dt, triggerVar),
                            RooFit.Import(ftree), RooFit.Cut(cut))
dtdatahist = tmpdtdataset.binnedClone('dtdatahist', 'Binned dt')
dtdatahist = dtdatahist.reduce(dtargset)
errorPdf = RooHistPdf('errorPdf', 'Time error Hist PDF', dtargset, dtdatahist)

decaywdt = RooProdPdf('decaywdt', 'Decay function with dt distribution',
                      RooArgSet(errorPdf),
                      RooFit.Conditional(decayargset, timeargset))

del tmpdtdataset, dtdatahist

# Variable width binning
nbins1 = 50
nbins2 = 24
binedges1 = numpy.zeros(nbins1+1 , dtype=float)
binedges2 = numpy.zeros(nbins2+1 , dtype=float)
logwidth = log10((1E-2 + 2E-4) / 2E-4)

for i in range(nbins1+1):
    # binedges1[i] = 10**(log10(2E-4) + i*logwidth/nbins1)
    binedges1[i] = epsilon + i*1E-2/nbins1
    # print '%2d: %e' % (i, binedges1[i])

for i in range(nbins2+1):
    if i <= 15:
        binedges2[i] = epsilon + i*2E-4
    elif i <= 19:
        binedges2[i] = binedges2[15] + (i - 15)*5E-4
    else:
        binedges2[i] = binedges2[19] + (i - 19)*1E-3

# uniformbins = RooBinning(nbins1, binedges, 'uniformbins')

# Decay binned
decayfn = decaywdt.asTF(RooArgList(time), RooArgList(), timeargset)
# decayhist = decay.createHistogram('decayhist', time,
#                                   RooFit.Binning(uniformbins),
#                                   RooFit.ConditionalObservables(dtargset))
# decayhist.Sumw2()

# timehist = decayhist.Clone('timehist')
# timehist.Reset("ICESM")
timehist = TH1F('timehist', 'Lifetime distribution', nbins1, binedges1)
timehist.Sumw2()
timehist.SetLineColor(kAzure)

canvas1 = TCanvas('canvas1', 'Lifetime', 800, 600)
# canvas1.Divide(2, 1)
# canvas1.cd(1)

fname = 'plots/simple-%s-multi-page-%s.pdf' % (accfn, get_timestamp())
canvas1.Print(fname + '[')
ftree.Draw('time>>timehist', '(HLT2Topo3BodyTOS)', 'e1')
canvas1.Print(fname)
decayfn.Draw()
canvas1.Print(fname)

timehist2 = timehist.Clone('timehist2')
timehist2.SetLineColor(kRed)
# timehist.Divide(decayhist)
# timehist2 = timehist2.Rebin(nbins2, '', binedges2)
timehist2.Divide(decayfn)

# timehist.Draw('e1')
# canvas1.cd(2)
# decayfn.Draw()
# timehist2.Draw('e1 sames')
timehist2.Draw('e1')
canvas1.Print(fname)
# canvas1.Update()

# FIXME: Issues:
# 1. Normalisation of the decay PDF: What to normalise to, how?
# 2. How to get binned decay pdf to divide? createHistogram(..) gives
#    a histogram with one entry in each bin. The errors get screwed up.
# 3. How to get variable binning (wider bins for longer lifetimes)? 

## Acceptance
# Note: Using a PDF to represent an acceptance is not rigorously
# correct, but it is acceptable in this context since we only want to
# determine the shape, which is to be later included in the PDF for
# the fit as a function.
if accfn == 'powerlaw':
    # Condition to ensure acceptance function is always +ve definite.
    # The first condition protects against the undefined nature of the
    # function for times less than 0. Whereas the second condition
    # ensures the 0.2 ps selection cut present in the sample is
    # incorporated into the model.
    acc_cond = '((@1-@2)<0 || @1<0.0002)'
    expr = '(1.-1./(1.+(@0*(@1-@2))**3))'
    PDF = RooGenericPdf('PDF', '%s ? 0 : %s' % (acc_cond, expr),
                               RooArgList(turnon, time, offset))
elif accfn == 'arctan':
    acc_cond = '(@0<0.0002)'
    expr = '(atan(@0*exp(@1*@0-@2)))'
    PDF = RooGenericPdf('PDF', '%s ? 0 : %s' % (acc_cond, expr),
                               RooArgList(time, turnon, offset))
elif accfn == 'erf':
    acc_cond = '(@1<0.0002)'
    expr = '(0.5*(TMath::Erf((@1-@2)/@0)+1))'
    PDF = RooGenericPdf('PDF', '%s ? 0 : %s' % (acc_cond, expr),
                               RooArgList(turnon, time, offset))
else:
    print 'Unknown acceptance type. Aborting'
    assert(False)

# Dataset to fit to
datahist = RooDataHist('datahist', 'Dataset from a histogram',
                       RooArgList(time), RooFit.Import(timehist2, False))
# Debug
datahist.Print('v')

# Fit
PDF.fitTo(datahist, RooFit.SumW2Error(True), RooFit.NumCPU(1),
          RooFit.Range(epsilon, 0.005),
          RooFit.Optimize(False), RooFit.Verbose(True), RooFit.Strategy(2))

# Plot
tframe1 = time.frame(RooFit.Name('ptime'),
                     RooFit.Title('Lifetime acceptance fitted to %s' % accfn))
datahist.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe1, RooFit.LineColor(kGreen))

# canvas2 = TCanvas('canvas2', 'Acceptance', 800, 600)
tframe1.Draw()
canvas1.Print(fname)
canvas1.Print(fname + ']')

# timestamp = get_timestamp()
# canvas1.Print('plots/simple-distrib-%s.pdf' % timestamp)
# canvas2.Print('plots/simple-fit-%s-%s.pdf' % (accfn, timestamp))
