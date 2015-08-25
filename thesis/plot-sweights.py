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

hist_m0 = ROOT.TH1D('hist_m0', 'Mass', 500, 5200, 5700)
hist_m1 = ROOT.TH1D('hist_m1', 'Mass (w/ sw)', 500, 5200, 5700)
hist_m2 = ROOT.TH1D('hist_m2', 'Mass (sw > 0)', 500, 5200, 5700)
hist_m3 = ROOT.TH1D('hist_m3', 'Mass (sw < 0)', 500, 5200, 5700)
hist_w1 = ROOT.TH1D('hist_w1', 'sw (mass \in [5310,5430])', 200, -0.2, 1.2)
hist_w2 = ROOT.TH1D('hist_w2', 'sw (mass \notin [5310,5430])', 200, -0.2, 1.2)

# axis titles
blabel, swlabel = 'B mass [MeV]', '#it{s}-weights'
titles = {
    hist_m0: (blabel,),
    hist_m1: (blabel,),
    hist_m2: (blabel,),
    hist_m3: (blabel,),
    hist_w1: (swlabel,),
    hist_w2: (swlabel,),
    'hist_2d': (blabel, swlabel)
}

hist_m3.SetLineColor(ROOT.kRed)
hist_m3.SetMarkerColor(ROOT.kRed)
hist_w2.SetLineColor(ROOT.kRed)
hist_w2.SetMarkerColor(ROOT.kRed)


def get_minmax(hist, axis='y'):
    """Get histogram Y axis min and max"""
    assert(axis in ['x', 'y'])
    if 1 == hist.GetDimension() and 'y' == axis:
        return (hist.GetBinContent(hist.GetMinimumBin()),
                hist.GetBinContent(hist.GetMaximumBin()))
    else:
        if 'y' == axis:
            axis = hist.GetYaxis()
        elif 'x' == axis:
            axis = hist.GetXaxis()
        return (axis.GetXmin(), axis.GetXmax())


def annotate_mass(ymin, ymax, lo=5310, hi=5430):
    """Annotate signal mass range"""
    lo = ROOT.TLine(lo, ymin, lo, ymax)
    hi = ROOT.TLine(hi, ymin, hi, ymax)
    lo.SetLineColor(ROOT.kAzure)
    hi.SetLineColor(ROOT.kAzure)
    lo.Draw()
    hi.Draw()
    return (lo, hi)


from rplot.tselect import Tselect
selector = Tselect(tree)
selector.exprs = [
    ('lab0_MM>>hist_m0', ''),
    ('lab0_MM>>hist_m1', 'sw'),
    ('lab0_MM>>hist_m2', 'sw>0'),
    ('lab0_MM>>hist_m3', 'sw<0'),
    ('sw>>hist_w1', '5310<lab0_MM && lab0_MM<5430'),
    ('sw>>hist_w2', 'lab0_MM<5310 || 5430<lab0_MM'),
]
hists = selector.fill_hists()

canvas = ROOT.TCanvas('canvas', '', 800, 500)
canvas.Print('sweights.pdf[')

for hist in hists:
    hname = hist.GetName()
    opts = 'e1'
    # No 2D histogram in this loop
    hist.GetXaxis().SetTitle(titles[hist][0])
    if hname in ['hist_m3', 'hist_w2']:
        hist.Draw('{} same'.format(opts))
    else:
        hist.Draw(opts)
    if hname not in ['hist_m2', 'hist_w1']:
        if 0 == hname.find('hist_m'):  # annotate mass histograms
            minmax = get_minmax(hist, axis='y')
            lo, hi = annotate_mass(minmax[0], 1.05*minmax[1])
        canvas.Print('sweights.pdf')

hname = 'hist_2d'
tree.Draw('sw:lab0_MM>>{}'.format(hname))
hist = ROOT.gPad.FindObject(hname)
hist.GetXaxis().SetTitle(titles[hname][0])
hist.GetYaxis().SetTitle(titles[hname][1])
ymin, ymax = get_minmax(hist, axis='y')
xmin, xmax = get_minmax(hist, axis='x')
lo, hi = annotate_mass(ymin, ymax)
zero = ROOT.TLine(xmin, 0, xmax, 0)
zero.SetLineStyle(2)
zero.Draw()
canvas.Print('sweights.pdf')

canvas.Print('sweights.pdf]')
