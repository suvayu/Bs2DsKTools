#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>
#include <vector>

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
  // plotHistos(felist);
  // plotHistoPanel(felist);

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
  TString trigger("(lab0Hlt2TopoOSTF4BodyDecision_TOS>0)");

  TH1D *hlaccept = getLifetime(felist, trigger, true); // remember to delete
  TH1D *hltime   = getLifetime(felist, trigger);       // remember to delete

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
  hlaccept->Print("all");
  hltime  ->Print("all");
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


TH1D* getLifetime(TEntryList* felist, TString cuts, bool doAcc)
{
  TString name, title, select, weight;
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
  // cuts = "(lab0Hlt2TopoOSTF4BodyDecision_TOS>0)";
  // cuts = "(HLT2Topo4Body>0)";
  if (cuts == "") select = "(1)" + weight;
  else select = "(" + cuts + ")" + weight;

  TH1D* hist = new TH1D(name.Data(), title.Data(), 100, 0, 10);
  chain->Draw("lab0_TAU*1e3>>" + name, select.Data());
  return hist;
}


void getTriggers(std::vector<TString> &triggers)
{
  std::string fname("triggers.txt");
  Parsers::readlist(triggers, fname);

  for (unsigned int i = 0; i < triggers.size(); ++i) {
    std::cout << "Trigger " << i << ": " << triggers[i] << std::endl;
  }
  return;
}


void plotHistoPanel(TEntryList *felist)
{
  std::vector<TH1D*> histAcVec, histLTVec;
  std::vector<TString> triggers;
  getTriggers(triggers);

  unsigned int ntrigs(triggers.size());
  double width(1200), height(450*ntrigs);

  for (unsigned int i = 0; i < ntrigs; ++i) {
    histAcVec.push_back( getLifetime(felist, triggers[i]+">0", true) );
    histLTVec.push_back( getLifetime(felist, triggers[i]+">0") );

    TH1D *h1 = histAcVec.back();
    TH1D *h2 = histLTVec.back();
    h1->SetNameTitle("hla_"+triggers[i], "Acceptance for "+triggers[i]);
    h2->SetNameTitle("hlt_"+triggers[i], "Lifetime for "  +triggers[i]);
    h1->SetLineColor(kAzure);
    h2->SetLineColor(kRed);
    h1->SetXTitle("Bs lifetime in ps");
    h2->SetXTitle("Bs lifetime in ps");
  }

  assert(ntrigs = triggers.size() );
  assert(ntrigs = histAcVec.size());
  assert(ntrigs = histLTVec.size());

  TCanvas *canvas = new TCanvas("histpanel", "", width, height);
  canvas->Divide(2,ntrigs);
  for (unsigned int i = 0; i < ntrigs; ++i) {
    canvas->cd(i*2+1);
    histAcVec[i]->Draw("hist");
    canvas->cd(i*2+2);
    histLTVec[i]->Draw("hist");
  }
  canvas->Print(".png");

  histAcVec[0]->Print("all");
  histLTVec[0]->Print("all");

  // housekeeping
  for (unsigned int i = 0; i < ntrigs; ++i) {
    delete histAcVec[i]; delete histLTVec[i];
  }
  return;
}
