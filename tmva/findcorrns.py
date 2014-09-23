#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('files', metavar='file', nargs='+', help='ROOT file name')
optparser.add_argument('-c', metavar='config', dest='yamlfile',
                       default='tmva_output_description.yaml',
                       help='ROOT file description in yaml format')
optparser.add_argument('-p', dest='doprint', action='store_true',
                       default=False, help='Print to png/pdf files')
optparser.add_argument('-b', dest='batch', action='store_true',
                       default=False, help='Batch mode')
options = optparser.parse_args()
locals().update(_import_args(options))


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
import sys
if not rfiles:
    files = ', '.join(files)
    sys.exit('Could not find file(s) in config: {}'.format(files))

from rplot.rdir import Rdir
fnames = [ rfile[0]['file'] for rfile in rfiles ]
rpath_tool = Rdir(fnames)

# FIXME: only processes first file
rfileconf = rfiles[0]

transforms = {
    'identity' : 'Identity',
    'deco' : 'Decorrelate',
    'pca' : 'PCA',
    'uniform' : 'Uniform',
    'uniform_deco' : 'Uniform+Decorrelate',
    'gauss' : 'Gaussianise',
    'gauss_deco' : 'Gaussianise+Decorrelate',
}

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

## read scatter plots
hists = {}
for rdir in rfileconf:
    try:
        if rdir['key'][:-5] in transforms: # keys for corrn folder end in _corr
            def _filter(key):
                isth1 = ROOT.TClass.GetClass(key.GetClassName()) \
                                   .InheritsFrom(ROOT.TH1.Class())
                return isth1 and key.GetName().find('Signal') > 0
            hists.update({rdir['key']: rpath_tool.read(rdir['path'], robj_p = _filter)})
    except KeyError as err:
        if str(err) != '\'key\'': raise


# covariance matrices
import numpy as np
tril = np.tril_indices(14)
triu = np.triu_indices(14)

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
canvas.Print('correlations.pdf[')
for transform in transforms:
    matrices[transform].SetStats(False)
    matrices[transform].SetMaximum(95)
    matrices[transform].SetMinimum(-95)
    matrices[transform].Draw('colz text')
    canvas.Update()
    canvas.Print('correlations.pdf')
canvas.Print('correlations.pdf]')

from utils import thn_print
for transform in transforms:
    thn_print(matrices[transform])
