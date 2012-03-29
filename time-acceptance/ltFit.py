#!/usr/bin/env python

"""
Use RooFit to fit for lifetime acceptance in Monte Carlo
"""

import sys
epsilon = sys.float_info.epsilon

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad
# RooFit utilities and ROOT basic types
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow, kFullTriangleUp
from ROOT import RooFit, RooGlobalFunc, RooPlot, RooWorkspace, RooFitResult
from ROOT import RooRealVar, RooRealConstant, RooFormulaVar, RooArgSet, RooArgList
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooDataSet
from ROOT import RooExponential, RooDecay, RooGaussModel, RooAbsReal

# Get tree
ffile           = TFile('smalltree.root', 'read')
ftree           = ffile.Get('ftree')

# # some RooFit foo for more stable integration
# RooAbsReal.defaultIntegratorConfig().method1D().setLabel("RooAdaptiveGaussKronrodIntegrator1D");
# RooAbsReal.defaultIntegratorConfig().getConfigSection("RooAdaptiveGaussKronrodIntegrator1D").setRealValue("maxSeg", 50);
# RooAbsReal.defaultIntegratorConfig().getConfigSection("RooAdaptiveGaussKronrodIntegrator1D").setCatLabel("method", "31Points");
# RooAbsReal.defaultIntegratorConfig().getConfigSection("RooIntegrator1D").setRealValue("maxSteps", 50);

# observables
time            = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01)
dt              = RooRealVar('dt', 'Error in lifetime measurement (ns)', epsilon, 1E-4) # limits determined from tree
dt.setBins(100)

# parameters
turnon          = RooRealVar('turnon', 'turnon'    , 500, 5000)
exponent        = RooRealVar('exponent', 'exponent', 2, 4)

# trigger
trigger         = 'HLT2Topo3BodyTOS'
triggerVar      = RooRealVar(trigger, trigger, 0, 2)

# dataset
cut             = trigger+'>0' # hack to avoid entries with negative errors
dataset         = RooDataSet('dataset', 'Dataset',
                             RooArgSet(time, dt, triggerVar),
                             RooFit.Import(ftree), RooFit.Cut(cut))

# weighted dataset
wt              = RooRealVar('wt', 'wt', 0, 1e5)
wdataset        = RooDataSet('wdataset', 'Weighted dataset',
                             RooArgSet(time, wt, triggerVar),
                             RooFit.WeightVar(wt), RooFit.Import(ftree),
                             RooFit.Cut(cut))

# # exponential decay
# decayH          = RooExponential('decayH', 'Decay function for the B_{s,H}',
#                                  time, RooRealConstant.value(-1E3/1.536875))
# decayL          = RooExponential('decayL', 'Decay function for the B_{s,L}',
#                                  time, RooRealConstant.value(-1E3/1.407125))
# decay           = RooAddPdf('decay', 'Decay function for the B_{s}',
#                             decayH, decayL, RooRealConstant.value(0.5))

# resolution model
scale           = RooRealVar('scale', 'Scale factor for lifetime per-event error', 1)
resmodel        = RooGaussModel('resmodel', 'Time resolution model', time,
                                RooRealConstant.value(0), scale, dt) # RooRealConstant.value(0.00004)) # 

# decay model
decayH          = RooDecay('decayH', 'Decay function for the B_{s,H}', time,
                           RooRealConstant.value(1.536875/1E3), resmodel,
                           RooDecay.SingleSided)
decayL          = RooDecay('decayL', 'Decay function for the B_{s,L}', time,
                           RooRealConstant.value(1.407125/1E3), resmodel,
                           RooDecay.SingleSided)
decay           = RooAddPdf('decay', 'Decay function for the B_{s}', decayH, decayL,
                            RooRealConstant.value(0.5))

# acceptance
acceptance      = RooFormulaVar('acceptance', '1-1/(1+(@0*@1)**@2)',
                                RooArgList(turnon, time, exponent))
acceptancePdf   = RooGenericPdf('acceptancePdf', '@0', RooArgList(acceptance))

# Define PDF and fit
Model           = RooEffProd('Model', 'Acceptance model', decay, acceptance)
Model.fitTo(dataset, RooFit.Range(epsilon, 0.01), RooFit.ConditionalObservables(RooArgSet(dt)))

tframe1         = time.frame(RooFit.Name('pfit'), RooFit.Title('Lifetime acceptance with Monte Carlo'))
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
Model  .plotOn(tframe1, RooFit.ProjWData(RooArgSet(dt), dataset, True), RooFit.LineColor(kBlue))

tframe2         = time.frame(RooFit.Name('pmodel'), RooFit.Title('a(t) = decay(t) #times acc(t)'))
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
canvas.Print(trigger+'_ltFit_py.png')
