#!/usr/bin/env python
# coding=utf-8
"""Summarise fit results from the mass fit

@author: Suvayu Ali
@email:  Suvayu dot Ali at cern dot ch

"""

import argparse
from utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                 description=__doc__)
parser.add_argument('rfile', metavar='file', help='Input ROOT file')
parser.add_argument('-w', '--workspace', required=True,
                    help='Name of workspace')
parser.add_argument('-c', '--combi', action='store_true',
                    help='Summarise combinatorial background')
parser.add_argument('-s', '--signal', action='store_true',
                    help='Summarise signal')
parser.add_argument('-d', '--decay', choices=['BsDsPi', 'BsDsK'],
                    default='BsDsPi', help='Decay type to summarise')
parser.add_argument('-r', '--range', nargs=2, type=float,
                    help='Mass range to summarise')
options = parser.parse_args()

import sys
import os
assert(os.path.exists(options.rfile))

from fixes import ROOT
ROOT.gROOT.SetBatch(True)
# shutup RooFit
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

rfile = ROOT.TFile.Open(options.rfile, 'read')
wsp = rfile.Get(options.workspace)

from itertools import product
from ROOT import RooFit, RooArgSet
mass = wsp.var('lab0_MM')
mass.setRange('full', mass.getMin(), mass.getMax())

# hold on to objects so that python does not garbage collect
variables, pdfs = [], []

integrals = {}
modes = ('up', 'down')

if options.combi:
    variables += map(lambda i: wsp.var('{}_{}'.format(*i)),
                     product(('p1', 'p0'), modes))
    for mo in modes:
        # NOTE: normalisation and integration sets are the same for us
        # as we want to integrate over the pdf, the integration ranges
        # are different however.
        #
        #   ∫ pdf(range) = ∫dm pdf(range) / ∫dm pdf(full)
        iset = RooArgSet(mass)
        pdf = wsp.pdf('Comb_{}'.format(mo))
        pdfs.append(pdf)

        if options.range:
            mass.setRange('win', *options.range)
            integrals[mo] = pdf.createIntegral(iset, RooFit.NormSet(iset),
                                               RooFit.Range('win'))
        else:
            integrals[mo] = pdf.createIntegral(iset, RooFit.NormSet(iset),
                                               RooFit.Range('full'))
elif options.signal:
    variables += [wsp.var('Signal_mean'), wsp.var('Signal_sigmas')]
    variables += [wsp.var('Signal_{}{}'.format(*i))
                  for i in product(('alpha', 'n'), (1, 2))]
    for mo in modes:
        iset = RooArgSet(mass)
        pdf_t = wsp.pdf('pre_prior_TotPdf_{}'.format(mo))
        pdf = pdf_t.pdfList().at(0)
        pdfs.append(pdf)

        if options.range:
            mass.setRange('win', *options.range)
            integrals[mo] = pdf.createIntegral(iset, RooFit.NormSet(iset),
                                               RooFit.Range('win'))
        else:
            integrals[mo] = pdf.createIntegral(iset, RooFit.NormSet(iset),
                                               RooFit.Range('full'))

for mo, i in integrals.iteritems():
    if options.combi:
        evts = wsp.var('NComb_{}'.format(mo))
    elif options.signal:
        evts = wsp.var('NBsDsPi_{}'.format(mo))
    variables.append(evts)
    print '{}: {}'.format(i.GetName(), evts.getValV() * i.getValV())
