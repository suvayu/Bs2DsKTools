#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>

#include <TChain.h>
#include <TCanvas.h>
#include <TH1D.h>

#include "utils.hh"
#include "lifetime.hxx"
#include "accept.hh"


int accept(bool doSelect)
{
  // remember to delete ftree and felist
  TTree *ftree = NULL;
  TEntryList *felist = NULL;

  string fileaccess((doSelect) ? "recreate" : "read");
  TFile rfile("smalltree.root", fileaccess.c_str());

  // select
  if (doSelect) {
    TChain * MCChain = initChain("MCChain", "../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
    lifetime MCsample(MCChain);
    selAccTree(MCsample, ftree, felist); // remember to delete ftree and felist
  } else {
    ftree  = (TTree*)      rfile.Get("ftree");
    felist = (TEntryList*) rfile.Get("felist");
  }

  // ftree and felist can't be NULL pointers
  assert(ftree);
  assert(felist);

  std::cout << "Entries: " << ftree->GetEntries()
	    << ", " << felist->GetN() << std::endl;
  // plotHistos(ftree);
  plotHistos(felist);

  if (doSelect) {
    rfile.cd();
    ftree ->Write();
    felist->Write();
  }

  // housekeeping
  delete ftree; delete felist;
  return 0;
}


TChain* initChain(std::string name, std::string fileglob)
{
  TChain *chain = new TChain(name.c_str());
  chain->Add(fileglob.c_str());
  return chain;
}


void plotHistos(TEntryList* felist)
{
  Style::setStyle();

  TH1D *hlaccept = getLifetime(felist, true); // remember to delete
  TH1D *hltime   = getLifetime(felist);       // remember to delete

  hlaccept->SetLineColor(kAzure);
  hltime  ->SetLineColor(kAzure);
  hlaccept->SetXTitle("Bs lifetime in ps");
  hltime  ->SetXTitle("Bs lifetime in ps");

  TCanvas *canvas = new TCanvas("canvas", "", 1200, 450);
  canvas->Divide(2,1);
  canvas->cd(1);
  hlaccept->Draw("hist");
  canvas->cd(2);
  hltime->Draw("hist");
  canvas->Print(".png");

  // housekeeping
  // hlaccept->Print("all");
  // hltime  ->Print("all");
  delete hlaccept; delete hltime;
  return;
}


void plotHistos(TTree* ftree)
{
  Style::setStyle();

  TH1D *hlaccept = getLifetime(ftree, true); // remember to delete
  TH1D *hltime   = getLifetime(ftree);	     // remember to delete

  hlaccept->SetLineColor(kAzure);
  hltime  ->SetLineColor(kAzure);
  hlaccept->SetXTitle("Bs lifetime in ps");
  hltime  ->SetXTitle("Bs lifetime in ps");

  TCanvas *canvas = new TCanvas("canvas", "", 1200, 450);
  canvas->Divide(2,1);
  canvas->cd(1);
  hlaccept->Draw("hist");
  canvas->cd(2);
  hltime->Draw("hist");
  canvas->Print(".png");

  // housekeeping
  delete hlaccept; delete hltime;
  return;
}


int selAccTree(readTree &sample, TTree *& ftree, TEntryList *& felist)
{
  ftree  = new TTree("ftree", "Selected events for lifetime acceptance");
  felist = new TEntryList("felist", "Pre trigger"); // , "DecayTree", "../../ntuples/MC/Merged_Bs2Ds*.root"
  sample.Loop(*ftree, *felist);
  return felist->GetN();
}


TH1D* getLifetime(TTree* ftree, bool doAcc)
{
  TString name, title, select, trigger, weight;

  if (doAcc) {
    title = "B_{s} lifetime acceptance";
    name  = "hlaccept";
  }
  else {
    title = "B_{s} lifetime";
    name  = "hltime";
  }

  if (doAcc) weight  = "*exp(tau*1e3/1.472)";
  trigger = "(HLT2Topo4Body>0)";
  // trigger = "(1)";
  select  = trigger + weight;

  // binning for ps, tree has lifetimes in ns
  TH1D* hist = new TH1D(name.Data(), title.Data(), 100, 0, 10);
  ftree->Draw("tau*1e3>>" + name, select.Data());
  return hist;
}


TH1D* getLifetime(TEntryList* felist, bool doAcc)
{
  TString name, title, select, trigger, weight;
  TChain *chain = initChain("chain", "../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
  chain->SetEntryList(felist);

  if (doAcc) {
    title = "B_{s} lifetime acceptance";
    name  = "hlaccept";
  }
  else {
    title = "B_{s} lifetime";
    name  = "hltime";
  }

  if (doAcc) weight  = "*exp(lab0_TAU*1e3/1.472)";
  trigger = "(lab0Hlt2TopoOSTF4BodyDecision_TOS>0)";
  // trigger = "(HLT2Topo4Body>0)";
  // trigger = "(1)";
  select  = trigger + weight;

  // binning for ps, tree has lifetimes in ns
  TH1D* hist = new TH1D(name.Data(), title.Data(), 100, 0, 10);
  chain->Draw("lab0_TAU*1e3>>" + name, select.Data());
  return hist;
}
