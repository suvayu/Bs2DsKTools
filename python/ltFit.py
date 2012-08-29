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

# execfile('rootlogon.py')
# Load custom ROOT classes
loadstatus = { 0: 'loaded',
               1: 'already loaded',
               -1: 'does not exist',
               -2: 'version mismatch' }

library = 'libacceptance.so'
status = gSystem.Load(library)
if status < 0: sys.exit('Problem loading %s, %s' % (library, loadstatus[status]) )
from ROOT import PowLawAcceptance, BdPTAcceptance #, ErfAcceptance

epsilon = 2E-4
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this

def main(accfn='powerlaw', mode='DsK', fsuffix='', isToy=False):
    """Setup RooFit variables then construct the PDF as per options.

    Fit the model to a dataset. If toy generation is requested,
    generate toys from the model and use as dataset, otherwise read
    dataset from ntuple in data/smalltree.root.

    """

    # for persistency
    varlist = []

    # Observables
    time = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01+epsilon)
    time.setRange('fullrange', epsilon, 0.01+epsilon)
    # Limits determined from tree
    dt = RooRealVar('dt', 'Error in lifetime measurement (ns)', 1E-5, 9E-5)
    dt.setBins(100)

    varlist += [ time, dt ]

    # Parameters
    if not accfn.find('powerlaw') < 0:
        turnon = RooRealVar('turnon', 'turnon', 1500., 500., 5000.)
        exponent = RooRealVar('exponent', 'exponent', 2., 1., 4.)
        offset = RooRealVar('offset', 'offset', 0.0, -0.2, 0.1)
        beta = RooRealVar('beta', 'beta', 50, 0.0, 100)
        varlist += [ turnon, exponent, offset, beta ]
    elif accfn == 'bdpt':
        beta = RooRealVar('beta', 'beta', 40.0, 10.0, 70.0)
        slope = RooRealVar('slope', 'slope', 1100, 100.0, 2000.0)
        offset = RooRealVar('offset', 'offset', 1.5E-4, 0.0, 3E-4)
        varlist += [ beta, slope, offset ]
    elif accfn == 'arctan':
        # turnon has a different range as it is in the denominator
        turnon = RooRealVar('turnon', 'turnon', 1., 1E-3, 1.)
        offset = RooRealVar('offset', 'offset', 1E-3, 0, 5E-3)
        varlist += [ turnon, offset ]
    elif accfn == 'erf':
        # turnon has a different range as it is in the denominator
        turnon = RooRealVar('turnon', 'turnon', 1., 1E-4, 100.)
        offset = RooRealVar('offset', 'offset', 0., -1E-3, 1E-3)
        varlist += [ turnon, offset ]
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
        expr = '(1.-1./(1. + (@0*@1)**2.75 - @2))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset))
    elif accfn == 'powerlaw3':
        acc_cond = '(((@0*@1)**@3 - @2)<0 || @1<0.0002)'
        expr = '(1.-1./(1. + (@0*@1)**@3 - @2))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset, exponent))
    elif accfn == 'powerlaw4':
        acc_cond = '(((@0*@1)**@3 - @2)<0 || @1<0.0002)'
        expr = '((1.-1./(1. + (@0*@1)**@3 - @2))*(1 - @4*@1))'
        acceptance = RooFormulaVar('acceptance', '%s ? 0 : %s' % (acc_cond, expr),
                                   RooArgList(turnon, time, offset, exponent, beta))
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
    elif accfn == 'cpowerlaw':
        acceptance = PowLawAcceptance('acceptance',  'Power law acceptance',
                                      turnon, time, offset, exponent, beta)
    elif accfn == 'bdpt':
        acceptance = BdPTAcceptance('acceptance',  'Bd PT acceptance',
                                    time, beta, slope, offset)
    else:
        print 'Unknown acceptance type. Aborting'
        return

    # Define PDF and fit
    ModelL = RooEffProd('ModelL', 'Acceptance model B_{s,L}', decayL, acceptance)
    ModelH = RooEffProd('ModelH', 'Acceptance model B_{s,H}', decayH, acceptance)

    # Build full 2-D PDF (t, δt)
    argset = RooArgSet(time,dt)
    # Get tree
    rfile = get_file('data/smalltree-new-MC%s.root' % fsuffix, 'read')
    ftree = get_object('ftree', rfile)

    # Trigger:
    # HLT2Topo4BodyTOS
    # HLT2Topo3BodyTOS
    # HLT2Topo2BodyTOS
    # HLT2TopoIncPhiTOS
    trigger2 = 'HLT2Topo2BodyTOS'
    trigger2Var = RooRealVar(trigger2, trigger2, 0, 2)
    trigger3 = 'HLT2Topo3BodyTOS'
    trigger3Var = RooRealVar(trigger3, trigger3, 0, 2)
    trigger4 = 'HLT2Topo4BodyTOS'
    trigger4Var = RooRealVar(trigger4, trigger4, 0, 2)

    cut = '(%s > 0 || %s > 0 || %s > 0)' % (trigger2, trigger3, trigger4)

    modeVar = RooRealVar('hID', 'Decay mode %s' % mode, -350, 350)
    if mode == 'DsK':
        cut += '&& abs(hID) == 321'
    elif mode == 'DsPi':
        cut += '&& abs(hID) == 211'
    else:                       # don't mix modes anymore
        print 'Unrecognised mode: %s. Aborting.' % mode
        return

    try:
        dataset = get_dataset(argset, ftree, cut, modeVar, trigger2Var,
                              trigger3Var, trigger4Var)
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
    fitresult.Print()

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
    plotfile = 'plots/canvas-%s-%s-%s.png' % (mode, accfn, timestamp)
    rootfile = 'data/fitresult-%s-%s-%s.root' % (mode, accfn, timestamp)

    # Print plots
    canvas.Print(plotfile)

    # Persistify variables, PDFs and datasets
    save_in_workspace(rootfile, var=varlist, pdf=[PDF], data=[dataset],
                      fit=[fitresult], plots=[tframe1, tframe2])


if __name__ == "__main__":

    if len(sys.argv) > 1:
        fn = sys.argv[1]
        mode = sys.argv[2]
        fsuffix = sys.argv[3]
    else:
        fn = 'cpowerlaw'
        mode = 'DsK'
        fsuffix = ''

    main(fn, mode, fsuffix, False)
