#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>
#include <vector>

#include <TFile.h>
#include <TChain.h>
#include <TTree.h>
#include <TEntryList.h>
#include <TH1D.h>
#include <TString.h>

#include "lifetime.hxx"


TChain* initChain(std::string name, std::string fileglob);


/** 
 * Loop over ntuple and return selected events in a tree
 *
 * @param sample MC tree reader
 * @param ftree Tree with selected events
 * @param felist Selected entry list
 *
 * @return Total events selected
 */
int selAccTree(readTree &sample, TTree *& ftree, TEntryList *& felist, bool DsK);


int main()
{
  bool doSelect = true;
  for (unsigned i = 0; i < 2; ++i) {
    // remember to delete ftree and felist
    TTree *ftree = NULL;
    TEntryList *felist = NULL;

    string fileaccess((doSelect) ? "recreate" : "read");
    string fname((i < 1) ? "data/smalltree-new-MC-pico-offline-DsK.root" :
		 "data/smalltree-new-MC-pico-offline-DsPi.root");
    TFile rfile(fname.c_str(), fileaccess.c_str());
    // TFile rfile("data/smalltree-new-MC-pico-stripping.root", fileaccess.c_str());

    // select
    if (doSelect) {
      bool DsK(i < 1);
      string tuplename((i < 1) ? "../ntuples/MC/Dsh-MC11/Merged_Bs2DsK*BsHypo_BDTG.root/DecayTree" :
		       "../ntuples/MC/Dsh-MC11/Merged_Bs2DsPi*BsHypo_BDTG.root/DecayTree");
      TChain * MCChain = initChain("MCChain", tuplename.c_str());
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
