#!/usr/bin/env python
# coding=utf-8
"""Plot random things from Monte Carlo

Look at different things (pT, χ², η, ..) that might be affected by
PIDK cuts.  The goal is to find something that influences the Bs decay
time distribution which in turn leads to less DsK events for very
small decay times (< 0.5 ps).

\033[1mNon-standard dependencies\033[0m: rootpy.{io,tree,plotting}

@author Suvayu Ali
@date   [2013-04-29 Mon]

"""

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                       help='Print plots to png/pdf files')
optparser.formatter_class = argparse.RawDescriptionHelpFormatter
options = optparser.parse_args()
doPrint = options.doPrint

# Python modules
import os
import sys
from collections import OrderedDict

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
if doPrint: gROOT.SetBatch(True)

from ROOT import gPad, gDirectory

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow, kCyan
from ROOT import kPlus, kFullDotMedium, kFullDotSmall

# ROOT classes
from ROOT import TCanvas, TLegend

# rootpy modules
from rootpy.io import File
from rootpy.tree import Tree
from rootpy.tree import Cut
from rootpy.plotting import Hist


## Read from file
modes = OrderedDict([('dsk',0), ('dspi',1)])

# chains = (                       # 0 - DsK, 1 - Dsπ
#     TreeChain('DecayTree', glob.glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsK*BsHypo_BDTG.root')),
#     TreeChain('DecayTree', glob.glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsPi*BsHypo_BDTG.root'))
# )

trees = (                       # 0 - DsK, 1 - Dsπ
    File('data/smalltree-really-new-MC-pre-PID-DsK.root').Get('ftree'),
    File('data/smalltree-really-new-MC-pre-PID-DsPi.root').Get('ftree')
)

histograms = []                 # list of pairs, each element is [hdsk, hdspi]

variables = ('Pt', 'Eta')

cuts = {
    'nocuts'    : Cut(''),
    'timelt1ps' : Cut('time<1.0'),
    'dsk'       : Cut('PIDK>10'),
    'dspi'      : Cut('PIDK<0'),
    'bdt'       : Cut('BDTG>0.5'),
    'HLT1'      : Cut('HLT1TrackAllL0TOS > 0'),
    'HLT22Body' : Cut('HLT2Topo2BodyTOS > 0'),
    'HLT23Body' : Cut('HLT2Topo3BodyTOS > 0'),
    'HLT24Body' : Cut('HLT2Topo4BodyTOS > 0')
    # 'HLT1'      : Cut('lab0_Hlt1TrackAllL0Decision_TOS > 0'),
    # 'HLT22Body' : Cut('lab0_Hlt2Topo4BodyBBDTDecision_TOS > 0'),
    # 'HLT23Body' : Cut('lab0_Hlt2Topo3BodyBBDTDecision_TOS > 0'),
    # 'HLT24Body' : Cut('lab0_Hlt2Topo2BodyBBDTDecision_TOS > 0')
}
cuts.update(dict(HLT2 = cuts['HLT22Body'] | cuts['HLT23Body'] | cuts['HLT24Body']))
cuts.update(dict(trig = cuts['HLT1'] & cuts['HLT2']))

htypes = [
    'nocuts', 'pid', 'bdt', 'trig',    # base
    'pid_bdt', 'pid_trig', 'bdt_trig', # permutations of 2
    'pid_bdt_trig'                     # all
]


## pT and η distributions for different cuts
for htype in htypes:
    for var in variables:
        if var == 'Pt':
            binning = (100, 0.0, 20000.0)
        elif var == 'Eta':
            binning = (100, 1.5, 5.0)
        else:
            print 'Unknown variable, weird things will happen.'
        hpair = []
        for mode in modes:
            # ensure identical binning
            hist = Hist(*binning, name='h' + mode + '_' + htype + '_' + var, type='D')
            cut = cuts['timelt1ps']
            cut_tokens = htype.split('_')
            for token in cut_tokens:
                if token.find('nocuts') >= 0:
                    pass
                elif token.find('pid') >= 0:
                    cut = cut & cuts[mode]
                elif token.find('bdt') >= 0:
                    cut = cut & cuts['bdt']
                elif token.find('trig') >= 0:
                    cut = cut & cuts['trig']
                else:
                    print 'Unknown permutation of cuts, weird things will happen.'
            hpair.append(trees[modes[mode]].Draw('hMom.%s()' % var, cut, '', hist))
        histograms.append(hpair)


## plot distributions
canvas = TCanvas('canvas', '', 1600, 500)
canvas.Divide(2,1)

# open file
plotfile = 'plots/timelt1ps_%s.pdf' % '_'.join(variables)
if doPrint:
    canvas.Print(plotfile + '[')

# create legend
legend = TLegend(0.65, 0.5, 0.85, 0.65)
legend.SetLineColor(0)
legend.SetFillStyle(0)

# draw distributions side by side
for idx in enumerate(histograms):
    canvas.cd(idx[0] % 2 + 1)
    var = variables[idx[0] % len(variables)]
    legend.SetHeader('%s for %s ps' % (var, cuts['timelt1ps'].str))
    for mode in modes.iteritems():
        htitle = ' '.join(idx[1][mode[1]].GetName().split('_')[1:])
        idx[1][mode[1]].SetTitle(htitle + ';%s' % var)
        if mode[0] == 'dsk':
            idx[1][mode[1]].SetLineColor(kBlue)
            idx[1][mode[1]].DrawNormalized('hist')
            legend.AddEntry(idx[1][mode[1]], 'DsK', 'l')
        if mode[0] == 'dspi':
            idx[1][mode[1]].SetLineColor(kRed)
            idx[1][mode[1]].DrawNormalized('hist same')
            legend.AddEntry(idx[1][mode[1]], 'Ds#pi', 'l')
    legend.Draw()
    if idx[0] % 2 > 0:
        canvas.Update()
        if doPrint:
            canvas.Print(plotfile)
    legend.Clear()              # necessary for legend on both pads

# close file
if doPrint:
    canvas.Print(plotfile + ']')
