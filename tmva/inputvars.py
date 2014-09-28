#!/usr/bin/env python
"""Different input variable plots.

   1) Distributions after different transforms (transforms.pdf).

   2) Linear correlation coefficients for different transforms
      (correlations.pdf).

   3) Scatter and profile plots for different transforms
      (correlations_<transform>.png).

"""

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
optparser.add_argument('-d', dest='distribs', action='store_true',
                       default=False, help='Plot input variable distributions')
optparser.add_argument('-l', dest='lcorrns', action='store_true',
                       default=False, help='Plot linear correlations')
optparser.add_argument('-v', dest='verbose', action='store_true',
                       default=False, help='Print linear correlation matrices')
optparser.add_argument('-s', dest='scatter', action='store_true',
                       default=False, help='Make correlation scatter plots')
options = optparser.parse_args()
locals().update(_import_args(options))


from pprint import pprint
import sys
if verbose and not lcorrns:
    print('Error: verbose depends on linear correlations!')
    optparser.print_help()
    sys.exit()

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
transforms = OrderedDict({
    'identity' : 'Identity',
    'deco' : 'Decorrelate',
    'pca' : 'PCA',
    'uniform' : 'Uniform',
    'uniform_deco' : 'Uniform+Decorrelate',
    'gauss' : 'Gaussianise',
    'gauss_deco' : 'Gaussianise+Decorrelate',
})

varmap = {
    'lab0_DIRA_OWNPV' : 'B_{s} DIRA',
    'lab0_IPCHI2_OWNPV' : 'B_{s} IP #chi^{2}',
    'lab1_IPCHI2_OWNPV' : 'h IP #chi^{2}',
    'lab1_PT' : 'h p_{T}',
    'lab2_MINIPCHI2' : 'D_{s} IP #chi^{2}',
    'lab3_IPCHI2_OWNPV' : 'D_{s} dau1 IP #chi^{2}',
    'lab4_IPCHI2_OWNPV' : 'D_{s} dau2 IP #chi^{2}',
    'lab5_IPCHI2_OWNPV' : 'D_{s} dau3 IP #chi^{2}',
    'Bs_vtx_chi2_ndof' : 'B_{s} vtx #chi^{2}',
    'Bs_radial_fd' : 'B_{s} FD',
    'Ds_radial_fd' : 'D_{s} FD',
    'Ds_vtx_chi2_ndof' : 'D_{s} vtx #chi^{2}',
    'max_ghost_prob' : 'max ghost trk prob',
    'min_Ds_child_trk_pt' : 'min D_{s} child trk p_{T}',
    'min_Ds_child_trk_chi2' : 'min D_{s} child trk #chi^{2}',
}

from fixes import ROOT
if batch: ROOT.gROOT.SetBatch(True)

from utils import get_hists
from rplot.rplot import Rplot, arrange

## variable distributions
if distribs:
    distributions = get_hists(transforms, rfileconf, rpath_tool, robj_t = ROOT.TH1)

    ROOT.gStyle.SetHatchesLineWidth(1)
    ROOT.gStyle.SetHatchesSpacing(2.5)
    for transform in transforms:
        def _style(l):
            # l.reverse()
            l[0].SetFillStyle(3345)
            l[1].SetFillStyle(3354)
        distributions[transform] = arrange(distributions[transform], 2,
                                           predicate=_style)

    plotter = Rplot(5, 3, 2000, 1200)
    plotter.alpha = 0.2
    canvas = plotter.prep_canvas()
    if doprint: canvas.Print('transforms.pdf[')

    for transform in transforms:
        plotter.draw_hist(distributions[transform], 'hist')
        canvas.Update()
        if doprint: canvas.Print('transforms.pdf')

    if doprint: canvas.Print('transforms.pdf]')
    del plotter, canvas


## correlation plots
if lcorrns or scatter:
    _filter = lambda string: lambda k: k.GetName().find(string) > 0
    sig_hists = get_hists(['{}_corr'.format(k) for k in transforms],
                          rfileconf, rpath_tool, robj_t = ROOT.TH1,
                          robj_p = _filter('Signal'))
    bkg_hists = get_hists(['{}_corr'.format(k) for k in transforms],
                          rfileconf, rpath_tool, robj_t = ROOT.TH1,
                          robj_p = _filter('Background'))
    ihists = get_hists(['file'], rfileconf, rpath_tool, robj_t = ROOT.TH1)

    # triangular matrix indices for use w/ both cov matrices & scatter plots
    import numpy as np
    dims = ihists['file'][0].GetXaxis().GetNbins() - 1 # nvars - 1 in corrn matrix
    opts = np.empty(shape=(dims, dims), dtype=object)
    tril = np.tril_indices(dims)
    triu = np.triu_indices(dims)

## covariance matrices
if lcorrns:
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
                    corrn[i].GetXaxis().SetBinLabel(idx[0]+1, varmap[varnames[1]])
                    corrn[i].GetYaxis().SetBinLabel(idx[1]+1, varmap[varnames[0]])

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
    if doprint: canvas.Print('correlations.pdf[')
    for transform in transforms:
        for hist in matrices[transform]:
            hist.SetStats(False)
            hist.SetMaximum(95)
            hist.SetMinimum(-95)
            hist.Draw('colz text')
            canvas.Update()
            if doprint: canvas.Print('correlations.pdf')
    del canvas

    # correlation in input variables
    canvas = ROOT.TCanvas('canvas', '', 1200, 600)
    # need wider margins, as bin labels are longer
    canvas.SetLeftMargin(0.2)
    canvas.SetBottomMargin(0.18)
    canvas.SetRightMargin(0.15)
    for hist in ihists['file']:
        hist.SetStats(False)
        hist.Draw('colz text')
        canvas.Update()
        if doprint: canvas.Print('correlations.pdf')
    if doprint: canvas.Print('correlations.pdf]')
    del canvas

    if verbose:
        from utils import thn_print
        for transform in transforms:
            thn_print(matrices[transform])


## draw correlation plots
if scatter:
    # options
    for idx in zip(*tril): # empty lower triangular
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
    # if doprint: canvas.Print('correlations.pdf[')

    for transform in transforms:
        plotter.draw_hist(hists[transform+'_corr'], opts)
        canvas.Update()
        if doprint: canvas.Print('correlations_{}.png'.format(transform))
        # if doprint: canvas.Print('correlations.pdf')

    # if doprint: canvas.Print('correlations.pdf]')
    del plotter, canvas
