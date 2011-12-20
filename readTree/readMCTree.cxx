/**
 * @file   readMCTree.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Sun Dec 11 01:27:13 2011
 * 
 * @brief  
 * 
 * 
 */

#include <iostream>

#include "readMCTree.hxx"
// #include "Event.h"

#include <Rtypes.h>
#include <TNtuple.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>

using namespace std;

readMCTree::readMCTree(TTree *tree)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("Merged_Bs2DsK.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../../ntuples/MC/Merged_Bs2DsK.root");
      }
      f->GetObject("DecayTree",tree);

   }
   Init(tree);
}


readMCTree::~readMCTree()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}


Int_t readMCTree::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}


Long64_t readMCTree::LoadTree(Long64_t entry)
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


void readMCTree::Init(TTree *tree)
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

  // TODO: what is mini?
  fChain->SetBranchAddress("lab0_MINIP", &lab0_MINIP, &b_lab0_MINIP);
  fChain->SetBranchAddress("lab0_MINIPCHI2", &lab0_MINIPCHI2, &b_lab0_MINIPCHI2);

  // TODO: not sure about this block
  fChain->SetBranchAddress("lab0_OWNPV_X", &lab0_OWNPV_X, &b_lab0_OWNPV_X);
  fChain->SetBranchAddress("lab0_OWNPV_Y", &lab0_OWNPV_Y, &b_lab0_OWNPV_Y);
  fChain->SetBranchAddress("lab0_OWNPV_Z", &lab0_OWNPV_Z, &b_lab0_OWNPV_Z);
  fChain->SetBranchAddress("lab0_OWNPV_XERR", &lab0_OWNPV_XERR, &b_lab0_OWNPV_XERR);
  fChain->SetBranchAddress("lab0_OWNPV_YERR", &lab0_OWNPV_YERR, &b_lab0_OWNPV_YERR);
  fChain->SetBranchAddress("lab0_OWNPV_ZERR", &lab0_OWNPV_ZERR, &b_lab0_OWNPV_ZERR);
  fChain->SetBranchAddress("lab0_OWNPV_CHI2", &lab0_OWNPV_CHI2, &b_lab0_OWNPV_CHI2);
  fChain->SetBranchAddress("lab0_OWNPV_NDOF", &lab0_OWNPV_NDOF, &b_lab0_OWNPV_NDOF);
  fChain->SetBranchAddress("lab0_OWNPV_COV_", lab0_OWNPV_COV_, &b_lab0_OWNPV_COV_);
  fChain->SetBranchAddress("lab0_IP_OWNPV", &lab0_IP_OWNPV, &b_lab0_IP_OWNPV);
  fChain->SetBranchAddress("lab0_IPCHI2_OWNPV", &lab0_IPCHI2_OWNPV, &b_lab0_IPCHI2_OWNPV);
  fChain->SetBranchAddress("lab0_FD_OWNPV", &lab0_FD_OWNPV, &b_lab0_FD_OWNPV);
  fChain->SetBranchAddress("lab0_FDCHI2_OWNPV", &lab0_FDCHI2_OWNPV, &b_lab0_FDCHI2_OWNPV);
  fChain->SetBranchAddress("lab0_DIRA_OWNPV", &lab0_DIRA_OWNPV, &b_lab0_DIRA_OWNPV);

  // TODO: not sure about this block
  fChain->SetBranchAddress("lab0_ENDVERTEX_X", &lab0_ENDVERTEX_X, &b_lab0_ENDVERTEX_X);
  fChain->SetBranchAddress("lab0_ENDVERTEX_Y", &lab0_ENDVERTEX_Y, &b_lab0_ENDVERTEX_Y);
  fChain->SetBranchAddress("lab0_ENDVERTEX_Z", &lab0_ENDVERTEX_Z, &b_lab0_ENDVERTEX_Z);
  fChain->SetBranchAddress("lab0_ENDVERTEX_XERR", &lab0_ENDVERTEX_XERR, &b_lab0_ENDVERTEX_XERR);
  fChain->SetBranchAddress("lab0_ENDVERTEX_YERR", &lab0_ENDVERTEX_YERR, &b_lab0_ENDVERTEX_YERR);
  fChain->SetBranchAddress("lab0_ENDVERTEX_ZERR", &lab0_ENDVERTEX_ZERR, &b_lab0_ENDVERTEX_ZERR);
  fChain->SetBranchAddress("lab0_ENDVERTEX_CHI2", &lab0_ENDVERTEX_CHI2, &b_lab0_ENDVERTEX_CHI2);
  fChain->SetBranchAddress("lab0_ENDVERTEX_NDOF", &lab0_ENDVERTEX_NDOF, &b_lab0_ENDVERTEX_NDOF);
  fChain->SetBranchAddress("lab0_ENDVERTEX_COV_", lab0_ENDVERTEX_COV_, &b_lab0_ENDVERTEX_COV_);

  // kinematic variables
  fChain->SetBranchAddress("lab0_P", &lab0_P, &b_lab0_P);
  fChain->SetBranchAddress("lab0_PT", &lab0_PT, &b_lab0_PT);
  fChain->SetBranchAddress("lab0_PE", &lab0_PE, &b_lab0_PE);
  fChain->SetBranchAddress("lab0_PX", &lab0_PX, &b_lab0_PX);
  fChain->SetBranchAddress("lab0_PY", &lab0_PY, &b_lab0_PY);
  fChain->SetBranchAddress("lab0_PZ", &lab0_PZ, &b_lab0_PZ);
  fChain->SetBranchAddress("lab0_MM", &lab0_MM, &b_lab0_MM);
  fChain->SetBranchAddress("lab0_MMERR", &lab0_MMERR, &b_lab0_MMERR);
  fChain->SetBranchAddress("lab0_M", &lab0_M, &b_lab0_M);
  fChain->SetBranchAddress("lab0_BKGCAT", &lab0_BKGCAT, &b_lab0_BKGCAT);

  // MC truth
  fChain->SetBranchAddress("lab0_TRUEID", &lab0_TRUEID, &b_lab0_TRUEID);
  fChain->SetBranchAddress("lab0_TRUEP_E", &lab0_TRUEP_E, &b_lab0_TRUEP_E);
  fChain->SetBranchAddress("lab0_TRUEP_X", &lab0_TRUEP_X, &b_lab0_TRUEP_X);
  fChain->SetBranchAddress("lab0_TRUEP_Y", &lab0_TRUEP_Y, &b_lab0_TRUEP_Y);
  fChain->SetBranchAddress("lab0_TRUEP_Z", &lab0_TRUEP_Z, &b_lab0_TRUEP_Z);
  fChain->SetBranchAddress("lab0_TRUEPT", &lab0_TRUEPT, &b_lab0_TRUEPT);
  fChain->SetBranchAddress("lab0_TRUEORIGINVERTEX_X", &lab0_TRUEORIGINVERTEX_X, &b_lab0_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab0_TRUEORIGINVERTEX_Y", &lab0_TRUEORIGINVERTEX_Y, &b_lab0_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab0_TRUEORIGINVERTEX_Z", &lab0_TRUEORIGINVERTEX_Z, &b_lab0_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab0_TRUEENDVERTEX_X", &lab0_TRUEENDVERTEX_X, &b_lab0_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab0_TRUEENDVERTEX_Y", &lab0_TRUEENDVERTEX_Y, &b_lab0_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab0_TRUEENDVERTEX_Z", &lab0_TRUEENDVERTEX_Z, &b_lab0_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab0_TRUEISSTABLE", &lab0_TRUEISSTABLE, &b_lab0_TRUEISSTABLE);
  fChain->SetBranchAddress("lab0_TRUETAU", &lab0_TRUETAU, &b_lab0_TRUETAU);

  // lifetime
  fChain->SetBranchAddress("lab0_OSCIL", &lab0_OSCIL, &b_lab0_OSCIL);
  fChain->SetBranchAddress("lab0_ID", &lab0_ID, &b_lab0_ID);
  fChain->SetBranchAddress("lab0_TAU", &lab0_TAU, &b_lab0_TAU);
  fChain->SetBranchAddress("lab0_TAUERR", &lab0_TAUERR, &b_lab0_TAUERR);
  fChain->SetBranchAddress("lab0_TAUCHI2", &lab0_TAUCHI2, &b_lab0_TAUCHI2);

  // L0 trigger
  fChain->SetBranchAddress("lab0L0Global_Dec", &lab0L0Global_Dec, &b_lab0L0Global_Dec);
  fChain->SetBranchAddress("lab0L0Global_TIS", &lab0L0Global_TIS, &b_lab0L0Global_TIS);
  fChain->SetBranchAddress("lab0L0Global_TOS", &lab0L0Global_TOS, &b_lab0L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab0Hlt1Global_Dec", &lab0Hlt1Global_Dec, &b_lab0Hlt1Global_Dec);
  fChain->SetBranchAddress("lab0Hlt1Global_TIS", &lab0Hlt1Global_TIS, &b_lab0Hlt1Global_TIS);
  fChain->SetBranchAddress("lab0Hlt1Global_TOS", &lab0Hlt1Global_TOS, &b_lab0Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab0Hlt2Global_Dec", &lab0Hlt2Global_Dec, &b_lab0Hlt2Global_Dec);
  fChain->SetBranchAddress("lab0Hlt2Global_TIS", &lab0Hlt2Global_TIS, &b_lab0Hlt2Global_TIS);
  fChain->SetBranchAddress("lab0Hlt2Global_TOS", &lab0Hlt2Global_TOS, &b_lab0Hlt2Global_TOS);

  /**
   * Declaration of branches for the bachelor (h, lab1_*)
   *
   */

  // TODO: what is mini?
  fChain->SetBranchAddress("lab1_MINIP", &lab1_MINIP, &b_lab1_MINIP);
  fChain->SetBranchAddress("lab1_MINIPCHI2", &lab1_MINIPCHI2, &b_lab1_MINIPCHI2);

  fChain->SetBranchAddress("lab1_OWNPV_X", &lab1_OWNPV_X, &b_lab1_OWNPV_X);
  fChain->SetBranchAddress("lab1_OWNPV_Y", &lab1_OWNPV_Y, &b_lab1_OWNPV_Y);
  fChain->SetBranchAddress("lab1_OWNPV_Z", &lab1_OWNPV_Z, &b_lab1_OWNPV_Z);
  fChain->SetBranchAddress("lab1_OWNPV_XERR", &lab1_OWNPV_XERR, &b_lab1_OWNPV_XERR);
  fChain->SetBranchAddress("lab1_OWNPV_YERR", &lab1_OWNPV_YERR, &b_lab1_OWNPV_YERR);
  fChain->SetBranchAddress("lab1_OWNPV_ZERR", &lab1_OWNPV_ZERR, &b_lab1_OWNPV_ZERR);
  fChain->SetBranchAddress("lab1_OWNPV_CHI2", &lab1_OWNPV_CHI2, &b_lab1_OWNPV_CHI2);
  fChain->SetBranchAddress("lab1_OWNPV_NDOF", &lab1_OWNPV_NDOF, &b_lab1_OWNPV_NDOF);
  fChain->SetBranchAddress("lab1_OWNPV_COV_", lab1_OWNPV_COV_, &b_lab1_OWNPV_COV_);
  fChain->SetBranchAddress("lab1_IP_OWNPV", &lab1_IP_OWNPV, &b_lab1_IP_OWNPV);
  fChain->SetBranchAddress("lab1_IPCHI2_OWNPV", &lab1_IPCHI2_OWNPV, &b_lab1_IPCHI2_OWNPV);

  // TODO: what is this?
  fChain->SetBranchAddress("lab1_ORIVX_X", &lab1_ORIVX_X, &b_lab1_ORIVX_X);
  fChain->SetBranchAddress("lab1_ORIVX_Y", &lab1_ORIVX_Y, &b_lab1_ORIVX_Y);
  fChain->SetBranchAddress("lab1_ORIVX_Z", &lab1_ORIVX_Z, &b_lab1_ORIVX_Z);
  fChain->SetBranchAddress("lab1_ORIVX_XERR", &lab1_ORIVX_XERR, &b_lab1_ORIVX_XERR);
  fChain->SetBranchAddress("lab1_ORIVX_YERR", &lab1_ORIVX_YERR, &b_lab1_ORIVX_YERR);
  fChain->SetBranchAddress("lab1_ORIVX_ZERR", &lab1_ORIVX_ZERR, &b_lab1_ORIVX_ZERR);
  fChain->SetBranchAddress("lab1_ORIVX_CHI2", &lab1_ORIVX_CHI2, &b_lab1_ORIVX_CHI2);
  fChain->SetBranchAddress("lab1_ORIVX_NDOF", &lab1_ORIVX_NDOF, &b_lab1_ORIVX_NDOF);
  fChain->SetBranchAddress("lab1_ORIVX_COV_", lab1_ORIVX_COV_, &b_lab1_ORIVX_COV_);

  // kinematic variables
  fChain->SetBranchAddress("lab1_P", &lab1_P, &b_lab1_P);
  fChain->SetBranchAddress("lab1_PT", &lab1_PT, &b_lab1_PT);
  fChain->SetBranchAddress("lab1_PE", &lab1_PE, &b_lab1_PE);
  fChain->SetBranchAddress("lab1_PX", &lab1_PX, &b_lab1_PX);
  fChain->SetBranchAddress("lab1_PY", &lab1_PY, &b_lab1_PY);
  fChain->SetBranchAddress("lab1_PZ", &lab1_PZ, &b_lab1_PZ);
  fChain->SetBranchAddress("lab1_M", &lab1_M, &b_lab1_M);

  // MC truth
  fChain->SetBranchAddress("lab1_TRUEID", &lab1_TRUEID, &b_lab1_TRUEID);
  fChain->SetBranchAddress("lab1_TRUEP_E", &lab1_TRUEP_E, &b_lab1_TRUEP_E);
  fChain->SetBranchAddress("lab1_TRUEP_X", &lab1_TRUEP_X, &b_lab1_TRUEP_X);
  fChain->SetBranchAddress("lab1_TRUEP_Y", &lab1_TRUEP_Y, &b_lab1_TRUEP_Y);
  fChain->SetBranchAddress("lab1_TRUEP_Z", &lab1_TRUEP_Z, &b_lab1_TRUEP_Z);
  fChain->SetBranchAddress("lab1_TRUEPT", &lab1_TRUEPT, &b_lab1_TRUEPT);
  fChain->SetBranchAddress("lab1_TRUEORIGINVERTEX_X", &lab1_TRUEORIGINVERTEX_X, &b_lab1_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab1_TRUEORIGINVERTEX_Y", &lab1_TRUEORIGINVERTEX_Y, &b_lab1_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab1_TRUEORIGINVERTEX_Z", &lab1_TRUEORIGINVERTEX_Z, &b_lab1_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab1_TRUEENDVERTEX_X", &lab1_TRUEENDVERTEX_X, &b_lab1_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab1_TRUEENDVERTEX_Y", &lab1_TRUEENDVERTEX_Y, &b_lab1_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab1_TRUEENDVERTEX_Z", &lab1_TRUEENDVERTEX_Z, &b_lab1_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab1_TRUEISSTABLE", &lab1_TRUEISSTABLE, &b_lab1_TRUEISSTABLE);
  fChain->SetBranchAddress("lab1_TRUETAU", &lab1_TRUETAU, &b_lab1_TRUETAU);

  // lifetime?
  fChain->SetBranchAddress("lab1_OSCIL", &lab1_OSCIL, &b_lab1_OSCIL);
  fChain->SetBranchAddress("lab1_ID", &lab1_ID, &b_lab1_ID);
  fChain->SetBranchAddress("lab1_PIDe", &lab1_PIDe, &b_lab1_PIDe);	// TODO: what are PIDx ?
  fChain->SetBranchAddress("lab1_PIDmu", &lab1_PIDmu, &b_lab1_PIDmu);
  fChain->SetBranchAddress("lab1_PIDK", &lab1_PIDK, &b_lab1_PIDK);
  fChain->SetBranchAddress("lab1_PIDp", &lab1_PIDp, &b_lab1_PIDp);
  fChain->SetBranchAddress("lab1_CaloEcalE", &lab1_CaloEcalE, &b_lab1_CaloEcalE);      /**< Calibrated EM energy? */
  fChain->SetBranchAddress("lab1_CaloHcalE", &lab1_CaloHcalE, &b_lab1_CaloHcalE);      /**< Calibrated Hadronic energy? */
  fChain->SetBranchAddress("lab1_hasMuon", &lab1_hasMuon, &b_lab1_hasMuon);
  fChain->SetBranchAddress("lab1_isMuon", &lab1_isMuon, &b_lab1_isMuon);
  fChain->SetBranchAddress("lab1_hasRich", &lab1_hasRich, &b_lab1_hasRich);
  fChain->SetBranchAddress("lab1_hasCalo", &lab1_hasCalo, &b_lab1_hasCalo);

  // L0 trigger
  fChain->SetBranchAddress("lab1L0Global_Dec", &lab1L0Global_Dec, &b_lab1L0Global_Dec);
  fChain->SetBranchAddress("lab1L0Global_TIS", &lab1L0Global_TIS, &b_lab1L0Global_TIS);
  fChain->SetBranchAddress("lab1L0Global_TOS", &lab1L0Global_TOS, &b_lab1L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab1Hlt1Global_Dec", &lab1Hlt1Global_Dec, &b_lab1Hlt1Global_Dec);
  fChain->SetBranchAddress("lab1Hlt1Global_TIS", &lab1Hlt1Global_TIS, &b_lab1Hlt1Global_TIS);
  fChain->SetBranchAddress("lab1Hlt1Global_TOS", &lab1Hlt1Global_TOS, &b_lab1Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab1Hlt2Global_Dec", &lab1Hlt2Global_Dec, &b_lab1Hlt2Global_Dec);
  fChain->SetBranchAddress("lab1Hlt2Global_TIS", &lab1Hlt2Global_TIS, &b_lab1Hlt2Global_TIS);
  fChain->SetBranchAddress("lab1Hlt2Global_TOS", &lab1Hlt2Global_TOS, &b_lab1Hlt2Global_TOS);

  // tracking
  fChain->SetBranchAddress("lab1_TRACK_Type", &lab1_TRACK_Type, &b_lab1_TRACK_Type);
  fChain->SetBranchAddress("lab1_TRACK_Key", &lab1_TRACK_Key, &b_lab1_TRACK_Key);
  fChain->SetBranchAddress("lab1_TRACK_CHI2NDOF", &lab1_TRACK_CHI2NDOF, &b_lab1_TRACK_CHI2NDOF);
  fChain->SetBranchAddress("lab1_TRACK_PCHI2", &lab1_TRACK_PCHI2, &b_lab1_TRACK_PCHI2);
  fChain->SetBranchAddress("lab1_TRACK_GhostProb", &lab1_TRACK_GhostProb, &b_lab1_TRACK_GhostProb);
  fChain->SetBranchAddress("lab1_TRACK_CloneDist", &lab1_TRACK_CloneDist, &b_lab1_TRACK_CloneDist);

  /**
   * Declaration of branches for the Ds (lab2_*)
   *
   */

  fChain->SetBranchAddress("lab2_MINIP", &lab2_MINIP, &b_lab2_MINIP);
  fChain->SetBranchAddress("lab2_MINIPCHI2", &lab2_MINIPCHI2, &b_lab2_MINIPCHI2);

  fChain->SetBranchAddress("lab2_OWNPV_X", &lab2_OWNPV_X, &b_lab2_OWNPV_X);
  fChain->SetBranchAddress("lab2_OWNPV_Y", &lab2_OWNPV_Y, &b_lab2_OWNPV_Y);
  fChain->SetBranchAddress("lab2_OWNPV_Z", &lab2_OWNPV_Z, &b_lab2_OWNPV_Z);
  fChain->SetBranchAddress("lab2_OWNPV_XERR", &lab2_OWNPV_XERR, &b_lab2_OWNPV_XERR);
  fChain->SetBranchAddress("lab2_OWNPV_YERR", &lab2_OWNPV_YERR, &b_lab2_OWNPV_YERR);
  fChain->SetBranchAddress("lab2_OWNPV_ZERR", &lab2_OWNPV_ZERR, &b_lab2_OWNPV_ZERR);
  fChain->SetBranchAddress("lab2_OWNPV_CHI2", &lab2_OWNPV_CHI2, &b_lab2_OWNPV_CHI2);
  fChain->SetBranchAddress("lab2_OWNPV_NDOF", &lab2_OWNPV_NDOF, &b_lab2_OWNPV_NDOF);
  fChain->SetBranchAddress("lab2_OWNPV_COV_", lab2_OWNPV_COV_, &b_lab2_OWNPV_COV_);
  fChain->SetBranchAddress("lab2_IP_OWNPV", &lab2_IP_OWNPV, &b_lab2_IP_OWNPV);
  fChain->SetBranchAddress("lab2_IPCHI2_OWNPV", &lab2_IPCHI2_OWNPV, &b_lab2_IPCHI2_OWNPV);
  fChain->SetBranchAddress("lab2_FD_OWNPV", &lab2_FD_OWNPV, &b_lab2_FD_OWNPV);
  fChain->SetBranchAddress("lab2_FDCHI2_OWNPV", &lab2_FDCHI2_OWNPV, &b_lab2_FDCHI2_OWNPV);
  fChain->SetBranchAddress("lab2_DIRA_OWNPV", &lab2_DIRA_OWNPV, &b_lab2_DIRA_OWNPV);

  fChain->SetBranchAddress("lab2_ORIVX_X", &lab2_ORIVX_X, &b_lab2_ORIVX_X);
  fChain->SetBranchAddress("lab2_ORIVX_Y", &lab2_ORIVX_Y, &b_lab2_ORIVX_Y);
  fChain->SetBranchAddress("lab2_ORIVX_Z", &lab2_ORIVX_Z, &b_lab2_ORIVX_Z);
  fChain->SetBranchAddress("lab2_ORIVX_XERR", &lab2_ORIVX_XERR, &b_lab2_ORIVX_XERR);
  fChain->SetBranchAddress("lab2_ORIVX_YERR", &lab2_ORIVX_YERR, &b_lab2_ORIVX_YERR);
  fChain->SetBranchAddress("lab2_ORIVX_ZERR", &lab2_ORIVX_ZERR, &b_lab2_ORIVX_ZERR);
  fChain->SetBranchAddress("lab2_ORIVX_CHI2", &lab2_ORIVX_CHI2, &b_lab2_ORIVX_CHI2);
  fChain->SetBranchAddress("lab2_ORIVX_NDOF", &lab2_ORIVX_NDOF, &b_lab2_ORIVX_NDOF);
  fChain->SetBranchAddress("lab2_ORIVX_COV_", lab2_ORIVX_COV_, &b_lab2_ORIVX_COV_);
  fChain->SetBranchAddress("lab2_FD_ORIVX", &lab2_FD_ORIVX, &b_lab2_FD_ORIVX);
  fChain->SetBranchAddress("lab2_FDCHI2_ORIVX", &lab2_FDCHI2_ORIVX, &b_lab2_FDCHI2_ORIVX);
  fChain->SetBranchAddress("lab2_DIRA_ORIVX", &lab2_DIRA_ORIVX, &b_lab2_DIRA_ORIVX);

  fChain->SetBranchAddress("lab2_ENDVERTEX_X", &lab2_ENDVERTEX_X, &b_lab2_ENDVERTEX_X);
  fChain->SetBranchAddress("lab2_ENDVERTEX_Y", &lab2_ENDVERTEX_Y, &b_lab2_ENDVERTEX_Y);
  fChain->SetBranchAddress("lab2_ENDVERTEX_Z", &lab2_ENDVERTEX_Z, &b_lab2_ENDVERTEX_Z);
  fChain->SetBranchAddress("lab2_ENDVERTEX_XERR", &lab2_ENDVERTEX_XERR, &b_lab2_ENDVERTEX_XERR);
  fChain->SetBranchAddress("lab2_ENDVERTEX_YERR", &lab2_ENDVERTEX_YERR, &b_lab2_ENDVERTEX_YERR);
  fChain->SetBranchAddress("lab2_ENDVERTEX_ZERR", &lab2_ENDVERTEX_ZERR, &b_lab2_ENDVERTEX_ZERR);
  fChain->SetBranchAddress("lab2_ENDVERTEX_CHI2", &lab2_ENDVERTEX_CHI2, &b_lab2_ENDVERTEX_CHI2);
  fChain->SetBranchAddress("lab2_ENDVERTEX_NDOF", &lab2_ENDVERTEX_NDOF, &b_lab2_ENDVERTEX_NDOF);
  fChain->SetBranchAddress("lab2_ENDVERTEX_COV_", lab2_ENDVERTEX_COV_, &b_lab2_ENDVERTEX_COV_);

  // kinematic variables
  fChain->SetBranchAddress("lab2_P", &lab2_P, &b_lab2_P);
  fChain->SetBranchAddress("lab2_PT", &lab2_PT, &b_lab2_PT);
  fChain->SetBranchAddress("lab2_PE", &lab2_PE, &b_lab2_PE);
  fChain->SetBranchAddress("lab2_PX", &lab2_PX, &b_lab2_PX);
  fChain->SetBranchAddress("lab2_PY", &lab2_PY, &b_lab2_PY);
  fChain->SetBranchAddress("lab2_PZ", &lab2_PZ, &b_lab2_PZ);
  fChain->SetBranchAddress("lab2_MM", &lab2_MM, &b_lab2_MM);
  fChain->SetBranchAddress("lab2_MMERR", &lab2_MMERR, &b_lab2_MMERR);
  fChain->SetBranchAddress("lab2_M", &lab2_M, &b_lab2_M);
  fChain->SetBranchAddress("lab2_BKGCAT", &lab2_BKGCAT, &b_lab2_BKGCAT);

  // MC truth
  fChain->SetBranchAddress("lab2_TRUEID", &lab2_TRUEID, &b_lab2_TRUEID);
  fChain->SetBranchAddress("lab2_TRUEP_E", &lab2_TRUEP_E, &b_lab2_TRUEP_E);
  fChain->SetBranchAddress("lab2_TRUEP_X", &lab2_TRUEP_X, &b_lab2_TRUEP_X);
  fChain->SetBranchAddress("lab2_TRUEP_Y", &lab2_TRUEP_Y, &b_lab2_TRUEP_Y);
  fChain->SetBranchAddress("lab2_TRUEP_Z", &lab2_TRUEP_Z, &b_lab2_TRUEP_Z);
  fChain->SetBranchAddress("lab2_TRUEPT", &lab2_TRUEPT, &b_lab2_TRUEPT);
  fChain->SetBranchAddress("lab2_TRUEORIGINVERTEX_X", &lab2_TRUEORIGINVERTEX_X, &b_lab2_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab2_TRUEORIGINVERTEX_Y", &lab2_TRUEORIGINVERTEX_Y, &b_lab2_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab2_TRUEORIGINVERTEX_Z", &lab2_TRUEORIGINVERTEX_Z, &b_lab2_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab2_TRUEENDVERTEX_X", &lab2_TRUEENDVERTEX_X, &b_lab2_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab2_TRUEENDVERTEX_Y", &lab2_TRUEENDVERTEX_Y, &b_lab2_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab2_TRUEENDVERTEX_Z", &lab2_TRUEENDVERTEX_Z, &b_lab2_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab2_TRUEISSTABLE", &lab2_TRUEISSTABLE, &b_lab2_TRUEISSTABLE);
  fChain->SetBranchAddress("lab2_TRUETAU", &lab2_TRUETAU, &b_lab2_TRUETAU);

  // lifetime
  fChain->SetBranchAddress("lab2_OSCIL", &lab2_OSCIL, &b_lab2_OSCIL);
  fChain->SetBranchAddress("lab2_ID", &lab2_ID, &b_lab2_ID);
  fChain->SetBranchAddress("lab2_TAU", &lab2_TAU, &b_lab2_TAU);
  fChain->SetBranchAddress("lab2_TAUERR", &lab2_TAUERR, &b_lab2_TAUERR);
  fChain->SetBranchAddress("lab2_TAUCHI2", &lab2_TAUCHI2, &b_lab2_TAUCHI2);

  // L0 trigger
  fChain->SetBranchAddress("lab2L0Global_Dec", &lab2L0Global_Dec, &b_lab2L0Global_Dec);
  fChain->SetBranchAddress("lab2L0Global_TIS", &lab2L0Global_TIS, &b_lab2L0Global_TIS);
  fChain->SetBranchAddress("lab2L0Global_TOS", &lab2L0Global_TOS, &b_lab2L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab2Hlt1Global_Dec", &lab2Hlt1Global_Dec, &b_lab2Hlt1Global_Dec);
  fChain->SetBranchAddress("lab2Hlt1Global_TIS", &lab2Hlt1Global_TIS, &b_lab2Hlt1Global_TIS);
  fChain->SetBranchAddress("lab2Hlt1Global_TOS", &lab2Hlt1Global_TOS, &b_lab2Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab2Hlt2Global_Dec", &lab2Hlt2Global_Dec, &b_lab2Hlt2Global_Dec);
  fChain->SetBranchAddress("lab2Hlt2Global_TIS", &lab2Hlt2Global_TIS, &b_lab2Hlt2Global_TIS);
  fChain->SetBranchAddress("lab2Hlt2Global_TOS", &lab2Hlt2Global_TOS, &b_lab2Hlt2Global_TOS);

  /**
   * Declaration of branches for the K (lab3_*)
   *
   */

  // what is mini?
  fChain->SetBranchAddress("lab3_MINIP", &lab3_MINIP, &b_lab3_MINIP);
  fChain->SetBranchAddress("lab3_MINIPCHI2", &lab3_MINIPCHI2, &b_lab3_MINIPCHI2);

  fChain->SetBranchAddress("lab3_OWNPV_X", &lab3_OWNPV_X, &b_lab3_OWNPV_X);
  fChain->SetBranchAddress("lab3_OWNPV_Y", &lab3_OWNPV_Y, &b_lab3_OWNPV_Y);
  fChain->SetBranchAddress("lab3_OWNPV_Z", &lab3_OWNPV_Z, &b_lab3_OWNPV_Z);
  fChain->SetBranchAddress("lab3_OWNPV_XERR", &lab3_OWNPV_XERR, &b_lab3_OWNPV_XERR);
  fChain->SetBranchAddress("lab3_OWNPV_YERR", &lab3_OWNPV_YERR, &b_lab3_OWNPV_YERR);
  fChain->SetBranchAddress("lab3_OWNPV_ZERR", &lab3_OWNPV_ZERR, &b_lab3_OWNPV_ZERR);
  fChain->SetBranchAddress("lab3_OWNPV_CHI2", &lab3_OWNPV_CHI2, &b_lab3_OWNPV_CHI2);
  fChain->SetBranchAddress("lab3_OWNPV_NDOF", &lab3_OWNPV_NDOF, &b_lab3_OWNPV_NDOF);
  fChain->SetBranchAddress("lab3_OWNPV_COV_", lab3_OWNPV_COV_, &b_lab3_OWNPV_COV_);
  fChain->SetBranchAddress("lab3_IP_OWNPV", &lab3_IP_OWNPV, &b_lab3_IP_OWNPV);
  fChain->SetBranchAddress("lab3_IPCHI2_OWNPV", &lab3_IPCHI2_OWNPV, &b_lab3_IPCHI2_OWNPV);

  fChain->SetBranchAddress("lab3_ORIVX_X", &lab3_ORIVX_X, &b_lab3_ORIVX_X);
  fChain->SetBranchAddress("lab3_ORIVX_Y", &lab3_ORIVX_Y, &b_lab3_ORIVX_Y);
  fChain->SetBranchAddress("lab3_ORIVX_Z", &lab3_ORIVX_Z, &b_lab3_ORIVX_Z);
  fChain->SetBranchAddress("lab3_ORIVX_XERR", &lab3_ORIVX_XERR, &b_lab3_ORIVX_XERR);
  fChain->SetBranchAddress("lab3_ORIVX_YERR", &lab3_ORIVX_YERR, &b_lab3_ORIVX_YERR);
  fChain->SetBranchAddress("lab3_ORIVX_ZERR", &lab3_ORIVX_ZERR, &b_lab3_ORIVX_ZERR);
  fChain->SetBranchAddress("lab3_ORIVX_CHI2", &lab3_ORIVX_CHI2, &b_lab3_ORIVX_CHI2);
  fChain->SetBranchAddress("lab3_ORIVX_NDOF", &lab3_ORIVX_NDOF, &b_lab3_ORIVX_NDOF);
  fChain->SetBranchAddress("lab3_ORIVX_COV_", lab3_ORIVX_COV_, &b_lab3_ORIVX_COV_);

  // kinematic variables
  fChain->SetBranchAddress("lab3_P", &lab3_P, &b_lab3_P);
  fChain->SetBranchAddress("lab3_PT", &lab3_PT, &b_lab3_PT);
  fChain->SetBranchAddress("lab3_PE", &lab3_PE, &b_lab3_PE);
  fChain->SetBranchAddress("lab3_PX", &lab3_PX, &b_lab3_PX);
  fChain->SetBranchAddress("lab3_PY", &lab3_PY, &b_lab3_PY);
  fChain->SetBranchAddress("lab3_PZ", &lab3_PZ, &b_lab3_PZ);
  fChain->SetBranchAddress("lab3_M", &lab3_M, &b_lab3_M);

  // MC truth
  fChain->SetBranchAddress("lab3_TRUEID", &lab3_TRUEID, &b_lab3_TRUEID);
  fChain->SetBranchAddress("lab3_TRUEP_E", &lab3_TRUEP_E, &b_lab3_TRUEP_E);
  fChain->SetBranchAddress("lab3_TRUEP_X", &lab3_TRUEP_X, &b_lab3_TRUEP_X);
  fChain->SetBranchAddress("lab3_TRUEP_Y", &lab3_TRUEP_Y, &b_lab3_TRUEP_Y);
  fChain->SetBranchAddress("lab3_TRUEP_Z", &lab3_TRUEP_Z, &b_lab3_TRUEP_Z);
  fChain->SetBranchAddress("lab3_TRUEPT", &lab3_TRUEPT, &b_lab3_TRUEPT);
  fChain->SetBranchAddress("lab3_TRUEORIGINVERTEX_X", &lab3_TRUEORIGINVERTEX_X, &b_lab3_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab3_TRUEORIGINVERTEX_Y", &lab3_TRUEORIGINVERTEX_Y, &b_lab3_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab3_TRUEORIGINVERTEX_Z", &lab3_TRUEORIGINVERTEX_Z, &b_lab3_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab3_TRUEENDVERTEX_X", &lab3_TRUEENDVERTEX_X, &b_lab3_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab3_TRUEENDVERTEX_Y", &lab3_TRUEENDVERTEX_Y, &b_lab3_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab3_TRUEENDVERTEX_Z", &lab3_TRUEENDVERTEX_Z, &b_lab3_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab3_TRUEISSTABLE", &lab3_TRUEISSTABLE, &b_lab3_TRUEISSTABLE);
  fChain->SetBranchAddress("lab3_TRUETAU", &lab3_TRUETAU, &b_lab3_TRUETAU);

  fChain->SetBranchAddress("lab3_OSCIL", &lab3_OSCIL, &b_lab3_OSCIL);
  fChain->SetBranchAddress("lab3_ID", &lab3_ID, &b_lab3_ID);
  fChain->SetBranchAddress("lab3_PIDe", &lab3_PIDe, &b_lab3_PIDe);
  fChain->SetBranchAddress("lab3_PIDmu", &lab3_PIDmu, &b_lab3_PIDmu);
  fChain->SetBranchAddress("lab3_PIDK", &lab3_PIDK, &b_lab3_PIDK);
  fChain->SetBranchAddress("lab3_PIDp", &lab3_PIDp, &b_lab3_PIDp);
  fChain->SetBranchAddress("lab3_CaloEcalE", &lab3_CaloEcalE, &b_lab3_CaloEcalE);
  fChain->SetBranchAddress("lab3_CaloHcalE", &lab3_CaloHcalE, &b_lab3_CaloHcalE);
  fChain->SetBranchAddress("lab3_hasMuon", &lab3_hasMuon, &b_lab3_hasMuon);
  fChain->SetBranchAddress("lab3_isMuon", &lab3_isMuon, &b_lab3_isMuon);
  fChain->SetBranchAddress("lab3_hasRich", &lab3_hasRich, &b_lab3_hasRich);
  fChain->SetBranchAddress("lab3_hasCalo", &lab3_hasCalo, &b_lab3_hasCalo);

  // L0 trigger
  fChain->SetBranchAddress("lab3L0Global_Dec", &lab3L0Global_Dec, &b_lab3L0Global_Dec);
  fChain->SetBranchAddress("lab3L0Global_TIS", &lab3L0Global_TIS, &b_lab3L0Global_TIS);
  fChain->SetBranchAddress("lab3L0Global_TOS", &lab3L0Global_TOS, &b_lab3L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab3Hlt1Global_Dec", &lab3Hlt1Global_Dec, &b_lab3Hlt1Global_Dec);
  fChain->SetBranchAddress("lab3Hlt1Global_TIS", &lab3Hlt1Global_TIS, &b_lab3Hlt1Global_TIS);
  fChain->SetBranchAddress("lab3Hlt1Global_TOS", &lab3Hlt1Global_TOS, &b_lab3Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab3Hlt2Global_Dec", &lab3Hlt2Global_Dec, &b_lab3Hlt2Global_Dec);
  fChain->SetBranchAddress("lab3Hlt2Global_TIS", &lab3Hlt2Global_TIS, &b_lab3Hlt2Global_TIS);
  fChain->SetBranchAddress("lab3Hlt2Global_TOS", &lab3Hlt2Global_TOS, &b_lab3Hlt2Global_TOS);

  // tracking
  fChain->SetBranchAddress("lab3_TRACK_Type", &lab3_TRACK_Type, &b_lab3_TRACK_Type);
  fChain->SetBranchAddress("lab3_TRACK_Key", &lab3_TRACK_Key, &b_lab3_TRACK_Key);
  fChain->SetBranchAddress("lab3_TRACK_CHI2NDOF", &lab3_TRACK_CHI2NDOF, &b_lab3_TRACK_CHI2NDOF);
  fChain->SetBranchAddress("lab3_TRACK_PCHI2", &lab3_TRACK_PCHI2, &b_lab3_TRACK_PCHI2);
  fChain->SetBranchAddress("lab3_TRACK_GhostProb", &lab3_TRACK_GhostProb, &b_lab3_TRACK_GhostProb);
  fChain->SetBranchAddress("lab3_TRACK_CloneDist", &lab3_TRACK_CloneDist, &b_lab3_TRACK_CloneDist);

  /**
   * Declaration of branches for the K (lab4_*)
   *
   */

  fChain->SetBranchAddress("lab4_MINIP", &lab4_MINIP, &b_lab4_MINIP);
  fChain->SetBranchAddress("lab4_MINIPCHI2", &lab4_MINIPCHI2, &b_lab4_MINIPCHI2);

  fChain->SetBranchAddress("lab4_OWNPV_X", &lab4_OWNPV_X, &b_lab4_OWNPV_X);
  fChain->SetBranchAddress("lab4_OWNPV_Y", &lab4_OWNPV_Y, &b_lab4_OWNPV_Y);
  fChain->SetBranchAddress("lab4_OWNPV_Z", &lab4_OWNPV_Z, &b_lab4_OWNPV_Z);
  fChain->SetBranchAddress("lab4_OWNPV_XERR", &lab4_OWNPV_XERR, &b_lab4_OWNPV_XERR);
  fChain->SetBranchAddress("lab4_OWNPV_YERR", &lab4_OWNPV_YERR, &b_lab4_OWNPV_YERR);
  fChain->SetBranchAddress("lab4_OWNPV_ZERR", &lab4_OWNPV_ZERR, &b_lab4_OWNPV_ZERR);
  fChain->SetBranchAddress("lab4_OWNPV_CHI2", &lab4_OWNPV_CHI2, &b_lab4_OWNPV_CHI2);
  fChain->SetBranchAddress("lab4_OWNPV_NDOF", &lab4_OWNPV_NDOF, &b_lab4_OWNPV_NDOF);
  fChain->SetBranchAddress("lab4_OWNPV_COV_", lab4_OWNPV_COV_, &b_lab4_OWNPV_COV_);
  fChain->SetBranchAddress("lab4_IP_OWNPV", &lab4_IP_OWNPV, &b_lab4_IP_OWNPV);
  fChain->SetBranchAddress("lab4_IPCHI2_OWNPV", &lab4_IPCHI2_OWNPV, &b_lab4_IPCHI2_OWNPV);

  fChain->SetBranchAddress("lab4_ORIVX_X", &lab4_ORIVX_X, &b_lab4_ORIVX_X);
  fChain->SetBranchAddress("lab4_ORIVX_Y", &lab4_ORIVX_Y, &b_lab4_ORIVX_Y);
  fChain->SetBranchAddress("lab4_ORIVX_Z", &lab4_ORIVX_Z, &b_lab4_ORIVX_Z);
  fChain->SetBranchAddress("lab4_ORIVX_XERR", &lab4_ORIVX_XERR, &b_lab4_ORIVX_XERR);
  fChain->SetBranchAddress("lab4_ORIVX_YERR", &lab4_ORIVX_YERR, &b_lab4_ORIVX_YERR);
  fChain->SetBranchAddress("lab4_ORIVX_ZERR", &lab4_ORIVX_ZERR, &b_lab4_ORIVX_ZERR);
  fChain->SetBranchAddress("lab4_ORIVX_CHI2", &lab4_ORIVX_CHI2, &b_lab4_ORIVX_CHI2);
  fChain->SetBranchAddress("lab4_ORIVX_NDOF", &lab4_ORIVX_NDOF, &b_lab4_ORIVX_NDOF);
  fChain->SetBranchAddress("lab4_ORIVX_COV_", lab4_ORIVX_COV_, &b_lab4_ORIVX_COV_);

  fChain->SetBranchAddress("lab4_P", &lab4_P, &b_lab4_P);
  fChain->SetBranchAddress("lab4_PT", &lab4_PT, &b_lab4_PT);
  fChain->SetBranchAddress("lab4_PE", &lab4_PE, &b_lab4_PE);
  fChain->SetBranchAddress("lab4_PX", &lab4_PX, &b_lab4_PX);
  fChain->SetBranchAddress("lab4_PY", &lab4_PY, &b_lab4_PY);
  fChain->SetBranchAddress("lab4_PZ", &lab4_PZ, &b_lab4_PZ);
  fChain->SetBranchAddress("lab4_M", &lab4_M, &b_lab4_M);

  // MC truth
  fChain->SetBranchAddress("lab4_TRUEID", &lab4_TRUEID, &b_lab4_TRUEID);
  fChain->SetBranchAddress("lab4_TRUEP_E", &lab4_TRUEP_E, &b_lab4_TRUEP_E);
  fChain->SetBranchAddress("lab4_TRUEP_X", &lab4_TRUEP_X, &b_lab4_TRUEP_X);
  fChain->SetBranchAddress("lab4_TRUEP_Y", &lab4_TRUEP_Y, &b_lab4_TRUEP_Y);
  fChain->SetBranchAddress("lab4_TRUEP_Z", &lab4_TRUEP_Z, &b_lab4_TRUEP_Z);
  fChain->SetBranchAddress("lab4_TRUEPT", &lab4_TRUEPT, &b_lab4_TRUEPT);
  fChain->SetBranchAddress("lab4_TRUEORIGINVERTEX_X", &lab4_TRUEORIGINVERTEX_X, &b_lab4_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab4_TRUEORIGINVERTEX_Y", &lab4_TRUEORIGINVERTEX_Y, &b_lab4_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab4_TRUEORIGINVERTEX_Z", &lab4_TRUEORIGINVERTEX_Z, &b_lab4_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab4_TRUEENDVERTEX_X", &lab4_TRUEENDVERTEX_X, &b_lab4_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab4_TRUEENDVERTEX_Y", &lab4_TRUEENDVERTEX_Y, &b_lab4_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab4_TRUEENDVERTEX_Z", &lab4_TRUEENDVERTEX_Z, &b_lab4_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab4_TRUEISSTABLE", &lab4_TRUEISSTABLE, &b_lab4_TRUEISSTABLE);
  fChain->SetBranchAddress("lab4_TRUETAU", &lab4_TRUETAU, &b_lab4_TRUETAU);

  // lifetime?
  fChain->SetBranchAddress("lab4_OSCIL", &lab4_OSCIL, &b_lab4_OSCIL);
  fChain->SetBranchAddress("lab4_ID", &lab4_ID, &b_lab4_ID);
  fChain->SetBranchAddress("lab4_PIDe", &lab4_PIDe, &b_lab4_PIDe);
  fChain->SetBranchAddress("lab4_PIDmu", &lab4_PIDmu, &b_lab4_PIDmu);
  fChain->SetBranchAddress("lab4_PIDK", &lab4_PIDK, &b_lab4_PIDK);
  fChain->SetBranchAddress("lab4_PIDp", &lab4_PIDp, &b_lab4_PIDp);
  fChain->SetBranchAddress("lab4_CaloEcalE", &lab4_CaloEcalE, &b_lab4_CaloEcalE);
  fChain->SetBranchAddress("lab4_CaloHcalE", &lab4_CaloHcalE, &b_lab4_CaloHcalE);
  fChain->SetBranchAddress("lab4_hasMuon", &lab4_hasMuon, &b_lab4_hasMuon);
  fChain->SetBranchAddress("lab4_isMuon", &lab4_isMuon, &b_lab4_isMuon);
  fChain->SetBranchAddress("lab4_hasRich", &lab4_hasRich, &b_lab4_hasRich);
  fChain->SetBranchAddress("lab4_hasCalo", &lab4_hasCalo, &b_lab4_hasCalo);

  // L0 trigger
  fChain->SetBranchAddress("lab4L0Global_Dec", &lab4L0Global_Dec, &b_lab4L0Global_Dec);
  fChain->SetBranchAddress("lab4L0Global_TIS", &lab4L0Global_TIS, &b_lab4L0Global_TIS);
  fChain->SetBranchAddress("lab4L0Global_TOS", &lab4L0Global_TOS, &b_lab4L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab4Hlt1Global_Dec", &lab4Hlt1Global_Dec, &b_lab4Hlt1Global_Dec);
  fChain->SetBranchAddress("lab4Hlt1Global_TIS", &lab4Hlt1Global_TIS, &b_lab4Hlt1Global_TIS);
  fChain->SetBranchAddress("lab4Hlt1Global_TOS", &lab4Hlt1Global_TOS, &b_lab4Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab4Hlt2Global_Dec", &lab4Hlt2Global_Dec, &b_lab4Hlt2Global_Dec);
  fChain->SetBranchAddress("lab4Hlt2Global_TIS", &lab4Hlt2Global_TIS, &b_lab4Hlt2Global_TIS);
  fChain->SetBranchAddress("lab4Hlt2Global_TOS", &lab4Hlt2Global_TOS, &b_lab4Hlt2Global_TOS);

  // tracking
  fChain->SetBranchAddress("lab4_TRACK_Type", &lab4_TRACK_Type, &b_lab4_TRACK_Type);
  fChain->SetBranchAddress("lab4_TRACK_Key", &lab4_TRACK_Key, &b_lab4_TRACK_Key);
  fChain->SetBranchAddress("lab4_TRACK_CHI2NDOF", &lab4_TRACK_CHI2NDOF, &b_lab4_TRACK_CHI2NDOF);
  fChain->SetBranchAddress("lab4_TRACK_PCHI2", &lab4_TRACK_PCHI2, &b_lab4_TRACK_PCHI2);
  fChain->SetBranchAddress("lab4_TRACK_GhostProb", &lab4_TRACK_GhostProb, &b_lab4_TRACK_GhostProb);
  fChain->SetBranchAddress("lab4_TRACK_CloneDist", &lab4_TRACK_CloneDist, &b_lab4_TRACK_CloneDist);

  /**
   * Declaration of branches for the pi (lab5_*)
   *
   */

  fChain->SetBranchAddress("lab5_MINIP", &lab5_MINIP, &b_lab5_MINIP);
  fChain->SetBranchAddress("lab5_MINIPCHI2", &lab5_MINIPCHI2, &b_lab5_MINIPCHI2);

  fChain->SetBranchAddress("lab5_OWNPV_X", &lab5_OWNPV_X, &b_lab5_OWNPV_X);
  fChain->SetBranchAddress("lab5_OWNPV_Y", &lab5_OWNPV_Y, &b_lab5_OWNPV_Y);
  fChain->SetBranchAddress("lab5_OWNPV_Z", &lab5_OWNPV_Z, &b_lab5_OWNPV_Z);
  fChain->SetBranchAddress("lab5_OWNPV_XERR", &lab5_OWNPV_XERR, &b_lab5_OWNPV_XERR);
  fChain->SetBranchAddress("lab5_OWNPV_YERR", &lab5_OWNPV_YERR, &b_lab5_OWNPV_YERR);
  fChain->SetBranchAddress("lab5_OWNPV_ZERR", &lab5_OWNPV_ZERR, &b_lab5_OWNPV_ZERR);
  fChain->SetBranchAddress("lab5_OWNPV_CHI2", &lab5_OWNPV_CHI2, &b_lab5_OWNPV_CHI2);
  fChain->SetBranchAddress("lab5_OWNPV_NDOF", &lab5_OWNPV_NDOF, &b_lab5_OWNPV_NDOF);
  fChain->SetBranchAddress("lab5_OWNPV_COV_", lab5_OWNPV_COV_, &b_lab5_OWNPV_COV_);
  fChain->SetBranchAddress("lab5_IP_OWNPV", &lab5_IP_OWNPV, &b_lab5_IP_OWNPV);
  fChain->SetBranchAddress("lab5_IPCHI2_OWNPV", &lab5_IPCHI2_OWNPV, &b_lab5_IPCHI2_OWNPV);

  fChain->SetBranchAddress("lab5_ORIVX_X", &lab5_ORIVX_X, &b_lab5_ORIVX_X);
  fChain->SetBranchAddress("lab5_ORIVX_Y", &lab5_ORIVX_Y, &b_lab5_ORIVX_Y);
  fChain->SetBranchAddress("lab5_ORIVX_Z", &lab5_ORIVX_Z, &b_lab5_ORIVX_Z);
  fChain->SetBranchAddress("lab5_ORIVX_XERR", &lab5_ORIVX_XERR, &b_lab5_ORIVX_XERR);
  fChain->SetBranchAddress("lab5_ORIVX_YERR", &lab5_ORIVX_YERR, &b_lab5_ORIVX_YERR);
  fChain->SetBranchAddress("lab5_ORIVX_ZERR", &lab5_ORIVX_ZERR, &b_lab5_ORIVX_ZERR);
  fChain->SetBranchAddress("lab5_ORIVX_CHI2", &lab5_ORIVX_CHI2, &b_lab5_ORIVX_CHI2);
  fChain->SetBranchAddress("lab5_ORIVX_NDOF", &lab5_ORIVX_NDOF, &b_lab5_ORIVX_NDOF);
  fChain->SetBranchAddress("lab5_ORIVX_COV_", lab5_ORIVX_COV_, &b_lab5_ORIVX_COV_);

  fChain->SetBranchAddress("lab5_P", &lab5_P, &b_lab5_P);
  fChain->SetBranchAddress("lab5_PT", &lab5_PT, &b_lab5_PT);
  fChain->SetBranchAddress("lab5_PE", &lab5_PE, &b_lab5_PE);
  fChain->SetBranchAddress("lab5_PX", &lab5_PX, &b_lab5_PX);
  fChain->SetBranchAddress("lab5_PY", &lab5_PY, &b_lab5_PY);
  fChain->SetBranchAddress("lab5_PZ", &lab5_PZ, &b_lab5_PZ);
  fChain->SetBranchAddress("lab5_M", &lab5_M, &b_lab5_M);

  fChain->SetBranchAddress("lab5_TRUEID", &lab5_TRUEID, &b_lab5_TRUEID);
  fChain->SetBranchAddress("lab5_TRUEP_E", &lab5_TRUEP_E, &b_lab5_TRUEP_E);
  fChain->SetBranchAddress("lab5_TRUEP_X", &lab5_TRUEP_X, &b_lab5_TRUEP_X);
  fChain->SetBranchAddress("lab5_TRUEP_Y", &lab5_TRUEP_Y, &b_lab5_TRUEP_Y);
  fChain->SetBranchAddress("lab5_TRUEP_Z", &lab5_TRUEP_Z, &b_lab5_TRUEP_Z);
  fChain->SetBranchAddress("lab5_TRUEPT", &lab5_TRUEPT, &b_lab5_TRUEPT);
  fChain->SetBranchAddress("lab5_TRUEORIGINVERTEX_X", &lab5_TRUEORIGINVERTEX_X, &b_lab5_TRUEORIGINVERTEX_X);
  fChain->SetBranchAddress("lab5_TRUEORIGINVERTEX_Y", &lab5_TRUEORIGINVERTEX_Y, &b_lab5_TRUEORIGINVERTEX_Y);
  fChain->SetBranchAddress("lab5_TRUEORIGINVERTEX_Z", &lab5_TRUEORIGINVERTEX_Z, &b_lab5_TRUEORIGINVERTEX_Z);
  fChain->SetBranchAddress("lab5_TRUEENDVERTEX_X", &lab5_TRUEENDVERTEX_X, &b_lab5_TRUEENDVERTEX_X);
  fChain->SetBranchAddress("lab5_TRUEENDVERTEX_Y", &lab5_TRUEENDVERTEX_Y, &b_lab5_TRUEENDVERTEX_Y);
  fChain->SetBranchAddress("lab5_TRUEENDVERTEX_Z", &lab5_TRUEENDVERTEX_Z, &b_lab5_TRUEENDVERTEX_Z);
  fChain->SetBranchAddress("lab5_TRUEISSTABLE", &lab5_TRUEISSTABLE, &b_lab5_TRUEISSTABLE);
  fChain->SetBranchAddress("lab5_TRUETAU", &lab5_TRUETAU, &b_lab5_TRUETAU);

  fChain->SetBranchAddress("lab5_OSCIL", &lab5_OSCIL, &b_lab5_OSCIL);
  fChain->SetBranchAddress("lab5_ID", &lab5_ID, &b_lab5_ID);
  fChain->SetBranchAddress("lab5_PIDe", &lab5_PIDe, &b_lab5_PIDe);
  fChain->SetBranchAddress("lab5_PIDmu", &lab5_PIDmu, &b_lab5_PIDmu);
  fChain->SetBranchAddress("lab5_PIDK", &lab5_PIDK, &b_lab5_PIDK);
  fChain->SetBranchAddress("lab5_PIDp", &lab5_PIDp, &b_lab5_PIDp);
  fChain->SetBranchAddress("lab5_CaloEcalE", &lab5_CaloEcalE, &b_lab5_CaloEcalE);
  fChain->SetBranchAddress("lab5_CaloHcalE", &lab5_CaloHcalE, &b_lab5_CaloHcalE);
  fChain->SetBranchAddress("lab5_hasMuon", &lab5_hasMuon, &b_lab5_hasMuon);
  fChain->SetBranchAddress("lab5_isMuon", &lab5_isMuon, &b_lab5_isMuon);
  fChain->SetBranchAddress("lab5_hasRich", &lab5_hasRich, &b_lab5_hasRich);
  fChain->SetBranchAddress("lab5_hasCalo", &lab5_hasCalo, &b_lab5_hasCalo);

  // L0 trigger
  fChain->SetBranchAddress("lab5L0Global_Dec", &lab5L0Global_Dec, &b_lab5L0Global_Dec);
  fChain->SetBranchAddress("lab5L0Global_TIS", &lab5L0Global_TIS, &b_lab5L0Global_TIS);
  fChain->SetBranchAddress("lab5L0Global_TOS", &lab5L0Global_TOS, &b_lab5L0Global_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab5Hlt1Global_Dec", &lab5Hlt1Global_Dec, &b_lab5Hlt1Global_Dec);
  fChain->SetBranchAddress("lab5Hlt1Global_TIS", &lab5Hlt1Global_TIS, &b_lab5Hlt1Global_TIS);
  fChain->SetBranchAddress("lab5Hlt1Global_TOS", &lab5Hlt1Global_TOS, &b_lab5Hlt1Global_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab5Hlt2Global_Dec", &lab5Hlt2Global_Dec, &b_lab5Hlt2Global_Dec);
  fChain->SetBranchAddress("lab5Hlt2Global_TIS", &lab5Hlt2Global_TIS, &b_lab5Hlt2Global_TIS);
  fChain->SetBranchAddress("lab5Hlt2Global_TOS", &lab5Hlt2Global_TOS, &b_lab5Hlt2Global_TOS);

  // tracking
  fChain->SetBranchAddress("lab5_TRACK_Type", &lab5_TRACK_Type, &b_lab5_TRACK_Type);
  fChain->SetBranchAddress("lab5_TRACK_Key", &lab5_TRACK_Key, &b_lab5_TRACK_Key);
  fChain->SetBranchAddress("lab5_TRACK_CHI2NDOF", &lab5_TRACK_CHI2NDOF, &b_lab5_TRACK_CHI2NDOF);
  fChain->SetBranchAddress("lab5_TRACK_PCHI2", &lab5_TRACK_PCHI2, &b_lab5_TRACK_PCHI2);
  fChain->SetBranchAddress("lab5_TRACK_GhostProb", &lab5_TRACK_GhostProb, &b_lab5_TRACK_GhostProb);
  fChain->SetBranchAddress("lab5_TRACK_CloneDist", &lab5_TRACK_CloneDist, &b_lab5_TRACK_CloneDist);

  /**
   * Declaration of branches not related to particles
   *
   */

  // others
  fChain->SetBranchAddress("nCandidate", &nCandidate, &b_nCandidate);
  fChain->SetBranchAddress("totCandidates", &totCandidates, &b_totCandidates);
  fChain->SetBranchAddress("EventInSequence", &EventInSequence, &b_EventInSequence);
  fChain->SetBranchAddress("runNumber", &runNumber, &b_runNumber);
  fChain->SetBranchAddress("eventNumber", &eventNumber, &b_eventNumber);
  fChain->SetBranchAddress("BCID", &BCID, &b_BCID);
  fChain->SetBranchAddress("BCType", &BCType, &b_BCType);
  fChain->SetBranchAddress("OdinTCK", &OdinTCK, &b_OdinTCK);
  fChain->SetBranchAddress("L0DUTCK", &L0DUTCK, &b_L0DUTCK);
  fChain->SetBranchAddress("HLTTCK", &HLTTCK, &b_HLTTCK);
  fChain->SetBranchAddress("GpsTime", &GpsTime, &b_GpsTime);
  fChain->SetBranchAddress("Primaries", &Primaries, &b_Primaries);
  fChain->SetBranchAddress("nPV", &nPV, &b_nPV);
  fChain->SetBranchAddress("PVX", PVX, &b_PVX);   //[nPV]
  fChain->SetBranchAddress("PVY", PVY, &b_PVY);   //[nPV]
  fChain->SetBranchAddress("PVZ", PVZ, &b_PVZ);   //[nPV]
  fChain->SetBranchAddress("PVXERR", PVXERR, &b_PVXERR);   //[nPV]
  fChain->SetBranchAddress("PVYERR", PVYERR, &b_PVYERR);   //[nPV]
  fChain->SetBranchAddress("PVZERR", PVZERR, &b_PVZERR);   //[nPV]
  fChain->SetBranchAddress("PVCHI2", PVCHI2, &b_PVCHI2);   //[nPV]
  fChain->SetBranchAddress("PVNDOF", PVNDOF, &b_PVNDOF);   //[nPV]
  fChain->SetBranchAddress("PVNTRACKS", PVNTRACKS, &b_PVNTRACKS);   //[nPV]
  fChain->SetBranchAddress("ChargedProtos", &ChargedProtos, &b_ChargedProtos);
  fChain->SetBranchAddress("NeutralProtos", &NeutralProtos, &b_NeutralProtos);
  fChain->SetBranchAddress("BestTracks", &BestTracks, &b_BestTracks);
  fChain->SetBranchAddress("MuonTracks", &MuonTracks, &b_MuonTracks);
  fChain->SetBranchAddress("ITClusters", &ITClusters, &b_ITClusters);
  fChain->SetBranchAddress("VeloLiteClusters", &VeloLiteClusters, &b_VeloLiteClusters);
  fChain->SetBranchAddress("OTClusters", &OTClusters, &b_OTClusters);
  fChain->SetBranchAddress("spdMult", &spdMult, &b_spdMult);
  fChain->SetBranchAddress("backwardTracks", &backwardTracks, &b_backwardTracks);
  fChain->SetBranchAddress("veloTracks", &veloTracks, &b_veloTracks);

  // trigger
  fChain->SetBranchAddress("L0Global", &L0Global, &b_L0Global);
  fChain->SetBranchAddress("Hlt1Global", &Hlt1Global, &b_Hlt1Global);
  fChain->SetBranchAddress("Hlt2Global", &Hlt2Global, &b_Hlt2Global);
  fChain->SetBranchAddress("L0HadronDecision", &L0HadronDecision, &b_L0HadronDecision);
  fChain->SetBranchAddress("L0MuonDecision", &L0MuonDecision, &b_L0MuonDecision);
  fChain->SetBranchAddress("L0MuonHighDecision", &L0MuonHighDecision, &b_L0MuonHighDecision);
  fChain->SetBranchAddress("L0DiMuonDecision", &L0DiMuonDecision, &b_L0DiMuonDecision);
  fChain->SetBranchAddress("L0ElectronDecision", &L0ElectronDecision, &b_L0ElectronDecision);
  fChain->SetBranchAddress("L0PhotonDecision", &L0PhotonDecision, &b_L0PhotonDecision);
  fChain->SetBranchAddress("L0nSelections", &L0nSelections, &b_L0nSelections);

  Notify();
}


Bool_t readMCTree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


void readMCTree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}


void readMCTree::Loop(TNtuple &noangle)
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   // Double_t BsM(0.0), DsM(0.0);
   TLorentzVector BsP(0,0,0,0), DsP(0,0,0,0), hP(0,0,0,0),
     Pi3P(0,0,0,0), K4P(0,0,0,0), K5P(0,0,0,0);

   TVector3 boost(0,0,0);

   Long64_t nbytes = 0, nb = 0;
   // for (Long64_t jentry=0; jentry<10000;jentry++)
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       // Selection in python:
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

       if ( CommonSelection() == false ) continue;
       // if ( BDTGResponse[0] < 0.1 ) continue; // not in TTree!
       // if ( lab1_PIDK[0] < 5 ) continue;
       // if ( pPIDcut[0] != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       /**
	* This PID selection is the Lb veto
	* + not required since Bs2DsK & Bs2Dsπ MC
	* + moreover, s/lab5/lab1/ since only way to distinguish Lb
	*   from Bs is using the bachelor particle (p and K/π)
	* TODO: ask Rose
	*/
       // if (! lab5_PIDK - lab5_PIDp > 0) continue;

       /*
	 mass(K) = 493.677 MeV
	 mass(π) = 139.57  MeV
	*/

       Pi3P.SetXYZM( lab3_PX, lab3_PY, lab3_PZ, lab3_M);
       K4P .SetXYZM( lab4_PX, lab4_PY, lab4_PZ, lab4_M);
       K5P .SetXYZM( lab5_PX, lab5_PY, lab5_PZ, lab5_M);
       // K mass instead of lab1_M to emulate wrong mass hypothesis
       hP  .SetXYZM( lab1_PX, lab1_PY, lab1_PZ, 493.677);

       DsP = Pi3P + K4P + K5P;
       BsP = DsP + hP;

       // DsM = DsP.M();
       // BsM = BsP.M();

       boost = - BsP.BoostVector();
       hP .Boost(boost(0), boost(1), boost(2));

       // noangle.Fill(lab0_MM, TMath::Cos((hP.Angle(boost))), lab1_TRUEID);
       noangle.Fill(BsP.M(), TMath::Cos((hP.Angle(boost))), lab1_TRUEID); // correct
     }

   std::cout << "readMCTree::Loop(TNtuple&): Read " << nbytes << " bytes." << std::endl;
}


void readMCTree::Loop(vector<TNtuple*>& nlabvector, vector<TNtuple*>& ntrulabvector)
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   // Double_t BsM(0.0), DsM(0.0);
   TLorentzVector BsP(0,0,0,0), DsP(0,0,0,0), hP(0,0,0,0),
     Pi3P(0,0,0,0), K4P(0,0,0,0), K5P(0,0,0,0);

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       if ( CommonSelection() == false ) continue;
       // if ( BDTGResponse[0] < 0.1 ) continue; // not in TTree!
       if ( lab1_PIDK < 5 ) continue;
       // if ( pPIDcut[0] != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       /**
	* This PID selection is the Lb veto
	* + not required since Bs2DsK & Bs2Dsπ MC
	* + moreover, s/lab5/lab1/ since only way to distinguish Lb
	*   from Bs is using the bachelor particle (p and K/π)
	* TODO: ask Rose
	*/
       if (lab5_PIDK - lab5_PIDp < 0) continue;

       /*
	 mass(K) = 493.677 MeV
	 mass(π) = 139.57  MeV
	*/

       Pi3P.SetXYZM( lab3_PX, lab3_PY, lab3_PZ, lab3_M);
       K4P .SetXYZM( lab4_PX, lab4_PY, lab4_PZ, lab4_M);
       K5P .SetXYZM( lab5_PX, lab5_PY, lab5_PZ, lab5_M);
       // K mass instead of lab1_M to emulate wrong mass hypothesis
       hP  .SetXYZM( lab1_PX, lab1_PY, lab1_PZ, 493.677);

       DsP = Pi3P + K4P + K5P;
       BsP = DsP + hP;

       // DsM = DsP.M();
       // BsM = BsP.M();

       // Bs meson
       nlabvector[0]->Fill(lab0_OWNPV_X, lab0_OWNPV_Y, lab0_OWNPV_Z,
			   0, 0, 0, // no ORIVX for Bs
			   lab0_ENDVERTEX_X, lab0_ENDVERTEX_Y, lab0_ENDVERTEX_Z,
			   lab0_PX, lab0_PY, lab0_PZ, lab0_MM);

       // bachelor
       nlabvector[1]->Fill(lab1_OWNPV_X, lab1_OWNPV_Y, lab1_OWNPV_Z,
			   lab1_ORIVX_X, lab1_ORIVX_Y, lab1_ORIVX_Z,
			   -1, -1, -1, // doesn't decay
			   lab1_PX, lab1_PY, lab1_PZ, lab1_M);

       nlabvector[2]->Fill(lab2_OWNPV_X, lab2_OWNPV_Y, lab2_OWNPV_Z,
			   lab2_ORIVX_X, lab2_ORIVX_Y, lab2_ORIVX_Z,
			   lab2_ENDVERTEX_X, lab2_ENDVERTEX_Y, lab2_ENDVERTEX_Z,
			   lab2_PX, lab2_PY, lab2_PZ, lab2_MM);

       nlabvector[3]->Fill(lab3_OWNPV_X, lab3_OWNPV_Y, lab3_OWNPV_Z,
			   lab3_ORIVX_X, lab3_ORIVX_Y, lab3_ORIVX_Z,
			   -1, -1, -1,
			   lab3_PX, lab3_PY, lab3_PZ, lab3_M);

       nlabvector[4]->Fill(lab4_OWNPV_X, lab4_OWNPV_Y, lab4_OWNPV_Z,
			   lab4_ORIVX_X, lab4_ORIVX_Y, lab4_ORIVX_Z,
			   -1, -1, -1,
			   lab4_PX, lab4_PY, lab4_PZ, lab4_M);

       nlabvector[5]->Fill(lab5_OWNPV_X, lab5_OWNPV_Y, lab5_OWNPV_Z,
			   lab5_ORIVX_X, lab5_ORIVX_Y, lab5_ORIVX_Z,
			   -1, -1, -1,
			   lab5_PX, lab5_PY, lab5_PZ, lab5_M);

       // MC truth
       ntrulabvector[0]->Fill(lab0_TRUEID, lab0_TRUEP_E, lab0_TRUEP_X, lab0_TRUEP_Y, lab0_TRUEP_Z,
			      lab0_TRUEORIGINVERTEX_X, lab0_TRUEORIGINVERTEX_Y, lab0_TRUEORIGINVERTEX_Z, 
			      lab0_TRUEENDVERTEX_X, lab0_TRUEENDVERTEX_Y, lab0_TRUEENDVERTEX_Z, lab0_TRUETAU);

       ntrulabvector[1]->Fill(lab1_TRUEID, lab1_TRUEP_E, lab1_TRUEP_X, lab1_TRUEP_Y, lab1_TRUEP_Z,
			      lab1_TRUEORIGINVERTEX_X, lab1_TRUEORIGINVERTEX_Y, lab1_TRUEORIGINVERTEX_Z, 
			      lab1_TRUEENDVERTEX_X, lab1_TRUEENDVERTEX_Y, lab1_TRUEENDVERTEX_Z, lab1_TRUETAU);

       ntrulabvector[2]->Fill(lab2_TRUEID, lab2_TRUEP_E, lab2_TRUEP_X, lab2_TRUEP_Y, lab2_TRUEP_Z,
			      lab2_TRUEORIGINVERTEX_X, lab2_TRUEORIGINVERTEX_Y, lab2_TRUEORIGINVERTEX_Z, 
			      lab2_TRUEENDVERTEX_X, lab2_TRUEENDVERTEX_Y, lab2_TRUEENDVERTEX_Z, lab2_TRUETAU);

       ntrulabvector[3]->Fill(lab3_TRUEID, lab3_TRUEP_E, lab3_TRUEP_X, lab3_TRUEP_Y, lab3_TRUEP_Z,
			      lab3_TRUEORIGINVERTEX_X, lab3_TRUEORIGINVERTEX_Y, lab3_TRUEORIGINVERTEX_Z, 
			      lab3_TRUEENDVERTEX_X, lab3_TRUEENDVERTEX_Y, lab3_TRUEENDVERTEX_Z, lab3_TRUETAU);

       ntrulabvector[4]->Fill(lab4_TRUEID, lab4_TRUEP_E, lab4_TRUEP_X, lab4_TRUEP_Y, lab4_TRUEP_Z,
			      lab4_TRUEORIGINVERTEX_X, lab4_TRUEORIGINVERTEX_Y, lab4_TRUEORIGINVERTEX_Z, 
			      lab4_TRUEENDVERTEX_X, lab4_TRUEENDVERTEX_Y, lab4_TRUEENDVERTEX_Z, lab4_TRUETAU);

       ntrulabvector[5]->Fill(lab5_TRUEID, lab5_TRUEP_E, lab5_TRUEP_X, lab5_TRUEP_Y, lab5_TRUEP_Z,
			      lab5_TRUEORIGINVERTEX_X, lab5_TRUEORIGINVERTEX_Y, lab5_TRUEORIGINVERTEX_Z, 
			      lab5_TRUEENDVERTEX_X, lab5_TRUEENDVERTEX_Y, lab5_TRUEENDVERTEX_Z, lab5_TRUETAU);
     }

   std::cout << "readMCTree::Loop(vector<TNtuple*>&, vector<TNtuple*>&): Read " << nbytes << " bytes." << std::endl;
}


bool readMCTree::CommonSelection()
{
  // selecting only "true" Bs2DsK and Bs2Dsπ events
  if ( fabs(lab0_TRUEID) == 531 and fabs(lab2_TRUEID) == 431 and
       ( fabs(lab1_TRUEID) == 321 or fabs(lab1_TRUEID) == 211 ) and
       ( 5000 < lab0_MM and lab0_MM < 5800 ) and // Bs mass
       ( 1944 < lab2_MM and lab2_MM < 1990 ) and // Ds mass
       ( lab1_P < 100000 )) return true;
  else return false;
}
