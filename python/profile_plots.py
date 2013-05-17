#!/usr/bin/python
# coding=utf8
"""Profile plots

Dependencies: rootpy.{io,tree,plotting}

"""

import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                    help='Print plots to png/pdf files')
parser.formatter_class = argparse.RawDescriptionHelpFormatter
options = parser.parse_args()
doPrint = options.doPrint

# clean up
del parser, options

# Python modules
import os
import sys
from glob import glob

# rootpy modules
from rootpy import QROOT
from rootpy.io import File
from rootpy.tree import Tree, TreeChain
from rootpy.plotting import Hist, Hist2D, Profile #, Legend


# setup
modes = ['dsk', 'dspi']
trees = {
    'dsk'  : File('data/smalltree-really-new-MC-pre-PID-DsK.root').Get('ftree'),
    'dspi' : File('data/smalltree-really-new-MC-pre-PID-DsPi.root').Get('ftree')
}
pidcuts = { 'dsk' : 10, 'dspi' : 0 }
colours = { 'dsk' : QROOT.kBlue, 'dspi' : QROOT.kRed }


# profile plots
hprofiles_pt, hprofiles_ip = {}, {}
for mode in modes:
    hprofiles_pt[mode] = Profile(100, 0.0, 4E4, name='hprof_pt_%s' % mode,
                                 title='Profile plot of PIDK vs p_{T};p_{T} (MeV/c);PIDK',
                                 markerstyle = QROOT.kPlus,
                                 markercolor = colours[mode],
                                 linecolor = colours[mode])
    hprofiles_pt[mode].SetMaximum(50)
    hprofiles_pt[mode].SetMinimum(-50)
    trees[mode].Draw('hMom.Pt():PIDK', 'time<1', 'prof', hprofiles_pt[mode])

    hprofiles_ip[mode] = Profile(100, 0.0, 8E3, name='hprof_ip_%s' % mode,
                                  title='Profile plot of PIDK vs IP #chi^{2};IP #chi^{2};PIDK',
                                  markerstyle = QROOT.kPlus,
                                  markercolor = colours[mode],
                                  linecolor = colours[mode])
    hprofiles_ip[mode].SetMaximum(50)
    hprofiles_ip[mode].SetMinimum(-50)
    trees[mode].Draw('hIPchi2:PIDK', 'time<1', 'prof', hprofiles_ip[mode])


# legend
legend = QROOT.TLegend(0.6, 0.7, 0.7, 0.8)
legend.AddEntry(hprofiles_pt['dsk'], 'DsK', 'pel')
legend.AddEntry(hprofiles_pt['dspi'], 'Ds#pi', 'pel')
legend.SetFillStyle(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.SetTextSize(0.035)

# pid cut axes
axes = {}
for mode in modes:
    axes[mode] = QROOT.TGaxis(0, pidcuts[mode], 4E4, pidcuts[mode], 0, 4E4, 0)
    axes[mode].SetLineColor(colours[mode])

# draw plots
canvas = QROOT.TCanvas('canvas', '', 800, 500)
if doPrint:
    plotfile = 'plots/timelt1ps_profile_%s.pdf' % 'pT_IPchi2_PIDK' # sanitise_str_src('_'.join(variables))
    canvas.Print(plotfile + '[')

stats = {}
for midx, mode in enumerate(modes):
    drawopts = 'e1'
    if midx > 0:
        drawopts += ' sames'
    hprofiles_pt[mode].Draw(drawopts)
    axes[mode].Draw()
    stats[mode] = hprofiles_pt[mode].FindObject('stats')
    if midx > 0:
        stats[mode].SetY1NDC(y1)
        stats[mode].SetY2NDC(y2)
    else:
        y1 = stats[mode].GetY1NDC() - 0.5
        y2 = stats[mode].GetY2NDC() - 0.5
legend.Draw()

if doPrint:
    canvas.Print(plotfile)

for midx, mode in enumerate(modes):
    drawopts = 'e1'
    if midx > 0:
        drawopts += ' sames'
    hprofiles_ip[mode].Draw(drawopts)
    stats[mode] = hprofiles_ip[mode].FindObject('stats')
    if midx > 0:
        stats[mode].SetY1NDC(y1)
        stats[mode].SetY2NDC(y2)
    else:
        y1 = stats[mode].GetY1NDC() - 0.5
        y2 = stats[mode].GetY2NDC() - 0.5
legend.Draw()

if doPrint:
    canvas.Print(plotfile)
    canvas.Print(plotfile + ']')
