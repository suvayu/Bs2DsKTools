#!/usr/bin/env python
# coding=utf-8
"""Plot acceptance ratio between Dsπ and DsK.

"""

# Python modules
import os
import sys
import math
import numpy

# # option parsing
# import argparse
# optparser = argparse.ArgumentParser(description='Lifetime acceptance plots')
# optparser.add_argument('--print', dest='doPrint', type=bool, default=False,
#                        help='Print to multi-page pdf file')

# options = optparser.parse_args()
# doPrint = options.doPrint

fname1 = sys.argv[1]
fname2 = sys.argv[2]
accfntype1 = fname1[15:24]
accfntype2 = fname2[15:24]

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
# if doPrint: gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass, TLatex
from ROOT import TF1, TMatrixDSym

# RooFit classes
from ROOT import RooPlot, RooWorkspace, RooFitResult, RooFit
from ROOT import RooArgSet, RooArgList
from ROOT import RooDataSet, RooMultiVarGaussian

# my stuff
from factory import get_workspace
from utilities import RunningAverage

# Files with fitresults:
# data/fitresult-DsPi-powerlaw4-2012-08-10-Fri-05-30.root
# data/fitresult-DsK-powerlaw4-2012-08-10-Fri-07-56.root

# Get objects from workspace
workspace1 = get_workspace(fname1, 'workspace')
workspace1.SetName('workspace1')
workspace2 = get_workspace(fname2, 'workspace')
workspace2.SetName('workspace2')

fitresult1 = workspace1.obj('fitresult_FullModel_dataset')
fitresult1.SetNameTitle('fitresult_FullModel_dataset1', 'DsK decay time acceptance')
fitresult2 = workspace2.obj('fitresult_FullModel_dataset')
fitresult2.SetNameTitle('fitresult_FullModel_dataset2', 'DsPi decay time acceptance')

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

dset1 = multigauss1.generate(RooArgSet(veclist1), 100)
dset2 = multigauss2.generate(RooArgSet(veclist2), 100)

# (1) DsK, (2) DsPi
formula1 = '((1.-1./(1. + ([3]*x)**[1] - [2]))*(1 - [0]*x))'
formula2 = '((1.-1./(1. + ([7]*x)**[5] - [6]))*(1 - [4]*x))'
ratio = TF1('ratio', '(%s)/(%s)' % (formula1, formula2), 2E-4, 1.02E-2)
ratio.SetMinimum(0.8)
ratio.SetMaximum(1.2)

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
# ratio.GetXaxis().SetTitle('B decay time (ns)')
# ratio.GetYaxis().SetTitle('Acceptance ratio (DsK/Ds#pi)')

# if doPrint:
gPad.Print('plots/acceptance-ratio.png')
gPad.Print('plots/acceptance-ratio.pdf')

bins = 100

means = numpy.zeros(bins, dtype=float)
varis = numpy.zeros(bins, dtype=float)
xbins = numpy.arange(2.5E-4, 1.02E-2, 1E-4)

for ibin in range(bins):
    ravg = RunningAverage()
    for fn in fns:
        ravg.fill(fn.Eval(xbins[ibin]))
    means[ibin] = ravg.mean()
    varis[ibin] = ravg.var()

import matplotlib.pyplot as plt

x = range(bins)

plt.figure()
plt.title('DsK/DsPi acceptance ratio mean with variance shown as error bars\n')
plt.errorbar(xbins, means, varis)
axes = plt.axes()
axes.set_xlabel('B decay time')
axes.set_ylabel('DsK/DsPi acceptance ratio')
axes.set_xlim(2E-4, 1.02E-2)
axes.set_ylim(0.8, 1.2)

# if doPrint:
plt.savefig('plots/acceptance-ratio-mean-rms.png')
plt.savefig('plots/acceptance-ratio-mean-rms.pdf')
# else:
#     plt.show()
