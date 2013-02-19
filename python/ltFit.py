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
usage='Usage: $ %s [options]' % sys.argv[0]
description = ''
# description  = "<accfn> is Fit type to perform, cpowerlaw, ratio(default), etc.  "
# description += "<mode> is Bs decay mode, DsK (default) or DsPi."
parser = optparse.OptionParser(description=description, usage=usage)

parser.add_option('-s', '--save', action='store_true', default=False,
                  help='Save the fitresult in a ROOT file (default: False).')

# parser.add_option('accfn', default='ratio',
#                   help='Fit type to perform, cpowerlaw, ratio(default), etc.')
# parser.add_option('mode', default='DsK',
#                   help='Bs decay mode, DsK (default) or DsPi.')

options, args = parser.parse_args()
save = options.save
# fitresultfile = options.ref
# accfn = args[0]
# mode = args[1]

# # test program argument consistency
# if accfn == 'ratio' and fitresultfile == None:
#     sys.exit('Please provide a ROOT file with the fitresult from DsPi when fitting for acceptance ratio')


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
from ROOT import RooFit, RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList # containers
from ROOT import RooAbsReal, RooAbsPdf # abstract classes
# variables and pdfs
from ROOT import RooRealVar, RooRealConstant, RooFormulaVar, RooGaussian
from ROOT import RooEffProd, RooAddPdf, RooProdPdf, RooProduct # operations
from ROOT import RooDataSet, RooDataHist, RooHistPdf, RooKeysPdf # data
from ROOT import RooDecay, RooBDecay, RooGaussModel, RooUniformBinning # models
from ROOT import RooSimultaneous, RooCategory

## my stuff
from factory import *           # FIXME: clean up, do not use *
set_integrator_config()

# execfile('rootlogon.py')
# Load custom ROOT classes
load_library('libacceptance.so')
from ROOT import PowLawAcceptance, AcceptanceRatio

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


## Read dataset, apply trigger and decay mode selection
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

# Get dataset: DsPi and DsK
time.setBins(150)
dsetlist = []
for mode in [ 'DsPi', 'DsK' ]:
    # Get tree
    rfile = get_file('data/smalltree-new-MC-pico-offline-%s.root' % mode, 'read')
    ftree = get_object('ftree', rfile)
    print 'Reading from file: %s' % rfile.GetName()

    modeVar = RooRealVar('hID', 'Decay mode %s' % mode, -350, 350)
    if mode == 'DsK':
        cut += '&& abs(hID) == 321'
    elif mode == 'DsPi':
        cut += '&& abs(hID) == 211'

    try:
        dataset = get_dataset(RooArgSet(time), ftree, cut, modeVar, *triggerVars)
        dataset.SetName('%s_%s' % (dataset.GetName(), mode))
        dsetlist += [dataset]
    except TypeError, IOError:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

decaycat = RooCategory('decaycat', 'Decay mode category')
decaycat.defineType('DsPi')
decaycat.defineType('DsK')

dataset = RooDataSet('dataset', 'Combined dataset (DsK + DsPi)',
                     RooArgSet(time), RooFit.Index(decaycat),
                     RooFit.Import('DsPi', dsetlist[0]),
                     RooFit.Import('DsK', dsetlist[1]))


## Basic B decay pdf with time resolution
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

pdflist += [ Bdecay ]


## Acceptance model: 1-1/(1+(a*(t-t₀)³)
# NB: Acceptance is not a PDF by nature

# Condition to ensure acceptance function is always +ve definite.
# The first condition protects against the undefined nature of the
# function for times less than 0. Whereas the second condition
# ensures the 0.2 ps selection cut present in the sample is
# incorporated into the model.

# acceptance fn parameters: common to both DsK and Dsπ
turnon = RooRealVar('turnon', 'turnon', 1.5, 0.5, 5.0)
exponent = RooRealVar('exponent', 'exponent', 2., 1., 4.)
offset = RooRealVar('offset', 'offset', 0.0, -0.5, 0.5)
beta = RooRealVar('beta', 'beta', 0.04, 0.0, 0.05)


## Dsπ acceptance and pdf
dspi_acceptance = PowLawAcceptance('dspi_acceptance',
                                   'DsPi Power law acceptance',
                                   turnon, time, offset, exponent, beta)
DsPi_Model = RooEffProd('DsPi_Model', 'DsPi acceptance model B_{s}',
                        Bdecay, dspi_acceptance)

varlist += [ turnon, exponent, offset, beta ]
pdflist += [ dspi_acceptance, DsPi_Model ]

# fit to Dsπ only
print '=' * 5, ' 2-step fit: Dsπ ', '=' * 5
dspi_fitresult = DsPi_Model.fitTo(dsetlist[0], RooFit.Optimize(0),
                                  RooFit.Strategy(2), RooFit.Save(True),
                                  RooFit.NumCPU(1),
                                  RooFit.Verbose(True))
dspi_fitresult.Print()


## DsK acceptance and pdf
# ratio parameters: only for DsK
rturnon = RooRealVar('rturnon', 'rturnon', 6.4, 0.5, 10.0)
roffset = RooRealVar('roffset', 'roffset', 0.0, -0.5, 0.1)
# rbeta = RooRealVar('rbeta', 'rbeta', 0.0, -0.05, 0.05)
rbeta = RooRealConstant.value(0.0)

ratio = AcceptanceRatio('ratio', 'Acceptance ratio',
                        time, rturnon, roffset, rbeta)
# dsk_acceptance = RooProduct('dsk_acceptance', 'DsK Acceptance with ratio',
#                             RooArgList(dspi_acceptance, ratio))
dsk_acceptance = PowLawAcceptance(dspi_acceptance, 'dsk_acceptance', ratio)
DsK_Model = RooEffProd('DsK_Model', 'DsK acceptance model B_{s}',
                        Bdecay, dsk_acceptance)

varlist += [ rturnon, roffset, rbeta ]
pdflist += [ dsk_acceptance, DsK_Model ]

# fit to DsK only
turnon.setConstant(True)
exponent.setConstant(True)
offset.setConstant(True)
beta.setConstant(True)

print '=' * 5, ' 2-step fit: DsK ', '=' * 5
dsk_fitresult = DsK_Model.fitTo(dsetlist[1], RooFit.Optimize(0),
                                RooFit.Strategy(2), RooFit.Save(True),
                                RooFit.NumCPU(1),
                                RooFit.Verbose(True))
dsk_fitresult.Print()

# undo earlier set constant
turnon.setConstant(False)
exponent.setConstant(False)
offset.setConstant(False)
beta.setConstant(False)


## Build simultaneous 2-D PDF (t, δt) for DsPi and DsK
PDF = RooSimultaneous('PDF', 'Simultaneous PDF', decaycat)
PDF.addPdf(DsPi_Model, 'DsPi')
PDF.addPdf(DsK_Model, 'DsK')

pdflist += [ PDF ]

# #errorPdf = RooHistPdf('errorPdf', 'Time error Hist PDF',
# #                       RooArgSet(dt), datahist)
# errorPdf = RooKeysPdf('errorPdf', 'errorPdf', dt, tmpdata)

# PDF = RooProdPdf('PDF', 'Acceptance model with errors B_{s}',
#                    RooArgSet(errorPdf),
#                    RooFit.Conditional(RooArgSet(Model), RooArgSet(time)))
# # enable caching for dt integral
# PDF.setParameterizeIntegral(RooArgSet(dt))


## Logging
print '=' * 5, ' Simultaneous fit with initial values from 2-step fit', '=' * 5
print 'Variables: ', varlist
for var in varlist:
    var.Print('v')
print 'PDFs: ', pdflist
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
dkcatset = RooArgSet(decaycat)
tframe1 = time.frame(RooFit.Name('ptime'),
                     RooFit.Title('Projection on time'))
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe1, RooFit.Slice(decaycat, 'DsPi'),
           RooFit.ProjWData(dkcatset, dataset, True),
           RooFit.LineColor(kBlue))
PDF.plotOn(tframe1, RooFit.Slice(decaycat, 'DsK'),
           RooFit.ProjWData(dkcatset, dataset, True),
           RooFit.LineColor(kBlue+2))
Bdecay.plotOn(tframe1, RooFit.LineColor(kRed))
dspi_acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                       RooFit.Normalization(500, RooAbsReal.Relative))
dsk_acceptance.plotOn(tframe1, RooFit.LineColor(kGreen+2),
                      RooFit.Normalization(500, RooAbsReal.Relative))

# NOTE: this range is for the RooPlot axis
tframe2 = time.frame(RooFit.Range(0., 2), RooFit.Name('zptime'),
                     RooFit.Title('Projection on time (zoomed)'))
dataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe2, RooFit.Slice(decaycat, 'DsPi'),
           RooFit.ProjWData(dkcatset, dataset, True),
           RooFit.LineColor(kBlue))
PDF.plotOn(tframe2, RooFit.Slice(decaycat, 'DsK'),
           RooFit.ProjWData(dkcatset, dataset, True),
           RooFit.LineColor(kBlue+2))
dspi_acceptance.plotOn(tframe2, RooFit.LineColor(kGreen),
                       RooFit.Normalization(100, RooAbsReal.Relative))
dsk_acceptance.plotOn(tframe2, RooFit.LineColor(kGreen+2),
                      RooFit.Normalization(100, RooAbsReal.Relative))

canvas = TCanvas('canvas', 'canvas', 1600, 600)
canvas.Divide(2,1)
canvas.cd(1)
tframe1.Draw()
canvas.cd(2)
tframe2.Draw()

# Save plots and PDFs
timestamp = get_timestamp()
plotfile = 'plots/canvas-cpowerlaw-w-ratio-%s.png' % timestamp
rootfile = 'data/fitresult-cpowerlaw-w-ratio-%s.root' % timestamp

# Print plots
canvas.Print(plotfile)
print 'Plotting to file: %s' % plotfile

if save:
    hfile = TFile(rootfile, 'recreate')
    # Persistify variables, PDFs and datasets
    save_in_workspace(hfile, var=varlist, pdf=[PDF], data=[dataset],
                      fit=[fitresult], plots=[tframe1, tframe2])
