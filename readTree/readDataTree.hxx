//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri Nov 18 20:13:14 2011 by ROOT version 5.30/03
// from TTree MyOffSelTree/MyOffSelTree
// found on file: FitTuple_BsDs1Pi_K_MU_BDTG_01_vavaStyle.root
//////////////////////////////////////////////////////////

#ifndef __READDATATREE_HXX
#define __READDATATREE_HXX

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

#include "readTree.hxx"

class readDataTree : public readTree {

public :

  readDataTree(TTree *tree=0);
  virtual ~readDataTree();
  virtual Int_t    GetEntry(Long64_t entry);
  virtual Long64_t LoadTree(Long64_t entry);
  virtual void     Init(TTree *tree);
  virtual void     Loop() {}
  virtual void     Loop(TH1D&) {}
  virtual void     Loop(TH2D&) {}
  virtual void     Loop(TNtuple &noangle) {}
  virtual void     Loop(TTree&) {}
  virtual void     Loop(TH1D &hBsM, TH2D &h2oangle);
  virtual Bool_t   Notify();
  virtual void     Show(Long64_t entry = -1);

private:

  TTree          *fChain;   //!pointer to the analyzed TTree or TChain
  Int_t           fCurrent; //!current Tree number in a TChain

  // Declaration of leaf types
  Int_t           nSig;
  Double_t        BDTGResponse[1];   //[nSig]
  Double_t        lab0_MM[1];   //[nSig]
  Double_t        lab0_MM_NoConstr[1];   //[nSig]
  Double_t        lab0_PT[1];   //[nSig]
  Double_t        lab0_TAU[1];   //[nSig]
  Double_t        lab0_P[1];   //[nSig]
  Double_t        lab1_isMuon[1];   //[nSig]
  Double_t        lab1_PIDK[1];   //[nSig]
  Double_t        lab1_PIDp[1];   //[nSig]
  Double_t        lab1_P[1];   //[nSig]
  Double_t        lab1_M[1];   //[nSig]
  Double_t        lab1_PX[1];   //[nSig]
  Double_t        lab1_PY[1];   //[nSig]
  Double_t        lab1_PZ[1];   //[nSig]
  Double_t        lab1_PT[1];   //[nSig]
  Double_t        lab1_MINIPCHI2[1];   //[nSig]
  Double_t        lab3_PIDK[1];   //[nSig]
  Double_t        lab3_PIDp[1];   //[nSig]
  Double_t        lab3_isMuon[1];   //[nSig]
  Double_t        lab4_PIDK[1];   //[nSig]
  Double_t        lab4_PIDp[1];   //[nSig]
  Double_t        lab4_isMuon[1];   //[nSig]
  Double_t        lab3_M[1];   //[nSig]
  Double_t        lab4_M[1];   //[nSig]
  Double_t        lab3_ID[1];   //[nSig]
  Double_t        lab4_ID[1];   //[nSig]
  Double_t        lab2_MM[1];   //[nSig]
  Double_t        lab2_FDCHI2_ORIVX[1];   //[nSig]
  Double_t        lab2_PX[1];   //[nSig]
  Double_t        lab2_PY[1];   //[nSig]
  Double_t        lab2_PZ[1];   //[nSig]
  Double_t        lab3_PX[1];   //[nSig]
  Double_t        lab3_PY[1];   //[nSig]
  Double_t        lab3_PZ[1];   //[nSig]
  Double_t        lab4_PX[1];   //[nSig]
  Double_t        lab4_PY[1];   //[nSig]
  Double_t        lab4_PZ[1];   //[nSig]
  Double_t        lab5_PX[1];   //[nSig]
  Double_t        lab5_PY[1];   //[nSig]
  Double_t        lab5_PZ[1];   //[nSig]
  Double_t        lab5_M[1];   //[nSig]
  Double_t        lab5_PIDK[1];   //[nSig]
  Double_t        lab5_PIDp[1];   //[nSig]
  Double_t        lab5_isMuon[1];   //[nSig]
  Double_t        lab5_ID[1];   //[nSig]
  Double_t        pPIDcut[1];   //[nSig]
  Double_t        eventNumber[1];   //[nSig]

  // List of branches
  TBranch        *b_nSig;   //!
  TBranch        *b_BDTGResponse;   //!
  TBranch        *b_lab0_MM;   //!
  TBranch        *b_lab0_MM_NoConstr;   //!
  TBranch        *b_lab0_PT;   //!
  TBranch        *b_lab0_TAU;   //!
  TBranch        *b_lab0_P;   //!
  TBranch        *b_lab1_isMuon;   //!
  TBranch        *b_lab1_PIDK;   //!
  TBranch        *b_lab1_PIDp;   //!
  TBranch        *b_lab1_P;   //!
  TBranch        *b_lab1_M;   //!
  TBranch        *b_lab1_PX;   //!
  TBranch        *b_lab1_PY;   //!
  TBranch        *b_lab1_PZ;   //!
  TBranch        *b_lab1_PT;   //!
  TBranch        *b_lab1_MINIPCHI2;   //!
  TBranch        *b_lab3_PIDK;   //!
  TBranch        *b_lab3_PIDp;   //!
  TBranch        *b_lab3_isMuon;   //!
  TBranch        *b_lab4_PIDK;   //!
  TBranch        *b_lab4_PIDp;   //!
  TBranch        *b_lab4_isMuon;   //!
  TBranch        *b_lab3_M;   //!
  TBranch        *b_lab4_M;   //!
  TBranch        *b_lab3_ID;   //!
  TBranch        *b_lab4_ID;   //!
  TBranch        *b_lab2_MM;   //!
  TBranch        *b_lab2_FDCHI2_ORIVX;   //!
  TBranch        *b_lab2_PX;   //!
  TBranch        *b_lab2_PY;   //!
  TBranch        *b_lab2_PZ;   //!
  TBranch        *b_lab3_PX;   //!
  TBranch        *b_lab3_PY;   //!
  TBranch        *b_lab3_PZ;   //!
  TBranch        *b_lab4_PX;   //!
  TBranch        *b_lab4_PY;   //!
  TBranch        *b_lab4_PZ;   //!
  TBranch        *b_lab5_PX;   //!
  TBranch        *b_lab5_PY;   //!
  TBranch        *b_lab5_PZ;   //!
  TBranch        *b_lab5_M;   //!
  TBranch        *b_lab5_PIDK;   //!
  TBranch        *b_lab5_PIDp;   //!
  TBranch        *b_lab5_isMuon;   //!
  TBranch        *b_lab5_ID;   //!
  TBranch        *b_pPIDcut;   //!
  TBranch        *b_eventNumber;   //!

};

#endif // __READDATATREE_HXX
