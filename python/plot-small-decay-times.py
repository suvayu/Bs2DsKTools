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
from ROOT import kDot, kPlus, kFullDotMedium, kFullDotSmall

# ROOT classes
from ROOT import TCanvas, TLegend

# rootpy modules
from rootpy.io import File
from rootpy.tree import Tree
from rootpy.tree import TreeChain
from rootpy.tree import Cut
from rootpy.plotting import Hist, Profile

# my libs
from helpers import *


## Read from file
if reverse:
    modes = ['dspi', 'dsk']
else:
    modes = ['dsk', 'dspi']

# trees = {
#     'dsk'  : TreeChain('DecayTree', glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsK_*BsHypo_BDTG.root')),
#     'dspi' : TreeChain('DecayTree', glob('../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsPi_*BsHypo_BDTG.root'))
# }

files = {
    'dsk'  : File('data/smalltree-really-new-MC-pre-PID-DsK.root'),
    'dspi' : File('data/smalltree-really-new-MC-pre-PID-DsPi.root')
}
trees = {
    'dsk'  : files['dsk'].Get('ftree'),
    'dspi' : files['dspi'].Get('ftree')
}

variables = ('hMom.Pt()', 'hMom.Eta()', 'hIPchi2', 'time')
prettyvars = ('h p_{T}', 'h #eta', 'h IP #chi^{2}', 'decay time')
# variables = ['lab1_IPCHI2_OWNPV']
# prettyvars = ['h IP #chi^{2}']

cuts = {
    'nocuts'    : Cut(''),
    'timelt1ps' : Cut('time<1.0'), # from small tree
    'dsk'       : Cut('PIDK>10'),
    'dspi'      : Cut('PIDK<0'),
    'bdt'       : Cut('BDTG>0.5'),
    'HLT1'      : Cut('HLT1TrackAllL0TOS > 0'),
    'HLT22Body' : Cut('HLT2Topo2BodyTOS > 0'),
    'HLT23Body' : Cut('HLT2Topo3BodyTOS > 0'),
    'HLT24Body' : Cut('HLT2Topo4BodyTOS > 0')
    # 'timelt1ps' : Cut('lab0_TAU<1.0'), # from ntuples directly
    # 'dsk'       : Cut('lab1_PIDK>10'),
    # 'dspi'      : Cut('lab1_PIDK<0'),
    # 'bdt'       : Cut('BDTGResponse_1>0.5'),
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

histograms = []                 # list of dicts, keys: dsk, dspi
hprofiles = []                  # list of dicts, keys: dsk, dspi


## pT and η distributions for different cuts
for htype in htypes:
    for var in variables:
        if var.lower().find('pt') >= 0:
            binning = (100, 0.0, 2E4)
        elif var.lower().find('eta') >= 0:
            binning = (100, 1.5, 5.0)
        elif var.lower().find('ipchi2') >= 0:
            binning = (100, 0.0, 1E3)
        elif var.lower().find('time') >= 0:
            binning = (100, 0.0, 1.0)
        else:
            print 'Unknown variable, weird things will happen.'
        hpair, hprof_pair = {}, {}
        max_y_n = 0             # max Y after normalisation
        for mode in modes:
            # ensure identical binning
            hist = Hist(*binning, name='h' + mode + '_' + htype + '_'
                        + sanitise_str_src(var), type='D')
            if var.lower().find('pt') >= 0:
                hprof = Profile(*binning, name='h' + mode + '_prof_' + htype +
                                '_' + sanitise_str_src(var) + '_IPchi2')
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
            trees[mode].Draw(var, cut, '', hist)
            hpair[mode] = hist
            if var.lower().find('pt') >= 0:
                trees[mode].Draw(var + ':' + variables[-1],
                                 cut, 'prof', hprof)
                hprof_pair[mode] = hprof
            # FIXME: TreeChain does some copying of histograms internally
            if isinstance(trees[mode], TreeChain):
                hpair[mode].SetName(hist.GetName())
            # determine max Y for normalised histograms
            if max_y_n < hpair[mode].GetMaximum()/hpair[mode].Integral():
                max_y_n = hpair[mode].GetMaximum() / hpair[mode].Integral()
        # set max Y so that histograms fits in pad
        for mode in modes:
            hpair[mode].SetMaximum(1.1 * max_y_n * hpair[mode].Integral())
        histograms.append(hpair)
        if var.lower().find('pt') >= 0:
            hprofiles.append(hprof_pair)


## plot distributions
nvars = len(variables)
canvas = TCanvas('canvas', '', 800*nvars, 500)
canvas.Divide(nvars,1)

# open file
plotfile = 'plots/timelt1ps_%s.pdf' % sanitise_str_src('_'.join(variables))
if doPrint:
    canvas.Print(plotfile + '[')

# create legend
legend = TLegend(0.6, 0.5, 0.85, 0.65)
legend.SetLineColor(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.035)

# draw distributions side by side
for hidx, hpair in enumerate(histograms):
    canvas.cd(hidx % nvars + 1)
    var = prettyvars[hidx % nvars]
    legend.SetHeader('%s (%s ps)' % (var, sanitise_str(cuts['timelt1ps'].str)))
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
    if (hidx + 1) % nvars == 0:
        canvas.Update()
        if doPrint:
            canvas.Print(plotfile)
    legend.Clear()              # necessary for legend on both pads

# close file
if doPrint:
    canvas.Print(plotfile + ']')
legend.Clear()

## plot profiles
canvas = TCanvas('canvas', '', 800, 500)

# open file
# FIXME: sensitive to change in order
plotfile = 'plots/timelt1ps_prof_%s.pdf' % sanitise_str_src('_'.join([variables[0], variables[2]]))
if doPrint:
    canvas.Print(plotfile + '[')

# draw profile plots
legend.SetX1NDC(0.4)
legend.SetY1NDC(0.7)
legend.SetX2NDC(0.65)
legend.SetY2NDC(0.85)
xvar, yvar = prettyvars[0], prettyvars[2] # FIXME: sensitive to change in order

for hidx, hprof_pair in enumerate(hprofiles):
    legend.SetHeader('%s vs %s (%s ps)' % (xvar, yvar,
                                           sanitise_str(cuts['timelt1ps'].str)))
    for midx, mode in enumerate(modes):
        # print mode, hprof_pair[mode]
        htitle = ' '.join(hprof_pair[mode].GetName().split('_')[1:])
        hprof_pair[mode].SetTitle(htitle + ';%s;%s' % (xvar, yvar))
        hprof_pair[mode].SetMarkerStyle(kPlus)
        drawopts = 'e1'
        if midx > 0:
            drawopts += ' same'
        if mode == 'dsk':
            hprof_pair[mode].SetLineColor(kBlue)
            hprof_pair[mode].SetMarkerColor(kBlue)
            legend.AddEntry(hprof_pair[mode], 'DsK', 'pe')
        if mode == 'dspi':
            hprof_pair[mode].SetLineColor(kRed)
            hprof_pair[mode].SetMarkerColor(kRed)
            legend.AddEntry(hprof_pair[mode], 'Ds#pi', 'pe')
        hprof_pair[mode].Draw(drawopts)
    legend.Draw()
    if doPrint:
        canvas.Print(plotfile)
    legend.Clear()              # necessary to clear old legends

# close file
if doPrint:
    canvas.Print(plotfile + ']')
