#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>

#include <TTree.h>
#include <TFile.h>
#include <TPad.h>

#include <RooDataSet.h>
#include <RooGenericPdf.h>
#include <RooRealVar.h>
#include <RooGlobalFunc.h>
#include <RooPlot.h>
#include <RooWorkspace.h>
#include <RooFitResult.h>

#include "utils.hh"

using namespace RooFit;


void fitDataset() //TTree *ftree)
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  RooRealVar tau("tau", "tau", 0.0001, 0.008);
  RooRealVar turnon("turnon", "turnon", 1000, 10000);
  RooRealVar wt("wt", "wt", 0, 1e5);
  RooRealVar HLT2Topo4Body("HLT2Topo4Body", "HLT2Topo4Body", 0, 2);

  RooDataSet dataset("dataset", "dataset", RooArgSet(tau, wt, HLT2Topo4Body),
		     WeightVar(wt), Import(*ftree), Cut("HLT2Topo4Body>0"));
  // RooDataSet dataset("dataset", "dataset", ftree, RooArgSet(tau), "(HLT2Topo4Body>0)"); // alternate declaration

  RooGenericPdf acc("acc", "(@0*@1)**3/(1+(@0*@1)**3)", RooArgList(turnon, tau));
  acc.fitTo(dataset, SumW2Error(kTRUE));
  RooPlot *tframe = tau.frame();
  dataset.plotOn(tframe);
  acc.plotOn(tframe);
  tframe->Draw();

  gPad->Print(".png");
  return;
}
