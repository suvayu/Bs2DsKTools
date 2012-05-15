#!/usr/bin/env python
# coding=utf-8
"""Plot fit results from persistified workspace.

"""

# Python modules
import os
import sys
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this
epsilon = 1E-4

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
# gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass

# RooFit classes
from ROOT import RooFit, RooGlobalFunc
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel

# Hack around RooWorkspace.import() and python keyword import clash
_import = getattr(RooWorkspace, 'import')

# More precise integrals in RooFit
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)

def get_workspace(fname=None):
    """Read RooWorkspace from file."""

    if fname == None:
        fname = 'data/fitresult.root'
    if os.path.exists(fname):
        ffile = TFile(fname, 'read')
        fworkspace = ffile.Get('workspace')
        return fworkspace
    else:
        raise IOError('File %s does not exist!' % fname)


def get_obj(objname=None, workspace=None, objtype=''):
    """Return obj named `objname' from workspace."""

    objclass = TClass.GetClass(workspace.ClassName())
    if objclass.InheritsFrom(RooWorkspace.Class()):
        if objtype.lower() == 'pdf':
            return workspace.pdf(objname)
        elif objtype.lower() == 'var':
            return workspace.var(objname)
        elif objtype.lower() == 'data':
            return workspace.data(objname)
        else:
            return workspace.obj(objname)
    else:
        raise TypeError('Wrong type. workspace should inherit from RooWorkspace.')


def main(identifier='zoomed'):
    """Plot PDF and dataset from workspace."""

    # workspace
    workspace = get_workspace('data/fitresult.root')
    # variables
    time = get_obj(objname='time', workspace=workspace, objtype='var')
    dt = get_obj(objname='dt', workspace=workspace, objtype='var')
    # PDFs
    acceptance = get_obj(objname='acceptance', workspace=workspace, objtype='var')
    acceptancePdf = RooGenericPdf('acceptancePdf', '@0', RooArgList(acceptance))
    PDF = get_obj(objname='FullModel', workspace=workspace, objtype='pdf')
    # dataset
    dataset = get_obj(objname='dataset', workspace=workspace, objtype='data')

    # argset
    timeargset = RooArgSet(time)
    dtargset = RooArgSet(dt)
    # time.setRange('fullrange', epsilon, 0.01)

    # plot
    # NOTE: this range is for the dataset binning
    time.setRange('zoom', 0., 1E-3)
    # NOTE: this range is for the RooPlot axis
    tframe1 = time.frame(RooFit.Range('zoom'), RooFit.Name('pztime'),
                         RooFit.Title('Projection on time (zoomed)'))
    dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp),
                   RooFit.CutRange('zoom'))
    PDF.plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
               RooFit.LineColor(kBlue))
    acceptancePdf.plotOn(tframe1, RooFit.LineColor(kGreen))

    # draw and print
    canvas = TCanvas('canvas', 'canvas', 800, 600)
    # tframe1.SetAxisRange(0, 1E-3) # probably same as 2nd RooFit.Range()
    tframe1.Draw()
    canvas.Print('plots/canvas_%s.png' % identifier)


if __name__ == "__main__":
    main()
