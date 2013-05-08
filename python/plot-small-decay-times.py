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
optparser.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                       help=u'Reverse DsK and Dsπ overlay order'.encode('utf8'))
optparser.formatter_class = argparse.RawDescriptionHelpFormatter
options = optparser.parse_args()
doPrint = options.doPrint
reverse = options.reverse

# Python modules
import os
import sys
from glob import glob

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
from rootpy.tree import TreeChain
from rootpy.tree import Cut
from rootpy.plotting import Hist


## Read from file
if reverse:
    modes = ['dspi', 'dsk']
else:
    modes = ['dsk', 'dspi']

trees = {
    'dsk'  : TreeChain('DecayTree', glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsK*BsHypo_BDTG.root')),
    'dspi' : TreeChain('DecayTree', glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsPi*BsHypo_BDTG.root'))
}

# trees = {
#     'dsk'  : File('data/smalltree-really-new-MC-pre-PID-DsK.root').Get('ftree'),
#     'dspi' : File('data/smalltree-really-new-MC-pre-PID-DsPi.root').Get('ftree')
# }

histograms = []                 # list of dicts, keys: dsk, dspi

# variables = ('Pt', 'Eta')
# prettyvars = ('p#T', '#eta')
variables = ['lab1_IPCHI2_OWNPV']
prettyvars = ['IP #chi^{2}']

cuts = {
    'nocuts'    : Cut(''),
    # 'timelt1ps' : Cut('time<1.0'), # from small tree
    # 'dsk'       : Cut('PIDK>10'),
    # 'dspi'      : Cut('PIDK<0'),
    # 'bdt'       : Cut('BDTG>0.5'),
    # 'HLT1'      : Cut('HLT1TrackAllL0TOS > 0'),
    # 'HLT22Body' : Cut('HLT2Topo2BodyTOS > 0'),
    # 'HLT23Body' : Cut('HLT2Topo3BodyTOS > 0'),
    # 'HLT24Body' : Cut('HLT2Topo4BodyTOS > 0')
    'timelt1ps' : Cut('lab0_TAU<1.0'), # from ntuples directly
    'dsk'       : Cut('lab1_PIDK>10'),
    'dspi'      : Cut('lab1_PIDK<0'),
    'bdt'       : Cut('BDTGResponse_1>0.5'),
    'HLT1'      : Cut('lab0_Hlt1TrackAllL0Decision_TOS > 0'),
    'HLT22Body' : Cut('lab0_Hlt2Topo4BodyBBDTDecision_TOS > 0'),
    'HLT23Body' : Cut('lab0_Hlt2Topo3BodyBBDTDecision_TOS > 0'),
    'HLT24Body' : Cut('lab0_Hlt2Topo2BodyBBDTDecision_TOS > 0')
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
            binning = (100, 0.0, 2E4)
        elif var == 'Eta':
            binning = (100, 1.5, 5.0)
        elif var == 'lab1_IPCHI2_OWNPV':
            binning = (100, 0.0, 1E3)
        else:
            print 'Unknown variable, weird things will happen.'
        hpair = {}
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
            if isinstance(trees[mode], TreeChain):
                hpair[mode] = trees[mode].Draw(var, cut, '', hist)
                # FIXME: TreeChain does some copying of histograms internally
                hpair[mode].SetName(hist.GetName())
            else:
                hpair[mode] = trees[mode].Draw('hMom.%s()' % var, cut, '', hist)
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
legend.SetTextSize(0.035)

# draw distributions side by side
for hidx, hpair in enumerate(histograms):
    canvas.cd(hidx % 2 + 1)
    var = prettyvars[hidx % len(variables)]
    legend.SetHeader('%s for %s ps' % (var, cuts['timelt1ps'].str))
    for midx, mode in enumerate(modes):
        htitle = ' '.join(hpair[mode].GetName().split('_')[1:])
        hpair[mode].SetTitle(htitle + ';%s' % var)
        drawopts = 'hist'
        if midx > 0:
            drawopts += ' same'
        if mode == 'dsk':
            hpair[mode].SetLineColor(kBlue)
            legend.AddEntry(hpair[mode], 'DsK', 'l')
        if mode == 'dspi':
            hpair[mode].SetLineColor(kRed)
            legend.AddEntry(hpair[mode], 'Ds#pi', 'l')
        hpair[mode].DrawNormalized(drawopts)
    legend.Draw()
    if hidx % 2 > 0:
        canvas.Update()
        if doPrint:
            canvas.Print(plotfile)
    legend.Clear()              # necessary for legend on both pads

# close file
if doPrint:
    canvas.Print(plotfile + ']')
