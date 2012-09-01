#!/usr/bin/env python
# coding=utf-8
"""Plot fit results from persistified workspace.

"""

# Python modules
import os
import sys
import re

# option parsing
import argparse
optparser = argparse.ArgumentParser(description='Lifetime acceptance plots')
optparser.add_argument('--file', dest='fname',
                       help='Filename with saved fit result')
optparser.add_argument('--print', dest='doPrint', type=bool, default=False,
                       help='Print to multi-page pdf file')
optparser.add_argument('--logscale', type=bool, default=False,
                       help='Print final plot in logscale')

options = optparser.parse_args()
doPrint = options.doPrint
logscale = options.logscale
fname = options.fname
# sample filename fitresult-DsK-powerlaw4-2012-08-25-Sat-13-24.root
fnametokens = fname.split('-')
accfntype = fnametokens[2]
mode = fnametokens[1]

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

# RooFit classes
from ROOT import RooFit, RooGlobalFunc
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooAbsData, RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel
from ROOT import RooList, RooCurve, RooHist

# Load custom ROOT classes
loadstatus = { 0: 'loaded',
               1: 'already loaded',
               -1: 'does not exist',
               -2: 'version mismatch' }

library = 'libacceptance.so'
status = gSystem.Load(library)
if status < 0: sys.exit('Problem loading %s, %s' % (library, loadstatus[status]) )
from ROOT import PowLawAcceptance, BdPTAcceptance #, ErfAcceptance

# my stuff
from factory import *

set_integrator_config()
epsilon = 2E-4

# Files with fitresults:
# data/fitresult-powerlaw2-2012-06-22-Fri-15-47.root
# data/fitresult-powerlaw3-2012-06-23-Sat-23-50.root

# Get objects from workspace
workspace = get_workspace(fname, 'workspace')
# variables
time = workspace.var('time')
dt = workspace.var('dt')
offset = workspace.var('offset')

if -1 < accfntype.find('powerlaw'):
    turnon = workspace.var('turnon')
    exponent = workspace.var('exponent')
elif -1 < accfntype.find('bdpt'):
    slope = workspace.var('slope')

patt = re.compile('powerlaw4|cpowerlaw|bdpt')
if re.search(patt, accfntype): beta = workspace.var('beta')

# PDFs
PDF = workspace.pdf('FullModel')
acceptance = workspace.function('acceptance')
dataset = workspace.data('dataset')

# argset
timeargset = RooArgSet(time)
dtargset = RooArgSet(dt)

# plot
# NOTE: this range is for the dataset binning
time.setRange('zoom1', 0., 2E-3)
# NOTE: this range is for the RooPlot axis
tframe1 = time.frame(RooFit.Range('zoom1'), RooFit.Name('pztime1'),
                     RooFit.Title('Projection on time (0 - 2 ps) with %s (%s)' %
                                  (accfntype.rstrip('1234'), mode)))
# tframe1.SetAxisRange(0, 1E-3) # probably same as 2nd RooFit.Range()
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp),
               RooFit.CutRange('zoom'))
PDF.plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                  RooFit.Normalization(200, RooAbsReal.Relative))

time.setRange('zoom2', 2E-3, 1E-2)
tframe2 = time.frame(RooFit.Range('zoom2'), RooFit.Name('pztime2'),
                     RooFit.Title('Projection on time (2 - 10 ps) with %s (%s)' %
                                  (accfntype.rstrip('1234'), mode)))
dataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp),
               RooFit.CutRange('zoom2'))
PDF.plotOn(tframe2, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe2, RooFit.LineColor(kGreen),
                  RooFit.Normalization(800, RooAbsReal.Relative))

time.setRange('fullrange', epsilon, 1E-2 + epsilon)
tframe3 = time.frame(RooFit.Range('fullrange'), RooFit.Name('ptime3'),
                     RooFit.Title('Projection on time (0.2 - 10 ps) with %s (%s)' %
                                  (accfntype.rstrip('1234'), mode)))
dataset.plotOn(tframe3, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe3, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe3, RooFit.LineColor(kGreen),
                  RooFit.Normalization(1000, RooAbsReal.Relative))

print
tframe3.Print('v')

# FIXME: hard coded RooCurve and RooHist name strings
pullhist = tframe3.residHist('h_dataset', 'FullModel_Norm[time]_DataAvg[dt]', True)
print 'Y Mean: %E' % pullhist.GetMean(2)
print 'Y RMS:  %E' % pullhist.GetRMS(2)

tframe4 = time.frame(RooFit.Range('fullrange'), RooFit.Name('fitpulls'),
                     RooFit.Title('Fit pulls w.r.t. PDF (%s %s)' % (mode, accfntype)))
tframe4.addPlotable(pullhist, 'P')

# draw and print
timestamp = str(workspace.GetTitle())[19:]
if logscale: plotfile = 'plots/savedcanvas_%s_%s_%s_%s.pdf' % ('log', mode, accfntype, timestamp)
else: plotfile = 'plots/savedcanvas_%s_%s_%s.pdf' % (mode, accfntype, timestamp)
canvas = TCanvas('canvas', 'canvas', 800, 600)

if doPrint: canvas.Print(plotfile + '[')
tframe1.Draw()
if doPrint: canvas.Print(plotfile)
tframe2.Draw()
if doPrint: canvas.Print(plotfile)
tframe3.Draw()
if doPrint: canvas.Print(plotfile)
if logscale:
    gPad.SetLogy(1)
    tframe3.Draw()
    if doPrint: canvas.Print(plotfile)
gPad.SetLogy(0)
tframe4.Draw()
if doPrint: canvas.Print(plotfile)
if doPrint: canvas.Print(plotfile + ']')

# # χ² comparison for offset and turnon
# ilist = gPad.GetListOfPrimitives()
# for obj in ilist:
#     if obj.InheritsFrom(RooCurve.Class()):
#         if -1 < str(obj.GetName()).find('FullModel'):
#             pdfname = obj.GetName()
#     if obj.InheritsFrom(RooHist.Class()):
#         dstname = obj.GetName()
# if len(pdfname) and len(dstname):
#     chi2 = tframe3.chiSquare(pdfname, dstname, 2)
# print 'Fit χ² b/w %s and %s: %G' % (pdfname, dstname, chi2)

# # label on final plot
# chi2label = TLatex()
# chi2label.SetNDC(True)
# chi2label.DrawLatex(0.6, 0.7, '#chi^{2} = %G' % chi2)
# gPad.Modified()
# gPad.Update()
