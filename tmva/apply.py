#!/usr/bin/env python
# coding=utf-8
"""Apply trained MVA"""

import argparse
from utils import RawArgDefaultFormatter

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('filename', help='Input ROOT file')
optparser.add_argument('-s', '--session', required=True, help='Session name')
optparser.add_argument('-o', '--out', required=True, help='Output ROOT file')
optparser.add_argument('-n', '--name', required=True, help='Input tree name')
options = optparser.parse_args()

import sys
import os
if not os.path.exists(options.filename):
    sys.exit('File not found: {}'.format(options.filename))

from tmvaconfig import ConfigFile
conf = ConfigFile('TMVA.conf')
if conf.read() > 0:             # read config
    session = conf.get_session_config(options.session)
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
ifile = ROOT.TFile.Open(options.filename, 'read')
ofile = ROOT.TFile.Open(options.out, 'recreate')

from ROOT import TTreeFormula, TH1D
from array import array
# NOTE: This is to ignore a warning from the call to
# TTreeFormula::EvalInstance().  One of the default arguments is a
# char**.  PyROOT does not provide converters for that, leading to the
# warning.  As long as this feature is not accessed, ignoring is safe.
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                        message='creating converter for unknown type.*')


def add_var_set_br_addr(varlist, reader_method, intree, allvars):
    """Add variables to TMVA::Reader, and associate to tree branch"""
    for var in varlist:
        expr = var.split(':=', 1)  # split var:=var1+var2 -> (var, var1+var2)
        simple = (len(expr) == 1)  # if simple, (var,)
        if simple:
            expr = expr * 2        # expr same as key: (var,) -> (var, var)
        allvars[expr[0]] = [
            array('f', [0.]),      # array for TMVA::Reader
            TTreeFormula(expr[0], expr[1], intree)
        ]
        reader_method(var, allvars[expr[0]][0])

# input tree
itree = ifile.Get(options.name)
allvars = {}                    # {varname: (value, expr)}
# training variables
add_var_set_br_addr(session.all_vars(), reader.AddVariable, itree, allvars)
# spectators
add_var_set_br_addr(session.spectators, reader.AddSpectator, itree, allvars)

# output tree
ofile.cd()
otree = itree.CloneTree(0)
# FIXME: I think the following two lines are redundant
for var, val in allvars.iteritems():  # var, val = varname, (value, expr)
    otree.Branch(var, val[0], '{}/F'.format(var))

# book methods
discriminant = {}               # {MVA: (value, histogram)}
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
