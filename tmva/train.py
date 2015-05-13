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
optparser.add_argument('-n', dest='norm', action='store_true',
                       help='Normalise (ensure similar order) sample sizes')
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

nentries_s = tree_s.GetEntries(str(session.cut_sig))
nentries_b = tree_b.GetEntries(str(session.cut_bkg))

# NOTE: normalise: create option like
# nTrain_Signal=num:nTrain_Background=num:...
if options.norm:
    size = nentries_b if nentries_s > nentries_b else nentries_s

    from itertools import product
    get_optstr = lambda i: '{1}_{2}={0}'.format(int(size/2), *i)
    samples = product(('nTrain', 'nTest'), ('Background', 'Signal'))
    session.training_opts += map(get_optstr, samples)

# TODO: x-validate


from rplot.utils import Rtmpfile
with Rtmpfile() as tmpfile:
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
        # FIXME: correct weights for ignored events, since sweights:
        # MVA weight = sw - (∑sw(M<5310 && M>5430))/entries(M<5310 && M>5430)
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

# move output to session directory
import os
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
