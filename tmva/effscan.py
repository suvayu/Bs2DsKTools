#!/usr/bin/env python
#coding=utf-8
"""Scan observables and evaluate efficiencies

Observables scanned:
- decay time (t)
- decay time error (δt)
- Bs⁰ invariant mass

Features:
- Can toggle b/w signal selection efficiency (default) and background
  rejection efficiency.
- Classifier cuts can be specified as multiples of 0.1.
- Can operate on ntuples from TMVA output, or normal ntuples as long
  as necessary branches are present.
- Can perform truth matching when run from normal ntuples.

@author: Suvayu Ali
@email:  Suvayu dot Ali at cern dot ch

"""

import argparse
from rplot.utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(description=__doc__)
optparser.formatter_class = RawArgDefaultFormatter
optparser.add_argument('filename', help='ROOT files with signal & background events.')
optparser.add_argument('-n', dest='tree', default='DecayTree', help='Tree name.')
optparser.add_argument('-T', dest='istmva', action='store_true',
                       help='ROOT file is from TMVA output.')
optparser.add_argument('-s', '--session', help='TMVA training session')
optparser.add_argument('--conf', default='TMVA.conf', help='TMVA configuration file')
optparser.add_argument('-r', dest='bkgeff', action='store_true',
                       help='Evaluate background rejection efficiency '
                       'instead of signal selection efficiency.')
optparser.add_argument('-t', dest='truthmatch', action='store_true',
                       help='Enable truth matching for signal.')
optparser.add_argument('-c', dest='classifier', choices=['BDTA', 'BDTG', 'BDTB'],
                       default='BDTB', help='Classifier to use.')
optparser.add_argument('-i', dest='intervals', nargs='+', type=int,
                       help='Intervals of classifier cuts.')
optparser.add_argument('--title', action='store_true',
                       help='Add title to plots.')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files.')
optparser.add_argument('--backend', choices=['root', 'mpl'], default='mpl',
                       help='Plotting backend.  root -> png, mpl -> pdf')
optparser.add_argument('-b', dest='batch', action='store_true', help='Batch mode.')
options = optparser.parse_args()
locals().update(_import_args(options))

# option consistency checks
errmsg = 'Incompatible options: {}.'
import sys
if (bkgeff or istmva) and truthmatch:
    sys.exit(errmsg.format('bkgeff and truthmatch, or istmva and truthmatch'))
if istmva and session:
    sys.exit(errmsg.format('istmva and session'))
if bool(session) != bool(conf):
    sys.exit(errmsg.format('both session and conf should be present, or not'))

# batch mode
from fixes import ROOT
ROOT.gROOT.SetBatch(batch)
ROOT.gStyle.SetOptTitle(title)


## read signal and background trees, define cuts
from ROOT import TFile
if istmva:             # TMVA output
    rfile = TFile.Open(filename, 'read')
    tree = rfile.Get(tree)
    istmva = 'classID=={}'.format(int(bkgeff))
else:
    rfile = TFile.Open(filename, 'read')
    tree = rfile.Get(tree)
    from tmvaconfig import ConfigFile
    conf = ConfigFile(conf)
    if conf.read() > 0:
        session = conf.get_session_config(session)
        if not session:
            sys.exit('No matching sessions found')
    else:
        sys.exit('No sesions found!')
    istmva = str(session.cut_bkg if bkgeff else session.cut_sig)

# common cuts
truthmatch = 'abs(lab0_TRUEID) == 531' if truthmatch else ''
refcut = '{}&&{}'.format(truthmatch, istmva)

# classifier cuts
mva_cuts = [0.1*i for i in intervals]

# per-variable efficiency histograms, ranges, and titles
variables = {
    # var : [histograms, var-range, matplotlib title, ROOT title]
    'time': [[], (0, 15), 'time [ps]', 'time [ps]'],
    'terr': [[], (0, 0.12), 'time error ($\delta t$) [ps]', 'time error (#delta t) [ps]'],
    'lab0_MM': [[], (4700, 5700), r'$B_{s}$ mass [MeV]', 'B_{s} mass [MeV]']
}


## make efficiency histograms
from ROOT import TH1D, TCanvas
tmp = TCanvas('c', '', 400, 400)          # temporary canvas
from utils import scan_range, make_varefffn, colours
from rplot.utils import th1offset
for var in variables:
    htemp = TH1D('htemp', '', 100, *variables[var][1])
    # iterates over mva_cuts, returns list of efficiency histograms
    variables[var][0] = scan_range(make_varefffn(htemp, refcut),
                                   mva_cuts, classifier, tree, var)
    del htemp

    # aesthetics
    for j in xrange(len(mva_cuts)):
        heff = variables[var][0][j]
        if j > 0: th1offset(heff, j)
        heff.SetYTitle('Efficiency (w/ offset)')
        heff.SetXTitle(variables[var][3])
        heff.SetLineColor(colours(j))
        heff.SetMarkerColor(colours(j))
        heff.SetMarkerSize(0.2)
        heff.SetMaximum(3.5)
        heff.SetMinimum(0)
        heff.SetStats(False)
del tmp


## Plots
if backend == 'root':           # ROOT
    canvas = TCanvas('canvas', '', 800, 550)
    for var, histos in variables.iteritems():
        histos = histos[0]      # drop metadata
        for k, cut in enumerate(mva_cuts):
            opts = 'e1' if k == 0 else 'e1 same'
            histos[k].Draw(opts)
        canvas.Modified()
        canvas.Update()
        if doprint:
            canvas.Print('{}_eff_{}_{}.png'.format(
                'bkg' if bkgeff else 'sig', classifier, var))
    del canvas
else:                           # Matplotlib
    ncuts = len(mva_cuts)

    import matplotlib as mpl
    if batch: mpl.use('pdf')    # plotting w/o X11
    mpl.rc('font', family='Liberation Sans') # choose font
    mpl.rc('mathtext', default='regular')    # use default font for math

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf
    if doprint: pp = PdfPages('{}_eff_{}_{}.pdf'.format(
            'bkg' if bkgeff else 'sig', classifier,
            '_'.join(variables.iterkeys())))

    # use the API
    from matplotlib.figure import Figure
    # Style
    from matplotlib.legend_handler import HandlerErrorbar
    from rplot.r2mpl import th12errorbar

    # Plots
    for var, histos in variables.iteritems():
        histos = histos[0]          # drop metadata
        fig = Figure()              # one figure per variable
        canvas = FigureCanvasPdf(fig)
        axes = fig.add_subplot(111) # row, col, id (121+j, when plotting both)
        axes.grid(axis='y')
        if title:
            if bkgeff:
                axes.set_title('Background rejection efficiency')
            else:
                axes.set_title('Signal selection efficiency')
        axes.set_ylim(0, 3.5)
        axes.set_ylabel('Efficiency (w/ offset)')
        axes.set_xlim(*variables[var][1])
        axes.set_xlabel(variables[var][2])
        axes.xaxis.set_label_coords(0.9,-0.05)
        for k, cut in enumerate(mva_cuts):
            if not histos[k].GetEntries(): continue
            x, y, yerr = th12errorbar(histos[k], yerr=True, asym=True)
            axes.errorbar(x, y, yerr=yerr, xerr=None, fmt='none',
                          label='{}>{}'.format(classifier, cut))
        axes.legend(fontsize=10, numpoints=1, frameon=False, ncol=ncuts,
                    handler_map={mpl.lines.Line2D: HandlerErrorbar()})

        if doprint: pp.savefig(fig) # pp.savefig() for current fig

    if doprint: pp.close()

