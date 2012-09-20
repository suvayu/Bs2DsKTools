#!/usr/bin/env python
# coding=utf-8
"""Plot acceptance ratio between Dsπ and DsK.

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
                       help='Print plots to png/pdf files')

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
from ROOT import RooDataSet, RooMultiVarGaussian

# Load custom ROOT classes
loadstatus = { 0: 'loaded',
               1: 'already loaded',
               -1: 'does not exist',
               -2: 'version mismatch' }

library = 'libacceptance.so'
status = gSystem.Load(library)
if status < 0: sys.exit('Problem loading %s, %s' % (library, loadstatus[status]) )
from ROOT import PowLawAcceptance

# my stuff
from factory import get_workspace
from utilities import RunningAverage

# time range and bins for ratio plots
tfloor = 0.2
tceil = 15.0
nbins = 150

# Files with fitresults:
# data/fitresult-DsPi-powerlaw4-2012-08-10-Fri-05-30.root
# data/fitresult-DsK-powerlaw4-2012-08-10-Fri-07-56.root

# Get objects from workspace
workspace1 = get_workspace(fname1, 'workspace')
workspace1.SetName('workspace1')
workspace2 = get_workspace(fname2, 'workspace')
workspace2.SetName('workspace2')

fitresult1 = workspace1.obj('fitresult_PDF_dataset')
fitresult1.SetNameTitle('fitresult_PDF_dataset_%s' % mode1,
                        '%s decay time acceptance' % mode1)
fitresult2 = workspace2.obj('fitresult_PDF_dataset')
fitresult2.SetNameTitle('fitresult_PDF_dataset_%s' % mode2,
                        '%s decay time acceptance' % mode2)

# order of parameters:
# - beta
# - exponent
# - offset
# - turnon
parlist1 = fitresult1.floatParsFinal()
parlist2 = fitresult2.floatParsFinal()

cmatrix1 = fitresult1.covarianceMatrix()
cmatrix2 = fitresult2.covarianceMatrix()

veclist1 = RooArgList()
veclist2 = RooArgList()

for i in range(parlist1.getSize()):
    name = '%s1' % parlist1[i].GetName()
    veclist1.add(parlist1[i].clone(name))

    name = '%s2' % parlist2[i].GetName()
    veclist2.add(parlist2[i].clone(name))

multigauss1 = RooMultiVarGaussian('multigauss1', 'multigauss1', veclist1, parlist1, cmatrix1)
multigauss2 = RooMultiVarGaussian('multigauss2', 'multigauss2', veclist2, parlist2, cmatrix2)

dset1 = multigauss1.generate(RooArgSet(veclist1), 1000)
dset2 = multigauss2.generate(RooArgSet(veclist2), 1000)

# (1) DsK, (2) DsPi
formula1 = '((1.-1./(1. + ([3]*x)**[1] - [2]))*(1 - [0]*x))'
formula2 = '((1.-1./(1. + ([7]*x)**[5] - [6]))*(1 - [4]*x))'
ratio = TF1('ratio', '(%s)/(%s)' % (formula1, formula2), tfloor, tceil)
ratio.SetMinimum(0.5)
ratio.SetMaximum(1.5)

ratio.SetLineColor(kBlack)
ratio.SetLineStyle(3)

fns = []
for entry in range(dset1.numEntries()):
    vecset1 = dset1.get(entry)
    vecset2 = dset2.get(entry)

    veclist1 = RooArgList(vecset1)
    veclist2 = RooArgList(vecset2)
    for i in range(veclist1.getSize()):
        ratio.SetParameter(i, veclist1[i].getVal())
        ratio.SetParameter(i+4, veclist2[i].getVal())

    fns += [ratio.Clone('%s_%d' % (ratio.GetName(), entry))]
    if entry == 0:
        ratio.DrawCopy('l')
    else:
        ratio.DrawCopy('same')

for i in range(parlist1.getSize()):
    ratio.SetParameter(i, parlist1[i].getVal())
    ratio.SetParameter(i+4, parlist2[i].getVal())

ratio.SetLineColor(kRed)
ratio.SetLineStyle(1)
ratio.SetLineWidth(5)
ratio.DrawCopy('lsame')
fns += [ratio.Clone('%s_%d' % (ratio.GetName(), entry+1))]

# # labels
# ratio.GetXaxis().SetTitle('B decay time (ps)')
# ratio.GetYaxis().SetTitle('Acceptance ratio (DsK/Ds#pi)')

if doPrint:
    gPad.Print('plots/acceptance-ratio-%s.png' % accfntype1)
    gPad.Print('plots/acceptance-ratio-%s.pdf' % accfntype1)


# get the ratio from the ensemble of generated parameter sets
means = numpy.zeros(nbins, dtype=float)
varis = numpy.zeros(nbins, dtype=float)
xbincs = numpy.linspace(tfloor + 0.05, tceil - 0.05, nbins)

hratiodist = []
for ibin in range(nbins):
    ravg = RunningAverage()
    for fn in fns:
        ravg.fill(fn.Eval(xbincs[ibin]))
    means[ibin] = ravg.mean()
    varis[ibin] = math.sqrt(ravg.var())

#     if 0 == (ibin % 30):
#         hratiodist += [ TH1D('hratiodist_%d' % ibin, 'Distribution of acceptance ratio',
#                              100, 0.5, 1.5) ]
#         for fn in fns:
#             hratiodist[-1].Fill(fn.Eval(xbincs[ibin]))

# gPad.Print('plots/acceptance-ratio-projection-%s.pdf[' % accfntype1)
# for hist in hratiodist:
#     hist.Draw('hist')
#     gPad.Print('plots/acceptance-ratio-projection-%s.pdf' % accfntype1)
# gPad.Print('plots/acceptance-ratio-projection-%s.pdf]' % accfntype1)

# print 'Mean: ', means
# print 'Vars: ', varis

import matplotlib.pyplot as plt

plt.figure()
plt.title('%s/%s %s acceptance ratio' % (mode1, mode2, accfntype1))
plt.errorbar(xbincs, means, varis)
axes = plt.axes()
axes.set_xlabel('B decay time (ps)')
axes.set_ylabel('%s/%s acceptance ratio mean\n(variance shown as error bars)' % (mode1, mode2))
axes.set_xlim(tfloor, tceil)
axes.set_ylim(0.5, 1.5)

# Dump ratio histogram to ROOT file
xbins = numpy.linspace(tfloor, tceil, nbins + 1)
haccratio = TH1D('haccratio_%s' % accfntype1, 'Acceptance ratio %s' % accfntype1,
                 nbins, xbins)
haccratio.SetXTitle('B decay time (ps)')
haccratio.SetYTitle('%s/%s acceptance ratio mean' % (mode1, mode2))

# for i, mean in enumerate(means):
#     if i < nbins:
#         haccratio.SetBinContent(i+1, mean)
#         haccratio.SetBinError(i+1, varis[i])

for i in range(nbins):
    # fns[-1] point to the best fit value ratio
    val = fns[-1].Eval(haccratio.GetBinCenter(i+1))
    haccratio.SetBinContent(i+1, val)

if doPrint:
    plt.savefig('plots/acceptance-ratio-%s-mean-rms.png' % accfntype1)
    plt.savefig('plots/acceptance-ratio-%s-mean-rms.pdf' % accfntype1)
    print 'Printed: plots/acceptance-ratio-%s-mean-rms.{png,pdf}' % accfntype1

    # save acceptance ratio as ROOT histogram
    rfile = TFile('data/acceptance-ratio-hists.root', 'update')
    haccratio.SetDirectory(rfile)
    rfile.Write('', TFile.kOverwrite)
    rfile.Close()
    print 'Wrote ROOT file: data/acceptance-ratio-hists.root'
else:
    plt.show()


# # 2-D distribution of acceptance ratio as
# xbins = numpy.linspace(2E-4, 1E-2, bins)
# ybins = numpy.linspace(0.5, 1.5, 101)
# hratiodist = TH2D('hratiodist', 'Distribution of acceptance ratio',
#                   nbins, xbins, 100, ybins)

# for i, xb in enumerate(xbins):
#     if i >= 100: continue
#     for fn in fns:
#         binc = (xbins[i] + xbins[i+1]) / 2
#         hratiodist.Fill(binc, fn.Eval(binc))

# hratiodist.Print()

# # bug is below
# hratiox = []
# canvas = TCanvas('canvas', 'canvas', 1500, 600)
# canvas.Divide(5,2)

# for i in range(10):
#     hratiox += hratiodist.ProjectionX('_px', 0 + i, 9 + i)
#     canvas.cd(i + 1)
#     hratiox[i].Draw('hist')

# if doPrint:
#     canvas.Print('plots/acceptance-ratio-projection-%s.png' % accfntype1)
