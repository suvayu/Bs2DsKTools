#ifndef __READTREE_HXX
#define __READTREE_HXX

#include <TROOT.h>
#include <TChain.h>
#include <TNtuple.h>
#include <TH1D.h>
#include <TH2D.h>

class readTree {

public:

  // constructor & destructor
  readTree() {}
  readTree(TTree*) {}
  virtual ~readTree() {}

  // accessors
  // TODO: add const qualifer to methods
  virtual Int_t GetEntry(Long64_t) = 0;
  virtual void  Show(Long64_t) = 0;
  virtual void  Loop() = 0;
  virtual void  Loop(TNtuple&) = 0;
  virtual void  Loop(TTree&) = 0;
  virtual void  Loop(TTree &, TEntryList &, bool DsK=true) = 0;

};

#endif // __READTREE_HXX
