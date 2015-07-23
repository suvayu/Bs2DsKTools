# coding=utf-8
"""
This module provides helper functions to get different ROOT and RooFit
objects.

@author Suvayu Ali

"""

# Python modules
import os
import sys
from datetime import datetime


# Hack around RooWorkspace.import() and python keyword import clash
# _import = getattr(RooWorkspace, 'import')  # ROOT 6 bug
def _import(wsp, obj):
    getattr(wsp, 'import')(obj)


# Python wrappers
def get_timestamp(fmt='%Y-%m-%d-%a-%H-%M'):
    """Return formatted timestamp."""
    return datetime.strftime(datetime.today(), fmt)


# ROOT wrappers
def load_library(library):
    from rplot.fixes import ROOT
    loadstatus = {
        0: 'loaded',
        1: 'already loaded',
        -1: 'does not exist',
        -2: 'version mismatch'
    }
    status = ROOT.gSystem.Load(library)
    if status < 0:
        sys.exit('Problem loading %s, %s' % (library, loadstatus[status]))


def get_file(fname, mode='read'):
    """Open and return a ROOT file."""
    from rplot.fixes import ROOT
    if os.path.exists(fname):
        return ROOT.TFile(fname, mode)
    else:
        raise IOError('File %s does not exist!' % fname)


def get_object(objname, rfile, subdir=''):
    """Get a ROOT object from a ROOT file by name."""
    if len(subdir):
        subdir += '/'
    return rfile.Get('%s%s' % (subdir, objname))


# RooFit wrappers
def get_argset(args):
    """Return and argset of the RooFit objects."""
    from rplot.fixes import ROOT
    argset = ROOT.RooArgSet()
    for arg in args:
        if arg.InheritsFrom(ROOT.RooAbsArg.Class()):
            argset.add(arg)
        else:
            TypeError('%s should inherit from RooAbsArg' % arg.GetName())
    return argset


def get_arglist(args):
    """Return and arglist of the RooFit objects."""
    from rplot.fixes import ROOT
    arglist = ROOT.RooArgList()
    for arg in args:
        if arg.InheritsFrom(ROOT.RooAbsArg.Class()):
            arglist.add(arg)
        else:
            TypeError('%s should inherit from RooAbsArg' % arg.GetName())
    return arglist


def set_integrator_config():
    """Configure numerical integration in RooFit.

    More precise integrals in RooFit and how intervals are
    determined and integrals calculated.

    """

    from rplot.fixes import ROOT
    # More precise integrals in RooFit
    numintconf = ROOT.RooAbsReal.defaultIntegratorConfig()
    numintconf.setEpsAbs(1e-9)
    numintconf.setEpsRel(1e-9)
    # Set how intervals are determined and integrals calculated
    numintconf.getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method', '21Points')
    numintconf.getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    numintconf.method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    numintconf.method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')


def get_toy_dataset(varargset, PDF=None):
    """Return a toy dataset for the given PDF."""

    from rplot.fixes import ROOT
    from ROOT import TClass, RooAbsPdf, RooFit
    objclass = TClass.GetClass(PDF.ClassName())
    if objclass.InheritsFrom(RooAbsPdf.Class()):
        dataset = PDF.generate(varargset, 10000, RooFit.Name('toydataset'),
                               RooFit.Verbose(True))
        print 'Toy generation completed with %s' % PDF.GetName()
        return dataset
    else:
        raise TypeError('PDF should inherit from RooAbsPdf.')


def get_dataset(varargset, ftree, cut='', wt=''):
    """Return a dataset.

    Return a dataset from the ntuple `ftree'. Apply a selection cut
    using the `cutVar' variable and the selection `cut'.

    """

    from rplot.fixes import ROOT
    from rplot.tselect import Tsplice
    splice = Tsplice(ftree)
    splice.make_splice('sel', cut)
    from ROOT import RooDataSet, RooFit, RooFormulaVar, RooArgList
    tmpdst = RooDataSet('tmpdataset', '', varargset, RooFit.Import(ftree))
    if wt:
        wtvar = RooFormulaVar('wt', '@0', RooArgList(varargset[wt]))
        wtvar = tmpdst.addColumn(wtvar)
        varargset.remove(varargset[wt])
        varargset.add(wtvar)
        dst = RooDataSet('dataset', 'Dataset', varargset,
                         RooFit.Import(tmpdst), RooFit.WeightVar(wtvar))
        varargset.remove(wtvar)
        dst = dst.reduce(varargset)
    return dst


def fill_dataset(varargset, ftree, wt, wtvar, cut=''):
    """Return a dataset (slow, get_dataset is more efficient).

    Return a dataset from the ntuple `ftree', also apply `cut'.  Use
    `wt' as the weight expression in the tree.  `wtvar' is the
    corresponding RooRealVar weight.  Note, varargset should contain
    wtvar.

    The dataset is filled by iterating over the tree.  This is needed
    when you want to ensure different datasets have the same weight
    variable names, so that they can be combined later on.  This is
    needed even if they are combined as different categories.

    """

    from rplot.fixes import ROOT
    from ROOT import RooDataSet, RooFit, TTreeFormula
    from helpers import suppress_warnings
    suppress_warnings()
    from rplot.tselect import Tsplice
    splice = Tsplice(ftree)
    splice.make_splice('sel', cut)

    formulae = {}
    wtname = wtvar.GetName()
    for var in varargset:
        name = var.GetName()
        expr = wt if name == wtname else name
        formulae[name] = TTreeFormula(name, expr, ftree)

    dataset = RooDataSet('dataset', 'Dataset', varargset,
                         RooFit.WeightVar(wtvar))
    for i in xrange(ftree.GetEntries()):
        ftree.GetEntry(i)
        for var, expr in formulae.iteritems():
            realvar = varargset.find(var)
            realvar.setVal(expr.EvalInstance())
        dataset.add(varargset, varargset[wtname].getVal())
    return dataset


def save_in_workspace(rfile, **argsets):
    """Save RooFit objects in workspace and persistify.

    Pass the different types of objects as a keyword arguments. e.g.
    save_in_workspace(pdf=[pdf1, pdf2], variable=[var1, var2])

    """

    from rplot.fixes import ROOT
    import traceback
    # Persistify variables, PDFs and datasets
    workspace = ROOT.RooWorkspace('workspace',
                                  'Workspace saved at %s' % get_timestamp())
    keys = argsets.keys()
    for key in keys:
        print 'Importing RooFit objects in %s list.' % key
        for arg in argsets[key]:
            try:
                _import(workspace, arg)
            except TypeError:
                print type(arg), arg
                traceback.print_exc()
    rfile.WriteTObject(workspace)
    print 'Saving arguments to file: %s' % rfile.GetName()


def get_workspace(fname, wname):
    """Read and return RooWorkspace from file."""
    ffile = get_file(fname, 'read')
    workspace = ffile.Get(wname)
    return workspace, ffile
