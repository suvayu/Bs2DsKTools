#!/usr/bin/env python
# coding=utf-8
"""Plot fit results from persistified workspace.

"""

# Python modules
import os
import sys

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
accfntype = fname[15:24]

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
turnon = workspace.var('turnon')
offset = workspace.var('offset')
exponent = workspace.var('exponent')
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
                     RooFit.Title('Projection on time (0 - 2 ps) with %s' % accfntype))
# tframe1.SetAxisRange(0, 1E-3) # probably same as 2nd RooFit.Range()
dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp),
               RooFit.CutRange('zoom'))
PDF.plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                  RooFit.Normalization(200, RooAbsReal.Relative))

time.setRange('zoom2', 2E-3, 1E-2)
tframe2 = time.frame(RooFit.Range('zoom2'), RooFit.Name('pztime2'),
                     RooFit.Title('Projection on time (2 - 10 ps) with %s' % accfntype))
dataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp),
               RooFit.CutRange('zoom2'))
PDF.plotOn(tframe2, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe2, RooFit.LineColor(kGreen),
                  RooFit.Normalization(800, RooAbsReal.Relative))

time.setRange('fullrange', epsilon, 1E-2 + epsilon)
tframe3 = time.frame(RooFit.Range('fullrange'), RooFit.Name('ptime3'),
                     RooFit.Title('Projection on time (0.2 - 10 ps) with %s' % accfntype))
dataset.plotOn(tframe3, RooFit.MarkerStyle(kFullTriangleUp))
PDF.plotOn(tframe3, RooFit.ProjWData(dtargset, dataset, True),
           RooFit.LineColor(kBlue))
acceptance.plotOn(tframe3, RooFit.LineColor(kGreen),
                  RooFit.Normalization(1000, RooAbsReal.Relative))

# draw and print
timestamp = str(workspace.GetTitle())[19:]
if logscale: plotfile = 'plots/savedcanvas_%s_%s_%s.pdf' % ('log', accfntype, timestamp)
else: plotfile = 'plots/savedcanvas_%s_%s.pdf' % (accfntype, timestamp)
canvas = TCanvas('canvas', 'canvas', 800, 600)
if doPrint: canvas.Print(plotfile + '[')
tframe1.Draw()
if doPrint: canvas.Print(plotfile)
tframe2.Draw()
if doPrint: canvas.Print(plotfile)
tframe3.Draw()
if doPrint: canvas.Print(plotfile)
if logscale: gPad.SetLogy(1)
tframe3.Draw()
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
