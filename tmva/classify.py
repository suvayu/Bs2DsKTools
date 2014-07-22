#!/usr/bin/env python
# coding=utf-8

import argparse

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', help='ROOT file')
optparser.add_argument('-s', dest='session', help='Session name')
optparser.add_argument('-o', dest='out', help='Output ROOT file')
options = optparser.parse_args()
filename = options.filename
session = options.session
out = options.out 

import sys, os
if not os.path.exists(filename):
    sys.exit('File not found: {}'.format(filename))

from ROOT import gDirectory, gROOT, gSystem, gPad, gStyle
from ROOT import TFile, TTree, TH1D, TH2D, TH3D, TCanvas, TPad

from ROOT import TMVA
from tmvaconfig import TMVAconfig, ConfigFile

# instantiate
TMVA.Tools.Instance()

# ownership
TFile.Open._creates = True

# files
ifile = TFile.Open(filename)
ofile = TFile.Open(out, 'recreate')

factory = TMVA.Factory("TMVAClassification", ofile, "!V:!Silent:Color" + \
                       ":DrawProgressBar:Transformations=I;D;P;G,D")

# read config
conf = ConfigFile('TMVA.conf')
if conf.read() > 0:
    session = conf.get_session_config(session)
print '::: Training {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

# training variables
for var in session.all_vars():
    factory.AddVariable(var, 'F')

# spectator variables
for var in session.spectators:
    factory.AddSpectator(var, 'F')

# get tree and perform branch name mappings if necessary
tree_s = ifile.Get('TreeS')
tree_b = ifile.Get('TreeB')
factory.AddSignalTree(tree_s, 1.0)
factory.AddBackgroundTree(tree_b, 1.0)

# apply event weights if necessary
factory.SetBackgroundWeightExpression('weight')

# selection cuts, if any
factory.PrepareTrainingAndTestTree(session.cut_sig, session.cut_bkg,
                                   'nTrain_Signal=0:nTrain_Background=0' + \
                                   ':SplitMode=Random:NormMode=NumEvents:!V')

# book methods (FIXME: only one for now)
for method in session.methods:
    factory.BookMethod(TMVA.Types.kBDT, method, '!H:!V:NTrees=1000' + \
                       ':MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10' +\
                       ':UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20' +\
                       ':MaxDepth=2')
                   # '!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.30:UseBaggedGrad'+
                   # ':GradBaggingFraction=0.6:SeparationType=GiniIndex:nCuts=20'+
                   # ':PruneMethod=CostComplexity:PruneStrength=50:NNodesMax=5')

# train, test, evaluate
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
ofile.Close()

print '::: Training MVAs done!'
