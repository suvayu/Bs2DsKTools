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

# Python modules
import os
import sys
from datetime import datetime

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass

# RooFit classes
from ROOT import RooFit
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel

# my stuff
from factory import *
set_integrator_config()

epsilon = 2E-4
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this

def main(accfn='powerlaw', isToy=False):
    """Setup RooFit variables then construct the PDF as per options.

    Fit the model to a dataset. If toy generation is requested,
    generate toys from the model and use as dataset, otherwise read
    dataset from ntuple in data/smalltree.root.

    """

    # Observables
    time = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01+epsilon)
    time.setRange('fullrange', epsilon, 0.01+epsilon)
    # Limits determined from tree
    dt = RooRealVar('dt', 'Error in lifetime measurement (ns)', 1E-5, 9E-5)
    dt.setBins(100)

    # Parameters
    if not accfn.find('powerlaw') < 0:
        turnon = RooRealVar('turnon', 'turnon', 1500., 500., 5000.)
        exponent = RooRealVar('exponent', 'exponent', 2., 1., 5.)
        offset = RooRealVar('offset', 'offset', -0.2, -0.5, 0.1)
    elif accfn == 'arctan':
        # turnon has a different range as it is in the denominator
        turnon = RooRealVar('turnon', 'turnon', 1., 1E-3, 1.)
        offset = RooRealVar('offset', 'offset', 1E-3, 0, 5E-3)
    elif accfn == 'erf':
        # turnon has a different range as it is in the denominator
        turnon = RooRealVar('turnon', 'turnon', 1., 1E-4, 100.)
        offset = RooRealVar('offset', 'offset', 0., -1E-3, 1E-3)
    else:
        print 'Unknown acceptance type. Aborting'
        return

    # Temporary RooArgSet to circumvent scoping issues for nested
    # temporary objects.
    timeargset = RooArgSet(time)
    dtargset = RooArgSet(dt)

    # Resolution model
    mean = RooRealVar('mean', 'Mean', 0.)
    scale = RooRealVar('scale', 'Per-event time error scale factor', 1.)
    resmodel = RooGaussModel('resmodel', 'Time resolution model', time,
                             mean, scale, dt)
                             # RooRealConstant::value(0), scale, dt)
                             # RooRealConstant::value(0), scale,
                             # RooRealConstant::value(0.00004))

    # Decay model
    decayH = RooDecay('decayH', 'Decay function for the B_{s,H}',
                      time, RooRealConstant.value(1.536875/1E3),
                      resmodel, RooDecay.SingleSided)
    decayL = RooDecay('decayL', 'Decay function for the B_{s,L}',
                      time, RooRealConstant.value(1.407125/1E3),
                      resmodel, RooDecay.SingleSided)
    decay = RooAddPdf('decay', 'Decay function for the B_{s}',
                      decayH, decayL, RooRealConstant.value(0.5))

    # Acceptance model: 1-1/(1+(a*(t-t₀)³)
    # NB: Acceptance is not a PDF by nature
    # Other functional forms:
    # 1. no offset - (1.-1./(1.+(@0*@1)**@2)) with
    #    RooArgList(turnon, time, offset, exponent)
    # 2. Error function - 0.5*(TMath::Erf((@1-@2)/@0)+1) with
    #    RooArgList(turnon, time, offset)

    # Condition to ensure acceptance function is always +ve definite.
    # The first condition protects against the undefined nature of the
    # function for times less than 0. Whereas the second condition
    # ensures the 0.2 ps selection cut present in the sample is
    # incorporated into the model.

    if accfn == 'powerlaw':
        acc_cond = '((@1-@2)<0 || @1<0.0002)'
        expr = '(1.-1./(1.+(@0*(@1-@2))**3))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset))
    elif accfn == 'powerlaw2':
        acc_cond = '(((@0*@1)**3 - @2)<0 || @1<0.0002)'
        expr = '(1.-1./(1. + (@0*@1)**3 - @2))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset))
    elif accfn == 'powerlaw3':
        acc_cond = '(((@0*@1)**@3 - @2)<0 || @1<0.0002)'
        expr = '(1.-1./(1. + (@0*@1)**@3 - @2))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset, exponent))
    elif accfn == 'arctan':
        acc_cond = '(@0<0.0002)'
        expr = '(atan(@0*exp(@1*@0-@2)))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(time, turnon, offset))
    elif accfn == 'erf':
        acc_cond = '(@1<0.0002)'
        expr = '(0.5*(TMath::Erf((@1-@2)/@0)+1))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset))
    else:
        print 'Unknown acceptance type. Aborting'
        return

    # Define PDF and fit
    ModelL = RooEffProd('ModelL', 'Acceptance model B_{s,L}', decayL, acceptance)
    ModelH = RooEffProd('ModelH', 'Acceptance model B_{s,H}', decayH, acceptance)

    # Build full 2-D PDF (t, δt)
    argset = RooArgSet(time,dt)
    # Get tree
    rfile = get_file('data/smalltree-new-MC.root', 'read')
    ftree = get_object('ftree', rfile)

    # Trigger:
    # HLT2Topo4BodyTOS
    # HLT2Topo3BodyTOS
    # HLT2Topo2BodyTOS
    # HLT2TopoIncPhiTOS
    trigger = 'HLT2Topo3BodyTOS'
    triggerVar = RooRealVar(trigger, trigger, 0, 2)
    cut = trigger+'>0'
    try:
        dataset = get_dataset(argset, ftree, triggerVar, cut)
    except TypeError, IOError:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
    tmpdatahist = dataset.binnedClone('datahist','Binned data')
    datahist = tmpdatahist.reduce(dtargset)
    del tmpdatahist
    if isToy: del dataset

    errorPdf = RooHistPdf('errorPdf', 'Time error Hist PDF',
                           dtargset, datahist)
    modelargset = RooArgSet(ModelL)
    FullModelL = RooProdPdf('FullModelL', 'Acceptance model with errors B_{s,L}',
                            RooArgSet(errorPdf),
                            RooFit.Conditional(modelargset, timeargset))
    modelargset = RooArgSet(ModelH)
    FullModelH = RooProdPdf('FullModelH', 'Acceptance model with errors B_{s,H}',
                            RooArgSet(errorPdf),
                            RooFit.Conditional(modelargset, timeargset))
    PDF = RooAddPdf('FullModel', 'Acceptance model',
                    FullModelH, FullModelL, RooRealConstant.value(0.5))

    # Generate toy if requested
    if isToy:
        try:
            dataset = get_toy_dataset(argset, PDF)
        except TypeError, IOError:
            print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

    fitresult = PDF.fitTo(dataset, RooFit.Optimize(False),
                          RooFit.Strategy(2), RooFit.Save(True),
                          RooFit.NumCPU(2), RooFit.Verbose(True))

    # Fit results
    fitresult.Print()
    fcanvas = TCanvas('fcanvas', 'Fit canvas', 800, 600)
    fitplot = RooPlot(offset, turnon)
    fitresult.plotOn(fitplot, turnon, offset, 'MEA')
    fitplot.Draw()

    # RooFit.Range(0, 0.01+epsilon),
    tframe1 = time.frame(RooFit.Name('ptime'),
                         RooFit.Title('Projection on time'))
    dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
    PDF.plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
               RooFit.LineColor(kBlue))
    decay.plotOn(tframe1, RooFit.LineColor(kRed))
    acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                      RooFit.Normalization(1000, RooAbsReal.Relative))

    # NOTE: this range is for the RooPlot axis
    tframe2 = time.frame(RooFit.Range(0., 2E-3), RooFit.Name('pztime'),
                         RooFit.Title('Projection on time (zoomed)'))
    dataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp))
    PDF.plotOn(tframe2, RooFit.ProjWData(dtargset, dataset, True),
               RooFit.LineColor(kBlue))
    acceptance.plotOn(tframe2, RooFit.LineColor(kGreen),
                      RooFit.Normalization(300, RooAbsReal.Relative))

    canvas = TCanvas('canvas', 'canvas', 1600, 600)
    canvas.Divide(2,1)
    canvas.cd(1)
    tframe1.Draw()
    canvas.cd(2)
    tframe2.Draw()

    # Save plots and PDFs
    timestamp = get_timestamp()
    plotfile = 'plots/canvas-%s-%s.png' % (accfn, timestamp)
    rootfile = 'data/fitresult-%s-%s.root' % (accfn, timestamp)
    fitfile = 'plots/fitcanvas-%s-%s.png' % (accfn, timestamp)

    # Print plots
    canvas.Print(plotfile)
    fcanvas.Print(fitfile)

    # Persistify variables, PDFs and datasets
    save_in_workspace(rootfile, var=[time, dt, turnon, offset, exponent],
                      pdf=[PDF], data=[dataset], fit=[fitresult],
                      plots=[fitplot, tframe1, tframe2])


if __name__ == "__main__":
    main('powerlaw2', False)
