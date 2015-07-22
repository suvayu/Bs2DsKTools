#!/usr/bin/env python
# coding=utf-8
"""Plot fit results from persistified workspace.

"""

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', help='ROOT file with saved fit result')
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print to multi-page pdf file')
optparser.add_argument('-l', '--log', action='store_true',
                       help='Print final plot in logscale')

options = optparser.parse_args()
doPrint = options.doPrint
logscale = options.log
fname = options.filename

from rplot.fixes import ROOT
if doPrint:
    ROOT.gROOT.SetBatch(True)

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp, kOpenTriangleDown

from ROOT import gPad, TCanvas

from ROOT import RooFit, RooAbsReal, RooRealConstant

# my stuff
from factory import load_library, set_integrator_config, get_workspace

# Load custom ROOT classes
load_library('libacceptance.so')
set_integrator_config()
epsilon = 0.2
tmax = 15.0

# Get objects from workspace
workspace, rfile = get_workspace(fname, 'workspace')

# sample filename: fitresult-cpowerlaw-w-flat-ratio-2013-02-22-Fri-20-27.root
fnametokens = rfile.GetTitle().split('-')
ratiofn = fnametokens[3]

# variables
time = workspace.var('time')

offset = workspace.var('offset')
turnon = workspace.var('turnon')
exponent = workspace.var('exponent')
beta = workspace.var('beta')

rturnon = workspace.var('rturnon')
roffset = workspace.var('roffset')
rbeta = workspace.var('rbeta')

# PDFs
DsPi_Model = workspace.pdf('DsPi_Model')
dspi_acceptance = workspace.function('dspi_acceptance')
DsK_Model = workspace.pdf('DsK_Model')
dsk_acceptance = workspace.function('dsk_acceptance')
ratio = workspace.function('ratio')

# Dataset
decaycat = workspace.var('decaycat')
dataset = workspace.data('dataset')
# also try RooAbsData::split(decaycat)
dspi_dataset = dataset.reduce(RooFit.Cut('decaycat==0'))
dsk_dataset = dataset.reduce(RooFit.Cut('decaycat==1'))
ndspi = dspi_dataset.numEntries()
ndsk = dsk_dataset.numEntries()


## Plots
# ultra zoomed: 0.0 - 1 ps
time.setRange('uzoom', 0.2, 0.7) # this range is for the dataset binning
# the following range is for the RooPlot axis
tframe0 = time.frame(RooFit.Range('uzoom'), RooFit.Name('pztime0'),
                     RooFit.Title('0.2-0.7 ps, Ds#pi - powerlaw, DsK - powerlaw * %s ratio' %
                                  ratiofn))
dspi_acceptance.plotOn(tframe0, RooFit.LineColor(kGreen),
                       RooFit.Normalization(10, RooAbsReal.Relative))
dsk_acceptance.plotOn(tframe0, RooFit.LineColor(kGreen+2),
                      RooFit.Normalization(10, RooAbsReal.Relative))
ratio.plotOn(tframe0)

# zoomed: 0.0 - 2 ps
time.setRange('zoom', 0., 2.0) # this range is for the dataset binning
# the following range is for the RooPlot axis
tframe1 = time.frame(RooFit.Range('zoom'), RooFit.Name('pztime1'),
                     RooFit.Title('0-2 ps, Ds#pi - powerlaw, DsK - powerlaw * %s ratio' %
                                  ratiofn))
# tframe1.SetAxisRange(0, 1E-3) # probably same as 2nd RooFit.Range()
dspi_dataset.plotOn(tframe1, RooFit.MarkerStyle(kOpenTriangleDown),
                    RooFit.CutRange('zoom'))
DsPi_Model.plotOn(tframe1, RooFit.LineColor(kBlue))
dsk_dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp),
                   RooFit.CutRange('zoom'))
DsK_Model.plotOn(tframe1, RooFit.LineColor(kBlue+2))
dspi_acceptance.plotOn(tframe1, RooFit.LineColor(kGreen),
                       RooFit.Normalization(40, RooAbsReal.Relative))
dsk_acceptance.plotOn(tframe1, RooFit.LineColor(kGreen+2),
                      RooFit.Normalization(40, RooAbsReal.Relative))

# full range: 0.2 - 15 ps
time.setRange('fullrange', epsilon, tmax)
tframe2 = time.frame(RooFit.Range('fullrange'), RooFit.Name('ptime2'),
                     RooFit.Title('0.2-15 ps, Ds#pi - powerlaw, DsK - powerlaw * %s ratio' %
                                  ratiofn))
dspi_dataset.plotOn(tframe2, RooFit.Name('hdspi_dataset'),
                    RooFit.MarkerStyle(kOpenTriangleDown))
DsPi_Model.plotOn(tframe2, RooFit.Name('hdspi_model'),
                  RooFit.LineColor(kBlue))
dsk_dataset.plotOn(tframe2, RooFit.Name('hdsk_dataset'),
                   RooFit.MarkerStyle(kFullTriangleUp))
DsK_Model.plotOn(tframe2, RooFit.Name('hdsk_model'),
                 RooFit.LineColor(kBlue+2))
dspi_acceptance.plotOn(tframe2, RooFit.Name('hdspi_acceptance'),
                       RooFit.LineColor(kGreen),
                       RooFit.Normalization(100, RooAbsReal.Relative))
dsk_acceptance.plotOn(tframe2, RooFit.Name('hdsk_acceptance'),
                      RooFit.LineColor(kGreen+2),
                      RooFit.Normalization(100, RooAbsReal.Relative))


## Pull distributions
# debug
# print
# tframe2.Print('v')

# FIXME: hard coded RooCurve and RooHist name strings
# pullhist = tframe2.residHist('h_dataset', 'Model_Norm[time]', True)
dspi_pullhist = tframe2.pullHist('hdspi_dataset', 'hdspi_model') # equivalent
dsk_pullhist = tframe2.pullHist('hdsk_dataset', 'hdsk_model')

# fit pulls
tblhdr = '| {0:<{width}} | {1:<{width}} |'
tblrow = '| {0:>{sign}{width}e} | {1:>{sign}{width}e} |'
print 'Power law acceptance with %s ratio:' % ratiofn
print tblhdr.format('Mean', 'RMS', width=13)
print tblrow.format(dspi_pullhist.GetMean(2), dspi_pullhist.GetRMS(2),
                    sign=' ', width=10)
print tblrow.format(dsk_pullhist.GetMean(2), dsk_pullhist.GetRMS(2),
                    sign=' ', width=10)

# Dsπ
xaxisvar = RooRealConstant.value(0.0)
tframe3 = time.frame(RooFit.Range('fullrange'), RooFit.Name('dspi_pull'),
                     RooFit.Title('Fit pulls - DsPi PDF'))
xaxisvar.plotOn(tframe3, RooFit.LineColor(kBlack), RooFit.LineWidth(1))
tframe3.addPlotable(dspi_pullhist, 'P')

# DsK
tframe4 = time.frame(RooFit.Range('fullrange'), RooFit.Name('dsk_pull'),
                     RooFit.Title('Fit pulls - DsK PDF w/ %s ratio' %
                                  ratiofn))
xaxisvar.plotOn(tframe4, RooFit.LineColor(kBlack), RooFit.LineWidth(1))
tframe4.addPlotable(dsk_pullhist, 'P')


## Draw and print
# filenames
timestamp = str(workspace.GetTitle())[19:]
if logscale:
    plotfile = 'plots/savedcanvas_%s_%s_%s.pdf' % ('log', ratiofn, timestamp)
else:
    plotfile = 'plots/savedcanvas_%s_%s.pdf' % (ratiofn, timestamp)

# 16:10 canvas
canvas = TCanvas('canvas', 'canvas', 1024, 640)

# open pdf file
if doPrint:
    canvas.Print(plotfile + '[')
gPad.SetGrid(1, 1)
# ultra zoomed
tframe0.Draw()
if doPrint:
    canvas.Print(plotfile)
gPad.SetGrid(0, 0)
# zoomed
tframe1.Draw()
if doPrint:
    canvas.Print(plotfile)
# full range
tframe2.Draw()
if doPrint:
    canvas.Print(plotfile)
# full range log scale
if logscale:
    gPad.SetLogy(1)
    tframe2.Draw()
    if doPrint:
        canvas.Print(plotfile)
    gPad.SetLogy(0)
# pull distributions
gPad.Clear()
gPad.Update()
canvas.Divide(1, 2)
canvas.cd(1)
tframe3.Draw()
canvas.cd(2)
tframe4.Draw()
if doPrint:
    canvas.Print(plotfile)
    # close pdf file
    canvas.Print(plotfile + ']')


# # χ² comparison for offset and turnon
# ilist = gPad.GetListOfPrimitives()
# for obj in ilist:
#     if obj.InheritsFrom(RooCurve.Class()):
#         if -1 < str(obj.GetName()).find('Model'):
#             pdfname = obj.GetName()
#     if obj.InheritsFrom(RooHist.Class()):
#         dstname = obj.GetName()
# if len(pdfname) and len(dstname):
#     chi2 = tframe2.chiSquare(pdfname, dstname, 2)
# print 'Fit χ² b/w %s and %s: %G' % (pdfname, dstname, chi2)

# # label on final plot
# chi2label = TLatex()
# chi2label.SetNDC(True)
# chi2label.DrawLatex(0.6, 0.7, '#chi^{2} = %G' % chi2)
# gPad.Modified()
# gPad.Update()
