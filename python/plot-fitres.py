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
                       help='Include logscale plot')

options = optparser.parse_args()
doPrint = options.doPrint
logscale = options.log
fname = options.filename

from rplot.fixes import ROOT
ROOT.gROOT.SetBatch(doPrint)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

from ROOT import TCanvas, RooFit, RooAbsReal, RooRealConstant

# my stuff
from factory import load_library, set_integrator_config, get_workspace

# suppress RooFit logging
from helpers import rf_msg_lvl
rf_msg_lvl(RooFit.ERROR, RooFit.Plotting, ROOT.RooPlot())

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
print u'Dsπ: {}, DsK: {}'.format(ndspi, ndsk)


# Plots: full range: 0.2 - 15 ps
time.setRange('full', 0, tmax)
tfr_fitres = time.frame(RooFit.Range('full'), RooFit.Name('time_fitres'))
dspi_dataset.plotOn(tfr_fitres, RooFit.Name('hdspi_dataset'),
                    RooFit.MarkerStyle(ROOT.kOpenTriangleDown))
DsPi_Model.plotOn(tfr_fitres, RooFit.Name('hdspi_model'),
                  RooFit.LineColor(ROOT.kBlue))
dsk_dataset.plotOn(tfr_fitres, RooFit.Name('hdsk_dataset'),
                   RooFit.MarkerStyle(ROOT.kFullTriangleUp))
DsK_Model.plotOn(tfr_fitres, RooFit.Name('hdsk_model'),
                 RooFit.LineColor(ROOT.kBlue+2))
dspi_acceptance.plotOn(tfr_fitres, RooFit.Name('hdspi_acceptance'),
                       RooFit.LineColor(ROOT.kGreen),
                       RooFit.Normalization(120, RooAbsReal.Relative))
dsk_acceptance.plotOn(tfr_fitres, RooFit.Name('hdsk_acceptance'),
                      RooFit.LineColor(ROOT.kGreen+2),
                      RooFit.Normalization(120, RooAbsReal.Relative))
tfr_fitres.SetTitle('')
tfr_fitres.SetAxisRange(0, 510, 'Y')


# Pull distributions
dspi_pullhist = tfr_fitres.pullHist('hdspi_dataset', 'hdspi_model')
dsk_pullhist = tfr_fitres.pullHist('hdsk_dataset', 'hdsk_model')

# fit pulls
tblhdr = '| {0:^{width}} | {1:^{width}} |'
tblrow = '| {0:>{sign}{width}e} | {1:>{sign}{width}e} |'
print 'Power law acceptance with %s ratio:' % ratiofn
print tblhdr.format('Mean', 'RMS', width=13)
print tblrow.format(dspi_pullhist.GetMean(2), dspi_pullhist.GetRMS(2),
                    sign=' ', width=10)
print tblrow.format(dsk_pullhist.GetMean(2), dsk_pullhist.GetRMS(2),
                    sign=' ', width=10)

# Dsπ
xaxisvar = RooRealConstant.value(0.0)
tfr_pull1 = time.frame(RooFit.Range('full'), RooFit.Name('dspi_pull'))
xaxisvar.plotOn(tfr_pull1, RooFit.LineColor(ROOT.kRed), RooFit.LineWidth(2))
tfr_pull1.addPlotable(dspi_pullhist, 'P')
tfr_pull1.SetTitle('')
tfr_pull1.SetAxisRange(-5, 5, 'Y')

# DsK
tfr_pull2 = time.frame(RooFit.Range('full'), RooFit.Name('dsk_pull'))
xaxisvar.plotOn(tfr_pull2, RooFit.LineColor(ROOT.kRed), RooFit.LineWidth(2))
tfr_pull2.addPlotable(dsk_pullhist, 'P')
tfr_pull2.SetTitle('')
tfr_pull2.SetAxisRange(-5, 5, 'Y')


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

# full range
tfr_fitres.Draw()
if doPrint:
    canvas.Print(plotfile)

# log scale
if logscale:
    ROOT.gPad.SetLogy(1)
    tfr_fitres.Draw()
    if doPrint:
        canvas.Print(plotfile)
    ROOT.gPad.SetLogy(0)

# pull distributions
ROOT.gPad.Clear()
ROOT.gPad.Update()
canvas.Divide(1, 2)
canvas.cd(1)
tfr_pull1.Draw()
canvas.cd(2)
tfr_pull2.Draw()
if doPrint:
    canvas.Print(plotfile)

# close pdf file
if doPrint:
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
#     chi2 = tfr_fitres.chiSquare(pdfname, dstname, 2)
# print 'Fit χ² b/w %s and %s: %G' % (pdfname, dstname, chi2)

# # label on final plot
# chi2label = TLatex()
# chi2label.SetNDC(True)
# chi2label.DrawLatex(0.6, 0.7, '#chi^{2} = %G' % chi2)
# gPad.Modified()
# gPad.Update()
