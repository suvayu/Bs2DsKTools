#!/usr/bin/env python
# coding=utf-8
"""Summarise fit results from the mass fit

@author: Suvayu Ali
@email:  Suvayu dot Ali at cern dot ch

"""

import argparse
from rplot.utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                 description=__doc__)
parser.add_argument('rfile', metavar='file', help='Input ROOT file')
parser.add_argument('-w', '--workspace', required=True,
                    help='Name of workspace')
parser.add_argument('-d', '--decay', choices=['BsDsPi', 'BsDsK'],
                    default='BsDsPi', help='Decay type to summarise')
parser.add_argument('-r', '--range', nargs=2, type=float,
                    help='Mass range to summarise')
options = parser.parse_args()

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


def get_pdf(wsp, mode, signal):
    """Return pdfs as per mode and sig/bkg"""
    if signal:
        pdf_t = wsp.pdf('pre_prior_TotPdf_{}'.format(mode))
        pdf = pdf_t.pdfList().at(0)
    else:
        pdf = wsp.pdf('Comb_{}'.format(mode))
    return pdf


def get_integral(pdf, var, varrange):
    """Return the integral of pdf over var for the given range

       NOTE: normalisation and integration sets are the same for us as
       we want to integrate over the pdf, the integration ranges are
       different however.

         ∫ pdf(range) = ∫dm pdf(range) / ∫dm pdf(full)

    """
    iset = RooArgSet(var)
    var.setRange('window', *varrange)
    return pdf.createIntegral(iset, RooFit.NormSet(iset),
                              RooFit.Range('window'))


mass = wsp.var('lab0_MM')
if options.range:
    massrange = options.range
else:
    massrange = (mass.getMin(), mass.getMax())

norms = {'sig': 'N{}_{{}}'.format(options.decay), 'bkg': 'NComb_{}'}
integrals = {'sig': [], 'bkg': []}
mag_modes = ('up', 'down')

# hold on to objects so that python does not garbage collect
variables, pdfs = [], []

# combinatorial params
variables += map(lambda i: wsp.var('{}_{}'.format(*i)),
                 product(('p1', 'p0'), mag_modes))

# signal params
variables += [wsp.var('Signal_mean'), wsp.var('Signal_sigmas')]
variables += [wsp.var('Signal_{}{}'.format(*i))
              for i in product(('alpha', 'n'), (1, 2))]

# normalisation variables
for key in integrals:
    norms[key] = [wsp.var(norms[key].format(mode)) for mode in mag_modes]

# integrals
for key in integrals:
    for mode in mag_modes:
        pdf = get_pdf(wsp, mode, signal=True if key == 'sig' else False)
        pdfs.append(pdf)
        integrals[key].append(get_integral(pdf, mass, massrange))

# print the table
print '|{}'.format(' {:^5} |'*4).format('type', 'up', 'down', 'total') # header
print '|{}\b|'.format('{}+'.format('-'*7)*4)
fmt = '| {{:<5}} |{}'.format(' {:>5.0f} |'*3)
for key in integrals:
    # mag_modes = ('up', 'down')
    up_evts = norms[key][0].getValV() * integrals[key][0].getValV()
    down_evts = norms[key][1].getValV() * integrals[key][1].getValV()
    print fmt.format(key,  up_evts, down_evts, up_evts + down_evts)
