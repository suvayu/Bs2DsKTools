#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filenames', nargs='+', help='ROOT file')
optparser.add_argument('-n', dest='tree', default='TestTree', help='Tree name')
optparser.add_argument('-c', dest='classifier', choices=['BDTA', 'BDTG', 'BDTB'],
                       default='BDTB', help='Classifier to use.')
optparser.add_argument('-t', dest='truthmatch', action='store_true', default=False, help='Enable truth matching for signal')
optparser.add_argument('-p', dest='doprint', action='store_true', default=False, help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true', default=False, help='Batch mode')
options = optparser.parse_args()
locals().update(_import_args(options))

from rootpy import QROOT
from ROOT import gROOT
gROOT.SetBatch(batch)
from ROOT import gPad

from rootpy.io import File, root_open
from rootpy.tree import Tree, Cut
from rootpy.plotting import Canvas, F1

mva_cuts = [0.1*i for i in [2, 3, 5, 6]]
colours = ['blue', 'red', 'green', 'black']
variables = ['time', 'terr', 'lab0_MM']
truthmatch = Cut('abs(lab0_TRUEID) == 531') if truthmatch else Cut('')

for n, fname in enumerate(filenames):
    rfile = root_open(fname, 'read')
    tree = rfile.Get(tree)

    tmp = Canvas(400, 400)          # temporary canvas
    hists = [[], []]                # stored histograms: sig, bkg
    for var in variables:
        for i in (0, 1):            # sig, bkg
            for j, cut in enumerate(mva_cuts):
                cuts = [Cut('{}>{}'.format(classifier, cut)),
                        Cut('{}<={}'.format(classifier, cut))]
                if 0 == i:      # signal
                    allevts = Cut('classID=={}'.format(i)) & truthmatch
                else:
                    allevts = Cut('classID=={}'.format(i))
                hnumerator = tree.Draw(var, selection = cuts[i] & allevts)
                hdenominator = tree.Draw(var, selection = allevts)
                heff = hnumerator.Clone('heff{}_{}_{}'.format(i, var, cut))
                heff.Reset('icesm')
                heff.SetTitle(cuts[i].latex() + '...')
                heff.Divide(hnumerator, hdenominator)
                # only offset bins with content
                for b in xrange(heff.GetXaxis().GetNbins()):
                    content = heff.GetBinContent(b)
                    if content != 0.: heff.SetBinContent(b, content+j)

                # aesthetics
                heff.linecolor = colours[j]
                heff.markercolor = colours[j]
                heff.markersize = 0.2
                heff.SetMaximum(6)
                heff.SetMinimum(0)
                heff.SetStats(False)
                hists[i].append(heff)

    ## Plots
    nvars = len(variables)
    ncuts = len(mva_cuts)

    # ROOT
    canvas = Canvas(800, 400, 500, 10)
    canvas.Divide(2, 1)
    for i, var in enumerate(variables):
        for j in (0, 1):        # sig, bkg
            canvas.cd(j+1)
            for k, cut in enumerate(mva_cuts):
                opts = 'e1' if k == 0 else 'e1 same'
                hists[j][i*ncuts + k].Draw(opts)
        canvas.Modified()
        canvas.Update()
        if doprint:
            for typ in ['png']: #, 'pdf']:
                canvas.Print('{}_bkg_sig_eff_{}.{}'.format(var, n, typ))
    del tmp, canvas             # clean up

    # Matplotlib
    import matplotlib.pyplot as plt
    plt.rc('font', family='Liberation Sans') # choose font
    plt.rc('mathtext', default='regular')    # use default font for math

    # ROOT to Matplotlib translation layer
    import rootpy.plotting.root2matplotlib as rplt

    # PDF backend
    from matplotlib.backends.backend_pdf import PdfPages
    if doprint: pp = PdfPages('bkg_sig_eff_{}.pdf'.format(n))

    # Style
    from matplotlib.legend_handler import HandlerErrorbar

    # Plots
    for i, var in enumerate(variables):
        fig = plt.figure(var)                # one figure per variable
        for j in (0, 1):                     # sig, bkg
            if j == 1: continue              # only plot signal now
            axes = fig.add_subplot(111)  # row, col, id (121+j, when plotting both)
            axes.grid(axis='y')
            axes.set_title('Signal selection efficiency')
            axes.set_ylim(0, 6)
            axes.set_ylabel('Efficiency (w/ offset)')
            if var == 'time':
                xlo, xhi = 0, 20
                var = 'time [ps]'
            elif var == 'terr':
                xlo, xhi = 0, 0.27
                var = 'time error [ps]'
            elif var == 'lab0_MM':
                xlo, xhi = 4600, 7000
                var = r'$B_{s}$ mass [MeV]'
            axes.set_xlim(xlo, xhi)
            axes.set_xlabel(var)
            axes.xaxis.set_label_coords(0.9,-0.05)
            for k, cut in enumerate(mva_cuts):
                line = rplt.errorbar(hists[j][i*ncuts + k], xerr=None,
                                     label='{}>{}'.format(classifier, cut))[0]
            axes.legend(fontsize=10, numpoints=1, frameon=False, ncol=ncuts,
                        handler_map={type(line): HandlerErrorbar()})

        if doprint:
            pp.savefig()
        elif not batch:
            plt.show()

    if doprint: pp.close()
