#include <iostream>
#include <cassert>
#include <string>
#include <string>

#include <TChain.h>
#include <TCanvas.h>
#include <TPad.h>
#include <TH2D.h>

#include "lifetime.hxx"


TChain* init_chain(std::string name, std::string fileglob);

int sel_tree(readTree &sample, TTree *& ftree, TEntryList *& felist);

TH2D* get_time_residual_n_pull(TTree* ftree);


int main()
{
  bool doSelect = false;
  // remember to delete ftree and felist
  TTree *ftree = NULL;
  TEntryList *felist = NULL;

  TFile rfile("data/smalltree.root", "read");

  // select
  if (doSelect) {
    TChain * MCChain = init_chain("MCChain", "../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
    lifetime MCsample(MCChain);
    sel_tree(MCsample, ftree, felist); // remember to delete ftree and felist
  } else {
    ftree = dynamic_cast<TTree*> (rfile.Get("ftree"));
  }

  assert(ftree);
  std::cout << "Entries: " << ftree->GetEntries() << std::endl;

  TH2D *hist = get_time_residual_n_pull(ftree);
  hist->Draw("colz");
  gPad->Print(".png");

  // housekeeping
  if (doSelect) {
    delete felist; delete ftree;
  }
  return 0;
}


TH2D* get_time_residual_n_pull(TTree* ftree)
{
  std::string name, title, select;
  title = "B_{s} time residual and pull";
  name  = "htime";

  float truetime(0.0), time(0.0), time_err(0.0), residue(0.0), pull(0.0);

  ftree->SetBranchAddress("truetime", &truetime);
  ftree->SetBranchAddress("time", &time);
  ftree->SetBranchAddress("dt", &time_err);

  TH2D* hist = new TH2D(name.c_str(), title.c_str(), 100, -0.002, 0.002, 100, -5, 5);

  unsigned long nentries = ftree->GetEntries();
  for (unsigned int i = 0; i < nentries; ++i) {
    ftree->GetEntry(i);
    residue = time - truetime;
    pull = residue/time_err;

    hist->Fill(residue, pull);
  }

  return hist;
}


TChain* init_chain(std::string name, std::string fileglob)
{
  TChain *chain = new TChain(name.c_str());
  chain->Add(fileglob.c_str());
  return chain;
}


int sel_tree(readTree &sample, TTree *& ftree, TEntryList *& felist)
{
  ftree  = new TTree("ftree", "Selected events for lifetime acceptance");
  felist = new TEntryList("felist", "Pre trigger");
  sample.Loop(*ftree, *felist);
  return felist->GetN();
}
