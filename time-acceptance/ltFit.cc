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
// #include <TCollection.h>

#include <RooGlobalFunc.h>
#include <RooPlot.h>
#include <RooWorkspace.h>
#include <RooFitResult.h>

#include <RooRealVar.h>
#include <RooRealConstant.h>
#include <RooExponential.h>
#include <RooDecay.h>
#include <RooGenericPdf.h>
#include <RooEffProd.h>
#include <RooFormulaVar.h>
#include <RooAddPdf.h>
#include <RooProdPdf.h>
#include <RooDataSet.h>

// #include "utils.hh"

using namespace RooFit;


void ltFit() //TTree *ftree)
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  // acceptance
  RooRealVar tau("tau", "lifetime in ns", 0.0001, 0.01);
  RooRealVar turnon("turnon", "turnon", 500, 5000);

  // trigger:
  // HLT2Topo4Body
  // HLT2Topo3Body
  // HLT2Topo2Body
  // HLT2TopoIncPhi
  std::string trigger("HLT2Topo4Body");
  RooRealVar HLT2Topo4Body(trigger.c_str(), trigger.c_str(), 0, 2);

  // dataset
  std::string cut(trigger+">0");
  RooDataSet dataset("dataset", "Dataset", RooArgSet(tau, HLT2Topo4Body),
		     Import(*ftree), Cut(cut.c_str()));

  // when using weights
  RooRealVar wt("wt", "wt", 0, 1e5);
  // weighted dataset
  RooDataSet wdataset("wdataset", "Weighted dataset", RooArgSet(tau, wt, HLT2Topo4Body),
		      WeightVar(wt), Import(*ftree), Cut(cut.c_str()));

  // Decay function: exp(-t*1e3/1.472)
  // RooExponential decay("decay", "Decay function for the B_{s}", tau, // (1)
  // 		       RooRealConstant::value(-1E3/1.472));
  RooExponential decayH("decayH", "Decay function for the B_{s,H}", tau,
			RooRealConstant::value(-1E3/1.536875));
  RooExponential decayL("decayL", "Decay function for the B_{s,L}", tau,
			RooRealConstant::value(-1E3/1.407125));
  RooAddPdf decay("decay", "Decay function for the B_{s}", RooArgList(decayH, decayL),
		  RooRealConstant::value(0.5)); // (2)
  // RooRealVar ratio("ratio", "ration", 0, 1);
  // RooAddPdf decay("decay", "Decay function for the B_{s}", RooArgList(decayH, decayL),
  // 		  RooArgList(ratio));

  // acceptance model: 1-1/(1+(at)³)
  // NB: acceptance is not a PDF by nature
  RooFormulaVar acceptance("acceptance", "1-1/(1+(@0*@1)**3)", RooArgList(turnon, tau)); // for fit
  RooGenericPdf acceptancePdf("acceptancePdf", "@0", RooArgList(acceptance)); // for plot

  RooEffProd Model("Model", "Acceptance model", decay, acceptance);
  Model.fitTo(dataset, Range(0.0001, 0.01)); // SumW2Error(kTRUE), Strategy(2),
  // RooFitResult *fitptr = Model.fitTo(dataset, Range(0.0001, 0.01), Save(true)); // SumW2Error(kTRUE), Strategy(2),

  RooPlot *tframe1 = tau.frame(Name("pfit"), Title("Lifetime acceptance with Monte Carlo"));
  dataset.plotOn(tframe1, MarkerStyle(kFullTriangleUp));
  Model  .plotOn(tframe1);

  RooPlot *tframe2 = tau.frame(Name("pmodel"), Title("a(t) = decay(t) #times acc(t)"));
  wdataset  .plotOn(tframe2, MarkerStyle(kFullTriangleUp)); // , RefreshNorm()
  decay     .plotOn(tframe2, LineColor(kRed));
  // decay     .plotOn(tframe2, LineColor(kRed-9), LineStyle(2), Components(decayL));
  // decay     .plotOn(tframe2, LineColor(kRed-1), LineStyle(2), Components(decayH));
  acceptancePdf.plotOn(tframe2, LineColor(kGreen));
  Model     .plotOn(tframe2, LineColor(kAzure));

  TCanvas *canvas = new TCanvas("canvas", "canvas", 960, 400);
  canvas ->Divide(2,1);
  canvas ->cd(1);
  tframe1->Draw();
  canvas ->cd(2);
  tframe2->Draw();

  std::string ofile(trigger+"_ltFit.pdf");
  canvas ->Print(ofile.c_str());
  canvas ->Print(".png");

  // for (unsigned int i = 0; i < 3; ++i) {
  //   TIter primitivesItr(canvas.cd(i)->GetListOfPrimitives());
  //   while (TObject *obj = primitivesItr()) {
  //     TClass *pclass = TClass::GetClass(obj->ClassName());
  //     std::cout << "Class: " << pclass->ClassName()
  // 	       << " Name: " << obj->GetName()
  // 	       << " Title: " << obj->GetTitle() << std::endl;
  //   }
  // }

  return;
}
