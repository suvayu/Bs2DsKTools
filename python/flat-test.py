#!/usr/bin/env python
# coding=utf-8
"""Flat test for DsK/Dsπ acceptance ratio.

NB: ratio histogram filename is hardcoded.

"""

# Python modules
import os
import sys
import math
import numpy

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('file1', help='ROOT file with DsK fit result')
optparser.add_argument('file2', help='ROOT file with Dsπ fit result')
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print to multi-page pdf file')

options = optparser.parse_args()
doPrint = options.doPrint

fname1 = options.file1
fname2 = options.file2

fname1tokens = fname1.split('-')
accfntype1 = fname1tokens[2]
mode1 = fname1tokens[1]

fname2tokens = fname2.split('-')
accfntype2 = fname2tokens[2]
mode2 = fname2tokens[1]

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
if doPrint: gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass, TLatex
from ROOT import TF1, TMatrixDSym, TH1D, TH2D

# RooFit classes
from ROOT import RooPlot, RooWorkspace, RooFitResult, RooFit
from ROOT import RooArgSet, RooArgList
from ROOT import RooHistFunc, RooDataHist
from ROOT import RooFormulaVar, RooMultiVarGaussian

# Hack around RooWorkspace.import() and python keyword import clash
_import = getattr(RooWorkspace, 'import')

# Load custom ROOT classes
loadstatus = { 0: 'loaded',
               1: 'already loaded',
               -1: 'does not exist',
               -2: 'version mismatch' }

status = gSystem.Load('libacceptance')
if status < 0: sys.exit('Problem loading %s, %s' % (library, loadstatus[status]) )

from ROOT import PowLawAcceptance

# my stuff
from factory import get_workspace
epsilon = 2E-4

# Get workspaces from files
workspace1 = get_workspace(fname1, 'workspace')
workspace1.SetName('workspace1')
workspace2 = get_workspace(fname2, 'workspace')
workspace2.SetName('workspace2')

# create new workspace
workspace = RooWorkspace('workspace')

# observable
time = workspace1.var('time')
time.setRange('fullrange', epsilon, 1E-2 + epsilon)
_import(workspace, time)

# parameters
offset = workspace1.var('offset')
turnon = workspace1.var('turnon')
exponent = workspace1.var('exponent')
beta = workspace1.var('beta')

# import acceptances
acceptance = workspace1.function('acceptance') # DsK
acceptance.SetNameTitle('acceptance_%s' % mode1,
                        '%s decay time acceptance' % mode1)
_import(workspace, acceptance,
        RooFit.RenameAllVariablesExcept(mode1, 'time'),
        RooFit.RecycleConflictNodes())

acceptance = workspace2.function('acceptance') # Dsπ
acceptance.SetNameTitle('acceptance_%s' % mode2,
                        '%s decay time acceptance' % mode2)
_import(workspace, acceptance,
        RooFit.RenameAllVariablesExcept(mode2, 'time'),
        RooFit.RecycleConflictNodes())


# retrieve acceptance functions
acceptance1 = workspace.function('acceptance_%s' % mode1) # DsK
acceptance2 = workspace.function('acceptance_%s' % mode2) # Dsπ

# Acceptance ratio FIXME: hardcoded ROOT file
rfile = TFile('data/acceptance-ratio-hists.root', 'read')
hcorr = rfile.Get('haccratio_cpowerlaw')

ardhist = RooDataHist('ardhist', 'DsK/DsPi acceptance ratio datahist',
                      RooArgList(time), RooFit.Import(hcorr, False))
accratio = RooHistFunc('accratio', 'DsK/DsPi acceptance ratio',
                       RooArgSet(time), ardhist)
cacceptance = PowLawAcceptance(acceptance2, 'cacceptance', accratio)
# cacceptance = PowLawAcceptance('cacceptance', 'Corrected Power law acceptance',
#                                turnon, time, offset, exponent, beta, accratio)

ratio = RooFormulaVar('ratio', '@0/@1', RooArgList(acceptance1, cacceptance))

tframe = time.frame(RooFit.Range('fullrange'), RooFit.Name('ptime'),
                    RooFit.Title('Acceptance ratio (0.2 - 10 ps)'))

acceptance1.plotOn(tframe, RooFit.LineColor(kBlue))
# acceptance2.plotOn(tframe, RooFit.LineColor(kRed))
# accratio.plotOn(tframe, RooFit.LineColor(kBlack))
cacceptance.plotOn(tframe, RooFit.LineColor(kRed))
ratio.plotOn(tframe, RooFit.LineColor(kGreen))
tframe.Draw()

if doPrint: gPad.Print('plots/flat-test.png')
