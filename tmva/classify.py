#!/usr/bin/env python
# coding=utf-8

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', nargs='?', default = None, help='ROOT file')
optparser.add_argument('-s', dest='session', required=True, help='Session name')
optparser.add_argument('--sig', dest='sig_tree', help='Signal tree name (mandatory when filename present)')
optparser.add_argument('--bkg', dest='bkg_tree', help='Background tree name (mandatory when filename present)')
optparser.add_argument('-o', dest='out', required=True, help='Output ROOT file')
options = optparser.parse_args()
locals().update(_import_args(options))
# variables for future proofing
wdir = 'weights'                # weights directory

import sys, os
if filename and not os.path.exists(filename):
    sys.exit('File not found: {}'.format(filename))
if filename and not (sig_tree and bkg_tree):
    # required when input file is provided as positional argument
    sys.exit('Missing signal and background tree names')

from ROOT import gROOT
gROOT.SetBatch(True)

from ROOT import gDirectory, gSystem, gPad, gStyle
from ROOT import TFile, TTree, TChain, TH1D, TH2D, TH3D, TCanvas, TPad

from ROOT import TMVA
from tmvaconfig import TMVAType, TMVAconfig, ConfigFile

# ownership
TFile.Open._creates = True

# read config
conf = ConfigFile('TMVA.conf')
if conf.read() > 0:
    session = conf.get_session_config(session)
print '::: Training {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

# files & trees
if not filename:                # config file
    tree_s = TChain(sig_tree if sig_tree else 'TreeSig')
    for f in session.sig_file:
        tree_s.Add(f)
    tree_b = TChain(bkg_tree if bkg_tree else 'TreeBkg')
    for f in session.bkg_file:
        tree_b.Add(f)
else:                           # CLI options
    ifile = TFile.Open(filename)
    tree_s = ifile.Get(sig_tree)
    tree_b = ifile.Get(bkg_tree)

if not tree_s or not tree_b:
    sys.exit('Unable to read input trees.')

ofile = TFile.Open(out, 'recreate')

# instantiate TMVA
TMVA.Tools.Instance()
# TMVA.gConfig.GetIONames().fWeightFileDir = wdir
factory = TMVA.Factory(session._name, ofile, '!V:' + \
                       ':'.join(session.factory_opts))

# training variables
for var in session.all_vars():
    factory.AddVariable(var, 'F')

# spectator variables
for var in session.spectators:
    factory.AddSpectator(var, 'F')

# get tree and perform branch name mappings if necessary
factory.AddSignalTree(tree_s, 1.0)
factory.AddBackgroundTree(tree_b, 1.0)

# # apply event weights if necessary
# factory.SetBackgroundWeightExpression('weight')

# selection cuts, if any
factory.PrepareTrainingAndTestTree(session.cut_sig, session.cut_bkg,
                                   '!V:' + ':'.join(session.training_opts))

# book methods
for method in session.methods:
    opts = ':'.join(getattr(session, method))
    factory.BookMethod(TMVAType(method), method, '!H:!V:' + opts)

# train, test, evaluate
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
ofile.Close()

print '::: Training MVAs done!'

# move output to session directory
print '::: Moving all output to {}'.format(session._name)
try:
    os.makedirs(session._name)
except OSError as err:
    import errno
    if err.errno == errno.EEXIST:
        pass
    else:
        raise
import shutil
oldwdir = '{}/{}'.format(session._name, wdir)
shutil.rmtree(oldwdir, True)
os.rename(wdir, oldwdir)
os.rename(out, '{}/{}'.format(session._name, out))
