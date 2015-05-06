#!/usr/bin/env python
"""Draw MVA classifier performace plots

By default plot only classifier distributions.  Distributions from the
training sample are overlayed with distributions from the testing
sample.  On request, also plot rarity and probability distributions.

"""

import argparse
from utils import RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files')
optparser.add_argument('-b', '--batch', action='store_true', help='Batch mode')
optparser.add_argument('-c', dest='clnameglob', metavar='classifier',
                       help='Only plot matching classifiers (globs allowed)')
optparser.add_argument('--rarity', action='store_true',
                       help='Plot classifier rarity distributions')
optparser.add_argument('--probab', action='store_true',
                       help='Plot classifier probability distributions')
options = optparser.parse_args()


from pprint import pprint
import sys

from utils import read_yaml, get_rpaths
conf = read_yaml(options.yamlfile)
if isinstance(conf, list):
    for entry in conf:
        print entry['file']
        if entry['file'] != 'TMVA.root':
            continue
        rfiles = get_rpaths(options.files, entry)
else:
    if conf['file'] == 'TMVA.root':
        rfiles = get_rpaths(options.files, conf)

if not rfiles:
    sys.exit('Config parsing error.')

from rplot.rdir import Rdir
fnames = [rfile[0]['file'] for rfile in rfiles]
rpath_tool = Rdir(fnames)

# FIXME: only processes first file
rfileconf = rfiles[0]

from config import classifiers

if options.clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, options.clnameglob):
            del classifiers[key]

from fixes import ROOT
ROOT.gROOT.SetBatch(options.batch)

from utils import get_hists
from rplot.rplot import Rplot, arrange


def _filter(string):
    matches = ['MVA_{}{}'.format(cl, string) for cl in classifiers]
    return lambda k: k.GetName() in matches

_filter1 = lambda string: lambda k: _filter(string+'_S')(k) or _filter(string+'_B')(k)
_filter2 = lambda str1, str2: lambda k: _filter1(str1)(k) or _filter1(str2)(k)

distribs = get_hists(classifiers, rfileconf, rpath_tool,
                     robj_t=ROOT.TH1, robj_p=_filter2('', '_Train'))
if options.rarity:
    rarity = get_hists(classifiers, rfileconf, rpath_tool,
                       robj_t=ROOT.TH1, robj_p=_filter1('_Rarity'))
if options.probab:
    probab = get_hists(classifiers, rfileconf, rpath_tool,
                       robj_t=ROOT.TH1, robj_p=_filter1('_Proba'))

plotter = Rplot(1, 1, 800, 600)
plotter.alpha = 0.2
plotter.fill_colours = (ROOT.kAzure,   ROOT.kRed,   ROOT.kAzure,   ROOT.kRed)
plotter.line_colours = (ROOT.kAzure-6, ROOT.kRed+2, ROOT.kAzure-6, ROOT.kRed+2)
plotter.markers = (ROOT.kPlus, ROOT.kPlus, ROOT.kPlus, ROOT.kPlus)
canvas = plotter.prep_canvas()
if options.doprint:
    canvas.Print('overtraining.pdf[')

ROOT.gStyle.SetHatchesLineWidth(1)
ROOT.gStyle.SetHatchesSpacing(1)


def _style(l):
    l[0].SetFillStyle(3345)
    l[1].SetFillStyle(3354)
    try:
        l[2].SetLineWidth(2)
        l[3].SetLineWidth(2)
    except IndexError:          # fails for probab & rarity
        pass


def _plot(plots, opts):
    plotter.draw_hist(plots, opts)
    canvas.Update()
    if options.doprint:
        canvas.Print('overtraining.pdf')

for classifier in classifiers:
    # TODO: KS test b/w train & test
    _plot(arrange(distribs[classifier], 4, predicate=_style),
          [['hist', 'hist', 'e1', 'e1']])  # same as arrange(.., 4)
    if rarity or probab:
        opts = [['hist', 'hist']]  # same as arrange(.., 2)
    if rarity:
        _plot(arrange(rarity[classifier], 2, predicate=_style), opts)
    if probab:
        _plot(arrange(probab[classifier], 2, predicate=_style), opts)

if options.doprint:
    canvas.Print('overtraining.pdf]')
del canvas
