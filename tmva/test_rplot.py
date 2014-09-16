#!/usr/bin/env python

from fixes import ROOT
ROOT.gROOT.SetBatch(True)

## Test overlaying with transparency
hists = [ROOT.TH1F('hist{}'.format(i), '', 100, -10, 10) for i in xrange(16)]
for i, hist in enumerate(hists):
    fn = ROOT.TF1('fn{}'.format(i), 'TMath::Gaus(x, {0}, 1)'.format(i-8), -10, 10)
    hist.FillRandom('fn{}'.format(i), 1000)
    hist.SetXTitle('Foo[bar]')
    hist.SetYTitle('Events')
    del fn

from string import ascii_lowercase
histl = [ROOT.TH1F('hist{}'.format(l), '', 100, -10, 10) for l in ascii_lowercase[0:2]]
for i, l in enumerate(ascii_lowercase[0:2]):
    fn = ROOT.TF1('fn{}'.format(l), 'TMath::Gaus(x, {0}, 1)'.format(i), -10, 10)
    histl[i].FillRandom('fn{}'.format(l), 1000)
    histl[i].SetXTitle('Foo[bar]')
    histl[i].SetYTitle('Events')

histograms = [
    [h for i, h in enumerate(hists) if i % 2 == 0],
    [h for i, h in enumerate(hists) if i % 2 == 1],
    histl[0], histl[1]
]

import rplot

plotter = rplot.Rplot(2,2)
plotter.draw_hist(histograms, 'hist')

plotter.canvas.Update()
plotter.canvas.Print('test.pdf[')
plotter.canvas.Print('test.pdf')
del plotter, histograms

## Test stacking
hists = [ROOT.TH1F('hist{}'.format(i), '', 100, -10, 10) for i in xrange(6)]
for i, hist in enumerate(hists):
    fn = ROOT.TF1('fn{}'.format(i), '{}*TMath::Gaus(x, 0, {})'.format(1./(i+1), i-3), -10, 10)
    hist.FillRandom('fn{}'.format(i), 1000)
    hist.SetXTitle('Foo[bar]')
    hist.SetYTitle('Events')
    del fn

histograms = [
    [h for i, h in enumerate(hists) if i % 2 == 0],
    [h for i, h in enumerate(hists) if i % 2 == 1],
]

plotter = rplot.Rplot(2,1)
plotter.stack = True
plotter.draw_hist(histograms, 'hist')

plotter.canvas.Update()
plotter.canvas.Print('test.pdf')
plotter.canvas.Print('test.pdf]')
del plotter, histograms
