#!/usr/bin/env python
# coding=utf-8
"""Apply trained MVA"""

import argparse
from utils import _import_args, RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('filename', help='ROOT file')
optparser.add_argument('-s', dest='session',  required=True,
                       help='Session name')
optparser.add_argument('-o', dest='out', help='ROOT file with output')
optparser.add_argument('-n', dest='name', help='Input tree name')
optparser.add_argument('-v', dest='verbose', action='store_true',
                       help='Increase verbosity')
options = optparser.parse_args()
locals().update(_import_args(options))

import sys
import os
if not os.path.exists(filename):
    sys.exit('File not found: {}'.format(filename))

from tmvaconfig import ConfigFile
conf = ConfigFile('TMVA.conf')
if conf.read() > 0:             # read config
    session = conf.get_session_config(session)
print '::: Applying {} MVAs: {}\n{}'.format(len(session.methods),
                                            session.methods, '='*50)
print session
print ':::'

from fixes import ROOT
ROOT.gROOT.SetBatch(True)

# instantiate TMVA
ROOT.TMVA.Tools.Instance()
# reader
reader = ROOT.TMVA.Reader('!Color:!Silent')

# files
ifile = ROOT.TFile.Open(filename, 'read')
ofile = ROOT.TFile.Open(out, 'recreate')

from ROOT import TTreeFormula, TH1D
from array import array
# NOTE: This is to ignore a warning from the call to
# TTreeFormula::EvalInstance().  One of the default arguments is a
# char**.  PyROOT does not provide converters for that, leading to the
# warning.  As long as this feature is not accessed, ignoring is safe.
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                        message='creating converter for unknown type.*')


def add_var_set_br_addr(varlist, reader_method, intree):
    """Add variables to TMVA::Reader, and associate to tree branch"""
    for var in varlist:
        expr = var.split(':=', 1)
        simple = (len(expr) == 1)
        if simple:
            expr = expr * 2  # expr same as key
        allvars[expr[0]] = [array('f', [0.]), TTreeFormula(expr[0], expr[1],
                                                           itree)]
        reader_method(var, allvars[expr[0]][0])
        if simple:
            intree.SetBranchAddress(var, allvars[expr[0]][0])

# input tree
itree = ifile.Get(name)
allvars = {}                    # varname : (value, expr)
# trained variables
add_var_set_br_addr(session.all_vars(), reader.AddVariable, itree)
# spectators
add_var_set_br_addr(session.spectators, reader.AddSpectator, itree)

# output tree
ofile.cd()
otree = itree.CloneTree(0)
for var, val in allvars.iteritems():  # val = (value, expr)
    otree.Branch(var, val[0], '{}/F'.format(var))

# book methods
discriminant = {}               # MVA : (value, histogram)
for method in session.methods:
    reader.BookMVA(method, '{0}/weights/{0}_{1}.weights.xml'
                   .format(session._name, method))
    hname = 'MVA_{}'.format(method)
    # discriminant for output tree
    discriminant[method] = [array('f', [0.]), TH1D(hname, hname, 100, -1., 1.)]
    otree.Branch(method, discriminant[method][0], '{}/F'.format(method))

nentries = itree.GetEntries()
for i in xrange(nentries):
    itree.GetEntry(i)
    for var, val in allvars.iteritems():
        val[1].GetNdata()                  # load formula data
        val[0][0] = val[1].EvalInstance()  # evaluate formula
    for method in session.methods:
        discriminant[method][0][0] = reader.EvaluateMVA(method)
        discriminant[method][1].Fill(discriminant[method][0][0])
    otree.Fill()
    if i % 10000 == 0:
        print "Processed {}/{}".format(i, nentries)

for method in session.methods:
    discriminant[method][1].Write()
otree.Write()
ofile.Close()
ifile.Close()
