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


import sys
if verbose and not lcorrns:
    print('Error: verbose depends on linear correlations!')
    optparser.print_help()
    sys.exit()

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
if not rfiles:
    files = ', '.join(files)
    sys.exit('Could not find file(s) in config: {}'.format(files))

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

def get_hists(yaml_keys, conf, tool, robj_t = None, robj_p = None):
    """Read histograms for `keys' for given `conf'"""
    hists = {}
    for rdir in conf:
        try:
            if rdir['key'] in yaml_keys:
                hists.update({
                    rdir['key']:
                    tool.read(rdir['path'], robj_t = robj_t, robj_p = robj_p)
                })
        except KeyError as err:
            if str(err) != '\'key\'': raise
    return hists


## variable distributions
if distribs:
    hists = get_hists(transforms, rfileconf, rpath_tool, robj_t = ROOT.TH1)

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
    if doprint: canvas.Print('transforms.pdf[')

    for transform in transforms:
        plotter.draw_hist(hists[transform], 'hist')
        canvas.Update()
        if doprint: canvas.Print('transforms.pdf')

    if doprint: canvas.Print('transforms.pdf]')
    del plotter


## correlation plots
if lcorrns or scatter:
    def _filter(key):
        isth1 = ROOT.TClass.GetClass(key.GetClassName()) \
                           .InheritsFrom(ROOT.TH1.Class())
        return isth1 and key.GetName().find('Signal') > 0
    hists = get_hists(['{}_corr'.format(k) for k in transforms],
                      rfileconf, rpath_tool, robj_p = _filter)

import numpy as np
opts = np.empty(shape=(14, 14), dtype=object)
tril = np.tril_indices(14)
triu = np.triu_indices(14)

## covariance matrices
if lcorrns:
    matrices = {}
    for transform in transforms:
        corrn = ROOT.TH2I(transform, 'Correlation matrix after {} transform'
                          .format(transforms[transform]),
                          14, 0, 14, 14, 0, 14)

        for i, idx in enumerate(zip(*triu)):
            histo = hists[transform+'_corr'][i*2]
            if idx[0] == idx[1]:    # set bin label using diagonal
                name = histo.GetName()
                name = name[5:name.find('_Signal')]
                varnames = name.split('_vs_', 1)
                corrn.GetXaxis().SetBinLabel(idx[0]+1, varmap[varnames[1]])
                corrn.GetYaxis().SetBinLabel(idx[1]+1, varmap[varnames[0]])
            corrn.SetBinContent(idx[0]+1, idx[1]+1, int(100*histo.GetCorrelationFactor()))

        matrices[transform] = corrn

    # colour palette
    # red = np.array([0.0, 0.0, 1.0])
    # green = np.array([0.0, 1.0, 0.0])
    # blue = np.array([1.0, 0.0, 0.0])
    # stops = np.array([0.00, 0.5, 1.0])
    # ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 50)

    canvas = ROOT.TCanvas('canvas', '', 800, 600)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.11)
    canvas.SetRightMargin(0.11)
    if doprint: canvas.Print('correlations.pdf[')
    for transform in transforms:
        matrices[transform].SetStats(False)
        matrices[transform].SetMaximum(95)
        matrices[transform].SetMinimum(-95)
        matrices[transform].Draw('colz text')
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
    opts = np.reshape(np.flipud(opts.transpose()), 14*14)

    # plots
    for transform in transforms:
        plots = np.empty(shape=(14, 14), dtype=object)

        # empty lower triangular
        for idx in zip(*tril):
            plots[idx] = []

        for i, idx in enumerate(zip(*triu)):
            plots[idx] = hists[transform+'_corr'][i*2:i*2+2]

            # plots[idx][0].SetLineColor(ROOT.kBlack)
            # plots[idx][0].SetMarkerColor(ROOT.kBlack)

            # plots[idx][1].SetLineColor(ROOT.kYellow)
            # plots[idx][1].SetMarkerColor(ROOT.kYellow)

        # reshape to match covariance matrix above
        plots = np.flipud(plots.transpose())
        hists[transform+'_corr'] = np.reshape(plots, 14*14)

    plotter = Rplot(14, 14, 5600, 5600)
    plotter.shrink2fit = False
    canvas = plotter.prep_canvas('corr_canvas')
    # if doprint: canvas.Print('correlations.pdf[')

    for transform in transforms:
        plotter.draw_hist(hists[transform+'_corr'], opts)
        canvas.Update()
        if doprint: canvas.Print('correlations_{}.png'.format(transform))
        # if doprint: canvas.Print('correlations.pdf')

    # if doprint: canvas.Print('correlations.pdf]')
    del plotter
