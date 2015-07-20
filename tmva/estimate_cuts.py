#!/usr/bin/env python
# coding=utf-8
"""Estimate equivalent cuts for different MVA classifiers

For a reference MVA classifier cut, estimate equivalent cuts for other
classifiers based on the number of selected events.

@author: Suvayu Ali
@email:  Suvayu dot Ali at cern dot ch

"""

import argparse
from rplot.utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                 description=__doc__)
parser.add_argument('rfile', metavar='file', help='Input ROOT file')
parser.add_argument('--classifiers', nargs='+', required=True,
                    help='List of MVA classifiers (first is used as reference,'
                    ' and the rest to estimate)')
parser.add_argument('-c', dest='cut', type=float, required=True,
                    help='Reference MVA classifier cut')
parser.add_argument('-r', dest='range', type=float, default=1,
                    help='Reference MVA classifier cut')
parser.add_argument('--maxentries', default=200000,
                    help='Maximum input tree entries to process')
parser.add_argument('--tree', default='DecayTree', help='Tree name to use')
options = parser.parse_args()

import os
import sys
if not os.path.exists(options.rfile):
    sys.exit('Non-existent input file: {}'.format(options.rfile))

from fixes import ROOT
ROOT.gROOT.SetBatch(True)

rfile = ROOT.TFile.Open(options.rfile, 'read')
tree = rfile.Get(options.tree)


def get_estimate(mva, cut, tree=tree):
    cut = ROOT.TCut('{}>{}'.format(mva, cut))
    # NOTE: only process 200,000 entries
    tree.Draw('{0}>>h{0}'.format(mva), cut, 'goff', options.maxentries)
    hist = ROOT.gDirectory.Get('h{}'.format(mva))
    return hist.GetEntries()


def get_best_estimate(ref, mva, mvacut, refcut=options.cut, tree=tree):
    import numpy as np
    expected = get_estimate(ref, refcut)
    # print expected
    cuts = np.linspace(mvacut, mvacut-options.range, 101)
    # print cuts
    for cut in cuts:
        npassed = get_estimate(mva, cut)
        # print npassed
        if npassed >= expected:
            break
    return (cut, npassed, npassed >= expected)


fmt = '| {:<15} | {:>+.2f} | {:>10} |'
ref = options.classifiers[0]
failed = []

for mva in options.classifiers:
    if mva == 'BDTG':
        mvacut = 0.4
    elif mva == 'BDTB':
        mvacut = 0.2
    elif mva == 'BDTGResponse_1':
        mvacut = 0.4
    cut, evts, success = get_best_estimate(ref, mva, mvacut)
    if not success:
        failed.append(mva)
    print fmt.format(mva, cut, evts)

if failed:
    print 'failed best esitmates: {},'.format(failed), \
        'try inceasing the scan range'
