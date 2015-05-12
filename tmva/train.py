#!/usr/bin/env python
# coding=utf-8
"""Train TMVA algorithm"""

import argparse
from utils import RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('session', help='Session name')
optparser.add_argument('--sigtree', default='SigTree',
                       help='Signal tree name')
optparser.add_argument('--bkgtree', default='BkgTree',
                       help='Background tree name')
optparser.add_argument('-o', dest='out', required=True, help='Output file')
optparser.add_argument('-c', dest='conf', default='TMVA.conf',
                       help='TMVA config file')
options = optparser.parse_args()

# variables for future proofing
wdir = 'weights'                # weights directory

import sys
from tmvaconfig import TMVAType, ConfigFile
# read config
conf = ConfigFile(options.conf)
if conf.read() > 0:
    session = conf.get_session_config(options.session)
else:
    sys.exit('No usable sessions in config file')
if not session:
    sys.exit('Couldn\'t find session in config file')
print '::: Training {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

from fixes import ROOT
ROOT.gROOT.SetBatch(True)

# files & trees
tree_s = ROOT.TChain(options.sigtree)
map(lambda f: tree_s.Add(f), session.sig_file)
tree_b = ROOT.TChain(options.bkgtree)
map(lambda f: tree_b.Add(f), session.bkg_file)

if not tree_s or not tree_b:
    sys.exit('Unable to read input trees.')

# NOTE: This is to ignore the security warning from os.tmpnam.  There
# is no risk since I `recreate' the TFile.
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                        message='tmpnam is a potential security risk.*')
import os
from time import strftime, localtime
tmpfile = ROOT.TFile.Open('{}-{}.root'.format(
    os.tmpnam(), strftime('%y-%m-%d-%H%M%S%Z', localtime())), 'recreate')

# Apply selection cuts here instead of PrepareTrainingAndTestTree().
# If selection involves a branch present in only one of the trees, it
# will fail.  So copy selection to a tree in a temporary file, and
# pass that to TMVA::Factory(..).
clone_tree_s = tree_s.CopyTree(str(session.cut_sig))
clone_tree_s.SetName(options.sigtree)
clone_tree_s.Write()
clone_tree_b = tree_b.CopyTree(str(session.cut_bkg))
clone_tree_b.SetName(options.bkgtree)
clone_tree_b.Write()

del tree_s, tree_b
tree_s, tree_b = clone_tree_s, clone_tree_b

ofile = ROOT.TFile.Open(options.out, 'recreate')

# instantiate TMVA
ROOT.TMVA.Tools.Instance()
# TMVA.gConfig.GetIONames().fWeightFileDir = wdir
factory = ROOT.TMVA.Factory(session._name, ofile, '!V:DrawProgressBar=False:' +
                            ':'.join(session.factory_opts))

map(lambda var: factory.AddVariable(var, 'F'), session.all_vars())
map(lambda var: factory.AddSpectator(var, 'F'), session.spectators)

# get tree and perform branch name mappings if necessary
factory.AddSignalTree(tree_s, 1.0)
factory.AddBackgroundTree(tree_b, 1.0)

# apply event weights if necessary
if session.bkgwt:
    factory.SetBackgroundWeightExpression(session.bkgwt)
if session.sigwt:
    factory.SetSignalWeightExpression(session.sigwt)

# selection cuts, if any
factory.PrepareTrainingAndTestTree(ROOT.TCut(''),
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

# remove temporary file
tmpfile.Close()
os.remove(tmpfile.GetName())

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
os.rename(options.out, '{}/{}'.format(session._name, options.out))
