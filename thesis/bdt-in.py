#!/usr/bin/env python
# coding=utf-8
"""Plots from input ntuples used for training"""

import argparse
from rplot.utils import RawArgDefaultFormatter

parser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                 description=__doc__)
parser.add_argument('-n', '--ntuple', choices=['data', 'sdata', 'sig', 'bkg'],
                    help='Type of input ntuple')
parser.add_argument('-s', '--session', default='chitra_tune_sw2',
                    help='Session name')
parser.add_argument('-c', dest='conf', default='tmva/TMVA.conf',
                    help='TMVA config file')
parser.add_argument('--vars', nargs='+', help='Variables to plot')
parser.add_argument('--marks', nargs='+', type=float,
                    help='Marker positions along plot axis')
parser.add_argument('-a', '--arrow', nargs=2, type=float,
                    help='Coordinates for arrow head')
parser.add_argument('-y', '--yaxis', action='store_true', help='Mark Y-axis')
parser.add_argument('-b', '--batch', action='store_true', help='Batch mode')
options = parser.parse_args()

import sys
from tmva.tmvaconfig import ConfigFile
# read config
conf = ConfigFile(options.conf)
if conf.read() > 0:
    session = conf.get_session_config(options.session)
else:
    sys.exit('No usable sessions in config file')
if not session:
    sys.exit('Couldn\'t find session in config file')

from rplot.fixes import ROOT
ROOT.gROOT.SetBatch(options.batch)

# files & trees
if options.ntuple in ['sig', 'sdata']:
    infile = session.sig_file
elif options.ntuple in ['bkg', 'data']:
    infile = session.bkg_file
tree = ROOT.TChain('MyChain')
map(lambda f: tree.Add(f), infile)

if not tree:
    sys.exit('Unable to read input trees.')

from rplot.tselect import Tsplice
splice = Tsplice(tree)
if options.ntuple.find('data') >= 0:
    cut = ROOT.TCut(session.cut_both)
elif 'sig' == options.ntuple:
    cut = ROOT.TCut(session.cut_sig)
elif 'bkg' == options.ntuple:
    cut = ROOT.TCut(session.cut_bkg)
splice.make_splice(options.ntuple, cut)

# disable fluff
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)

variables = options.vars
marks = options.marks if options.marks else []
nvars, nmarks = len(variables), len(marks) if marks else 0
if nvars > nmarks:
    marks += [None] * (nvars - nmarks)
hists = {}

# histograms
import uuid
from tmva.utils import get_label
for var, mark in zip(variables, marks):
    hname = 'hist_{}'.format(uuid.uuid4())
    if options.ntuple in ['sdata', 'sig']:
        wt = session.sigwt
    else:
        wt = ''
    tree.Draw('{}>>{}'.format(var, hname), wt, 'goff')
    hist = ROOT.gROOT.FindObject(hname)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetMarkerStyle(ROOT.kFullDotLarge)
    hist.SetMarkerSize(0.4)
    # hist.SetMarkerColor(ROOT.kBlack)
    hist.SetXTitle(get_label(var))
    hists[var] = (hist, mark)

# plots
from utils import get_mark, get_arrow
for var, tup in hists.iteritems():
    hist, mark = tup
    hist.Draw('e')
    if mark:
        axis = get_mark(hist, mark, options.yaxis)
        axis.SetLineWidth(2)
        axis.SetLineColor(ROOT.kRed)
        axis.Draw()
        if options.arrow:
            arr = get_arrow(mark, options.arrow, options.yaxis, 0.03, '|>')
            arr.SetLineWidth(2)
            arr.SetAngle(45)
            arr.SetLineColor(ROOT.kRed)
            arr.SetFillColor(ROOT.kRed)
            arr.Draw()
    ROOT.gPad.Print('bdt_in_{}_{}.png'.format(options.ntuple, var))
