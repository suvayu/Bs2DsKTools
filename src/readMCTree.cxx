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

  // BDTG variables
  fChain->SetBranchAddress("lab0_MassFitConsD_nPV", &lab0_MassFitConsD_nPV, &b_lab0_MassFitConsD_nPV);
  fChain->SetBranchAddress("lab0_MassFitConsD_M", lab0_MassFitConsD_M, &b_lab0_MassFitConsD_M);
  fChain->SetBranchAddress("lab0_MassFitConsD_MERR", lab0_MassFitConsD_MERR, &b_lab0_MassFitConsD_MERR);
  fChain->SetBranchAddress("lab0_MassFitConsD_P", lab0_MassFitConsD_P, &b_lab0_MassFitConsD_P);
  fChain->SetBranchAddress("lab0_MassFitConsD_PERR", lab0_MassFitConsD_PERR, &b_lab0_MassFitConsD_PERR);
  fChain->SetBranchAddress("lab0_MassFitConsD_chi2_B", lab0_MassFitConsD_chi2_B, &b_lab0_MassFitConsD_chi2_B);
  fChain->SetBranchAddress("lab0_MassFitConsD_nDOF", lab0_MassFitConsD_nDOF, &b_lab0_MassFitConsD_nDOF);
  fChain->SetBranchAddress("lab0_MassFitConsD_nIter", lab0_MassFitConsD_nIter, &b_lab0_MassFitConsD_nIter);
  fChain->SetBranchAddress("lab0_MassFitConsD_status", lab0_MassFitConsD_status, &b_lab0_MassFitConsD_status);

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

  fChain->SetBranchAddress("lab0L0HadronDecision_Dec", &lab0L0HadronDecision_Dec, &b_lab0L0HadronDecision_Dec);
  fChain->SetBranchAddress("lab0L0HadronDecision_TIS", &lab0L0HadronDecision_TIS, &b_lab0L0HadronDecision_TIS);
  fChain->SetBranchAddress("lab0L0HadronDecision_TOS", &lab0L0HadronDecision_TOS, &b_lab0L0HadronDecision_TOS);

  // HLT1 trigger
  fChain->SetBranchAddress("lab0Hlt1Global_Dec", &lab0Hlt1Global_Dec, &b_lab0Hlt1Global_Dec);
  fChain->SetBranchAddress("lab0Hlt1Global_TIS", &lab0Hlt1Global_TIS, &b_lab0Hlt1Global_TIS);
  fChain->SetBranchAddress("lab0Hlt1Global_TOS", &lab0Hlt1Global_TOS, &b_lab0Hlt1Global_TOS);

  fChain->SetBranchAddress("lab0Hlt1TrackAllL0Decision_Dec", &lab0Hlt1TrackAllL0Decision_Dec, &b_lab0Hlt1TrackAllL0Decision_Dec);
  fChain->SetBranchAddress("lab0Hlt1TrackAllL0Decision_TIS", &lab0Hlt1TrackAllL0Decision_TIS, &b_lab0Hlt1TrackAllL0Decision_TIS);
  fChain->SetBranchAddress("lab0Hlt1TrackAllL0Decision_TOS", &lab0Hlt1TrackAllL0Decision_TOS, &b_lab0Hlt1TrackAllL0Decision_TOS);

  // HLT2 trigger
  fChain->SetBranchAddress("lab0Hlt2Global_Dec", &lab0Hlt2Global_Dec, &b_lab0Hlt2Global_Dec);
  fChain->SetBranchAddress("lab0Hlt2Global_TIS", &lab0Hlt2Global_TIS, &b_lab0Hlt2Global_TIS);
  fChain->SetBranchAddress("lab0Hlt2Global_TOS", &lab0Hlt2Global_TOS, &b_lab0Hlt2Global_TOS);

  fChain->SetBranchAddress("lab0Hlt2Topo2BodyBBDTDecision_Dec", &lab0Hlt2Topo2BodyBBDTDecision_Dec, &b_lab0Hlt2Topo2BodyBBDTDecision_Dec);
  fChain->SetBranchAddress("lab0Hlt2Topo2BodyBBDTDecision_TIS", &lab0Hlt2Topo2BodyBBDTDecision_TIS, &b_lab0Hlt2Topo2BodyBBDTDecision_TIS);
  fChain->SetBranchAddress("lab0Hlt2Topo2BodyBBDTDecision_TOS", &lab0Hlt2Topo2BodyBBDTDecision_TOS, &b_lab0Hlt2Topo2BodyBBDTDecision_TOS);
  fChain->SetBranchAddress("lab0Hlt2Topo3BodyBBDTDecision_Dec", &lab0Hlt2Topo3BodyBBDTDecision_Dec, &b_lab0Hlt2Topo3BodyBBDTDecision_Dec);
  fChain->SetBranchAddress("lab0Hlt2Topo3BodyBBDTDecision_TIS", &lab0Hlt2Topo3BodyBBDTDecision_TIS, &b_lab0Hlt2Topo3BodyBBDTDecision_TIS);
  fChain->SetBranchAddress("lab0Hlt2Topo3BodyBBDTDecision_TOS", &lab0Hlt2Topo3BodyBBDTDecision_TOS, &b_lab0Hlt2Topo3BodyBBDTDecision_TOS);
  fChain->SetBranchAddress("lab0Hlt2Topo4BodyBBDTDecision_Dec", &lab0Hlt2Topo4BodyBBDTDecision_Dec, &b_lab0Hlt2Topo4BodyBBDTDecision_Dec);
  fChain->SetBranchAddress("lab0Hlt2Topo4BodyBBDTDecision_TIS", &lab0Hlt2Topo4BodyBBDTDecision_TIS, &b_lab0Hlt2Topo4BodyBBDTDecision_TIS);
  fChain->SetBranchAddress("lab0Hlt2Topo4BodyBBDTDecision_TOS", &lab0Hlt2Topo4BodyBBDTDecision_TOS, &b_lab0Hlt2Topo4BodyBBDTDecision_TOS);
  fChain->SetBranchAddress("lab0Hlt2IncPhiDecision_Dec", &lab0Hlt2IncPhiDecision_Dec, &b_lab0Hlt2IncPhiDecision_Dec);;
  fChain->SetBranchAddress("lab0Hlt2IncPhiDecision_TIS", &lab0Hlt2IncPhiDecision_TIS, &b_lab0Hlt2IncPhiDecision_TIS);;
  fChain->SetBranchAddress("lab0Hlt2IncPhiDecision_TOS", &lab0Hlt2IncPhiDecision_TOS, &b_lab0Hlt2IncPhiDecision_TOS);;

  /**
   * Declaration of branches for the bachelor (h, lab1_*)
   *
   */

  // TODO: what is mini?
  fChain->SetBranchAddress("lab1_CosTheta", &lab1_CosTheta, &b_lab1_CosTheta);

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
  fChain->SetBranchAddress("lab1_ProbNNe", &lab1_ProbNNe, &b_lab1_ProbNNe);
  fChain->SetBranchAddress("lab1_ProbNNk", &lab1_ProbNNk, &b_lab1_ProbNNk);
  fChain->SetBranchAddress("lab1_ProbNNp", &lab1_ProbNNp, &b_lab1_ProbNNp);
  fChain->SetBranchAddress("lab1_ProbNNpi", &lab1_ProbNNpi, &b_lab1_ProbNNpi);
  fChain->SetBranchAddress("lab1_ProbNNmu", &lab1_ProbNNmu, &b_lab1_ProbNNmu);
  fChain->SetBranchAddress("lab1_ProbNNghost", &lab1_ProbNNghost, &b_lab1_ProbNNghost);
  fChain->SetBranchAddress("lab1_CaloEcalE", &lab1_CaloEcalE, &b_lab1_CaloEcalE);      /**< Calibrated EM energy? */
  fChain->SetBranchAddress("lab1_CaloHcalE", &lab1_CaloHcalE, &b_lab1_CaloHcalE);      /**< Calibrated Hadronic energy? */
  fChain->SetBranchAddress("lab1_hasMuon", &lab1_hasMuon, &b_lab1_hasMuon);
  fChain->SetBranchAddress("lab1_isMuon", &lab1_isMuon, &b_lab1_isMuon);
  fChain->SetBranchAddress("lab1_hasRich", &lab1_hasRich, &b_lab1_hasRich);
  fChain->SetBranchAddress("lab1_hasCalo", &lab1_hasCalo, &b_lab1_hasCalo);

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

  fChain->SetBranchAddress("lab2_CosTheta", &lab2_CosTheta, &b_lab2_CosTheta);

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

  /**
   * Declaration of branches for the K (lab3_*)
   *
   */

  // what is mini?
  fChain->SetBranchAddress("lab3_CosTheta", &lab3_CosTheta, &b_lab3_CosTheta);

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
  fChain->SetBranchAddress("lab3_ProbNNe", &lab3_ProbNNe, &b_lab3_ProbNNe);
  fChain->SetBranchAddress("lab3_ProbNNk", &lab3_ProbNNk, &b_lab3_ProbNNk);
  fChain->SetBranchAddress("lab3_ProbNNp", &lab3_ProbNNp, &b_lab3_ProbNNp);
  fChain->SetBranchAddress("lab3_ProbNNpi", &lab3_ProbNNpi, &b_lab3_ProbNNpi);
  fChain->SetBranchAddress("lab3_ProbNNmu", &lab3_ProbNNmu, &b_lab3_ProbNNmu);
  fChain->SetBranchAddress("lab3_ProbNNghost", &lab3_ProbNNghost, &b_lab3_ProbNNghost);
  fChain->SetBranchAddress("lab3_CaloEcalE", &lab3_CaloEcalE, &b_lab3_CaloEcalE);
  fChain->SetBranchAddress("lab3_CaloHcalE", &lab3_CaloHcalE, &b_lab3_CaloHcalE);
  fChain->SetBranchAddress("lab3_hasMuon", &lab3_hasMuon, &b_lab3_hasMuon);
  fChain->SetBranchAddress("lab3_isMuon", &lab3_isMuon, &b_lab3_isMuon);
  fChain->SetBranchAddress("lab3_hasRich", &lab3_hasRich, &b_lab3_hasRich);
  fChain->SetBranchAddress("lab3_hasCalo", &lab3_hasCalo, &b_lab3_hasCalo);

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

  fChain->SetBranchAddress("lab4_CosTheta", &lab4_CosTheta, &b_lab4_CosTheta);

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
  fChain->SetBranchAddress("lab4_ProbNNe", &lab4_ProbNNe, &b_lab4_ProbNNe);
  fChain->SetBranchAddress("lab4_ProbNNk", &lab4_ProbNNk, &b_lab4_ProbNNk);
  fChain->SetBranchAddress("lab4_ProbNNp", &lab4_ProbNNp, &b_lab4_ProbNNp);
  fChain->SetBranchAddress("lab4_ProbNNpi", &lab4_ProbNNpi, &b_lab4_ProbNNpi);
  fChain->SetBranchAddress("lab4_ProbNNmu", &lab4_ProbNNmu, &b_lab4_ProbNNmu);
  fChain->SetBranchAddress("lab4_ProbNNghost", &lab4_ProbNNghost, &b_lab4_ProbNNghost);
  fChain->SetBranchAddress("lab4_CaloEcalE", &lab4_CaloEcalE, &b_lab4_CaloEcalE);
  fChain->SetBranchAddress("lab4_CaloHcalE", &lab4_CaloHcalE, &b_lab4_CaloHcalE);
  fChain->SetBranchAddress("lab4_hasMuon", &lab4_hasMuon, &b_lab4_hasMuon);
  fChain->SetBranchAddress("lab4_isMuon", &lab4_isMuon, &b_lab4_isMuon);
  fChain->SetBranchAddress("lab4_hasRich", &lab4_hasRich, &b_lab4_hasRich);
  fChain->SetBranchAddress("lab4_hasCalo", &lab4_hasCalo, &b_lab4_hasCalo);

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

  fChain->SetBranchAddress("lab5_CosTheta", &lab5_CosTheta, &b_lab5_CosTheta);

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
  fChain->SetBranchAddress("lab5_ProbNNe", &lab5_ProbNNe, &b_lab5_ProbNNe);
  fChain->SetBranchAddress("lab5_ProbNNk", &lab5_ProbNNk, &b_lab5_ProbNNk);
  fChain->SetBranchAddress("lab5_ProbNNp", &lab5_ProbNNp, &b_lab5_ProbNNp);
  fChain->SetBranchAddress("lab5_ProbNNpi", &lab5_ProbNNpi, &b_lab5_ProbNNpi);
  fChain->SetBranchAddress("lab5_ProbNNmu", &lab5_ProbNNmu, &b_lab5_ProbNNmu);
  fChain->SetBranchAddress("lab5_ProbNNghost", &lab5_ProbNNghost, &b_lab5_ProbNNghost);
  fChain->SetBranchAddress("lab5_CaloEcalE", &lab5_CaloEcalE, &b_lab5_CaloEcalE);
  fChain->SetBranchAddress("lab5_CaloHcalE", &lab5_CaloHcalE, &b_lab5_CaloHcalE);
  fChain->SetBranchAddress("lab5_hasMuon", &lab5_hasMuon, &b_lab5_hasMuon);
  fChain->SetBranchAddress("lab5_isMuon", &lab5_isMuon, &b_lab5_isMuon);
  fChain->SetBranchAddress("lab5_hasRich", &lab5_hasRich, &b_lab5_hasRich);
  fChain->SetBranchAddress("lab5_hasCalo", &lab5_hasCalo, &b_lab5_hasCalo);

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
  fChain->SetBranchAddress("nPVs", &nPVs, &b_nPVs);
  fChain->SetBranchAddress("nTracks", &nTracks, &b_nTracks);
  fChain->SetBranchAddress("nLongTracks", &nLongTracks, &b_nLongTracks);
  fChain->SetBranchAddress("nDownstreamTracks", &nDownstreamTracks, &b_nDownstreamTracks);
  fChain->SetBranchAddress("nUpstreamTracks", &nUpstreamTracks, &b_nUpstreamTracks);
  fChain->SetBranchAddress("nVeloTracks", &nVeloTracks, &b_nVeloTracks);
  fChain->SetBranchAddress("nTTracks", &nTTracks, &b_nTTracks);
  fChain->SetBranchAddress("nBackTracks", &nBackTracks, &b_nBackTracks);
  fChain->SetBranchAddress("nRich1Hits", &nRich1Hits, &b_nRich1Hits);
  fChain->SetBranchAddress("nRich2Hits", &nRich2Hits, &b_nRich2Hits);
  fChain->SetBranchAddress("BDTGResponse_1", &BDTGResponse_1, &b_BDTGResponse_1);

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


void readMCTree::Loop() {}


void readMCTree::Loop(TTree &ftree)
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   Double_t Cosoangle(0.), BsM(0.0);
   // Double_t BsM(0.0), DsM(0.0);
   TLorentzVector BsP(0,0,0,0), DsP(0,0,0,0), hP(0,0,0,0),
     Pi3P(0,0,0,0), K4P(0,0,0,0), K5P(0,0,0,0);

   TVector3 boost(0,0,0);

   // use BsM instead of lab0_MM to emulate wrong mass hypothesis
   ftree.Branch("Bsmass"  , &BsM);
   ftree.Branch("cosangle", &Cosoangle);
   ftree.Branch("hPIDK"   , &lab1_PIDK);
   ftree.Branch("BsID"    , &lab0_TRUEID);
   ftree.Branch("hID"     , &lab1_TRUEID);

   Long64_t nbytes = 0, nb = 0;
   // for (Long64_t jentry=0; jentry<10000;jentry++) // for testing
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       if ( CommonSelection() == false ) continue;
       // if ( BDTGResponse[0] < 0.1 ) continue; // not in TTree!
       // if ( lab1_PIDK < 5 ) continue; // off so that you can apply later
       // if ( pPIDcut != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       Pi3P.SetXYZM( lab3_PX, lab3_PY, lab3_PZ, lab3_M);
       K4P .SetXYZM( lab4_PX, lab4_PY, lab4_PZ, lab4_M);
       K5P .SetXYZM( lab5_PX, lab5_PY, lab5_PZ, lab5_M);
       // K mass instead of lab1_M to emulate wrong mass hypothesis
       hP  .SetXYZM( lab1_PX, lab1_PY, lab1_PZ, 493.677);

       DsP = Pi3P + K4P + K5P;
       BsP = DsP + hP;

       // DsM = DsP.M();
       BsM = BsP.M();

       boost = BsP.BoostVector();
       hP .Boost(-boost(0), -boost(1), -boost(2));
       Cosoangle = TMath::Cos((hP.Angle(boost)));

       ftree.Fill();
     }

   cout << "readMCTree::Loop(TTree&): Read " << nbytes << " bytes." << std::endl;
}


void readMCTree::Loop(TNtuple &noangle)
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   Double_t Cosoangle(0.);
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
       if ( lab1_PIDK < 5 ) continue;
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
       Cosoangle = TMath::Cos((hP.Angle(boost)));

       // noangle.Fill(lab0_MM, TMath::Cos((hP.Angle(boost))), lab1_TRUEID);
       noangle.Fill(BsP.M(), Cosoangle, lab1_TRUEID); // correct
     }

   cout << "readMCTree::Loop(TNtuple&): Read " << nbytes << " bytes." << std::endl;
}


void readMCTree::Loop(TTree &, TEntryList &, bool) {}


bool readMCTree::CommonSelection()
{
  // selecting only "true" Bs2DsK and Bs2Dsπ events
  if (lab0_TRUEID*lab0_TRUEID == 531*531 and
      lab2_TRUEID*lab2_TRUEID == 431*431 and
      (lab1_TRUEID*lab1_TRUEID == 321*321 or
       lab1_TRUEID*lab1_TRUEID == 211*211) and
       (5000. < lab0_MM and lab0_MM < 5800.) and // Bs mass
       (1944. < lab2_MM and lab2_MM < 1990.) and // Ds mass
       (lab1_P < 100000.)) return true;
  else return false;
}
