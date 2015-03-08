#!/usr/bin/env python
# coding=utf-8
"""Train TMVA algorithm"""

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', nargs='?', default=None, help='ROOT file')
optparser.add_argument('-s', dest='session', required=True,
                       help='Session name')
optparser.add_argument('--sig', dest='sig_tree', help='Signal tree name '
                       '(mandatory when filename present)')
optparser.add_argument('--bkg', dest='bkg_tree', help='Background tree name '
                       '(mandatory when filename present)')
optparser.add_argument('-o', dest='out', required=True, help='Output file')
optparser.add_argument('-c', dest='conf', default='TMVA.conf',
                       help='TMVA config file')
options = optparser.parse_args()
locals().update(_import_args(options))
# variables for future proofing
wdir = 'weights'                # weights directory

import sys
import os
if filename and not os.path.exists(filename):
    sys.exit('File not found: {}'.format(filename))
if filename and not (sig_tree and bkg_tree):
    # required when input file is provided as positional argument
    sys.exit('Missing signal and background tree names')

from tmvaconfig import TMVAType, ConfigFile
# read config
conf = ConfigFile(conf)
if conf.read() > 0:
    session = conf.get_session_config(session)
print '::: Training {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

from fixes import ROOT
ROOT.gROOT.SetBatch(True)

# files & trees
if not filename:                # config file
    tree_s = ROOT.TChain(sig_tree if sig_tree else 'TreeSig')
    map(lambda f: tree_s.Add(f), session.sig_file)
    tree_b = ROOT.TChain(bkg_tree if bkg_tree else 'TreeBkg')
    map(lambda f: tree_b.Add(f), session.bkg_file)
else:                           # CLI options
    ifile = ROOT.TFile.Open(filename)
    tree_s = ifile.Get(sig_tree)
    tree_b = ifile.Get(bkg_tree)

if not tree_s or not tree_b:
    sys.exit('Unable to read input trees.')

ofile = ROOT.TFile.Open(out, 'recreate')

# instantiate TMVA
ROOT.TMVA.Tools.Instance()
# TMVA.gConfig.GetIONames().fWeightFileDir = wdir
factory = ROOT.TMVA.Factory(session._name, ofile, '!V:DrawProgressBar=False:' +
                            ':'.join(session.factory_opts))

map(lambda var: factory.AddVariable(var, 'F'))   # training variables
map(lambda var: factory.AddSpectator(var, 'F'))  # spectator variables

# get tree and perform branch name mappings if necessary
factory.AddSignalTree(tree_s, 1.0)
factory.AddBackgroundTree(tree_b, 1.0)

# # apply event weights if necessary
# factory.SetBackgroundWeightExpression('weight')

# selection cuts, if any
factory.PrepareTrainingAndTestTree(session.cut_sig, session.cut_bkg,
                                   '!V:' + ':'.join(session.training_opts))

# book methods
map(lambda method: factory.BookMethod(TMVAType(method), method, '!H:!V:' +
                                      ':'.join(getattr(session, method))),
    session.methods)

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
