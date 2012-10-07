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
gSystem.Load('libRooFit')

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
from ROOT import RooDataSet, RooDataHist, RooKeysPdf
from ROOT import RooDecay, RooBDecay, RooGaussModel, RooUniformBinning

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

epsilon = 0.2
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this


# Physics constants
# FIXME: check if the definitions are correct.  For now does not
# matter as symmetric
tauH = 1.536875
tauL = 1.407125
gammaH = 1.0/tauH
gammaL = 1.0/tauL
gamma = (gammaH + gammaL) / 2.0
tau = 1.0 / gamma
dgamma = gammaH - gammaL


def main(accfn='powerlaw', mode='DsK', fsuffix='', constoffset=False, isToy=False):
    """Setup RooFit variables then construct the PDF as per options.

    Fit the model to a dataset. If toy generation is requested,
    generate toys from the model and use as dataset, otherwise read
    dataset from ntuple in data/smalltree.root.

    """

    # for persistency/logging
    varlist = []
    pdflist = []
    print 'Fitting with constant offset set to: %d' % constoffset

    # Observables
    time = RooRealVar('time', 'B_{s} lifetime in ps', epsilon, 15.0)
    # # Limits determined from tree
    # dt = RooRealVar('dt', 'Error in lifetime measurement (ps)', 1E-2, 9E-2)
    # dt.setBins(100)             # default binning (since empty name)
    # # cache binning
    # dt.setBins(100, 'cache')

    varlist += [ time ]

    # Parameters
    if not accfn.find('powerlaw') < 0:
        turnon = RooRealVar('turnon', 'turnon', 1.5, 0.5, 5.0)
        exponent = RooRealVar('exponent', 'exponent', 2., 1., 4.)
        if constoffset:
            offset = RooRealVar('offset', 'offset', 0.0)
        else:
            offset = RooRealVar('offset', 'offset', 0.0, -0.5, 0.5)
        beta = RooRealVar('beta', 'beta', 0.04, 0.00, 0.05)
        varlist += [ turnon, exponent, offset, beta ]
    elif accfn == 'bdpt':
        beta = RooRealVar('beta', 'beta', 0.04, 0.01, 0.07)
        slope = RooRealVar('slope', 'slope', 1.1, 0.1, 2.0)
        offset = RooRealVar('offset', 'offset', 0.15, 0.0, 0.3)
        varlist += [ beta, slope, offset ]
    elif accfn == 'arctan':
        # here onwards, param ranges are such that time is in ns
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

    pdflist += [acceptance]

    # Build full 2-D PDF (t, δt)
    argset = RooArgSet(time)
    # Get tree
    rfile = get_file('data/smalltree-new-MC%s.root' % fsuffix, 'read')
    ftree = get_object('ftree', rfile)
    print 'Reading from file: %s' % rfile.GetName()

    # Trigger:
    # HLT1TrackAllL0TOS
    # HLT2Topo4BodyTOS
    # HLT2Topo3BodyTOS
    # HLT2Topo2BodyTOS
    # HLT2TopoIncPhiTOS
    trigger1 = 'HLT1TrackAllL0TOS'
    trigger1Var = RooRealVar(trigger1, trigger1, 0, 2)
    trigger2 = 'HLT2Topo2BodyTOS'
    trigger2Var = RooRealVar(trigger2, trigger2, 0, 2)
    trigger3 = 'HLT2Topo3BodyTOS'
    trigger3Var = RooRealVar(trigger3, trigger3, 0, 2)
    trigger4 = 'HLT2Topo4BodyTOS'
    trigger4Var = RooRealVar(trigger4, trigger4, 0, 2)

    cut = '(%s > 0) && (%s > 0 || %s > 0 || %s > 0)' % (trigger1, trigger2, trigger3, trigger4)

    modeVar = RooRealVar('hID', 'Decay mode %s' % mode, -350, 350)
    if mode == 'DsK':
        cut += '&& abs(hID) == 321'
    elif mode == 'DsPi':
        cut += '&& abs(hID) == 211'
    else:                       # don't mix modes anymore
        print 'Unrecognised mode: %s. Aborting.' % mode
        return

    time.setBins(150)
    try:
        dataset = get_dataset(RooArgSet(time), ftree, cut, modeVar, trigger1Var,
                              trigger2Var, trigger3Var, trigger4Var)
    except TypeError, IOError:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
    if isToy: del dataset
    datahist = dataset.binnedClone('datahist')
    hist = datahist.createHistogram('time')

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

    # Generate toy if requested
    if isToy:
        try:
            dataset = get_toy_dataset(argset, PDF)
        except TypeError, IOError:
            print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

    # Logging
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


if __name__ == "__main__":

    if len(sys.argv) > 1:
        fn = sys.argv[1]
        mode = sys.argv[2]
        fsuffix = sys.argv[3]
        if sys.argv[4] == '1':
            constoffset = True
        else:
            constoffset = False
    else:
        fn = 'cpowerlaw'
        mode = 'DsK'
        fsuffix = ''
        constoffset = False

    main(fn, mode, fsuffix, constoffset, False)
