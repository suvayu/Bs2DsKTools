#!/usr/bin/env python
"""Draw classifier performace plots (distribution)"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=True, help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       default=False, help='Batch mode')
optparser.add_argument('-c', dest='clnameglob', metavar='classifier',
                       default=None, help='Only plot matching classifiers (globs allowed)')
optparser.add_argument('--rarity', action='store_true',
                       default=False, help='Plot rarity distributions')
optparser.add_argument('--probab', action='store_true',
                       default=False, help='Plot classifier probability distributions')
options = optparser.parse_args()
locals().update(_import_args(options))


from pprint import pprint
import sys

from utils import read_yaml, get_rpaths
conf = read_yaml(yamlfile)
if isinstance(conf, list):
    for entry in conf:
        print entry['file']
        if entry['file'] != 'TMVA.root': continue
        rfiles = get_rpaths(files, entry)
else:
    if conf['file'] == 'TMVA.root':
        rfiles = get_rpaths(files, conf)

if not rfiles: sys.exit('Config parsing error.')

from rplot.rdir import Rdir
fnames = [ rfile[0]['file'] for rfile in rfiles ]
rpath_tool = Rdir(fnames)

# FIXME: only processes first file
rfileconf = rfiles[0]

from config import classifiers

if clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, clnameglob): del classifiers[key]

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

from utils import get_hists
from rplot.rplot import Rplot, arrange

def _filter(string):
    matches  = ['MVA_{}{}'.format(cl, string) for cl in classifiers]
    return lambda k: k.GetName() in matches

_filter1 = lambda string: lambda k: _filter(string+'_S')(k) or _filter(string+'_B')(k)
_filter2 = lambda str1, str2: lambda k: _filter1(str1)(k) or _filter1(str2)(k)

distribs = get_hists(classifiers, rfileconf, rpath_tool,
                     robj_t = ROOT.TH1, robj_p = _filter2('', '_Train'))
if rarity:
    rarity = get_hists(classifiers, rfileconf, rpath_tool,
                       robj_t = ROOT.TH1, robj_p = _filter1('_Rarity'))
if probab:
    probab = get_hists(classifiers, rfileconf, rpath_tool,
                       robj_t = ROOT.TH1, robj_p = _filter1('_Proba'))

plotter = Rplot(1, 1, 800, 600)
plotter.alpha = 0.2
plotter.fill_colours = (ROOT.kAzure,   ROOT.kRed,   ROOT.kAzure,   ROOT.kRed)
plotter.line_colours = (ROOT.kAzure-6, ROOT.kRed+2, ROOT.kAzure-6, ROOT.kRed+2)
plotter.markers = (ROOT.kPlus, ROOT.kPlus, ROOT.kPlus, ROOT.kPlus)
canvas = plotter.prep_canvas()
if doprint: canvas.Print('overtraining.pdf[')

ROOT.gStyle.SetHatchesLineWidth(1)
ROOT.gStyle.SetHatchesSpacing(1)
def _style(l):
    l[0].SetFillStyle(3345)
    l[1].SetFillStyle(3354)

def _plot(plots, opts):
    plotter.draw_hist(plots, opts)
    canvas.Update()
    if doprint: canvas.Print('overtraining.pdf')

for classifier in classifiers:
    # TODO: KS test b/w train & test
    _plot(arrange(distribs[classifier], 4, predicate = _style),
          [['hist', 'hist', 'e1', 'e1']])  # same as arrange(.., 4)
    if rarity or probab:
        opts = [['hist', 'hist']]  # same as arrange(.., 2)
    if rarity:
        _plot(arrange(rarity[classifier], 2, predicate = _style), opts)
    if probab:
        _plot(arrange(probab[classifier], 2, predicate = _style), opts)

if doprint: canvas.Print('overtraining.pdf]')
del canvas
