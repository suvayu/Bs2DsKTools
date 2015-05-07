#!/usr/bin/env python
"""Draw ROC (Receiver Operating Characteristic) curves

Draws ROC curves for different MVA classifiers from the TMVA output
files.  It generates the curves by looking at efficiencies for
different MVA classifier cuts from a ROOT tree where the classifier
variable is present as a branch.

"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-r', dest='axis_range', type=float, default=0.6,
                       help='Axis range')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files')
optparser.add_argument('--mpl', dest='usempl', action='store_true',
                       help='Use Matplotlib')
optparser.add_argument('-b', '--batch', action='store_true', help='Batch mode')
optparser.add_argument('-c', dest='clnameglob', metavar='classifier',
                       help='Only plot matching classifiers (globs allowed)')
optparser.add_argument('-m', '--marks', action='store_true',
                       help='Toggle markers')
options = optparser.parse_args()
locals().update(_import_args(options))


import sys

from utils import plot_conf
rfiles = plot_conf(options.yamlfile, 'TMVA.root', options.files)
if not rfiles:
    sys.exit('Config parsing error.')

# FIXME: only processes first file
rfileconf = rfiles[0]

from config import classifiers, sessions

if options.clnameglob:
    # only process matching classifiers
    from fnmatch import fnmatchcase
    for key in classifiers:
        if not fnmatchcase(key, options.clnameglob):
            del classifiers[key]

from fixes import ROOT
ROOT.gROOT.SetBatch(options.batch)

fnames = [f[0]['file'] for f in rfiles]


def get_hists(classifiers, rfile, name, marks):
    from ROOT import TProfile, TPolyMarker
    from numpy import linspace
    from array import array
    rfile = ROOT.TFile.Open(rfile)
    tree = rfile.Get(name)
    sig, bkg = 'classID=={}'.format(0), 'classID=={}'.format(1)
    hists = {}
    marks = {} if marks else None
    for cl in classifiers:
        name = '{}_{}'.format(cl, rfile.GetName().split('/', 1)[0])
        nsig = float(tree.GetEntries(sig))
        nbkg = float(tree.GetEntries(bkg))
        # variable bin width
        bins = array('f', [1.0/(-i*0.5-1) + 1 for i in xrange(100)] + [1])
        hist = TProfile('h_{}'.format(name), 'ROC curve ({})'.format(cl),
                        100, bins)
        hist.SetDirectory(0)    # otherwise current file owns histogram
        if isinstance(marks, dict):
            xmark, ymark = array('f'), array('f')
        for i, cut in enumerate(linspace(-1, 1, 1001)):
            cutstr = '{}>{}'.format(cl, cut)
            eff_s = tree.GetEntries('{}&&{}'.format(sig, cutstr))/nsig
            eff_b = 1 - tree.GetEntries('{}&&{}'.format(bkg, cutstr))/nbkg
            hist.Fill(eff_s, eff_b)
            if isinstance(marks, dict):
                if cl == 'BDTB':
                    window = -0.3 <= cut and cut <= 0.3
                    step = not i % 10
                else:
                    window = -0.9 <= cut and cut <= 0.9
                    step = not i % 50
                if window and step:
                    xmark.append(eff_s)
                    ymark.append(eff_b)
        hists[cl] = hist
        if isinstance(marks, dict):
            marks[cl] = TPolyMarker(len(xmark), xmark, ymark)
            print '{}: {} marks'.format(cl, len(xmark))
            for pt in zip(xmark, ymark): print pt,
            print
    return hists, marks

# from utils import thn_print
rocs, markers = [], []
for i, rfileconf in enumerate(rfiles):
    roc, marks = get_hists(classifiers, rfileconf[0]['file'], 'TestTree',
                           options.marks)
    rocs.append(roc)
    markers.append(marks)

# config
axis_range = options.axis_range
doprint = options.doprint

if options.usempl:                      # FIXME: no idea if it works
    # Matplotlib
    import matplotlib.pyplot as plt
    plt.rc('font', family='Liberation Sans')  # choose font
    plt.rc('mathtext', default='regular')     # use default font for math

    # ROOT to Matplotlib translation layer
    import rootpy.plotting.root2matplotlib as rplt

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages
    if doprint:
        pp = PdfPages('ROC_curves_mpl.pdf')

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
        canvas.Print('my_ROC_curves.pdf[')

    cols = (ROOT.kAzure, ROOT.kRed, ROOT.kBlack)
    coln = 0
    legend = ROOT.TLegend(0.12, 0.15, 0.8, 0.6)
    legend.SetHeader('MVA classifiers')
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    ROOT.gStyle.SetOptStat(False)

    from utils import th1integral, distance
    for i, roc in enumerate(rocs):
        for cl, hist in roc.iteritems():
            # metrics
            print '=> {}:: integral: {}, distance: {}'.format(
                cl,
                th1integral(hist),
                distance(hist, (1, 1))
            )
            hist.SetLineStyle(i+1)
            hist.SetLineColor(cols[coln])
            hist.GetXaxis().SetRangeUser(axis_range, 1.05)
            hist.GetYaxis().SetRangeUser(axis_range, 1.05)
            try:
                info = sessions[fnames[i]]
            except KeyError:
                info = fnames[i]
            text = '{} ({})'.format(classifiers[cl], info)
            legend.AddEntry(hist, text, 'l')
            if i == 0 and coln == 0:
                hist.SetTitle('MVA classifier ROC curves')
                hist.Draw('e')
            else:
                hist.Draw('e same')
            if marks:
                polymarker = markers[i][cl]
                polymarker.SetMarkerStyle(ROOT.kFullCircle)
                polymarker.SetMarkerColor(cols[coln])
                polymarker.Draw()
            coln += 1           # next colour

    legend.Draw()
    canvas.SetGrid(1, 1)
    canvas.Update()
    if doprint:
        canvas.Print('my_ROC_curves.pdf')
        canvas.Print('my_ROC_curves.pdf]')
    del canvas
