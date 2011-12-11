#include <cstdio>
#include <iostream>

#include "readDataTree.hxx"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TMath.h>


readDataTree::readDataTree(TTree *tree)
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


readDataTree::~readDataTree()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}


Int_t readDataTree::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}


Long64_t readDataTree::LoadTree(Long64_t entry)
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


void readDataTree::Init(TTree *tree)
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


Bool_t readDataTree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


void readDataTree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}


void readDataTree::Loop(TH1D &hBsM, TH2D &h2oangle)
{
//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch

   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   // Double_t BsM(0.0), DsM(0.0);
   TLorentzVector BsP(0,0,0,0), DsP(0,0,0,0), hP(0,0,0,0),
     Pi3P(0,0,0,0), K4P(0,0,0,0), K5P(0,0,0,0);

   TVector3 boost(0,0,0);

   // // for semantic
   // TLorentzVector BsP, DsP, hP, Pi3P, K4P, K5P;   

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       // PID_bach = 5.0
       // BMassRange =(5000,5800)
       // Ds_MM=(1944,1990)
       // BDTGCut = 0.1
       // condit = t.lab0_MM[0] >BMassRange[0] and
       // t.lab0_MM[0]<BMassRange[1] and
       // t.lab2_MM[0]>Ds_MM[0] and
       // t.lab2_MM[0]<Ds_MM[1]  and
       // t.lab1_P[0] < 100000 and
       // t.BDTGResponse[0]>BDTGCut and
       // t.pPIDcut[0] == 1

       if ( lab0_MM[0] < 5000 && 5800 < lab0_MM[0] ) continue; // Bs mass
       if ( lab2_MM[0] < 1944 && 1990 < lab2_MM[0] ) continue; // Ds mass
       if ( 100000 < lab1_P[0] ) continue;
       if ( BDTGResponse[0] < 0.1 ) continue;
       // if ( lab1_PIDK[0] < 5 ) continue;
       if ( pPIDcut[0] != 1) continue;

       Pi3P.SetXYZM( lab3_PX[0], lab3_PY[0], lab3_PZ[0], lab3_M[0]);
       K4P .SetXYZM( lab4_PX[0], lab4_PY[0], lab4_PZ[0], lab4_M[0]);
       K5P .SetXYZM( lab5_PX[0], lab5_PY[0], lab5_PZ[0], lab5_M[0]);
       hP  .SetXYZM( lab1_PX[0], lab1_PY[0], lab1_PZ[0], lab1_M[0]);

       DsP = Pi3P + K4P + K5P;
       BsP = DsP + hP;

       // DsM = DsP.M();
       // BsM = BsP.M();

       hBsM.Fill(lab0_MM[0]);

       boost = - BsP.BoostVector();
       //       DsP.Boost(boost(0), boost(1), boost(2));
       hP .Boost(boost(0), boost(1), boost(2));

       h2oangle.Fill( lab0_MM[0], TMath::Cos((hP.Angle(boost))));

       // printf("DsM: %.2f, %.2f, %.2f\n", DsM, lab2_MM[0], DsM - lab2_MM[0]);
       // printf("BsM: %.2f, %.2f, %.2f\n", BsM, lab0_MM[0], BsM - lab0_MM[0]);
     }

   // hBsM.Draw();
   // gPad->Print("BsMass.png");
   std::cout << "Read " << nbytes << " bytes." << std::endl;
}
