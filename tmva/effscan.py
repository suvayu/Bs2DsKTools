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
from utils import _import_args, RawArgDefaultFormatter

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
optparser.add_argument('-p', dest='doprint', action='store_true',
                       help='Print to png/pdf files.')
optparser.add_argument('--backend', choices=['root', 'mpl'], default='root',
                       help='Plotting backend.  root -> png, mpl -> pdf')
optparser.add_argument('-b', dest='batch', action='store_true', help='Batch mode.')
options = optparser.parse_args()
locals().update(_import_args(options))

errmsg = 'Incompatible options: {}.'
import sys
if (bkgeff or istmva) and truthmatch:
    sys.exit(errmsg.format('bkgeff and truthmatch, or istmva and truthmatch'))
if istmva and session:
    sys.exit(errmsg.format('istmva and session'))
if bool(session) != bool(conf):
    sys.exit(errmsg.format('both session and conf should be present, or not'))

from rootpy import QROOT
from ROOT import gROOT
gROOT.SetBatch(batch)
from ROOT import gPad

from rootpy.io import File, root_open
from rootpy.tree import Tree, Cut
from rootpy.plotting import Hist, Canvas

# signal and background trees
if istmva:             # TMVA output
    rfile = root_open(filename, 'read')
    tree = rfile.Get(tree)
    istmva = Cut('classID=={}'.format(int(bkgeff)))
else:
    rfile = root_open(filename, 'read')
    tree = rfile.Get(tree)
    from tmvaconfig import ConfigFile
    conf = ConfigFile(conf)
    if conf.read() > 0:
        session = conf.get_session_config(session)
    else:
        sys.exit('No sesions found!')
    istmva = Cut(str(session.cut_bkg if bkgeff else session.cut_sig))

# common cuts
truthmatch = Cut('fabs(lab0_TRUEID) == 531') if truthmatch else Cut('')
# different colour for each cut
mva_cuts = [0.1*i for i in intervals]
def colours(num, default='black'):
    cols = ['blue', 'red', 'green', 'black']
    try:
        return cols[num]
    except IndexError:
        return default

# store histograms as value
variables = {'time': [], 'terr': [], 'lab0_MM': []}
plots = {
    'time': [(0, 17), 'time [ps]'],
    'terr': [(0, 0.18), 'time error ($\delta t$) [ps]'],
    'lab0_MM': [(4600, 5800), r'$B_{s}$ mass [MeV]']
}


## make efficiency histograms
tmp = Canvas(400, 400)          # temporary canvas
for var in variables:
    for j, cut in enumerate(mva_cuts):
        sel = Cut('{}{}{}'.format(classifier, '<=' if bkgeff else '>', cut))
        base = truthmatch & istmva
        hnumer = Hist(100, *plots[var][0])
        hnumer.Sumw2()
        tree.Draw(var, selection = sel & base, hist = hnumer)
        hdenom = Hist(100, *plots[var][0])
        hdenom.Sumw2()
        tree.Draw(var, selection = base, hist = hdenom)
        heff = hnumer.Clone('heff_{}_{}'.format(var, cut))
        heff.Reset('icesm')
        heff.SetTitle(sel.latex() + '...')
        heff.Sumw2()
        heff.Divide(hnumer, hdenom, 1, 1, 'B')

        # only offset bins with content
        for b in xrange(heff.GetXaxis().GetNbins()):
            content = heff.GetBinContent(b)
            if content != 0.: heff.SetBinContent(b, content+j)

        # aesthetics
        heff.linecolor = colours(j)
        heff.markercolor = colours(j)
        heff.markersize = 0.2
        heff.SetMaximum(6)
        heff.SetMinimum(0)
        heff.SetStats(False)
        variables[var].append(heff)
del tmp


## Plots
if backend == 'root':           # ROOT
    canvas = Canvas(400, 400, 500, 10)
    for var, histos in variables.iteritems():
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
    import matplotlib.pyplot as plt
    plt.rc('font', family='Liberation Sans') # choose font
    plt.rc('mathtext', default='regular')    # use default font for math

    # ROOT to Matplotlib translation layer
    import rootpy.plotting.root2matplotlib as rplt

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages
    if doprint: pp = PdfPages('{}_eff_{}_{}.pdf'.format(
            'bkg' if bkgeff else 'sig', classifier,
            '_'.join(variables.iterkeys())))

    # Style
    from matplotlib.legend_handler import HandlerErrorbar

    # Plots
    for var, histos in variables.iteritems():
        fig = plt.figure(var)                # one figure per variable
        axes = fig.add_subplot(111)          # row, col, id (121+j, when plotting both)
        axes.grid(axis='y')
        if bkgeff:
            axes.set_title('Background rejection efficiency')
        else:
            axes.set_title('Signal selection efficiency')
        axes.set_ylim(0, 6)
        axes.set_ylabel('Efficiency (w/ offset)')
        axes.set_xlim(*plots[var][0])
        axes.set_xlabel(plots[var][1])
        axes.xaxis.set_label_coords(0.9,-0.05)
        for k, cut in enumerate(mva_cuts):
            if not histos[k].GetEntries(): continue
            line = rplt.errorbar(histos[k], xerr=None,
                                 label='{}>{}'.format(classifier, cut))[0]
        axes.legend(fontsize=10, numpoints=1, frameon=False, ncol=ncuts,
                    handler_map={mpl.lines.Line2D: HandlerErrorbar()})

        if doprint:
            pp.savefig()
        elif not batch:
            plt.show()

    if doprint: pp.close()
