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

options = optparser.parse_args()
doPrint = options.doPrint

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
workspace, rfile = get_workspace(options.filename, 'workspace')

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
Bdecay = workspace.pdf('Bdecay')
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
from helpers import rf_fr_style, diff_axis_style
time.setRange('full', 0, tmax)
tfr_fitres1 = time.frame(RooFit.Range('full'), RooFit.Name('time_fitres1'))
dspi_dataset.plotOn(tfr_fitres1, RooFit.Name('hdspi_dataset'),
                    RooFit.MarkerStyle(ROOT.kOpenTriangleDown))
DsPi_Model.plotOn(tfr_fitres1, RooFit.Name('hdspi_model'),
                  RooFit.LineColor(ROOT.kBlue))
dspi_acceptance.plotOn(tfr_fitres1, RooFit.Name('hdspi_acceptance'),
                       RooFit.LineColor(ROOT.kGreen),
                       RooFit.Normalization(100, RooAbsReal.Relative))
rf_fr_style(tfr_fitres1)
tfr_fitres1.SetAxisRange(0, 1.05*tfr_fitres1.GetMaximum(), 'Y')

tfr_fitres2 = tfr_fitres1.emptyClone('tfr_fitres2')
dsk_dataset.plotOn(tfr_fitres2, RooFit.Name('hdsk_dataset'),
                   RooFit.MarkerStyle(ROOT.kFullTriangleUp))
DsK_Model.plotOn(tfr_fitres2, RooFit.Name('hdsk_model'),
                 RooFit.LineColor(ROOT.kBlue+2))
dsk_acceptance.plotOn(tfr_fitres2, RooFit.Name('hdsk_acceptance'),
                      RooFit.LineColor(ROOT.kGreen+2),
                      RooFit.Normalization(10, RooAbsReal.Relative))
rf_fr_style(tfr_fitres2)
tfr_fitres2.SetAxisRange(0, 1.05*tfr_fitres2.GetMaximum(), 'Y')

tfr_th = time.frame(RooFit.Name('tfr_th'))
Bdecay.plotOn(tfr_th, RooFit.LineColor(ROOT.kRed))
dspi_acceptance.plotOn(tfr_th, RooFit.LineColor(ROOT.kGreen),
                       RooFit.Normalization(0.02, RooAbsReal.Relative))
dsk_acceptance.plotOn(tfr_th, RooFit.LineColor(ROOT.kGreen+2),
                      RooFit.Normalization(0.02, RooAbsReal.Relative))
rf_fr_style(tfr_th, ytitle='')


# Pull distributions
dspi_pullhist = tfr_fitres1.pullHist('hdspi_dataset', 'hdspi_model')
dsk_pullhist = tfr_fitres2.pullHist('hdsk_dataset', 'hdsk_model')

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
rf_fr_style(tfr_pull1, xtitle='', ytitle='')
tfr_pull1.SetAxisRange(-5, 5, 'Y')
diff_axis_style(tfr_pull1.GetYaxis(), 5)

# DsK
tfr_pull2 = tfr_pull1.emptyClone('dsk_pull')
xaxisvar.plotOn(tfr_pull2, RooFit.LineColor(ROOT.kRed), RooFit.LineWidth(2))
tfr_pull2.addPlotable(dsk_pullhist, 'P')
rf_fr_style(tfr_pull2, xtitle='', ytitle='')
tfr_pull2.SetAxisRange(-5, 5, 'Y')
diff_axis_style(tfr_pull2.GetYaxis(), 5)


## Draw and print
# filenames
timestamp = str(workspace.GetTitle())[19:]
plotfile = 'plots/savedcanvas_%s_%s.pdf' % (ratiofn, timestamp)

# 16:10 canvas
from helpers import plot_diff_canvas
plot, diff, canvas = plot_diff_canvas()

# open pdf file
if doPrint:
    canvas.Print(plotfile + '[')

# Dsπ
plot.cd()
tfr_fitres1.Draw()
diff.cd()
tfr_pull1.Draw()
canvas.Update()
if doPrint:
    canvas.Print(plotfile)


def _clean(pad):
    pad.Clear()
    pad.Update()
map(_clean, (plot, diff))

# DsK
plot.cd()
tfr_fitres2.Draw()
diff.cd()
tfr_pull2.Draw()
canvas.Update()
if doPrint:
    canvas.Print(plotfile)

del plot, diff, canvas
canvas = TCanvas('canvas', 'canvas', 1024, 640)
tfr_th.Draw()
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
