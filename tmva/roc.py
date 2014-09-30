#!/usr/bin/env python
"""Draw classifier comparison plots (ROC curves)"""

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=True, help='Print to png/pdf files')
optparser.add_argument('-m', dest='usempl', action='store_true',
                       default=False, help='Use Matplotlib')
optparser.add_argument('-b', dest='batch', action='store_true',
                       default=False, help='Batch mode')
optparser.add_argument('-c', dest='clnameglob', metavar='classifier',
                       default=None, help='Only plot matching classifiers (globs allowed)')
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

if clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, clnameglob): del classifiers[key]

sessions = OrderedDict({
    'test.root': 'test',
    'chitra_base/dsk_train_out.root': 'base',
    'chitra_less1a/dsk_train_out.root': 'base - Ds radial FD',
    'chitra_less1b/dsk_train_out.root': 'base - Bs radial FD',
    'chitra_less2/dsk_train_out.root': 'base - Bs & Ds radial FD',
    'chitra_less3/dsk_train_out.root': 'base - bach IP #chi^{2}',
    'chitra_less4/dsk_train_out.root': 'base - radial FD - bach IP #chi^{2}',
    'chitra_deco1/dsk_train_out.root': 'base + deco (all)',
    'chitra_deco2/dsk_train_out.root': 'base + 4 vars deco',
    'chitra_all/dsk_train_out.root': 'base + deco - 3 vars',
    'chitra_combi1/dsk_train_out.root': 'base + deco - Ds FD',
    'chitra_combi2/dsk_train_out.root': 'base + deco - bach IP #chi^{2}',
})

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

from utils import get_hists
from rplot.rplot import Rplot, arrange

def _filter(string):
    matches  = ['MVA_{}{}'.format(cl, string) for cl in classifiers]
    return lambda k: k.GetName() in matches

fnames = [f[0]['file'] for f in rfiles]
rocs = []
for i, rfileconf in enumerate(rfiles):
    # roc curve: MVA_<name>_rejBvsS
    roc = get_hists(classifiers, rfileconf, rpath_tool, robj_t = ROOT.TH1,
                    robj_p = _filter('_rejBvsS'))
    roc = dict((k, v[0]) for k, v in roc.iteritems()) # cleanup dict
    rocs.append(roc)

if usempl:
    # Matplotlib
    import matplotlib.pyplot as plt
    plt.rc('font', family='Liberation Sans') # choose font
    plt.rc('mathtext', default='regular')    # use default font for math

    # ROOT to Matplotlib translation layer
    import rootpy.plotting.root2matplotlib as rplt

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages
    if doprint: pp = PdfPages('ROC_curves_mpl.pdf')

    # hack
    from rootpy.plotting.hist import Hist
    from utils import pycopy, hist_info

    for i, roc in enumerate(rocs):
        fig = plt.figure('ROC curve')
        axes = fig.add_subplot(111)
        axes.grid(axis='both')
        axes.set_title('ROC curve')
        axes.set_xlim(0.7, 1)
        axes.set_ylim(0.7, 1)
        axes.set_xlabel('Signal selection efficiency')
        axes.set_ylabel('Background rejection efficiency')
        axes.xaxis.set_label_coords(0.9,-0.05)
        for key, hist in roc.iteritems():
            info = hist_info(hist)
            hist = pycopy(Hist, ROOT.TH1, hist, *info[0], **info[1])
            line = rplt.hist(hist, stacked=False)
            print type(line), line
        axes.legend(fontsize=10, numpoints=1, frameon=False, ncol=3)

    if doprint:
        pp.savefig()
        pp.close()
    elif not batch:
        plt.show()
else:
    canvas = ROOT.TCanvas('canvas', '', 800, 600)
    if doprint: canvas.Print('ROC_curves.pdf[')

    cols = (ROOT.kAzure, ROOT.kRed, ROOT.kBlack)
    legend = ROOT.TLegend(0.12, 0.15, 0.8, 0.6)
    legend.SetHeader('MVA classifiers')
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    ROOT.gStyle.SetOptStat(False)

    for i, roc in enumerate(rocs):
        for j, hist in enumerate(roc.iteritems()):
            hist[1].SetLineStyle(i+1)
            hist[1].SetLineColor(cols[j])
            hist[1].GetXaxis().SetRangeUser(0.7, 1.0)
            hist[1].GetYaxis().SetRangeUser(0.7, 1.0)
            try:
                info = sessions[fnames[i]]
            except KeyError:
                info = fnames[i]
            text = '{} ({})'.format(classifiers[hist[0]], info)
            legend.AddEntry(hist[1], text, 'l')
            if i ==0 and j == 0:
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
