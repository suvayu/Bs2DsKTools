#!/usr/bin/env python
"""Draw ROC (Receiver Operating Characteristic) curves

Draws ROC curves for different MVA classifiers from the TMVA output
files.  It just reads and plots the histograms from the file.

"""

import argparse
from rplot.utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('--schema', default='TMVA_Id.root',
                       help='ROOT file schema to choose from config file')
optparser.add_argument('-r', dest='axis_range', type=float, default=0.6,
                       help='Axis range lower bound')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files')
optparser.add_argument('--prefix', default='', help='Plot file name prefix')
optparser.add_argument('--mpl', dest='usempl', action='store_true',
                       help='Use Matplotlib')
optparser.add_argument('-b', '--batch', action='store_true', help='Batch mode')
optparser.add_argument('-c', dest='clnameglob', metavar='classifier',
                       help='Only plot matching classifiers (globs allowed)')
options = optparser.parse_args()
locals().update(_import_args(options))


import sys

from utils import plot_conf
rfiles = plot_conf(options.yamlfile, options.schema, options.files)
if not rfiles:
    sys.exit('Config parsing error.')

prefix = 'plots/{}'.format(options.prefix)

from config import classifiers, sessions

if options.clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, options.clnameglob):
            del classifiers[key]

from fixes import ROOT
ROOT.gROOT.SetBatch(options.batch)
ROOT.gStyle.SetOptTitle(0)

from utils import get_hists
from rplot.rdir import Rdir
fnames = [f[0]['file'] for f in rfiles]
rpath_tool = Rdir(fnames)


def _filter(string):
    matches = ['MVA_{}{}'.format(cl, string) for cl in classifiers]
    return lambda k: k.GetName() in matches

rocs = []
for i, rfileconf in enumerate(rfiles):
    # roc curve: MVA_<name>_rejBvsS
    roc = get_hists(classifiers, rfileconf, rpath_tool, robj_t=ROOT.TH1,
                    robj_p=_filter('_rejBvsS'))
    roc = dict((k, v[0]) for k, v in roc.iteritems())  # cleanup dict
    rocs.append(roc)

# config
axis_range = options.axis_range
doprint = options.doprint

if options.usempl:
    # Matplotlib
    import matplotlib.pyplot as plt
    plt.rc('font', family='Liberation Sans')  # choose font
    plt.rc('mathtext', default='regular')     # use default font for math

    # ROOT to Matplotlib translation layer
    import rootpy.plotting.root2matplotlib as rplt

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages
    if doprint:
        pp = PdfPages('{}_ROC_curves_mpl.pdf'.format(prefix))

    # hack
    from rootpy.plotting.hist import Hist
    from utils import pycopy, hist_info

    for i, roc in enumerate(rocs):
        fig = plt.figure('ROC curve')
        axes = fig.add_subplot(111)
        axes.grid(axis='both')
        axes.set_title('ROC curve')
        axes.set_xlim(axis_range, 1)
        axes.set_ylim(axis_range, 1)
        axes.set_xlabel('Signal selection efficiency')
        axes.set_ylabel('Background rejection efficiency')
        axes.xaxis.set_label_coords(0.9, -0.05)
        for key, hist in roc.iteritems():
            info = hist_info(hist)
            hist = pycopy(Hist, ROOT.TH1, hist, *info[0], **info[1])
            line = rplt.hist(hist, stacked=False)
            print type(line), line
        axes.legend(fontsize=10, numpoints=1, frameon=False, ncol=3)

    if doprint:
        pp.savefig()
        pp.close()
    elif not options.batch:
        plt.show()
else:
    canvas = ROOT.TCanvas('canvas', '', 800, 600)
    if doprint:
        canvas.Print('{}_ROC_curves.pdf['.format(prefix))

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
            hist[1].GetXaxis().SetRangeUser(axis_range, 1.0)
            hist[1].GetYaxis().SetRangeUser(axis_range, 1.0)
            hist[1].GetYaxis().SetTitleOffset(1.2)
            try:
                info = sessions[fnames[i]]
            except KeyError:
                info = fnames[i]
            text = '{} ({})'.format(classifiers[hist[0]], info)
            legend.AddEntry(hist[1], text, 'l')
            if i == 0 and j == 0:
                hist[1].SetTitle('MVA classifier ROC curves')
                hist[1].Draw('c')
            else:
                hist[1].Draw('c same')

    legend.Draw()
    canvas.SetGrid(1, 1)
    canvas.Update()
    if doprint:
        canvas.Print('{}_ROC_curves.pdf'.format(prefix))

    if doprint:
        canvas.Print('{}_ROC_curves.pdf]'.format(prefix))
    del canvas
