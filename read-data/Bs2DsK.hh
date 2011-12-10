//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri Nov 18 20:13:14 2011 by ROOT version 5.30/03
// from TTree MyOffSelTree/MyOffSelTree
// found on file: FitTuple_BsDs1Pi_K_MU_BDTG_01_vavaStyle.root
//////////////////////////////////////////////////////////

#ifndef Bs2DsK_hh
#define Bs2DsK_hh

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH2D.h>

class Bs2DsK {
public :
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

   Bs2DsK(TTree *tree=0);
   virtual ~Bs2DsK();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop(TH1D &hBsM, TH2D &h2oangle);
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef Bs2DsK_cc
Bs2DsK::Bs2DsK(TTree *tree)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("FitTuple_BsDs1Pi_K_MU_BDTG_01_vavaStyle.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../ntuples/data/FitTuple_BsDs1Pi_K_MU_BDTG_01_vavaStyle.root");
      }
      f->GetObject("MyOffSelTree",tree);

   }
   Init(tree);
}

Bs2DsK::~Bs2DsK()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t Bs2DsK::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t Bs2DsK::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void Bs2DsK::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("nSig", &nSig, &b_nSig);
   fChain->SetBranchAddress("BDTGResponse", BDTGResponse, &b_BDTGResponse);
   fChain->SetBranchAddress("lab0_MM", lab0_MM, &b_lab0_MM);
   fChain->SetBranchAddress("lab0_MM_NoConstr", lab0_MM_NoConstr, &b_lab0_MM_NoConstr);
   fChain->SetBranchAddress("lab0_PT", lab0_PT, &b_lab0_PT);
   fChain->SetBranchAddress("lab0_TAU", lab0_TAU, &b_lab0_TAU);
   fChain->SetBranchAddress("lab0_P", lab0_P, &b_lab0_P);
   fChain->SetBranchAddress("lab1_isMuon", lab1_isMuon, &b_lab1_isMuon);
   fChain->SetBranchAddress("lab1_PIDK", lab1_PIDK, &b_lab1_PIDK);
   fChain->SetBranchAddress("lab1_PIDp", lab1_PIDp, &b_lab1_PIDp);
   fChain->SetBranchAddress("lab1_P", lab1_P, &b_lab1_P);
   fChain->SetBranchAddress("lab1_M", lab1_M, &b_lab1_M);
   fChain->SetBranchAddress("lab1_PX", lab1_PX, &b_lab1_PX);
   fChain->SetBranchAddress("lab1_PY", lab1_PY, &b_lab1_PY);
   fChain->SetBranchAddress("lab1_PZ", lab1_PZ, &b_lab1_PZ);
   fChain->SetBranchAddress("lab1_PT", lab1_PT, &b_lab1_PT);
   fChain->SetBranchAddress("lab1_MINIPCHI2", lab1_MINIPCHI2, &b_lab1_MINIPCHI2);
   fChain->SetBranchAddress("lab3_PIDK", lab3_PIDK, &b_lab3_PIDK);
   fChain->SetBranchAddress("lab3_PIDp", lab3_PIDp, &b_lab3_PIDp);
   fChain->SetBranchAddress("lab3_isMuon", lab3_isMuon, &b_lab3_isMuon);
   fChain->SetBranchAddress("lab4_PIDK", lab4_PIDK, &b_lab4_PIDK);
   fChain->SetBranchAddress("lab4_PIDp", lab4_PIDp, &b_lab4_PIDp);
   fChain->SetBranchAddress("lab4_isMuon", lab4_isMuon, &b_lab4_isMuon);
   fChain->SetBranchAddress("lab3_M", lab3_M, &b_lab3_M);
   fChain->SetBranchAddress("lab4_M", lab4_M, &b_lab4_M);
   fChain->SetBranchAddress("lab3_ID", lab3_ID, &b_lab3_ID);
   fChain->SetBranchAddress("lab4_ID", lab4_ID, &b_lab4_ID);
   fChain->SetBranchAddress("lab2_MM", lab2_MM, &b_lab2_MM);
   fChain->SetBranchAddress("lab2_FDCHI2_ORIVX", lab2_FDCHI2_ORIVX, &b_lab2_FDCHI2_ORIVX);
   fChain->SetBranchAddress("lab2_PX", lab2_PX, &b_lab2_PX);
   fChain->SetBranchAddress("lab2_PY", lab2_PY, &b_lab2_PY);
   fChain->SetBranchAddress("lab2_PZ", lab2_PZ, &b_lab2_PZ);
   fChain->SetBranchAddress("lab3_PX", lab3_PX, &b_lab3_PX);
   fChain->SetBranchAddress("lab3_PY", lab3_PY, &b_lab3_PY);
   fChain->SetBranchAddress("lab3_PZ", lab3_PZ, &b_lab3_PZ);
   fChain->SetBranchAddress("lab4_PX", lab4_PX, &b_lab4_PX);
   fChain->SetBranchAddress("lab4_PY", lab4_PY, &b_lab4_PY);
   fChain->SetBranchAddress("lab4_PZ", lab4_PZ, &b_lab4_PZ);
   fChain->SetBranchAddress("lab5_PX", lab5_PX, &b_lab5_PX);
   fChain->SetBranchAddress("lab5_PY", lab5_PY, &b_lab5_PY);
   fChain->SetBranchAddress("lab5_PZ", lab5_PZ, &b_lab5_PZ);
   fChain->SetBranchAddress("lab5_M", lab5_M, &b_lab5_M);
   fChain->SetBranchAddress("lab5_PIDK", lab5_PIDK, &b_lab5_PIDK);
   fChain->SetBranchAddress("lab5_PIDp", lab5_PIDp, &b_lab5_PIDp);
   fChain->SetBranchAddress("lab5_isMuon", lab5_isMuon, &b_lab5_isMuon);
   fChain->SetBranchAddress("lab5_ID", lab5_ID, &b_lab5_ID);
   fChain->SetBranchAddress("pPIDcut", pPIDcut, &b_pPIDcut);
   fChain->SetBranchAddress("eventNumber", eventNumber, &b_eventNumber);
   Notify();
}

Bool_t Bs2DsK::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void Bs2DsK::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t Bs2DsK::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef Bs2DsK_cc
