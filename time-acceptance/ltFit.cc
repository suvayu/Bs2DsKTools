#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>

#include <TTree.h>
#include <TFile.h>
#include <TCanvas.h>
#include <TPad.h>
// #include <TSystem.h>

#include <RooDataSet.h>
#include <RooGenericPdf.h>
#include <RooRealVar.h>
#include <RooGlobalFunc.h>
#include <RooPlot.h>
#include <RooWorkspace.h>
#include <RooFitResult.h>

#include "utils.hh"

using namespace RooFit;


// void fitDataset() //TTree *ftree)

void ltFit() //TTree *ftree)
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  RooRealVar tau("tau", "lifetime in ns", 0.0001, 0.01);
  RooRealVar turnon("turnon", "turnon", 500, 5000);
  RooRealVar wt("wt", "wt", 0, 1e5);
  RooRealVar HLT2Topo4Body("HLT2Topo4Body", "HLT2Topo4Body", 0, 2);

  RooDataSet dataset("dataset", "dataset", RooArgSet(tau, wt, HLT2Topo4Body),
		     WeightVar(wt), Import(*ftree), Cut("HLT2Topo4Body>0"));

  RooGenericPdf accModel("accModel", "(@0*@1)**3/(1+(@0*@1)**3)", RooArgList(turnon, tau));
  // RooGenericPdf accModel("accModel", "1-1/(1+(@0*@1)**3)", RooArgList(turnon, tau));
  accModel.fitTo(dataset, SumW2Error(kTRUE), Strategy(2), Range(3*0.0001, 0.004));

  RooPlot *tframe1 = tau.frame(Title("Lifetime acceptance with Monte Carlo"));
  dataset.plotOn(tframe1, MarkerStyle(kFullTriangleUp));
  accModel.plotOn(tframe1);

  RooPlot *tframe2 = tau.frame(Range(0.0001,0.002), Title("Lifetime acceptance with Monte Carlo"));
  dataset.plotOn(tframe2, MarkerStyle(kFullTriangleUp));
  accModel.plotOn(tframe2);

  TCanvas canvas("canvas", "canvas", 960, 400);
  canvas .Divide(2,1);
  canvas .cd(1);
  tframe1->Draw();
  canvas .cd(2);
  tframe2->Draw();

  canvas .Print(".png");
  return;
}
