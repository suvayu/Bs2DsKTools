#!/usr/bin/env python

import argparse
from rplot.utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter)
parser.add_argument('rfile', help='ROOT file')
parser.add_argument('-b', dest='batch', action='store_true')
options = parser.parse_args()

import ROOT
ROOT.gROOT.SetBatch(options.batch)
ROOT.gStyle.SetOptTitle(False)
ROOT.gStyle.SetOptStat(False)

rfile = ROOT.TFile.Open(options.rfile)
tree = rfile.Get('DecayTree')

hist_m4 = ROOT.TH1D('hist_m4', 'Mass', 100, 5300, 5440)
hist_m5 = ROOT.TH1D('hist_m5', 'Mass w/ sw', 100, 5300, 5440)
hist_m6 = ROOT.TH1D('hist_m6', 'Mass w/ sw+offset', 100, 5300, 5440)

# axis titles
blabel, swlabel, ylabel = 'B mass [MeV]', '#it{s}-weights', 'Candidates'
titles = {
    hist_m4: (blabel, ylabel),
    hist_m5: (blabel, ylabel),
    hist_m6: (blabel, ylabel),
}

from rplot.tselect import Tselect
selector = Tselect(tree)
selector.exprs = [
    ('lab0_MM>>hist_m4', '5310<lab0_MM && lab0_MM<5430'),
    ('lab0_MM>>hist_m5', 'sw*(5310<lab0_MM && lab0_MM<5430)'),
    ('lab0_MM>>hist_m6', '(sw-0.113)*(5310<lab0_MM && lab0_MM<5430)'),
]
hists = selector.fill_hists()
map(lambda h: (h.GetXaxis().SetTitle(titles[h][0]), h.GetYaxis().SetTitle(titles[h][1])), hists)

from rplot.rplot import Rplot
plotter = Rplot(1, 1, 800, 500)

legend = ROOT.TLegend(0.65, 0.5, 0.9, 0.9)
legend.SetFillStyle(0)
legend.SetLineWidth(0)
plotter.add_legend(legend, 'lep')

canvas = plotter.prep_canvas()
canvas.Print('sw-B-mass.pdf[')
plotter.draw_hist([hists], 'e1')
canvas.Print('sw-B-mass.pdf')
canvas.Print('sw-B-mass.pdf]')
