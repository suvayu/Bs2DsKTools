#!/usr/bin/env python
"""Draw classifier comparison plots (ROC curves)"""

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('-c', metavar='config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=True, help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       default=False, help='Batch mode')
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

from collections import OrderedDict
classifiers = OrderedDict({
    'BDTA': 'BDT w/ adaptive boost',
    'BDTG': 'BDT w/ gradient boost',
    'BDTB': 'BDT w/ bagging'
})

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

from utils import get_hists
from rplot.rplot import Rplot, arrange

def _filter(string):
    matches  = ['MVA_{}{}'.format(cl, string) for cl in classifiers]
    return lambda k: k.GetName() in matches

# roc curve: MVA_<name>_rejBvsS
roc = get_hists(classifiers, rfileconf, rpath_tool, robj_t = ROOT.TH1,
                robj_p = _filter('_rejBvsS'))

canvas = ROOT.TCanvas('canvas', '', 800, 600)
if doprint: canvas.Print('ROC_curves.pdf[')

roc = dict((k, v[0]) for k, v in roc.iteritems()) # cleanup dict
cols = (ROOT.kAzure, ROOT.kRed, ROOT.kBlack)
legend = ROOT.TLegend(0.2, 0.2, 0.6, 0.4)
legend.SetHeader('MVA classifiers')
legend.SetBorderSize(0)
legend.SetFillStyle(0)
ROOT.gStyle.SetOptStat(False)
for i, hist in enumerate(roc.iteritems()):
    # hist.SetFillStyle(0)
    hist[1].SetLineColor(cols[i])
    hist[1].GetXaxis().SetRangeUser(0.7, 1.0)
    hist[1].GetYaxis().SetRangeUser(0.7, 1.0)
    legend.AddEntry(hist[1], classifiers[hist[0]], 'l')
    if i == 0:
        hist[1].SetTitle('MVA classifier ROC curves')
        hist[1].Draw('c')
    else:
        hist[1].Draw('c same')
legend.Draw()
canvas.SetGrid(1, 1)
canvas.Update()
if doprint: canvas.Print('ROC_curves.pdf')

if doprint: canvas.Print('ROC_curves.pdf]')
del canvas
