#!/usr/bin/env python
# coding=utf-8

import argparse

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', help='ROOT file')
optparser.add_argument('-s', dest='session', help='Session name')
optparser.add_argument('-o', dest='out', help='ROOT file with output histograms')
options = optparser.parse_args()
filename = options.filename
session = options.session
out = options.out 

import sys, os
if not os.path.exists(filename):
    sys.exit('File not found: {}'.format(filename))

from array import array

from ROOT import gROOT
gROOT.SetBatch(True)

from ROOT import gDirectory, gSystem, gPad, gStyle
from ROOT import TFile, TTree, TH1D, TH2D, TH3D, TCanvas, TPad

from ROOT import TMVA
from tmvaconfig import TMVAconfig, ConfigFile

# instantiate
TMVA.Tools.Instance()

# ownership
TFile.Open._creates = True

# files
ifile = TFile.Open(filename, 'read')
ofile = TFile.Open(out, 'recreate')

# reader
reader = TMVA.Reader('!Color:!Silent')

# read config
conf = ConfigFile('TMVA.conf')
if conf.read() > 0:
    session = conf.get_session_config(session)
print '::: Applying {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

# trained variables
allvars = []
for var in session.all_vars():
    allvars += [array('f', [0.])]
    reader.AddVariable(var, allvars[-1])

# prepare apply tree
itree = ifile.Get('TreeS')
for i, var in enumerate(session.vars):
    # combined vars at the end (ignored)
    itree.SetBranchAddress(var, allvars[i])

# prepare output tree
ofile.cd()
otree = itree.CloneTree(0)
for i, var in enumerate(session.all_vars()):
    # variables for output tree
    otree.Branch(var, allvars[i], '{}/F'.format(var))

# spectators
spectators = []
for var in session.spectators:
    spectators += [array('f', [0.])]
    reader.AddSpectator(var, spectators[-1])

# book methods
hists_discr = {}
discriminant = {}
for method in session.methods:
    reader.BookMVA(method, 'weights/TMVAClassification_{}.weights.xml'
                   .format(method))
    # output histogram
    hname = 'MVA_{}'.format(method)
    hists_discr[method] = TH1D(hname, hname, 100, -1.0, 1.0 )

    # discriminant for output tree
    discriminant[method] = array('f', [0.])
    otree.Branch(method, discriminant[method], '{}/F'.format(method))

for i in range(itree.GetEntries()):
    itree.GetEntry(i)
    allvars[4][0] = allvars[0][0] + allvars[1][0]
    allvars[5][0] = allvars[0][0] - allvars[1][0]
    for method in session.methods:
        discriminant[method][0] = reader.EvaluateMVA(method)
        hists_discr[method].Fill(discriminant[method][0])
    otree.Fill()

for method in session.methods:
    hists_discr[method].Write()
otree.Write()
ofile.Close()
ifile.Close()
