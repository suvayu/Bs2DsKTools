#!/usr/bin/env python
"""Different input variable plots.

   1) Distributions after different transforms (transforms.pdf).

   2) Linear correlation coefficients for different transforms
      (correlations.pdf).

   3) Scatter and profile plots for different transforms
      (correlations_<transform>.png).

"""

import argparse
from rplot.utils import RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file')
optparser.add_argument('--config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('--schema', default='TMVA_Id.root',
                       help='ROOT file schema to choose from config file')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=True, help='Print to png/pdf files')
optparser.add_argument('-b', '--batch', action='store_true', help='Batch mode')
optparser.add_argument('-t', dest='transglob', metavar='transform',
                       help='Only plot matching transforms (globs allowed)')
optparser.add_argument('-d', dest='distribs', action='store_true',
                       help='Plot input variable distributions')
optparser.add_argument('-l', dest='lcorrns', action='store_true',
                       help='Plot linear correlations')
optparser.add_argument('-v', dest='verbose', action='store_true',
                       help='Print linear correlation matrices')
optparser.add_argument('-s', dest='scatter', action='store_true',
                       help='Make correlation scatter plots')
optparser.add_argument('--title', action='store_true',
                       help='Add title to plots')
optparser.add_argument('--dump', default=None, type=str,
                       help='Dump correlation plots matching glob')
options = optparser.parse_args()


from pprint import pprint
import sys
if options.verbose and not options.lcorrns:
    print('Error: verbose depends on linear correlations!')
    optparser.print_help()
    sys.exit()

from utils import plot_conf
rfiles = plot_conf(options.yamlfile, options.schema, options.files)
if not rfiles:
    sys.exit('Config parsing error.')

from rplot.rdir import Rdir
fnames = [rfile[0]['file'] for rfile in rfiles]
pathtool = Rdir(fnames)

# FIXME: only processes first file
rfileconf = rfiles[0]

# guess session from file name
from utils import session_from_path
session = session_from_path(rfileconf[0]['file'])
prefix = 'plots/{}'.format(session)

from config import transforms

from fnmatch import fnmatchcase
if options.transglob:
    # only process matching transforms
    for key in transforms:
        if not fnmatchcase(key, options.transglob):
            del transforms[key]

from fixes import ROOT
ROOT.gROOT.SetBatch(options.batch)
ROOT.gStyle.SetOptTitle(options.title)

from utils import get_hists

from rplot.rplot import Rplot, arrange, partition

## variable distributions
if options.distribs:
    # histogram order: signal, background (repeat for diff transforms)
    distributions = get_hists(transforms, rfileconf, pathtool, robj_t=ROOT.TH1)

    ROOT.gStyle.SetHatchesLineWidth(1)
    ROOT.gStyle.SetHatchesSpacing(2.5)
    for transform in transforms:
        def _style(l):
            # l.reverse()
            l[0].SetFillStyle(3345)
            l[1].SetFillStyle(3354)
        distributions[transform] = arrange(distributions[transform], 2,
                                           predicate=_style)

    plotter = Rplot(3, 3, 2000, 1200)
    plotter.alpha = 0.2
    canvas = plotter.prep_canvas()
    if options.doprint:
        canvas.Print('{}_transforms.pdf['.format(prefix))

    def _plot_n_print(hlist, plotter=plotter, canvas=canvas):
        plotter.draw_hist(hlist, 'hist')
        canvas.Update()
        if options.doprint:
            canvas.Print('{}_transforms.pdf'.format(prefix))

    for transform in transforms:
        if len(distributions[transform]) > plotter.nplots:
            for hists in partition(distributions[transform], plotter.nplots):
                _plot_n_print(hists)
        else:
            _plot_n_print(distributions[transform])

    if options.doprint:
        canvas.Print('{}_transforms.pdf]'.format(prefix))
    del plotter, canvas


## correlation plots
if options.lcorrns or options.scatter:
    _filter = lambda string: lambda k: k.GetName().find(string) > 0
    sig_hists = get_hists(['{}_corr'.format(k) for k in transforms],
                          rfileconf, pathtool, robj_t=ROOT.TH1,
                          robj_p=_filter('Signal'))
    bkg_hists = get_hists(['{}_corr'.format(k) for k in transforms],
                          rfileconf, pathtool, robj_t=ROOT.TH1,
                          robj_p=_filter('Background'))
    ihists = get_hists(['file'], rfileconf, pathtool, robj_t=ROOT.TH1)

    # triangular matrix indices for use w/ both cov matrices & scatter plots
    import numpy as np
    dims = ihists['file'][0].GetXaxis().GetNbins() - 1  # nvars - 1 in corrn matrix
    opts = np.empty(shape=(dims, dims), dtype=object)
    tril = np.tril_indices(dims)
    triu = np.triu_indices(dims)

## covariance matrices
from utils import get_label
if options.lcorrns:
    matrices = {}
    for transform in transforms:
        corrn = [
            ROOT.TH2D(transform+'_sig', 'Correlation matrix after {} transform (sig)'
                      .format(transforms[transform]), dims, 0, dims, dims, 0, dims),
            ROOT.TH2D(transform+'_bkg', 'Correlation matrix after {} transform (bkg)'
                      .format(transforms[transform]), dims, 0, dims, dims, 0, dims)
            ]

        for i, idx in enumerate(zip(*triu)):
            hist = [
                sig_hists[transform+'_corr'][i*2],
                bkg_hists[transform+'_corr'][i*2]
            ]

            if idx[0] == idx[1]:    # set bin label using diagonal
                for i in xrange(len(hist)):
                    name = hist[i].GetName()
                    if i == 0:
                        name = name[5:name.find('_Signal')]
                    else:
                        name = name[5:name.find('_Background')]
                    varnames = name.split('_vs_', 1)
                    corrn[i].GetXaxis().SetBinLabel(idx[0]+1, get_label(varnames[1]))
                    corrn[i].GetYaxis().SetBinLabel(idx[1]+1, get_label(varnames[0]))

            for i in xrange(len(corrn)):
                corrn[i].SetBinContent(idx[0]+1, idx[1]+1, 100*hist[i].GetCorrelationFactor())

        matrices[transform] = corrn

    # colour palette
    # red = np.array([0.0, 0.0, 1.0])
    # green = np.array([0.0, 1.0, 0.0])
    # blue = np.array([1.0, 0.0, 0.0])
    # stops = np.array([0.00, 0.5, 1.0])
    # ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 50)

    # correlation after various transforms
    canvas = ROOT.TCanvas('canvas', '', 800, 600)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.11)
    canvas.SetRightMargin(0.11)
    ROOT.gStyle.SetPaintTextFormat('2.f')
    if options.doprint:
        canvas.Print('{}_correlations.pdf['.format(prefix))
    for transform in transforms:
        for hist in matrices[transform]:
            hist.SetStats(False)
            hist.SetMaximum(95)
            hist.SetMinimum(-95)
            hist.Draw('colz text')
            canvas.Update()
            if options.doprint:
                canvas.Print('{}_correlations.pdf'.format(prefix))
    del canvas

    # correlation in input variables
    canvas = ROOT.TCanvas('canvas', '', 1200, 600)
    # need wider margins, as bin labels are longer
    canvas.SetLeftMargin(0.2)
    canvas.SetBottomMargin(0.18)
    canvas.SetRightMargin(0.15)
    for hist in ihists['file']:
        hist.SetStats(False)
        axes = (hist.GetXaxis(), hist.GetYaxis())
        for axis in axes:
            sz = 1 + axis.GetNbins()
            for i in xrange(1, sz):
                axis.SetBinLabel(i, get_label(axis.GetBinLabel(i)))
        hist.SetMarkerColor(ROOT.kBlack)
        hist.Draw('colz text')
        canvas.Update()
        if options.doprint:
            canvas.Print('{}_correlations.pdf'.format(prefix))
    if options.doprint:
        canvas.Print('{}_correlations.pdf]'.format(prefix))
    del canvas

    if options.verbose:
        from utils import thn_print
        for transform in transforms:
            thn_print(matrices[transform])


## draw correlation plots
if options.scatter:
    # options
    for idx in zip(*tril):  # empty lower triangular
        opts[idx] = []

    for idx in zip(*triu):
        opts[idx] = ['scat', '']

    # reshape to match covariance matrix above
    opts = np.reshape(np.flipud(opts.transpose()), dims*dims)

    # plots
    hists = {}
    for transform in transforms:
        plots = np.empty(shape=(dims, dims), dtype=object)

        # empty lower triangular
        for idx in zip(*tril):
            plots[idx] = []

        for i, idx in enumerate(zip(*triu)):
            plots[idx] = sig_hists[transform+'_corr'][i*2:i*2+2]

            # plots[idx][0].SetLineColor(ROOT.kBlack)
            # plots[idx][0].SetMarkerColor(ROOT.kBlack)

            # plots[idx][1].SetLineColor(ROOT.kYellow)
            # plots[idx][1].SetMarkerColor(ROOT.kYellow)

        # reshape to match covariance matrix above
        plots = np.flipud(plots.transpose())
        hists[transform+'_corr'] = np.reshape(plots, dims*dims)

    plotter = Rplot(dims, dims, 5600, 5600)
    plotter.shrink2fit = False
    canvas = plotter.prep_canvas('corr_canvas')
    # if options.doprint:
    #     canvas.Print('{}_correlation_grid.pdf['.format(prefix))

    def _draw_match(fname, hists):
        for pair in hists:
            myc = None
            for obj in pair:
                if fnmatchcase(obj.GetName(), options.dump):
                    xaxis, yaxis = obj.GetXaxis(), obj.GetYaxis()
                    xaxis.SetTitle(get_label(xaxis.GetTitle()))
                    yaxis.SetTitle(get_label(yaxis.GetTitle()))
                    yaxis.SetTitleOffset(1.25)
                    if not myc:
                        myc = ROOT.TCanvas('myc', '', 800, 500)
                        myc.cd()
                        obj.Draw()
                    else:
                        obj.Draw('same')
            if myc:
                myc.Print(fname)
            del myc

    # def _write(rfile, hists):
    #     for pair in hists:
    #         map(lambda h: rfile.WriteTObject(h) if h else None, pair)

    if options.dump:
        rfile = ROOT.TFile.Open('correlation_hists.root', 'recreate')

    for transform in transforms:
        plotter.draw_hist(hists[transform+'_corr'], opts)
        canvas.Update()
        if options.dump:
            # _write(rfile, hists[transform+'_corr'])
            _draw_match('{}_matched_corrln_{}.pdf'.format(prefix, transform),
                        hists[transform+'_corr'])
        if options.doprint:
            canvas.Print('{}_corrln_grid_{}.png'.format(prefix, transform))
            # canvas.Print('{}_correlation_grid.pdf'.format(prefix))

    # if options.doprint:
    #     canvas.Print('{}_correlation_grid.pdf]'.format(prefix))
    del plotter, canvas
