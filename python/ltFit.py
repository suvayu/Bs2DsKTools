#!/usr/bin/env python
# coding=utf-8
"""
Fit it for lifetime acceptance in Monte Carlo.

Builds a PDF with a Gaussian time resolution model. Trigger acceptance
is modelled as an efficiency function.

If fullPDF is True, constructs the full 2-dimensional PDF with
per-event time errors instead.

  1-D  PDF = decay(t|δt) × trigAcc(t)
  Full PDF = decay(t|δt) × trigAcc(t) × gaussian(δt)

where,

  decay(t|δt) = ∫̣δt exp(-t/τ) × gaussian(δt).

If isToy is True, toys are generated and the model is fit to it, data
is read from an ntuple and fitted to the model otherwise.

@author Suvayu Ali

"""

# Python modules
import sys
# epsilon = sys.float_info.epsilon # python -> C++ doesn't like this
epsilon = 1E-6

# FIXME: Batch running fails on importing anything but gROOT
# ROOT global variables
from ROOT import gROOT
gROOT.SetBatch(True)

from ROOT import gStyle, gPad, gSystem

# ROOT colours and styles
from ROOT import kGreen, kRed, kBlack, kBlue, kAzure, kYellow
from ROOT import kFullTriangleUp

# ROOT classes
from ROOT import TTree, TFile, TCanvas, TPad, TClass

# RooFit classes
from ROOT import RooFit, RooGlobalFunc, RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel


def get_dataset(argset, isToy=True, PDF=False, time=False, dt=False):
    """Return a dataset.

    If isToy is True and PDF is a RooFit Probability Distribution
    inheriting from RooAbsPdf, generate and return a toy dataset. Read
    from an ntuple otherwise.

    """

    if isToy and PDF:
        objclass = TClass.GetClass(PDF.ClassName())
        if objclass.InheritsFrom(RooAbsPdf.Class()):
            dataset = PDF.generate(argset, 10000, RooFit.Name('toydataset'),
                                   RooFit.Verbose(True))
            dataset.Print('v')
            return dataset
        else:
            raise TypeError('Wrong type. PDF should inherit from RooAbsPdf.')
    elif time and dt:
        timeclass = TClass.GetClass(time.ClassName())
        dtclass = TClass.GetClass(dt.ClassName())

        istimeOK = timeclass.InheritsFrom(RooAbsReal.Class())
        isdtOK = dtclass.InheritsFrom(RooAbsReal.Class())
                                          
        if istimeOK and isdtOK:
            # Get tree
            ffile = TFile('data/smalltree.root', 'read')
            ftree = ffile.Get('ftree')
    
            # Trigger:
            # HLT2Topo4BodyTOS
            # HLT2Topo3BodyTOS
            # HLT2Topo2BodyTOS
            # HLT2TopoIncPhiTOS
            trigger = 'HLT2Topo3BodyTOS'
            triggerVar = RooRealVar(trigger, trigger, 0, 2)
    
            # Dataset
            cut = trigger+'>0'
            dataset = RooDataSet('dataset', 'Dataset',
                                 RooArgSet(time, dt, triggerVar),
                                 # RooArgSet(time, triggerVar),
                                 RooFit.Import(ftree), RooFit.Cut(cut))
    
            # dtdataset = gaussian.generate(dtargset,
            #                               RooFit.Name('dtdataset'),
            #                               RooFit.NumEvents(dataset.numEntries()))
            # dataset.merge(dtdataset)
    
            # # Debug
            # dataset.Print('v')
            # dtdataset.Print('v')
            return dataset
        else:
            raise TypeError('Wrong type. time and dt should be RooRealVar.')
    else:
        raise TypeError('Wrong type for one of the arguments.')


def main(fullPDF, isToy):
    """Setup RooFit variables then construct the PDF as per options.

    Fit the model to a dataset. If toy generation is requested,
    generate toys from the model and use as dataset, otherwise read
    dataset from ntuple in data/smalltree.root.

    """

    # Observables
    time = RooRealVar('time', 'B_{s} lifetime in ns', epsilon, 0.01)
    # Limits determined from tree
    dt = RooRealVar('dt', 'Error in lifetime measurement (ns)', epsilon, 1E-4)
    dt.setBins(100)

    # Parameters
    turnon = RooRealVar('turnon', 'turnon', 500, 5000)
    exponent = RooRealVar('exponent', 'exponent', 2, 4)

    # Temporary RooArgSet to circumvent scoping issues for nested
    # temporary objects.
    timeargset = RooArgSet(time)
    dtargset = RooArgSet(dt)

    # Resolution model
    mean = RooRealVar('mean', 'Mean', 0)
    scale = RooRealVar('scale', 'Per-event time error scale factor', 1)
    resmodel = RooGaussModel('resmodel', 'Time resolution model', time,
                                    mean, scale, dt)
                                    # RooRealConstant::value(0), scale, dt)
                                    # RooRealConstant::value(0), scale,
                                    # RooRealConstant::value(0.00004))

    # Decay model
    decayH = RooDecay('decayH', 'Decay function for the B_{s,H}',
                               time, RooRealConstant.value(1.536875/1E3),
                               resmodel, RooDecay.SingleSided)
    decayL = RooDecay('decayL', 'Decay function for the B_{s,L}',
                               time, RooRealConstant.value(1.407125/1E3),
                               resmodel, RooDecay.SingleSided)
    decay = RooAddPdf('decay', 'Decay function for the B_{s}',
                                decayH, decayL, RooRealConstant.value(0.5))

    # Acceptance model: 1-1/(1+(at)³)
    # NB: Acceptance is not a PDF by nature
    acceptance = RooFormulaVar('acceptance', '1-1/(1+(@0*@1)**@2)',
                                    RooArgList(turnon, time, exponent))
    acceptancePdf = RooGenericPdf('acceptancePdf', '@0', RooArgList(acceptance))

    # Define PDF and fit
    Model = RooEffProd('Model', 'Acceptance model', decay, acceptance)

    if fullPDF:
        # Assuming Gaussian time error
        gaussian = RooGaussian('gaussian', 'Gaussian', dt,
                                      RooRealConstant.value(4E-5),
                                      RooRealConstant.value(2E-5))
        modelargset = RooArgSet(Model)
        FullModel = RooProdPdf('FullModel', 'Acceptance model with errors',
                               RooArgSet(gaussian),
                               RooFit.Conditional(modelargset, timeargset))
        PDF = FullModel
    else:
        PDF = Model

    argset = RooArgSet(time,dt)
    try:
        dataset = get_dataset(argset, True, PDF)
    except TypeError:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

    # PDF.fitTo(dataset, RooFit.ConditionalObservables(dtargset),
    #           RooFit.NumCPU(4), RooFit.Optimize(True), RooFit.Verbose(True))
    PDF.fitTo(dataset, RooFit.NumCPU(4), RooFit.Optimize(True),
              RooFit.Verbose(True))
    PDF.Print('v')

    # # Weighted dataset
    # wt = RooRealVar('wt', 'wt', 0, 1e5)
    # wdataset = RooDataSet('wdataset', 'Weighted dataset',
    #                              RooArgSet(time, wt, triggerVar),
    #                              RooFit.WeightVar(wt), RooFit.Import(ftree),
    #                              RooFit.Cut(cut))

    tframe1 = time.frame(RooFit.Name('pfit'),
                         RooFit.Title('Lifetime acceptance with Monte Carlo'))
    dataset.plotOn(tframe1, RooFit.MarkerStyle(kFullTriangleUp))
    Model.plotOn(tframe1, RooFit.ProjWData(dtargset, dataset, True),
                 RooFit.LineColor(kBlue))

    # Testing
    decay.plotOn(tframe1, RooFit.LineColor(kRed))
    acceptancePdf.plotOn(tframe1, RooFit.LineColor(kGreen))

    canvas = TCanvas('canvas', 'canvas', 480, 400)
    tframe1.Draw()
    canvas.Print('plots/canvas.png')

    # tframe2 = time.frame(RooFit.Name('pmodel'),
    #                              RooFit.Title('a(t) = decay(t) #times acc(t)'))
    # wdataset.plotOn(tframe2, RooFit.MarkerStyle(kFullTriangleUp))
    # decay.plotOn(tframe2, RooFit.LineColor(kRed))
    # Model.plotOn(tframe2, RooFit.LineColor(kAzure))
    # acceptancePdf.plotOn(tframe2, RooFit.LineColor(kGreen))

    # canvas = TCanvas('canvas', 'canvas', 960, 400)
    # canvas.Divide(2,1)
    # canvas.cd(1)
    # tframe1.Draw()
    # canvas.cd(2)
    # tframe2.Draw()
    # canvas.Print('plots/'+trigger+'_ltFit_py.png')
    # canvas.Print('plots/'+trigger+'_ltFit_py.pdf')


if __name__ == "__main__":
    main(True, True)
