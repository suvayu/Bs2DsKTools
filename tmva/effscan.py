#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', nargs='?', default = None, help='ROOT file')
optparser.add_argument('-t', dest='tree', default='TestTree', help='Tree name')
optparser.add_argument('-p', dest='doprint', action='store_true', default=False, help='Print to png/pdf files')
options = optparser.parse_args()
locals().update(_import_args(options))

from rootpy import QROOT
from ROOT import gROOT
# gROOT.SetBatch(True)
from ROOT import gPad

from rootpy.io import File, root_open
from rootpy.tree import Tree, Cut
from rootpy.plotting import Canvas, F1

mva_cuts = [0.1*i for i in [2, 3, 5, 6]]
colours = ['blue', 'red', 'green', 'black']
variables = ['time', 'terr', 'lab0_MM']

rfile = root_open(filename, 'read')
tree = rfile.Get(tree)

tmp = Canvas(400, 400)          # temporary canvas
hists = [[], []]                # stored histograms: sig, bkg
for var in variables:
    for i in (0, 1):            # sig, bkg
        for j, cut in enumerate(mva_cuts):
            cuts = [Cut('BDTG>{}'.format(cut)), Cut('BDTG<={}'.format(cut))]
            allevts = Cut('classID=={}'.format(i))
            hnumerator = tree.Draw(var, selection = cuts[i] & allevts)
            hdenominator = tree.Draw(var, selection = allevts)
            heff = hnumerator.Clone('heff{}_{}_{}'.format(i, var, cut))
            heff.Reset('icesm')
            heff.SetTitle(cuts[i].latex() + '...')
            heff.Divide(hnumerator, hdenominator)
            heff.Add(F1('{}'.format(j), 0, 8000)) # offset for visibility

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
        for typ in ['png', 'pdf']:
            canvas.Print('{}_bkg_sig_eff.{}'.format(var, typ))
