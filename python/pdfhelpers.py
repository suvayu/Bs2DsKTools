# coding=utf-8
"""This module provides various helper functions useful in building
PDFs.

@author Suvayu Ali

"""


## ROOT classes
from ROOT import TTree, TFile, TClass

## RooFit classes
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooEffProd, RooAddPdf, RooProdPdf, RooProduct
from ROOT import RooAbsPdf, RooGaussian, RooGenericPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist, RooKeysPdf
from ROOT import RooDecay, RooBDecay, RooGaussModel, RooUniformBinning

## my stuff
from factory import get_workspace, load_library

## Load custom ROOT classes
load_library('libacceptance.so')
from ROOT import PowLawAcceptance, AcceptanceRatio


# Acceptance model: 1-1/(1+(a*(t-t₀)³)
# NB: Acceptance is not a PDF by nature

# Condition to ensure acceptance function is always +ve definite.
# The first condition protects against the undefined nature of the
# function for times less than 0. Whereas the second condition
# ensures the 0.2 ps selection cut present in the sample is
# incorporated into the model.

def cpowerlaw_fn(time, varlist):
    """Return a configured PowLawAcceptance object."""

    # parameters
    turnon = RooRealVar('turnon', 'turnon', 1.5, 0.5, 5.0)
    exponent = RooRealVar('exponent', 'exponent', 2., 1., 4.)
    offset = RooRealVar('offset', 'offset', 0.0, -0.5, 0.5)
    beta = RooRealVar('beta', 'beta', 0.04, 0.00, 0.05)

    # acceptance
    acceptance = PowLawAcceptance('acceptance',  'Power law acceptance',
                                  turnon, time, offset, exponent, beta)
    varlist += [ turnon, exponent, offset, beta ]
    return acceptance


def cpowerlaw_ratio_fn(time, mode, fitresultfile, varlist):
    """Return a the product of PowLawAcceptance and AcceptanceRatioo."""

    # get parameters from Dsπ fit and fix them
    ws, ffile = get_workspace(fitresultfile, 'workspace')
    ws.SetNameTitle('%s_%s' % (mode, ws.GetName()), '%s %s' % (
        mode, ws.GetTitle()))
    turnon = RooRealConstant.value(ws.var('turnon').getValV())
    exponent = RooRealConstant.value(ws.var('exponent').getValV())
    offset = RooRealConstant.value(ws.var('offset').getValV())
    beta = RooRealConstant.value(ws.var('beta').getValV())
    ffile.Close()
    del ws, ffile

    # ratio parameters
    rnorm = RooRealVar('rnorm', 'rnorm', 1.3, 0.9, 2.0)
    rturnon = RooRealVar('rturnon', 'rturnon', 6.4, 0.5, 10.0)
    roffset = RooRealVar('roffset', 'roffset', 0.0, -0.5, 0.5)
    rbeta = RooRealVar('rbeta', 'rbeta', 0.01, -0.05, 0.05)

    # acceptance
    acceptance_fn = PowLawAcceptance('acceptance_fn', 'Power law acceptance',
                                     turnon, time, offset, exponent, beta)
    ratio = AcceptanceRatio('ratio', 'Acceptance ratio',
                            time, rnorm, rturnon, roffset, rbeta)
    acceptance = RooProduct('acceptance', 'Acceptance with ratio',
                            RooArgList(acceptance_fn, ratio))
    varlist += [ turnon, exponent, offset, beta ,
                 rnorm, rturnon, roffset, rbeta ]
    return acceptance
