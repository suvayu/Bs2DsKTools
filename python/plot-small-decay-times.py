#!/usr/bin/env python
# coding=utf-8
"""Plot random things from Monte Carlo

Look at different things (pT, χ², η, ..) that might be affected by
PIDK cuts.  The goal is to find something that influences the Bs decay
time distribution which in turn leads to less DsK events for very
small decay times (< 0.5 ps).

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

from rplot.fixes import ROOT
ROOT.gROOT.SetBatch(doPrint)

# ROOT classes
from ROOT import TFile, TCut, TH1D, TLegend

# my libs
from helpers import sanitise_str_src, sanitise_str


## Read from file
if reverse:
    modes = ['dspi', 'dsk']
else:
    modes = ['dsk', 'dspi']
pmodes = {'dsk': 'DsK', 'dspi': 'Ds#pi'}

files = {
    'dsk' : TFile.Open('data/smalltree-really-new-MC-pre-PID-DsK.root'),
    'dspi': TFile.Open('data/smalltree-really-new-MC-pre-PID-DsPi.root')
}
trees = {
    'dsk' : files['dsk'].Get('ftree'),
    'dspi': files['dspi'].Get('ftree')
}

variables = ('hMom.Pt()', 'hMom.Eta()', 'hIPchi2')
prettyvars = ('h p_{T} [MeV/c]', 'h #eta', 'h IP #chi^{2}')
# variables = ['lab1_IPCHI2_OWNPV']
# prettyvars = ['h IP #chi^{2}']

cuts = {
    'nocuts'    : TCut(''),
    'timelt2ps' : TCut('time<2.0'), # from small tree
    'dsk'       : TCut('PIDK>10'),
    'dspi'      : TCut('PIDK<0'),
    'bdt'       : TCut('BDTG>0.5'),
    'HLT1'      : TCut('HLT1TrackAllL0TOS > 0'),
    'HLT22Body' : TCut('HLT2Topo2BodyTOS > 0'),
    'HLT23Body' : TCut('HLT2Topo3BodyTOS > 0'),
    'HLT24Body' : TCut('HLT2Topo4BodyTOS > 0')
    # 'timelt2ps' : Cut('lab0_TAU<1.0'), # from ntuples directly
    # 'dsk'       : Cut('lab1_PIDK>10'),
    # 'dspi'      : Cut('lab1_PIDK<0'),
    # 'bdt'       : Cut('BDTGResponse_1>0.5'),
    # 'HLT1'      : Cut('lab0_Hlt1TrackAllL0Decision_TOS > 0'),
    # 'HLT22Body' : Cut('lab0_Hlt2Topo4BodyBBDTDecision_TOS > 0'),
    # 'HLT23Body' : Cut('lab0_Hlt2Topo3BodyBBDTDecision_TOS > 0'),
    # 'HLT24Body' : Cut('lab0_Hlt2Topo2BodyBBDTDecision_TOS > 0')
}

cuts['HLT2'] = TCut('({})||({})||({})'.format(cuts['HLT22Body'],
                                              cuts['HLT23Body'],
                                              cuts['HLT24Body']))
cuts['trig'] = cuts['HLT1'] + cuts['HLT2']

htypes = [
    'nocuts', 'pid', 'bdt', 'trig',    # base
    # 'pid_bdt', 'pid_trig', 'bdt_trig', # permutations of 2
    # 'pid_bdt_trig'                     # all
]

histograms = []                 # list of dicts, keys: dsk, dspi
hprofiles = []                  # list of dicts, keys: dsk, dspi


## pT and η distributions for different cuts
for htype in htypes:
    for v, var in enumerate(variables):
        if var.lower().find('pt') >= 0:
            binning = (100, 0.0, 2E4)
        elif var.lower().find('eta') >= 0:
            binning = (100, 1.5, 5.0)
        elif var.lower().find('ipchi2') >= 0:
            binning = (100, 0.0, 1E3)
        elif var.lower().find('time') >= 0:
            binning = (100, 0.0, 1.5)
        else:
            print 'Unknown variable, weird things will happen.'
        hpair = {}
        max_y_n = 0             # max Y after normalisation
        for mode in modes:
            # ensure identical binning
            hname = 'h{}_{}_{}'.format(mode, htype, sanitise_str_src(var))
            # print hname
            hist = TH1D(hname, '{0} {1} {2};{2}'
                        .format(pmodes[mode], htype, prettyvars[v]), *binning)
            cut = cuts['timelt2ps']
            cut_tokens = htype.split('_')
            for token in cut_tokens:
                if token.find('nocuts') >= 0:
                    pass
                elif token.find('pid') >= 0:
                    cut = cut + cuts[mode]
                elif token.find('bdt') >= 0:
                    cut = cut + cuts['bdt']
                elif token.find('trig') >= 0:
                    cut = cut + cuts['trig']
                else:
                    print 'Unknown permutation of cuts, weird things will happen.'
            sel = trees[mode].Draw('{}>>{}'.format(var, hist.GetName()), cut, 'goff')
            hpair[mode] = hist
            # determine max Y for normalised histograms
            if max_y_n < hpair[mode].GetMaximum()/hpair[mode].Integral():
                max_y_n = hpair[mode].GetMaximum() / hpair[mode].Integral()
        # set max Y so that histograms fit in pad
        for mode in modes:
            hpair[mode].SetMaximum(1.1 * max_y_n * hpair[mode].Integral())
        histograms.append(hpair)

hists = map(lambda hs: (hs['dsk'], hs['dspi']), histograms)

from rplot.rplot import Rplot
plotter = Rplot(1, 3, 1024, 1920)
canvas = plotter.prep_canvas()
plotfile = 'plots/timelt2ps_%s.pdf' % sanitise_str_src('_'.join(variables))
if doPrint:
    canvas.Print(plotfile + '[')

# create legend
legend = TLegend(0.6, 0.6, 0.95, 0.75)
legend.SetLineWidth(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.035)
legend.SetHeader('%s ps'.format(sanitise_str(str(cuts['timelt2ps']))))
plotter.add_legend(legend, 'lep')

for i in xrange(0, len(hists), 3):
    plotter.draw_hist(hists[i:i+3], 'e1', normalised=True)
    if doPrint:
        canvas.Print(plotfile)
if doPrint:
    canvas.Print(plotfile + ']')
    del plotter
