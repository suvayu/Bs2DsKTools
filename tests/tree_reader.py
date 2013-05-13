#!/usr/bin/python
# coding=utf-8

"""Test tree reader in python.

"""

import os
import sys

from rootpy.io import File
from rootpy.tree import Tree
from rootpy import QROOT

if QROOT.gSystem.Load('libreadTree.so') < 0:
    sys.exit('Failed to load library: libreadTree.so')

tree = File('/home/jallad/codebaby/ntuples/MC/MC11a_AfterOfflineSel/'
            'MergedTree_Bs2DsK_Ds2KKPi_BsHypo_BDTG.root').Get('DecayTree')

tree_reader = QROOT.readMCTree(tree)

# print 'Loaded ', 
# print 'Read %g bytes from tree' % tree_reader.GetEntry(0)

# print tree_reader.fChain.GetEntries()

for i in range(tree_reader.fChain.GetEntries()):
    tree_reader.LoadTree(0)
    tree_reader.fChain.GetEntry(i)
    print 'B decay time: %g' % tree_reader.lab0_TAU
    if i > 10: break
