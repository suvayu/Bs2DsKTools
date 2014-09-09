#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', nargs='?', default = None, help='ROOT file')
optparser.add_argument('-t', dest='tree', default='TestTree', help='Tree name')
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

tmp = Canvas(400, 400)
canvas = Canvas(800, 400, 500, 10)
canvas.Divide(2, 1)

for var in variables:
    for i, cut in enumerate(mva_cuts):
        tmp.cd()
        sig_cut = Cut('BDTG>{}'.format(cut))
        sig_all = Cut('classID==0')
        hsig = tree.Draw(var, selection = sig_cut & sig_all)
        halls = tree.Draw(var, selection = sig_all)
        heff = [hsig.Clone('{}_{}_heffs'.format(var, cut))]
        heff[-1].Reset('icesm')
        heff[-1].SetTitle(sig_cut.latex() + '...')
        heff[-1].Divide(hsig, halls)
        heff[-1].Add(F1('{}'.format(i), 0, 8000))

        bkg_cut = Cut('BDTG<={}'.format(cut))
        bkg_all = Cut('classID==1')
        hbkg = tree.Draw(var, selection = bkg_cut & bkg_all)
        hallb = tree.Draw(var, selection = bkg_all)
        heff += [hbkg.Clone('{}_{}_heffb'.format(var, cut))]
        heff[-1].Reset('icesm')
        heff[-1].SetTitle(bkg_cut.latex() + '...')
        heff[-1].Divide(hbkg, hallb)
        heff[-1].Add(F1('{}'.format(i), 0, 8000))

        canvas.cd()
        for j, hist in enumerate(heff):
            canvas.cd(j+1)
            hist.linecolor = colours[i]
            hist.markercolor = colours[i]
            hist.markersize = 0.2
            hist.SetMaximum(6)
            hist.SetMinimum(0)
            hist.SetStats(False)
            if i == 0:          # first cut
                hist.Draw('e1')
            else:               # other cuts
                hist.Draw('e1 same')
    canvas.Modified()
    canvas.Update()
    for typ in ['png', 'pdf']:
        canvas.Print('{}_bkg_sig_eff.{}'.format(var, typ))
