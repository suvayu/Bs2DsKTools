#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('-c', metavar='config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=False, help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       default=False, help='Batch mode')
options = optparser.parse_args()
locals().update(_import_args(options))


from utils import read_yaml, make_paths
conf = read_yaml(yamlfile)
rfiles = []
if isinstance(conf, list):
    for entry in conf:
        for rfile in files:
            if entry['file'] == rfile:
                rfiles.append(make_paths(entry))
else:
    for rfile in files:
        if conf['file'] == rfile:
            rfiles.append(make_paths(conf))


from pprint import pprint
import sys
if not rfiles:
    files = ', '.join(files)
    sys.exit('Could not find file(s) in config: {}'.format(files))

from rplot.rdir import Rdir
fnames = [ rfile[0]['file'] for rfile in rfiles ]
rpath_tool = Rdir(fnames)

# FIXME: only processes first file
rfileconf = rfiles[0]

transforms = [
    'identity',
    'deco',
    'pca',
    'uniform',
    'uniform_deco',
    'gauss',
    'gauss_deco'
]

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

hists = {}

## variable distributions
for rdir in rfileconf:
    try:
        if rdir['key'] in transforms:
            hists.update({rdir['key']: rpath_tool.read(rdir['path'], robj_t = ROOT.TH1)})
    except KeyError as err:
        if str(err) != '\'key\'': raise

from rplot.rplot import arrange
ROOT.gStyle.SetHatchesLineWidth(1)
ROOT.gStyle.SetHatchesSpacing(2.5)
for transform in transforms:
    def _style(l):
        # l.reverse()
        l[0].SetFillStyle(3345)
        l[1].SetFillStyle(3354)
    hists[transform] = arrange(hists[transform], 2, pl_p=_style)

from rplot.rplot import Rplot
plotter = Rplot(5, 3, 2000, 1200)
plotter.alpha = 0.2
canvas = plotter.prep_canvas()
canvas.Print('transforms.pdf[')

for transform in transforms:
    plotter.draw_hist(hists[transform], 'hist')
    canvas.Update()
    canvas.Print('transforms.pdf')

canvas.Print('transforms.pdf]')
del plotter

# ## correlation plots
# for rdir in rfileconf:
#     try:
#         if rdir['key'][:-5] in transforms: # keys for corrn folder end in _corr
#             def _filter(key):
#                 isth1 = ROOT.TClass.GetClass(key.GetClassName()) \
#                                    .InheritsFrom(ROOT.TH1.Class())
#                 return isth1 and key.GetName().find('Signal') > 0
#             hists.update({rdir['key']: rpath_tool.read(rdir['path'], robj_p = _filter)})
#     except KeyError as err:
#         if str(err) != '\'key\'': raise

# import numpy as np
# opts = np.empty(shape=(14, 14), dtype=object)
# tril = np.tril_indices(14)
# triu = np.triu_indices(14)

# # draw options
# for idx in zip(*tril): # empty lower triangular
#     opts[idx] = []

# for idx in zip(*triu):
#     opts[idx] = ['scat', '']

# opts = np.reshape(opts, 14*14)

# # plots
# for transform in transforms:
#     plots = np.empty(shape=(14, 14), dtype=object)

#     # empty lower triangular
#     for idx in zip(*tril):
#         plots[idx] = []

#     for i, idx in enumerate(zip(*triu)):
#         plots[idx] = hists[transform+'_corr'][i*2:i*2+2]

#         # plots[idx][0].SetLineColor(ROOT.kBlack)
#         # plots[idx][0].SetMarkerColor(ROOT.kBlack)

#         # plots[idx][1].SetLineColor(ROOT.kYellow)
#         # plots[idx][1].SetMarkerColor(ROOT.kYellow)

#     hists[transform+'_corr'] = np.reshape(plots, 14*14)

# plotter = Rplot(14, 14, 5600, 5600)
# canvas = plotter.prep_canvas('corr_canvas')
# canvas.Print('correlations.pdf[')

# for transform in transforms:
#     plotter.draw_hist(hists[transform+'_corr'], opts)
#     canvas.Update()
#     # canvas.Print('correlations_{}.pdf'.format(transform))
#     canvas.Print('correlations.pdf')

# canvas.Print('correlations.pdf]')
# del plotter
