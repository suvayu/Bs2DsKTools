#!/usr/bin/env python
# coding=utf-8
"""
Fit it for lifetime acceptance in Monte Carlo.

Builds a PDF with a Gaussian time resolution model. Trigger acceptance
is modelled as an efficiency function.

If fullPDF is True, constructs the full 2-dimensional PDF with
per-event time errors instead.

  1-D  PDF = decay(t|δt) × trigAcc(t)
  Full PDF = decay(t|δt) × trigAcc(t) × gaussian(δt)

where,

  decay(t|δt) = ∫̣δt exp(-t/τ) × gaussian(δt).

If isToy is True, toys are generated and the model is fit to it, data
is read from an ntuple and fitted to the model otherwise.

@author Suvayu Ali

"""


## Python modules
import os
import sys
from datetime import datetime

## Option parsing
import optparse
usage='usage: $ %s <accfn> <mode> [options]' % sys.argv[0]
description  = "<accfn> is Fit type to perform, cpowerlaw, ratio(default), etc.  "
description += "<mode> is Bs decay mode, DsK (default) or DsPi."
parser = optparse.OptionParser(description=description, usage=usage)

# helpstr = 'ROOT file with fitresult from Dsπ fit, needed only for ratio fit with DsK (default: None).'
parser.add_option('-r', '--ref', default=None,
                  help='ROOT file with fitresult from DsPi fit, needed only for ratio fit with DsK (default: None).')

# parser.add_option('accfn', default='ratio',
#                   help='Fit type to perform, cpowerlaw, ratio(default), etc.')
# parser.add_option('mode', default='DsK',
#                   help='Bs decay mode, DsK (default) or DsPi.')

options, args = parser.parse_args()
fitresultfile = options.ref
accfn = args[0]
mode = args[1]

# test program argument consistency
if accfn == 'ratio' and fitresultfile == None:
    sys.exit('Please provide a ROOT file with the fitresult from DsPi when fitting for acceptance ratio')

# legacy options
isToy=False
constoffset = False


## ROOT global variables
# FIXME: Batch running fails on importing anything but gROOT
from ROOT import gROOT
gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem
gSystem.Load('libRooFit')

## ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

## ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass

## RooFit classes
from ROOT import RooFit
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf, RooProduct
from ROOT import RooDataSet, RooDataHist, RooKeysPdf
from ROOT import RooDecay, RooBDecay, RooGaussModel, RooUniformBinning

## my stuff
from factory import *           # FIXME: clean up, do not use *
set_integrator_config()

from pdfhelpers import *


## Physics constants
# FIXME: check if the definitions are correct.  For now does not
# matter as symmetric
tauH = 1.536875
tauL = 1.407125
gammaH = 1.0/tauH
gammaL = 1.0/tauL
gamma = (gammaH + gammaL) / 2.0
tau = 1.0 / gamma
dgamma = gammaH - gammaL

epsilon = 0.2
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this

# for persistency/logging
varlist = []
pdflist = []
print 'Legacy: Fitting with constant offset set to %d' % constoffset


## Fit
# Setup RooFit variables then construct the PDF as per options.
# Fit the model to a dataset. If toy generation is requested,
# generate toys from the model and use as dataset, otherwise read
# dataset from ntuple in data/smalltree.root.


## Observables
time = RooRealVar('time', 'B_{s} lifetime in ps', epsilon, 15.0)
# # Limits determined from tree
# dt = RooRealVar('dt', 'Error in lifetime measurement (ps)', 1E-2, 9E-2)
# dt.setBins(100)             # default binning (since empty name)
# # cache binning
# dt.setBins(100, 'cache')

varlist += [ time ]

## Acceptance function
if accfn == 'cpowerlaw':
    acceptance = cpowerlaw_fn(time, varlist)
elif accfn == 'ratio':
    acceptance = cpowerlaw_ratio_fn(time, mode, fitresultfile, varlist)
else:
    sys.exit('Unknown acceptance type. Aborting')

pdflist += [acceptance]


## Read dataset, apply trigger and decay mode selection
# Get tree
rfile = get_file('data/smalltree-new-MC-pico-offline-%s.root' % mode, 'read')
ftree = get_object('ftree', rfile)
print 'Reading from file: %s' % rfile.GetName()

# Trigger:
tlist = [
    'HLT1TrackAllL0TOS',
    'HLT2Topo2BodyTOS',
    'HLT2Topo3BodyTOS',
    'HLT2Topo4BodyTOS'
]

triggerVars = []
for var in tlist:
    triggerVars += [RooRealVar(var, var, 0, 2)]

cut = '(%s > 0) && (%s > 0 || %s > 0 || %s > 0)' % (
    tlist[0], tlist[1], tlist[2], tlist[3])

# Mode: DsPi or DsK
modeVar = RooRealVar('hID', 'Decay mode %s' % mode, -350, 350)
if mode == 'DsK':
    cut += '&& abs(hID) == 321'
elif mode == 'DsPi':
    cut += '&& abs(hID) == 211'
else:                       # don't mix modes anymore
    sys.exit( 'Unrecognised mode: %s. Aborting.' % mode)

# Get dataset
time.setBins(150)
try:
    dataset = get_dataset(RooArgSet(time), ftree, cut, modeVar, *triggerVars)
except TypeError, IOError:
    print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
if isToy: del dataset
datahist = dataset.binnedClone('datahist')
hist = datahist.createHistogram('time')


## Build full 2-D PDF (t, δt)
# Resolution model
mean = RooRealVar('mean', 'Mean', 0.)
scale = RooRealVar('scale', 'Per-event time error scale factor', 1.19)
resmodel = RooGaussModel('resmodel', 'Time resolution model', time,
                         mean, RooRealConstant.value(0.044),
                         RooRealConstant.value(1.0),
                         RooRealConstant.value(1.0))
                         # RooRealConstant::value(0), scale, dt)
                         # RooRealConstant::value(0), scale,
                         # RooRealConstant::value(0.00004))
# Decay model
Bdecay = RooBDecay('Bdecay', 'Decay function for the B_{s} (heavy + light)',
                   time, RooRealConstant.value(tau), # t, τ
                   RooRealConstant.value(dgamma),    # ΔΓ
                   RooRealConstant.value(1.0),       # f0 - cosh
                   RooRealConstant.value(0.0),       # f1 - sinh
                   RooRealConstant.value(0.0),       # f2 - cos
                   RooRealConstant.value(0.0),       # f3 - sin
                   RooRealConstant.value(0.0),       # Δm
                   resmodel, RooBDecay.SingleSided)
Model = RooEffProd('Model', 'Acceptance model B_{s}', Bdecay, acceptance)
PDF = Model

pdflist += [Bdecay, Model]

# #errorPdf = RooHistPdf('errorPdf', 'Time error Hist PDF',
# #                       RooArgSet(dt), datahist)
# errorPdf = RooKeysPdf('errorPdf', 'errorPdf', dt, tmpdata)

# PDF = RooProdPdf('PDF', 'Acceptance model with errors B_{s}',
#                    RooArgSet(errorPdf),
#                    RooFit.Conditional(RooArgSet(Model), RooArgSet(time)))
# # enable caching for dt integral
# PDF.setParameterizeIntegral(RooArgSet(dt))


## Generate toy if requested
if isToy:
    try:
        dataset = get_toy_dataset(RooArgSet(time), PDF)
    except TypeError, IOError:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]


## Logging
for var in varlist:
    var.Print('v')
for pdf in pdflist:
    pdf.Print('v')
dataset.Print('v')

# # Call Minuit by hand, good for debugging
# from ROOT import RooMinuit
# nll = PDF.createNLL(dataset, RooFit.Optimize(0), RooFit.NumCPU(4))
# minuit = RooMinuit(nll)
# minuit.setEps(1e-7)
# minuit.setStrategy(2)
# minuit.setVerbose(True)
# minuit.hesse()
# # minuit.seek()
# minuit.hesse()
# minuit.migrad()
# minuit.hesse()
# fitresult = minuit.save()

# exponent.setConstant(True)
# beta.setConstant(True)
fitresult = PDF.fitTo(dataset, RooFit.Optimize(0),
                      RooFit.Strategy(2), RooFit.Save(True),
                      RooFit.NumCPU(1),
                      RooFit.Verbose(True))
fitresult.Print()


## Plot results
# # Use when debugging plots
# dataset = dataset.reduce(RooFit.EventRange(0, 100))

# reduce precision otherwise plotting doesn't work
time.setRange('fullrange', epsilon, 15.0)
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-5)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-5)

# RooFit.Range(0, 0.01+epsilon),
tframe1 = time.frame(RooFit.Name('ptime'),
                     RooFit.Title('Projection on time'))
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe1,
           # RooFit.ProjWData(RooArgSet(dt), dataset, True),
           RooFit.LineColor(kBlue))
Bdecay.plotOn(tframe1, RooFit.LineColor(kRed))
acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                  RooFit.Normalization(500, RooAbsReal.Relative))

# NOTE: this range is for the RooPlot axis
tframe2 = time.frame(RooFit.Range(0., 2), RooFit.Name('pztime'),
                     RooFit.Title('Projection on time (zoomed)'))
dataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe2,
           # RooFit.ProjWData(RooArgSet(dt), dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe2, RooFit.LineColor(kGreen),
                  RooFit.Normalization(100, RooAbsReal.Relative))

canvas = TCanvas('canvas', 'canvas', 1600, 600)
canvas.Divide(2,1)
canvas.cd(1)
tframe1.Draw()
canvas.cd(2)
tframe2.Draw()

# Save plots and PDFs
timestamp = get_timestamp()
plotfile = 'plots/canvas-%s-%s-%s-const-offset-%d.png' % (mode, accfn, timestamp, constoffset)
rootfile = 'data/fitresult-%s-%s-%s-const-offset-%d.root' % (mode, accfn, timestamp, constoffset)

# Print plots
canvas.Print(plotfile)
print 'Plotting to file: %s' % plotfile

hfile = TFile(rootfile, 'recreate')
# Persistify variables, PDFs and datasets
save_in_workspace(hfile, var=varlist, pdf=[PDF], data=[dataset],
                  fit=[fitresult], plots=[tframe1, tframe2])

hist.SetName('hdataset_%s' % mode)
# hist.SetDirectory(hfile)
# hfile.Write('', TFile.kOverwrite)
hfile.WriteTObject(hist)
hfile.Close()
