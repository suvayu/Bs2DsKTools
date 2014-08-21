#!/usr/bin/env python
# coding=utf-8
"""Plot raw acceptance ratios from Monte Carlo

\033[1mNon-standard dependencies\033[0m: rootpy.{io,tree,plotting}

@author Suvayu Ali
@date   [2013-04-23 Tue]

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
# from numpy import fromfile

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
modes = {0:'dsk', 1:'dspi'}

files = (                       # 0 - DsK, 1 - Dsπ
    File('data/smalltree-really-new-MC-pre-PID-DsK.root'),
    File('data/smalltree-really-new-MC-pre-PID-DsPi.root')
)
trees = (                       # 0 - DsK, 1 - Dsπ
    files[0].Get('ftree'),
    files[1].Get('ftree')
)

histograms = ([], [])           # 0 - DsK, 1 - Dsπ

cuts = {
    'nocuts'    : Cut(''),
    'dsk'       : Cut('PIDK>10'),
    'dspi'      : Cut('PIDK<0'),
    'bdt'       : Cut('BDTG>0.5'),
    'HLT1'      : Cut('HLT1TrackAllL0TOS > 0'),
    'HLT22Body' : Cut('HLT2Topo2BodyTOS > 0'),
    'HLT23Body' : Cut('HLT2Topo3BodyTOS > 0'),
    'HLT24Body' : Cut('HLT2Topo4BodyTOS > 0')
}
cuts.update(dict(HLT2 = cuts['HLT22Body'] | cuts['HLT23Body'] | cuts['HLT24Body']))
cuts.update(dict(trig = cuts['HLT1'] & cuts['HLT2']))

htypes = [
    'nocuts', 'pid', 'bdt', 'trig',    # base
    'pid_bdt', 'pid_trig', 'bdt_trig', # permutations of 2
    'pid_bdt_trig',                    # all
    'pid_bdt_trig_zoom'
]

# # for variable binning (quite horrible at the moment)
# hbins = fromfile('data/binning_scheme.dat')
# nbins = len(hbins) - 1

## decay time distributions for different cuts
for htype in htypes:
    for mode in modes:
        # ensure identical binning
        hist = Hist(100, 0.2, 15.0, name='h' + modes[mode] + '_' + htype, type='D')
        cut = cuts['nocuts']
        cut_tokens = htype.split('_')
        for token in cut_tokens:
            if token.find('nocuts') >= 0:
                pass
            elif token.find('pid') >= 0:
                cut = cut & cuts[modes[mode]]
            elif token.find('bdt') >= 0:
                cut = cut & cuts['bdt']
            elif token.find('trig') >= 0:
                cut = cut & cuts['trig']
            elif token.find('zoom') >= 0:
                # overwrite histogram with new binning
                hist = Hist(60, 5.0, 8.0, name='h' + modes[mode] + '_' + htype, type='D')
                # handle warning, modify to say it is intended
            else:
                print 'Unknown permutation of cuts, weird things will happen.'
        histograms[mode].append(trees[mode].Draw('time', cut, '', hist))


## ratios for different cuts
canvas0 = TCanvas('canvas0', '', 800, 500)
canvas = TCanvas('canvas', '', 1600, 1000)
canvas.Divide(3,2)

ratio_histograms = [hist.clone() for hist in histograms[0]]
for zoom in range(2):
    for idx, hist in enumerate(ratio_histograms):
        ratio_histograms[idx].reset('ices')
        htitle = ' '.join(histograms[0][idx].GetName().split('_')[1:])
        ratio_histograms[idx].SetTitle(htitle+';decay time (ps);DsK/Ds#pi')
        ratio_histograms[idx].SetMarkerStyle(kPlus)
        ratio_histograms[idx].Divide(histograms[0][idx], histograms[1][idx])
        if zoom:
            if htitle.find('zoom') >= 0: continue
            ratio_histograms[idx].GetXaxis().SetRangeUser(0.2, 1)
            ratio_histograms[idx].GetYaxis().SetRangeUser(0.0, 2)
        if idx == 0 or idx > 6:
            canvas0.cd()
        if idx > 0 and idx < 7:
            canvas.cd(idx)
        # anomally, printing Dsπ and DsK distributtions overlayed by scaled ratio
        if htitle.find('zoom') >= 0:
            histograms[0][idx].SetLineColor(kRed)
            histograms[1][idx].SetLineColor(kAzure)
            histograms[0][idx].Draw('hist')
            histograms[1][idx].Draw('hist same')
            ratio_histograms[idx].SetFillColor(kBlack)
            ratio_histograms[idx].Scale(1000.0/ratio_histograms[idx].Integral())
            for nbin in range(1, ratio_histograms[idx].GetNbinsX() + 1):
                ratio_histograms[idx].SetBinContent(nbin, ratio_histograms[idx].GetBinContent(nbin) + 80.0)
            ratio_histograms[idx].Draw('e3 same')
            legend = TLegend(0.75, 0.3, 0.85, 0.5)
            legend.SetLineColor(0)
            legend.SetFillStyle(0)
            legend.AddEntry(histograms[0][idx], 'DsK', 'l')
            legend.AddEntry(histograms[1][idx], 'Ds#pi', 'l')
            legend.AddEntry(ratio_histograms[idx], 'ratio', 'l')
            legend.Draw()
            gPad.Update()
        else:
            ratio_histograms[idx].Draw('e1')
        if doPrint and (idx == 0 or idx > 6):
            canvas0.Print('plots/DsK_ratio_'+str(idx)+'_'+str(zoom)+'.png')
            canvas0.Print('plots/DsK_ratio_'+str(idx)+'_'+str(zoom)+'.pdf')
    canvas.Update()
    if not zoom:
        dfile = File('data/raw_ratios.root', 'recreate')
        dfile.cd()
        for hist in ratio_histograms:
            dfile.WriteTObject(hist)
        dfile.Close()

    if doPrint:
        canvas.Print('plots/DsK_ratio_grid_'+str(zoom)+'.png')
        canvas.Print('plots/DsK_ratio_grid_'+str(zoom)+'.pdf')
