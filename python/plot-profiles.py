#!/usr/bin/python
# coding=utf8
"""Profile plots

Dependencies: rootpy.{io,tree,plotting}

"""

import argparse
from rplot.utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-p', '--print', dest='doPrint', action='store_true',
                    help='Print plots to pdf files')
parser.add_argument('-s', '--stats', action='store_true',
                    help='Include stats boxes')
parser.formatter_class = RawArgDefaultFormatter
options = parser.parse_args()

# rootpy modules
from rplot.fixes import ROOT
ROOT.gROOT.SetBatch(options.doPrint)
ROOT.gStyle.SetOptTitle(0)
if not options.stats:
    ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

from ROOT import TFile, TProfile, TGaxis
# from pprint import pprint


# setup
modes = {
    'dsk': {
        'name': 'DsK',
        'file': TFile.Open('data/smalltree-really-new-MC-pre-PID-DsK.root'),
        'cuts': 10,            # pid cut
        'cols': ROOT.kBlue
    },
    'dspi': {
        'name': 'Ds#pi',
        'file': TFile.Open('data/smalltree-really-new-MC-pre-PID-DsPi.root'),
        'cuts': 0,             # pid cut
        'cols': ROOT.kRed
    }
}
for mode in modes:
    modes[mode]['tree'] = modes[mode]['file'].Get('ftree')


## Note there are a few selection cuts in the variables
# pT < 500, hIPchi2 < 4
plots = {
    'pt_pid': {
        'expr': 'PIDK:hMom.Pt()',
        'xbin': (100, 0, 2E4),
        'ybin': (100, -50, 50),
        'xname': 'p_{T} (MeV/c)',
        'yname': 'PIDK'
    },
    'ip_pid': {
        'expr': 'PIDK:hIPchi2',
        'xbin': (100, 0, 3E3),
        'ybin': (100, -50, 50),
        'xname': 'IP #chi^{2}',
        'yname': 'PIDK'
    },
    'pt_ip': {
        'expr': 'hIPchi2:hMom.Pt()',
        'xbin': (100, 0, 2E4),
        'ybin': (100, 0, 7E2),
        'xname': 'p_{T} (MeV/c)',
        'yname': 'IP #chi^{2}'
    },
    'ipt_ip': {
        'expr': 'hIPchi2:1/hMom.Pt()',
        'xbin': (100, 0, 2.5E-3),
        'ybin': (100, 0, 1E3),
        'xname': '1/p_{T}',
        'yname': 'IP #chi^{2}'
    },
}

# profile plots
hprofiles = {}
for plot in plots:
    hprofiles[plot] = {}
    for mode in modes:
        hname = 'hprof_%s_%s' % (plot, mode)
        htitle = 'Profile plot of {1} vs {0};{0};{1}'.format(
            plots[plot]['xname'], plots[plot]['yname'])
        hprofiles[plot][mode] = TProfile(hname, htitle, *plots[plot]['xbin'])
        hprofiles[plot][mode].SetMarkerStyle(ROOT.kPlus)
        hprofiles[plot][mode].SetMarkerColor(modes[mode]['cols'])
        hprofiles[plot][mode].SetLineColor(modes[mode]['cols'])
        hprofiles[plot][mode].SetMaximum(plots[plot]['ybin'][2])
        hprofiles[plot][mode].SetMinimum(plots[plot]['ybin'][1])
        modes[mode]['tree'].Draw('{}>>{}'.format(plots[plot]['expr'], hname),
                                 'time<1', 'prof')


# legend
legend = ROOT.TLegend(0.8, 0.7, 0.9, 0.8)
legend.SetFillStyle(0)
legend.SetFillColor(0)
legend.SetLineWidth(0)
legend.SetTextSize(0.035)

# pid cut axes
axes = {}
for plot in plots:
    if plots[plot]['expr'].find('PIDK') < 0:
        continue
    axes[plot] = {}
    for mode in modes:
        if plots[plot]['expr'].find('PIDK:') >= 0:  # PIDK on Y-axis
            axes[plot][mode] = TGaxis(plots[plot]['xbin'][1],
                                      modes[mode]['cuts'],
                                      plots[plot]['xbin'][2],
                                      modes[mode]['cuts'],
                                      plots[plot]['xbin'][1],
                                      plots[plot]['xbin'][2], 0)
            axes[plot][mode].SetLineColor(modes[mode]['cols'])
        elif plots[plot]['expr'].find(':PIDK') >= 0:  # PIDK on X-axis
            axes[plot][mode] = TGaxis(modes[mode]['cuts'],
                                      plots[plot]['ybin'][1],
                                      modes[mode]['cuts'],
                                      plots[plot]['ybin'][2],
                                      plots[plot]['ybin'][1],
                                      plots[plot]['ybin'][2], 0)
            axes[plot][mode].SetLineColor(modes[mode]['cols'])

# draw plots
canvas = ROOT.TCanvas('canvas', '', 800, 500)
if options.doPrint:
    plotfile = 'plots/timelt1ps_profile_%s.pdf' % 'pT_IPchi2_PIDK'
    canvas.Print(plotfile + '[')

for plot in plots:
    stats = {}
    for midx, mode in enumerate(modes):
        drawopts = 'e1'
        if midx > 0:
            drawopts += ' sames'
        hprofiles[plot][mode].Draw(drawopts)
        if (plots[plot]['expr'].find('PIDK') >= 0):
            axes[plot][mode].Draw()
        legend.AddEntry(hprofiles[plot][mode], modes[mode]['name'], 'pel')
        stats[mode] = hprofiles[plot][mode].FindObject('stats')
        if stats[mode]:
            if midx > 0:
                stats[mode].SetY1NDC(y1)
                stats[mode].SetY2NDC(y2)
            else:
                y1 = stats[mode].GetY1NDC() - 0.5
                y2 = stats[mode].GetY2NDC() - 0.5
    legend.Draw()
    ROOT.gPad.Update()
    if options.doPrint:
        canvas.Print(plotfile)
    legend.Clear()              # necessary to clear old legends

if options.doPrint:
    canvas.Print(plotfile + ']')
