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
modes = { 'dsk' : 'DsK', 'dspi' : 'Ds#pi'}
trees = {
    'dsk'  : File('data/smalltree-really-new-MC-pre-PID-DsK.root').Get('ftree'),
    'dspi' : File('data/smalltree-really-new-MC-pre-PID-DsPi.root').Get('ftree')
}
variables = { 'pt' : 'hMom.Pt()', 'ip' : 'hIPchi2' } #, 'pid' : 'PIDK' }
varbinning = { 'pt' : (100, 0, 4E4), 'ip' : (100, 0, 8E3) }
prettyvars = { 'pt' : 'p_{T} (MeV/c)', 'ip' : 'IP #chi^{2}' }
pidcuts = { 'dsk' : 10, 'dspi' : 0 }
colours = { 'dsk' : QROOT.kBlue, 'dspi' : QROOT.kRed }


# profile plots
hprofiles = {}
for var in variables:
    hprofiles[var] = {}
    for mode in modes:
        hname='hprof_%s_%s' % (var, mode)
        htitle='Profile plot of PIDK vs {0};{0};PIDK'.format(prettyvars[var])
        hprofiles[var][mode] = Profile(*varbinning[var], name=hname, title=htitle,
                                       markerstyle = QROOT.kPlus,
                                       markercolor = colours[mode],
                                       linecolor = colours[mode])
        hprofiles[var][mode].SetMaximum(50)
        hprofiles[var][mode].SetMinimum(-50)
        trees[mode].Draw('%s:PIDK' % variables[var], 'time<1', 'prof', hprofiles[var][mode])


# legend
legend = QROOT.TLegend(0.6, 0.7, 0.7, 0.8)
legend.SetFillStyle(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.SetTextSize(0.035)

# pid cut axes
axes = {}
for var in variables:
    axes[var] = {}
    for mode in modes:
        axes[var][mode] = QROOT.TGaxis(0, pidcuts[mode],
                                       varbinning[var][2], pidcuts[mode],
                                       0, varbinning[var][2], 0)
        axes[var][mode].SetLineColor(colours[mode])

# draw plots
canvas = QROOT.TCanvas('canvas', '', 800, 500)
if doPrint:
    plotfile = 'plots/timelt1ps_profile_%s.pdf' % 'pT_IPchi2_PIDK' # sanitise_str_src('_'.join(variables))
    canvas.Print(plotfile + '[')

stats = {}
for var in variables:
    for midx, mode in enumerate(modes):
        drawopts = 'e1'
        if midx > 0:
            drawopts += ' sames'
        hprofiles[var][mode].Draw(drawopts)
        axes[var][mode].Draw()
        legend.AddEntry(hprofiles[var][mode], modes[mode], 'pel')
        stats[mode] = hprofiles[var][mode].FindObject('stats')
        if midx > 0:
            stats[mode].SetY1NDC(y1)
            stats[mode].SetY2NDC(y2)
        else:
            y1 = stats[mode].GetY1NDC() - 0.5
            y2 = stats[mode].GetY2NDC() - 0.5
    legend.Draw()
    QROOT.gPad.Update()
    if doPrint:
        canvas.Print(plotfile)
    legend.Clear()              # necessary to clear old legends

if doPrint:
    canvas.Print(plotfile + ']')
