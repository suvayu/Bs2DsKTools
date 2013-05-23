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
QROOT.gROOT.SetBatch(True)
from rootpy.io import File
from rootpy.tree import Tree, TreeChain
from rootpy.plotting import Hist, Hist2D, Profile #, Legend


# setup
modes = {
    'dsk' : {
        'name' : 'DsK',
        'tree' : File('data/smalltree-really-new-MC-pre-PID-DsK.root').Get('ftree'),
        'cuts' : 10,            # pid cut
        'cols' : QROOT.kBlue
    },
    'dspi' : {
        'name' : 'Ds#pi',
        'tree' : File('data/smalltree-really-new-MC-pre-PID-DsPi.root').Get('ftree'),
        'cuts' : 0,             # pid cut
        'cols' : QROOT.kRed
    }
}

## Note there are a few selection cuts in the variables
# pT < 500, hIPchi2 < 4
plots = {
    'pt_pid' : {
        'expr' : 'hMom.Pt():PIDK',
        'xbin' : (100, 0, 4E4),
        'ybin' : (100, -50, 50),
        'xname': 'p_{T} (MeV/c)',
        'yname': 'PIDK'
    },
    'ip_pid' : {
        'expr' : 'hIPchi2:PIDK',
        'xbin' : (100, 0, 8E3),
        'ybin' : (100, -50, 50),
        'xname': 'IP #chi^{2}',
        'yname': 'PIDK'
    },
    'pt_ip' : {
        'expr' : 'hMom.Pt():hIPchi2',
        'xbin' : (100, 0, 4E4),
        'ybin' : (100, 0, 1E3),
        'xname': 'p_{T} (MeV/c)',
        'yname': 'IP #chi^{2}'
    },
    'ipt_ip' : {
        'expr' : '1/hMom.Pt():hIPchi2',
        'xbin' : (100, 0, 2.5E-3),
        'ybin' : (100, 0, 8E2),
        'xname': '1/p_{T}',
        'yname': 'IP #chi^{2}'
    },
}

# profile plots
hprofiles = {}
for plot in plots:
    hprofiles[plot] = {}
    for mode in modes:
        hname='hprof_%s_%s' % (plot, mode)
        htitle='Profile plot of {1} vs {0};{0};{1}'.format(plots[plot]['xname'], plots[plot]['yname'])
        hprofiles[plot][mode] = Profile(*plots[plot]['xbin'], name = hname,
                                        title = htitle,
                                        markerstyle = QROOT.kPlus,
                                        markercolor = modes[mode]['cols'],
                                        linecolor = modes[mode]['cols'])
        hprofiles[plot][mode].SetMaximum(plots[plot]['ybin'][2])
        hprofiles[plot][mode].SetMinimum(plots[plot]['ybin'][1])
        modes[mode]['tree'].Draw(plots[plot]['expr'], 'time<1',
                                 'prof', hprofiles[plot][mode])


# legend
legend = QROOT.TLegend(0.6, 0.7, 0.7, 0.8)
legend.SetFillStyle(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.SetTextSize(0.035)

# pid cut axes
axes = {}
for plot in plots:
    if plots[plot]['expr'].find('PIDK') < 0:
        continue
    axes[plot] = {}
    for mode in modes:
        if plots[plot]['expr'].find(':PIDK') > 0: # PIDK on Y-axis
            axes[plot][mode] = QROOT.TGaxis(plots[plot]['xbin'][1],
                                            modes[mode]['cuts'],
                                            plots[plot]['xbin'][2],
                                            modes[mode]['cuts'],
                                            plots[plot]['xbin'][1],
                                            plots[plot]['xbin'][2], 0)
            axes[plot][mode].SetLineColor(modes[mode]['cols'])
        elif plots[plot]['expr'].find('PIDK:') >= 0: # PIDK on X-axis
            axes[plot][mode] = QROOT.TGaxis(modes[mode]['cuts'],
                                            plots[plot]['ybin'][1],
                                            modes[mode]['cuts'],
                                            plots[plot]['ybin'][2],
                                            plots[plot]['ybin'][1],
                                            plots[plot]['ybin'][2], 0)
            axes[plot][mode].SetLineColor(modes[mode]['cols'])

# draw plots
canvas = QROOT.TCanvas('canvas', '', 800, 500)
if doPrint:
    plotfile = 'plots/timelt1ps_profile_%s.pdf' % 'pT_IPchi2_PIDK'
    canvas.Print(plotfile + '[')

for plot in plots:
    stats = {}
    for midx, mode in enumerate(modes):
        drawopts = 'e1'
        if midx > 0:
            drawopts += ' sames'
        hprofiles[plot][mode].Draw(drawopts)
        if (plots[plot]['expr'].find(':PIDK') > 0
            or plots[plot]['expr'].find('PIDK:') >= 0):
            axes[plot][mode].Draw()
        legend.AddEntry(hprofiles[plot][mode], modes[mode]['name'], 'pel')
        stats[mode] = hprofiles[plot][mode].FindObject('stats')
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
