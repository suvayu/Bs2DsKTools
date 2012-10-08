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
constoffset1 = fname1tokens[-1]

fname2tokens = fname2.split('-')
accfntype2 = fname2tokens[2]
mode2 = fname2tokens[1]
constoffset2 = fname2tokens[-1]

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
from ROOT import TF1, TMatrixDSym, TH1, TH1D, TH2D

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
if status < 0: sys.exit('Problem loading %s, %s' % (library, loadstatus[status]))
from ROOT import PowLawAcceptance

# my stuff
from factory import get_workspace, get_file, get_object
from stattools import *

# time range and bins for ratio plots
tfloor = 0.2
tceil = 15.0
nbins = 150

# Files with fitresults:
# data/fitresult-DsPi-powerlaw4-2012-08-10-Fri-05-30.root
# data/fitresult-DsK-powerlaw4-2012-08-10-Fri-07-56.root

# Get objects from workspace
fitresults = []
fnames = [ fname1, fname2 ]
modes = [mode1, mode2]
for i in xrange(0, len(fnames)):
    fn = fnames[i]
    mode = modes[i]
    ws, ffile = get_workspace(fn, 'workspace')
    # ws.Print('v')
    fitresult = ws.obj('fitresult_Model_dataset')
    fitresult.SetNameTitle('fitresult_Model_dataset_%s' % mode,
                           '%s decay time acceptance' % mode)
    fitresults.append(fitresult.Clone())
    ffile.Close()

# order of parameters:
# - beta
# - exponent
# - offset
# - turnon
formula = '((1.-1./(1. + ([3]*x)**[1] - [2]))*(1 - [0]*x))'
acceptance = TF1('acceptance', formula, tfloor, tceil)
acceptance.SetMinimum(0.5)
acceptance.SetMaximum(1.5)

# (1) DsK, (2) DsPi
accfns = []
accfnerrs = []
xbincs = numpy.linspace(tfloor + 0.05, tceil - 0.05, nbins)

for mode, fitresult in enumerate(fitresults):
    parlist = fitresult.floatParsFinal()
    cmatrix = fitresult.covarianceMatrix()

    veclist = RooArgList()
    for i in range(parlist.getSize()):
        name = '%s_%d' % (parlist[i].GetName(), i)
        veclist.add(parlist[i].clone(name))

    multigauss = RooMultiVarGaussian('multigauss', 'multigauss', veclist, parlist, cmatrix)
    dset = multigauss.generate(RooArgSet(veclist), 1000)

    fns = []
    for entry in range(dset.numEntries()):
        vecset = dset.get(entry)
        veclist = RooArgList(vecset)
        for pars in range(veclist.getSize()):
            acceptance.SetParameter(pars, veclist[pars].getVal())
        fns += [acceptance.Clone('%s_%d' % (acceptance.GetName(), entry))]

    avgfn = BinnedAvgFunction(fns, xbincs)
    avgfn.calculate()
    accfns += [avgfn.get_avg_fn()]
    accfnerrs += [avgfn.get_avg_fn_var()]


means = numpy.zeros(nbins, dtype=float)
varis = numpy.zeros(nbins, dtype=float)
for ibin in range(nbins):
    means[ibin] = accfns[0][ibin] / accfns[1][ibin]
    varis[ibin] = accfnerrs[0][ibin] + accfnerrs[1][ibin]

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

for i, mean in enumerate(means):
    if i < nbins:
        haccratio.SetBinContent(i+1, mean)
        haccratio.SetBinError(i+1, varis[i])

rfile1 = get_file(fname1, 'read')
hist1 = get_object('hdataset_%s' % mode1, rfile1)

rfile2 = get_file(fname2, 'read')
hist2 = get_object('hdataset_%s' % mode2, rfile2)

hratio = hist1.Clone('hdataset_ratio')
hratio.Divide(hist2)

if doPrint:
    plt.savefig('plots/acceptance-ratio-%s-mean-rms.png' % accfntype1)
    plt.savefig('plots/acceptance-ratio-%s-mean-rms.pdf' % accfntype1)
    print 'Printed: plots/acceptance-ratio-%s-mean-rms.{png,pdf}' % accfntype1

    # save acceptance ratio as ROOT histogram
    rfile = TFile('data/acceptance-ratio-hists-%s.root' % constoffset1, 'update')
    haccratio.SetDirectory(rfile)
    hratio.SetDirectory(rfile)
    rfile.Write('', TFile.kOverwrite)
    print 'Wrote ROOT file: %s' % rfile.GetName()
    rfile.Close()
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
