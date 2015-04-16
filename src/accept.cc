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


int main()
{
  bool doSelect = true;
  for (unsigned i = 0; i < 2; ++i) {
    // remember to delete ftree and felist
    TTree *ftree = NULL;
    TEntryList *felist = NULL;

    bool DsK(i < 1);
    string fileaccess((doSelect) ? "recreate" : "read");
    string fname(DsK ? "data/smalltree-really-new-MC-pre-PID-DsK.root" :
		 "data/smalltree-really-new-MC-pre-PID-DsPi.root");
    TFile rfile(fname.c_str(), fileaccess.c_str());
    // TFile rfile("data/smalltree-new-MC-pico-stripping.root", fileaccess.c_str());

    // select
    if (doSelect) {
      string tuplename(DsK ? "../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsK_*BsHypo_BDTG.root/DecayTree" :
		       "../ntuples/MC/MC11a_AfterOfflineSel/MergedTree_Bs2DsPi_*BsHypo_BDTG.root/DecayTree");
      TChain * MCChain = initChain("DecayTree", tuplename);
      lifetime MCsample(MCChain);
      selAccTree(MCsample, ftree, felist, DsK); // remember to delete ftree and felist
    } else {
      ftree  = (TTree*)      rfile.Get("ftree");
      felist = (TEntryList*) rfile.Get("felist");
    }

    // ftree and felist can't be NULL pointers
    assert(ftree);
    assert(felist);

    std::cout << "Entries: " << ftree->GetEntries() << std::endl;

    if (doSelect) {
      rfile.cd();
      ftree ->Write();
      felist->Write();
    }

    // housekeeping
    delete ftree; delete felist;
  }
  return 0;
}


TChain* initChain(std::string name, std::string fileglob)
{
  TChain *chain = new TChain(name.c_str());
  chain->Add(fileglob.c_str());
  return chain;
}


int selAccTree(readTree &sample, TTree *& ftree, TEntryList *& felist, bool DsK)
{
  ftree  = new TTree("ftree", "Selected events for lifetime acceptance");
  felist = new TEntryList("felist", "Pre trigger"); // , "DecayTree", "../../ntuples/MC/Merged_Bs2Ds*.root"
  sample.Loop(*ftree, *felist, DsK);
  return felist->GetN();
}
