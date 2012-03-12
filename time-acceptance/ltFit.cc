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
#include <TLegend.h>

#include <TCollection.h>

#include <RooGlobalFunc.h>
#include <RooPlot.h>
#include <RooWorkspace.h>
#include <RooFitResult.h>

#include <RooRealVar.h>
#include <RooRealConstant.h>
#include <RooExponential.h>
#include <RooDecay.h>
#include <RooGenericPdf.h>
#include <RooAddPdf.h>
#include <RooProdPdf.h>
#include <RooDataSet.h>

#include "utils.hh"

using namespace RooFit;


// void fitDataset() //TTree *ftree)

void ltFit() //TTree *ftree)
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  // acceptance
  RooRealVar tau("tau", "lifetime in ns", 0.0001, 0.01);
  RooRealVar turnon("turnon", "turnon", 500, 5000);

  // trigger
  RooRealVar HLT2Topo4Body("HLT2Topo4Body", "HLT2Topo4Body", 0, 2);

  // dataset
  RooDataSet dataset("dataset", "Dataset", RooArgSet(tau, HLT2Topo4Body),
		     Import(*ftree), Cut("HLT2Topo4Body>0"));

  // Decay function: exp(-t*1e3/1.472)
  // RooGenericPdf exponent("exponent", "exp(-@0*1e3/1.472)", tau); // (1)
  // RooRealVar Gamma("Gamma", "B_{s} lifetime in ns", -1E3/1.472); // (2)
  // RooExponential exponent("exponent", "exponent", tau, Gamma);
  // or use RooRealConstant::value(-1.472/1E3) when needed
  RooExponential decay("decay", "Decay function for the B_{s}", tau, // (3)
  			RooRealConstant::value(-1E3/1.472));

  // acceptance model
  RooGenericPdf acceptance("acceptance", "(@0*@1)**3/(1+(@0*@1)**3)", RooArgList(turnon, tau));

  RooProdPdf Model("Model", "Acceptance model", decay, acceptance);
  Model.fitTo(dataset, Range(0.0001, 0.01)); // SumW2Error(kTRUE), Strategy(2),

  RooPlot *tframe1 = tau.frame(Name("pfit"), Title("Lifetime acceptance with Monte Carlo"));
  dataset.plotOn(tframe1, MarkerStyle(kFullTriangleUp));
  Model  .plotOn(tframe1);

  RooPlot *tframe2 = tau.frame(Name("pmodel"), Title("a(t) = exp(t/#Gamma_{s}) #times acc(t)"));
  Model     .plotOn(tframe2, LineColor(kAzure));
  decay     .plotOn(tframe2, LineColor(kRed));
  acceptance.plotOn(tframe2, LineColor(kGreen));

  TCanvas canvas("canvas", "canvas", 960, 400);
  canvas .Divide(2,1);
  canvas .cd(1);
  tframe1->Draw();
  canvas .cd(2);
  tframe2->Draw();

 // for (unsigned int i = 0; i < 3; ++i) {
 //   TIter primitivesItr(canvas.cd(i)->GetListOfPrimitives());
 //   while (TObject *obj = primitivesItr()) {
 //     TClass *pclass = TClass::GetClass(obj->ClassName());
 //     std::cout << "Class: " << pclass->ClassName()
 // 	       << " Name: " << obj->GetName()
 // 	       << " Title: " << obj->GetTitle() << std::endl;
 //   }
 // }

  canvas .Print(".png");
  return;
}


void wtltFit()
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  // acceptance
  RooRealVar tau("tau", "lifetime in ns", 0.0001, 0.01);
  RooRealVar turnon("turnon", "turnon", 500, 5000);

  // when using weights
  RooRealVar wt("wt", "wt", 0, 1e5);
  // trigger
  RooRealVar HLT2Topo4Body("HLT2Topo4Body", "HLT2Topo4Body", 0, 2);

  // weighted dataset
  RooDataSet dataset("dataset", "Weighted dataset", RooArgSet(tau, wt, HLT2Topo4Body),
		     WeightVar(wt), Import(*ftree), Cut("HLT2Topo4Body>0"));

  // acceptance model with weighted dataset
  RooGenericPdf accModel("accModel", "(@0*@1)**3/(1+(@0*@1)**3)", RooArgList(turnon, tau));
  // RooGenericPdf accModel("accModel", "1-1/(1+(@0*@1)**3)", RooArgList(turnon, tau));
  accModel.fitTo(dataset, SumW2Error(kTRUE), Strategy(2), Range(0.0001, 0.008));

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
