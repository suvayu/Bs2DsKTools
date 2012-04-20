#!/usr/bin/env python
# coding=utf-8

"""
Use RooFit to fit for lifetime acceptance in Monte Carlo
"""

import sys
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this
epsilon = 1E-6

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad
# RooFit utilities and ROOT basic types
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow, kFullTriangleUp
# ROOT global variables
from ROOT import gSystem, gROOT, gStyle, gPad
from ROOT import RooFit, RooGlobalFunc, RooPlot, RooWorkspace, RooFitResult
from ROOT import RooRealVar, RooRealConstant, RooFormulaVar, RooArgSet, RooArgList
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist, RooGaussian
from ROOT import RooExponential, RooDecay, RooGaussModel

# setup
gROOT.SetBatch(True)

# Get tree
ffile           = TFile('../data/smalltree.root', 'read')
ftree           = ffile.Get('ftree')

# observables
time            = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01)
dt              = RooRealVar('dt', 'Error in lifetime measurement (ns)',
                             epsilon, 1E-4) # limits determined from tree
dt.setBins(100)

# temporary RooArgSet with dt to circumvent scoping issues for nested
# temporary obejcts
dtargset          = RooArgSet(dt)

# parameters
turnon          = RooRealVar('turnon', 'turnon'    , 500, 5000)
exponent        = RooRealVar('exponent', 'exponent', 2, 4)

# trigger:
# HLT2Topo4BodyTOS
# HLT2Topo3BodyTOS
# HLT2Topo2BodyTOS
# HLT2TopoIncPhiTOS
trigger         = 'HLT2Topo3BodyTOS'
triggerVar      = RooRealVar(trigger, trigger, 0, 2)

# dataset
cut             = trigger+'>0' # hack to avoid entries with negative errors
dataset         = RooDataSet('dataset', 'Dataset',
                             # RooArgSet(time, dt, triggerVar),
                             RooArgSet(time, triggerVar),
                             RooFit.Import(ftree), RooFit.Cut(cut))

gaussian1       = RooGaussian('gaussian1', 'Gaussian 1', dt,
                              RooRealConstant.value(4E-5),
                              RooRealConstant.value(2E-5))
gaussian2       = RooGaussian('gaussian2', 'Gaussian 2', dt,
                              RooRealConstant.value(4E-5),
                              RooRealConstant.value(1E-5))
gaussian        = RooAddPdf('gaussian', 'Double gaussian', gaussian1, gaussian2,
                            RooRealConstant.value(0.5))
dtdataset       = gaussian.generate(dtargset, RooFit.Name('dtdataset'),
                                    RooFit.NumEvents(dataset.numEntries()))

dataset.merge(dtdataset)

# debug
dataset.Print('v')
dtdataset.Print('v')

# weighted dataset
wt              = RooRealVar('wt', 'wt', 0, 1e5)
wdataset        = RooDataSet('wdataset', 'Weighted dataset',
                             RooArgSet(time, wt, triggerVar),
                             RooFit.WeightVar(wt), RooFit.Import(ftree),
                             RooFit.Cut(cut))

# resolution model
mean            = RooRealVar("mean", "Mean", 0)
scale           = RooRealVar('scale', 'Scale factor for lifetime per-event error', 1)
resmodel        = RooGaussModel('resmodel', 'Time resolution model', time,
                                mean, scale, dt)
			        # RooRealConstant::value(0), scale, dt)
			        # RooRealConstant::value(0), scale,
                                # RooRealConstant::value(0.00004))

# decay model
decayH          = RooDecay('decayH', 'Decay function for the B_{s,H}', time,
                           RooRealConstant.value(1.536875/1E3), resmodel,
                           RooDecay.SingleSided)
decayL          = RooDecay('decayL', 'Decay function for the B_{s,L}', time,
                           RooRealConstant.value(1.407125/1E3), resmodel,
                           RooDecay.SingleSided)
decay           = RooAddPdf('decay', 'Decay function for the B_{s}', decayH, decayL,
                            RooRealConstant.value(0.5))

# acceptance model: 1-1/(1+(at)³)
# NB: acceptance is not a PDF by nature
acceptance      = RooFormulaVar('acceptance', '1-1/(1+(@0*@1)**@2)',
                                RooArgList(turnon, time, exponent))
acceptancePdf   = RooGenericPdf('acceptancePdf', '@0', RooArgList(acceptance))

# Define PDF and fit
Model           = RooEffProd('Model', 'Acceptance model', decay, acceptance)

# debug
# assert False

Model.fitTo(dataset, # RooFit.Range(epsilon, 0.01), # cause of initial crashes
            RooFit.ConditionalObservables(dtargset),
            RooFit.NumCPU(2), RooFit.Optimize(True)) #, RooFit.Verbose(True))

tframe1         = time.frame(RooFit.Name('pfit'),
                             RooFit.Title('Lifetime acceptance with Monte Carlo'))
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
Model  .plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
               RooFit.LineColor(kBlue))

# # testing
# decay  .plotOn(tframe1, RooFit.LineColor(kRed))
# acceptancePdf.plotOn(tframe1, RooFit.LineColor(kGreen))

# canvas          = TCanvas('canvas', 'canvas', 480, 400)
# tframe1.Draw()
# canvas.Print('../plots/canvas.png')

tframe2         = time.frame(RooFit.Name('pmodel'),
                             RooFit.Title('a(t) = decay(t) #times acc(t)'))
wdataset     .plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp))
decay        .plotOn(tframe2, RooFit.LineColor(kRed))
Model        .plotOn(tframe2, RooFit.LineColor(kAzure))
acceptancePdf.plotOn(tframe2, RooFit.LineColor(kGreen))

canvas          = TCanvas('canvas', 'canvas', 960, 400)
canvas .Divide(2,1)
canvas .cd(1)
tframe1.Draw()
canvas .cd(2)
tframe2.Draw()
canvas.Print('../plots/'+trigger+'_ltFit_py.png')
canvas.Print('../plots/'+trigger+'_ltFit_py.pdf')
