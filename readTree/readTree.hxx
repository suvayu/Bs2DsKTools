#ifndef __READTREE_HXX
#define __READTREE_HXX

#include <TROOT.h>
#include <TChain.h>
#include <TNtuple.h>
#include <TH1D.h>
#include <TH2D.h>

class readTree {

public:

  readTree() {}
  readTree(TTree*) {}
  virtual ~readTree() {}
  virtual Int_t GetEntry(Long64_t) const = 0;
  virtual void  Show(Long64_t) const = 0;
  virtual void  Loop() const = 0;
  virtual void  Loop(TH1D&) const = 0;
  virtual void  Loop(TH2D&) const = 0;
  virtual void  Loop(TNtuple&) const = 0;
  virtual void  Loop(TTree&) const = 0;

};

#endif // __READTREE_HXX
