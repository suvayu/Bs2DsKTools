#!/usr/bin/env python
"""Output a tree with sweights reading from an sweigted dataset"""

import argparse
from utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter)
parser.add_argument('rfile', help='ROOT file')
parser.add_argument('-w', '--workspace', default='wsp_w_sw_data',
                    help='Workspace name')
parser.add_argument('-d', '--dst', default='sdata_BsDsPi_both',
                    help='Name of dataset')
parser.add_argument('-o', '--out', default='sdata_tree.root',
                    help='Output ROOT file')
options = parser.parse_args()

from rplot.fixes import ROOT
ROOT.gROOT.SetBatch(True)

rfile = ROOT.TFile.Open(options.rfile)
workspace = rfile.Get(options.workspace)

sdata = workspace.data(options.dst)
varset = workspace.allVars()
# clean up xtra vars
varnames = [v.GetName() for v in varset]
_to_del = lambda name: name.find('_up') > 0 or name.find('_down') > 0
map(lambda n: varset.remove(varset[n]), filter(_to_del, varnames))
print ':: Branches in tree:'
varset.Print()

dump = ROOT.TFile.Open(options.out, 'recreate')
tree = ROOT.TTree('DecayTree', 'DecayTree')

from numpy import empty
leaves = dict(sw=empty(1, dtype=float))
map(lambda v: leaves.update([(v.GetName(), empty(1, dtype=float))]), varset)
map(lambda k: tree.Branch(k, leaves[k], '{}/D'.format(k)), leaves)

from rplot.utils import dst_iter
count = 0
large_wts = 0

for var in leaves:
    width = len(var)
    hdr = '{{:>{}}}, '.format(15 if width < 15 else width)
    print hdr.format(var),
print

for obs in dst_iter(sdata):
    count += 1
    for var in leaves:
        width = len(var)
        hdr = '{{:>{}}}, '.format(15 if width < 15 else width)
        if var == 'sw':
            leaves[var][0] = sdata.weight()
        else:
            leaves[var][0] = obs[var].getVal()
        if count < 11:
            print hdr.format(leaves[var][0]),
    if count < 11:
        print
    if abs(leaves['sw'][0]) > 2:
        print leaves['sw'][0]
        large_wts += 1
    tree.Fill()
print 'Events w/ large wts: {}'.format(large_wts)
dump.Write()
dump.Close()
