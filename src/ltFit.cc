#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>
#include <limits>

#include <TTree.h>
#include <TFile.h>
#include <TCanvas.h>
#include <TPad.h>
// #include <TSystem.h>
// #include <TCollection.h>

#include <RooGlobalFunc.h>
#include <RooPlot.h>

#include <RooRealVar.h>
#include <RooRealConstant.h>
#include <RooDecay.h>
#include <RooEffProd.h>
#include <RooGenericPdf.h>
#include <RooEffProd.h>
#include <RooFormulaVar.h>
#include <RooAddPdf.h>
#include <RooProdPdf.h>
#include <RooDataSet.h>

using namespace RooFit;


int main() //TTree *ftree)
{
  TFile rfile("smalltree.root", "read");
  TTree *ftree = (TTree*) rfile.Get("ftree");

  const double epsilon(std::numeric_limits<double>::epsilon());

  // observables
  RooRealVar time("time", "lifetime in ns", epsilon, 0.01); // not zero w/ background
  RooRealVar dt("dt", "Error in lifetime measurement (ns)", epsilon, 1E-4);
  dt.setBins(100);

  RooRealVar turnon("turnon", "turnon", 500, 5000);
  RooRealVar exponent("exponent", "exponent", 2, 4);

  // trigger:
  // HLT2Topo4BodyTOS
  // HLT2Topo3BodyTOS
  // HLT2Topo2BodyTOS
  // HLT2TopoIncPhiTOS
  std::string trigger("HLT2Topo3BodyTOS");
  RooRealVar triggerVar(trigger.c_str(), trigger.c_str(), 0, 2);

  // dataset
  std::string cut(trigger+">0");
  RooDataSet dataset("dataset", "Dataset", RooArgSet(time, dt, triggerVar),
		     Import(*ftree), Cut(cut.c_str()));

  // resolution model
  RooRealVar mean("mean", "Mean", 0);
  RooRealVar scale("scale", "Scale factor for lifetime per-event error", 1);
  RooGaussModel resmodel("resmodel", "Time resolution model", time,
			 mean, scale, dt);

  // decay model
  RooDecay decayH("decayH", "Decay function for the B_{s,H}", time,
		  RooRealConstant::value(1.536875/1E3), resmodel, RooDecay::SingleSided);
  RooDecay decayL("decayL", "Decay function for the B_{s,L}", time,
		  RooRealConstant::value(1.407125/1E3), resmodel, RooDecay::SingleSided);
  RooAddPdf decay("decay", "Decay function for the B_{s}", decayH, decayL,
		  RooRealConstant::value(0.5));

  // acceptance model: 1-1/(1+(at)³)
  // NB: acceptance is not a PDF by nature
  RooFormulaVar acceptance("acceptance", "1-1/(1+(@0*@1)**@2)",
			   RooArgList(turnon, time, exponent)); // for fit
  RooGenericPdf acceptancePdf("acceptancePdf", "@0", RooArgList(acceptance));

  RooEffProd Model("Model", "Acceptance model", decay, acceptance);
  Model.fitTo(dataset, Range(0.0001, 0.01)); // SumW2Error(kTRUE), Strategy(2),
  // RooFitResult *fitptr = Model.fitTo(dataset, Range(0.0001, 0.01), Save(true)); // SumW2Error(kTRUE), Strategy(2),

  RooPlot *tframe1 = time.frame(Name("pfit"), Title("Lifetime acceptance with Monte Carlo"));
  dataset.plotOn(tframe1, MarkerStyle(kFullTriangleUp));
  Model  .plotOn(tframe1, ProjWData(RooArgSet(dt), dataset, true)); // Binning(1E-6, 1E-4, 100),

  RooPlot *tframe2 = time.frame(Name("pmodel"), Title("a(t) = decay(t) #times acc(t)"));
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
