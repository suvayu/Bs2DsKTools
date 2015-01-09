#!/usr/bin/env python
"""Draw classifier comparison plots (ROC curves)"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-r', dest='axis_range', type=float, default=0.6, help='Axis range')
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


import sys

from utils import plot_conf
rfiles = plot_conf(yamlfile, 'TMVA.root', files)
if not rfiles: sys.exit('Config parsing error.')

# FIXME: only processes first file
rfileconf = rfiles[0]

from config import classifiers, sessions

if clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, clnameglob): del classifiers[key]

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

fnames = [f[0]['file'] for f in rfiles]

def get_hists(classifiers, rfile, name):
    from ROOT import TFile, TTree, TProfile
    from numpy import linspace
    from array import array
    rfile = TFile.Open(rfile)
    tree = rfile.Get(name)
    sig, bkg = 'classID=={}'.format(0), 'classID=={}'.format(1)
    hists = {}
    for cl in classifiers:
        name = '{}_{}'.format(cl, rfile.GetName().split('/',1)[0])
        nsig = float(tree.GetEntries(sig))
        nbkg = float(tree.GetEntries(bkg))
        # variable bin width
        bins = array('f', [1.0/(-i*0.3-1) + 1 for i in xrange(200)] + [1])
        hist = TProfile('h_{}'.format(name), 'ROC curve ({})'.format(cl),
                        200, bins)
        hist.SetDirectory(0)    # otherwise current file owns histogram
        for i, cut in enumerate(linspace(-1, 1, 1001)):
            cut = '{}>{}'.format(cl, cut)
            eff_s = tree.GetEntries('{}&&{}'.format(sig, cut))/nsig
            eff_b = 1 - tree.GetEntries('{}&&{}'.format(bkg, cut))/nbkg
            hist.Fill(eff_s, eff_b)
        hists[cl] = hist
    return hists

from utils import thn_print
rocs = []
for i, rfileconf in enumerate(rfiles):
    roc = get_hists(classifiers, rfileconf[0]['file'], 'TestTree')
    # map(lambda k: thn_print(roc[k]), roc)
    rocs.append(roc)

if usempl:                      # FIXME: no idea if it works
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
        axes.set_xlim(axis_range, 1)
        axes.set_ylim(axis_range, 1)
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
    if doprint: canvas.Print('my_ROC_curves.pdf[')

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
            hist[1].GetXaxis().SetRangeUser(axis_range, 1.05)
            hist[1].GetYaxis().SetRangeUser(axis_range, 1.05)
            try:
                info = sessions[fnames[i]]
            except KeyError:
                info = fnames[i]
            text = '{} ({})'.format(classifiers[hist[0]], info)
            legend.AddEntry(hist[1], text, 'l')
            if i ==0 and j == 0:
                hist[1].SetTitle('MVA classifier ROC curves')
                hist[1].Draw('e')
            else:
                hist[1].Draw('e same')

    legend.Draw()
    canvas.SetGrid(1, 1)
    canvas.Update()
    if doprint: canvas.Print('my_ROC_curves.pdf')

    if doprint: canvas.Print('my_ROC_curves.pdf]')
    del canvas
