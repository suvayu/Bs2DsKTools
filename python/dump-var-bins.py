#!/usr/bin/env python
# coding=utf-8
"""Dump variable binning scheme (as a numpy array) to a binary file

"""

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', help='ROOT file with fit result')
options = optparser.parse_args()
fname = options.filename

# Python modules
import os
import sys
import math
import numpy

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
gROOT.SetBatch(True)

# ROOT classes
from ROOT import TTree, TFile
from ROOT import TH1, TH1D

# RooFit classes
from ROOT import RooWorkspace, RooFit
from ROOT import RooArgSet, RooArgList, RooDataHist

# my stuff
from factory import get_workspace, get_file, get_object, load_library

# Load custom ROOT classes
load_library('libacceptance.so')
from ROOT import PowLawAcceptance, AcceptanceRatio


## Read everything from file
# Get objects from workspace
workspace, ffile = get_workspace(fname, 'workspace')
workspace.Print('v')

# Variables
time = workspace.var('time')
# time range
tmin = time.getMin()
tmax = time.getMax()
time.setRange('fullrange', tmin, tmax)
nbins = time.getBins()

# Dataset
argset = RooArgSet(time)
decaycat = workspace.cat('decaycat')
decaycat.setRange('onlydspi', 'DsPi')
decaycat.setRange('onlydsk', 'DsK')

dataset = workspace.data('dataset')
# RooFit limits entry selection to variables specified in the argset
# passed to SelectVars.  Hence RooFit.SelectVars(argset) needs to be
# called separately on reduced dataset
dspi_data = dataset.reduce(RooFit.Name('dspi_data'),
                           RooFit.CutRange('onlydspi')).reduce(
                               RooFit.SelectVars(argset))
dsk_data = dataset.reduce(RooFit.Name('dsk_data'),
                          RooFit.CutRange('onlydsk')).reduce(
                              RooFit.SelectVars(argset))

print '=' * 5, ' Datasets retrieved ', '=' * 5
for dset in (dataset, dspi_data, dsk_data):
    dset.Print('v')


## Dynamic bin merging
dspihist = TH1D('dspihist', 'Ds#pi decay time', nbins, tmin, tmax)
dskhist = TH1D('dskhist', 'DsK decay time', nbins, tmin, tmax)

for hist in (dspihist, dskhist):
    hist.Sumw2()

dspihist = dspi_data.fillHistogram(dspihist, RooArgList(time))
dskhist = dsk_data.fillHistogram(dskhist, RooArgList(time))

# old binning
obins = numpy.zeros(nbins, dtype=float)
dspihist.GetLowEdge(obins)

# bin content and bin error arrays
dspicons = numpy.zeros(nbins, dtype=float)
dspierrs = numpy.zeros(nbins, dtype=float)
dskcons = numpy.zeros(nbins, dtype=float)
dskerrs = numpy.zeros(nbins, dtype=float)

# fill arrays
for i in range(nbins):
    dspicons[i] = dspihist.GetBinContent(i + 1)
    dspierrs[i] = dspihist.GetBinContent(i + 1)
    dskcons[i] = dskhist.GetBinContent(i + 1)
    dskerrs[i] = dskhist.GetBinContent(i + 1)

# find new binning
newbinedges = [obins[0]]
# start from 2nd bin (i=1) because first bin is in the rising region
# and might have fewer entries
i = 1

## Bin merging algorithm:
# 1. if δ/n > 0.1
# 2. merge with next bin
# 3. recalculate δ(=√(n₁+n₂)) & n(=n₁+n₂)
# 4. if new δ/n > 0.1, repeat 2-3, else continue
while i < nbins:
    dspideln = dspierrs[i] / dspicons[i]
    dskdeln = dskerrs[i] / dskcons[i]
    if dspideln < 0.1 or dskdeln < 0.1:
        newbinedges += [obins[i]]
        i += 1
    else:
        dspicon = dspicons[i]
        dskcon = dskcons[i]
        n = 1                   # start merging bins
        while i + n < nbins:
            dspicon += dspicons[i + n]
            dskcon += dskcons[i + n]
            tdspideln = math.sqrt(dspicon) / dspicon
            tdskdeln = math.sqrt(dskcon) / dskcon
            if not (tdspideln < 0.1 or tdskdeln < 0.1):
                n += 1
            else:
                newbinedges += [obins[i + n]]
                break
        i += n

# new number of bins
oldnbins = nbins
nbins = len(newbinedges)

# add upper bin edge for last bin
newbinedges += [dspihist.GetBinLowEdge(oldnbins) + dspihist.GetBinWidth(oldnbins)]
newbins = numpy.array(newbinedges)
print '='*5, ' Dynamic bin merging summary ', '='*5
print '# of bins %d -> %d ' % (oldnbins, nbins)

binfile = open('data/binning_scheme.dat', 'wb')
print 'Dumping binning scheme to binary file: %s' % binfile.name
newbins.tofile(binfile)
binfile.close()
