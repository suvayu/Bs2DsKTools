/**
 * @file   readMCTree.hxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Sun Dec 11 01:25:13 2011
 *
 * @brief
 *
 *
 */

#ifndef __READMCTREE_HXX
#define __READMCTREE_HXX

#include <vector>

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

#include "readTree.hxx"

using namespace std;


class readMCTree : public readTree {

public :

  // constructor & destructor
  readMCTree(TTree *tree=0);
  virtual ~readMCTree();

  // new methods
  Long64_t LoadTree(Long64_t entry);
  void     Init(TTree *tree);
  Bool_t   Notify();
  bool     CommonSelection();

  // overloaded virtual methods
  virtual Int_t GetEntry(Long64_t entry);
  virtual void  Show(Long64_t entry = -1);
  virtual void  Loop();
  virtual void  Loop(TNtuple &);
  virtual void  Loop(TTree &);
  virtual void  Loop(TTree &, TEntryList &, bool DsK=true);

protected:

  TTree          *fChain;   //!pointer to the analyzed TTree or TChain
  Int_t           fCurrent; //!current Tree number in a TChain

  /**
   * Declaration of leaf types for the Bs (lab0_*)
   *
   */

  // TODO: what is mini?
  Float_t         lab0_MINIP;
  Float_t         lab0_MINIPCHI2;

  // this is the PV with respect to which the given particle has the
  // smallest impact parameter.
  Float_t         lab0_OWNPV_X;
  Float_t         lab0_OWNPV_Y;
  Float_t         lab0_OWNPV_Z;
  Float_t         lab0_OWNPV_XERR;
  Float_t         lab0_OWNPV_YERR;
  Float_t         lab0_OWNPV_ZERR;
  Float_t         lab0_OWNPV_CHI2;
  Int_t           lab0_OWNPV_NDOF;
  Float_t         lab0_OWNPV_COV_[3][3];
  Float_t         lab0_IP_OWNPV;
  Float_t         lab0_IPCHI2_OWNPV;
  Float_t         lab0_FD_OWNPV;
  Float_t         lab0_FDCHI2_OWNPV;
  Float_t         lab0_DIRA_OWNPV;

  // this is the decay vertex of the particle
  Float_t         lab0_ENDVERTEX_X;
  Float_t         lab0_ENDVERTEX_Y;
  Float_t         lab0_ENDVERTEX_Z;
  Float_t         lab0_ENDVERTEX_XERR;
  Float_t         lab0_ENDVERTEX_YERR;
  Float_t         lab0_ENDVERTEX_ZERR;
  Float_t         lab0_ENDVERTEX_CHI2;
  Int_t           lab0_ENDVERTEX_NDOF;
  Float_t         lab0_ENDVERTEX_COV_[3][3];

  // kinematic variables
  Float_t         lab0_P;
  Float_t         lab0_PT;
  Float_t         lab0_PE;
  Float_t         lab0_PX;
  Float_t         lab0_PY;
  Float_t         lab0_PZ;
  Float_t         lab0_MM;
  Float_t         lab0_MMERR;
  Float_t         lab0_M;
  Int_t           lab0_BKGCAT;

  // BDTG variables
  Int_t           lab0_MassFitConsD_nPV;
  Float_t         lab0_MassFitConsD_M[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_MERR[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_P[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_PERR[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_chi2_B[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_nDOF[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_nIter[10];   //[lab0_MassFitConsD_nPV]
  Float_t         lab0_MassFitConsD_status[10];   //[lab0_MassFitConsD_nPV]

  // MC truth
  Int_t           lab0_TRUEID;
  Float_t         lab0_TRUEP_E;
  Float_t         lab0_TRUEP_X;
  Float_t         lab0_TRUEP_Y;
  Float_t         lab0_TRUEP_Z;
  Float_t         lab0_TRUEPT;

  // this is the origin vertex of the particle. For the B this is just
  // the same as "OWNPV" and so not filled. For the D this is the same
  // as the B vertex.
  Float_t         lab0_TRUEORIGINVERTEX_X;
  Float_t         lab0_TRUEORIGINVERTEX_Y;
  Float_t         lab0_TRUEORIGINVERTEX_Z;
  Float_t         lab0_TRUEENDVERTEX_X;
  Float_t         lab0_TRUEENDVERTEX_Y;
  Float_t         lab0_TRUEENDVERTEX_Z;
  Int_t           lab0_TRUEISSTABLE;
  Float_t         lab0_TRUETAU;

  // lifetime
  Int_t           lab0_OSCIL;
  Int_t           lab0_ID;
  Float_t         lab0_TAU;
  Float_t         lab0_TAUERR;
  Float_t         lab0_TAUCHI2;

  // L0 trigger
  Int_t           lab0L0Global_Dec;
  Int_t           lab0L0Global_TIS;
  Int_t           lab0L0Global_TOS;
  Int_t           lab0L0HadronDecision_Dec;
  Int_t           lab0L0HadronDecision_TIS;
  Int_t           lab0L0HadronDecision_TOS;

  // HLT1 trigger
  Int_t           lab0Hlt1Global_Dec;
  Int_t           lab0Hlt1Global_TIS;
  Int_t           lab0Hlt1Global_TOS;
  Int_t           lab0Hlt1TrackAllL0Decision_Dec;
  Int_t           lab0Hlt1TrackAllL0Decision_TIS;
  Int_t           lab0Hlt1TrackAllL0Decision_TOS;

  // HLT2 trigger
  Int_t           lab0Hlt2Global_Dec;
  Int_t           lab0Hlt2Global_TIS;
  Int_t           lab0Hlt2Global_TOS;
  Int_t           lab0Hlt2Topo2BodyBBDTDecision_Dec;
  Int_t           lab0Hlt2Topo2BodyBBDTDecision_TIS;
  Int_t           lab0Hlt2Topo2BodyBBDTDecision_TOS;
  Int_t           lab0Hlt2Topo3BodyBBDTDecision_Dec;
  Int_t           lab0Hlt2Topo3BodyBBDTDecision_TIS;
  Int_t           lab0Hlt2Topo3BodyBBDTDecision_TOS;
  Int_t           lab0Hlt2Topo4BodyBBDTDecision_Dec;
  Int_t           lab0Hlt2Topo4BodyBBDTDecision_TIS;
  Int_t           lab0Hlt2Topo4BodyBBDTDecision_TOS;
  Int_t           lab0Hlt2IncPhiDecision_Dec;
  Int_t           lab0Hlt2IncPhiDecision_TIS;
  Int_t           lab0Hlt2IncPhiDecision_TOS;

  /**
   * Declaration of leaf types for the bachelor (h, lab1_*)
   *
   */

  // TODO: what is mini?
  Float_t         lab1_CosTheta;

  Float_t         lab1_MINIP;
  Float_t         lab1_MINIPCHI2;

  Float_t         lab1_OWNPV_X;
  Float_t         lab1_OWNPV_Y;
  Float_t         lab1_OWNPV_Z;
  Float_t         lab1_OWNPV_XERR;
  Float_t         lab1_OWNPV_YERR;
  Float_t         lab1_OWNPV_ZERR;
  Float_t         lab1_OWNPV_CHI2;
  Int_t           lab1_OWNPV_NDOF;
  Float_t         lab1_OWNPV_COV_[3][3];
  Float_t         lab1_IP_OWNPV;
  Float_t         lab1_IPCHI2_OWNPV;

  // this is the origin vertex of the particle. For the B this is just
  // the same as "OWNPV" and so not filled. For the D this is the same
  // as the B vertex.
  Float_t         lab1_ORIVX_X;
  Float_t         lab1_ORIVX_Y;
  Float_t         lab1_ORIVX_Z;
  Float_t         lab1_ORIVX_XERR;
  Float_t         lab1_ORIVX_YERR;
  Float_t         lab1_ORIVX_ZERR;
  Float_t         lab1_ORIVX_CHI2;
  Int_t           lab1_ORIVX_NDOF;
  Float_t         lab1_ORIVX_COV_[3][3];

  // kinematic variables
  Float_t         lab1_P;
  Float_t         lab1_PT;
  Float_t         lab1_PE;
  Float_t         lab1_PX;
  Float_t         lab1_PY;
  Float_t         lab1_PZ;
  Float_t         lab1_M;

  // MC truth
  Int_t           lab1_TRUEID;
  Float_t         lab1_TRUEP_E;
  Float_t         lab1_TRUEP_X;
  Float_t         lab1_TRUEP_Y;
  Float_t         lab1_TRUEP_Z;
  Float_t         lab1_TRUEPT;
  Float_t         lab1_TRUEORIGINVERTEX_X;
  Float_t         lab1_TRUEORIGINVERTEX_Y;
  Float_t         lab1_TRUEORIGINVERTEX_Z;
  Float_t         lab1_TRUEENDVERTEX_X;
  Float_t         lab1_TRUEENDVERTEX_Y;
  Float_t         lab1_TRUEENDVERTEX_Z;
  Int_t           lab1_TRUEISSTABLE;
  Float_t         lab1_TRUETAU;

  // lifetime?
  Int_t           lab1_OSCIL;
  Int_t           lab1_ID;
  Float_t         lab1_PIDe;
  Float_t         lab1_PIDmu;
  Float_t         lab1_PIDK;
  Float_t         lab1_PIDp;
  Float_t         lab1_ProbNNe;
  Float_t         lab1_ProbNNk;
  Float_t         lab1_ProbNNp;
  Float_t         lab1_ProbNNpi;
  Float_t         lab1_ProbNNmu;
  Float_t         lab1_ProbNNghost;
  Float_t         lab1_CaloEcalE;      /**< Calibrated EM energy? */
  Float_t         lab1_CaloHcalE;      /**< Calibrated Hadronic energy? */
  Int_t           lab1_hasMuon;
  Int_t           lab1_isMuon;
  Int_t           lab1_hasRich;
  Int_t           lab1_hasCalo;

  // tracking
  Int_t           lab1_TRACK_Type;
  Int_t           lab1_TRACK_Key;
  Float_t         lab1_TRACK_CHI2NDOF;
  Float_t         lab1_TRACK_PCHI2;
  Float_t         lab1_TRACK_GhostProb;
  Float_t         lab1_TRACK_CloneDist;

  /**
   * Declaration of leaf types for the Ds (lab2_*)
   *
   */

  Float_t         lab2_CosTheta; // TODO: Opening angle?

  Float_t         lab2_MINIP;
  Float_t         lab2_MINIPCHI2;

  Float_t         lab2_OWNPV_X;
  Float_t         lab2_OWNPV_Y;
  Float_t         lab2_OWNPV_Z;
  Float_t         lab2_OWNPV_XERR;
  Float_t         lab2_OWNPV_YERR;
  Float_t         lab2_OWNPV_ZERR;
  Float_t         lab2_OWNPV_CHI2;
  Int_t           lab2_OWNPV_NDOF;
  Float_t         lab2_OWNPV_COV_[3][3];
  Float_t         lab2_IP_OWNPV;
  Float_t         lab2_IPCHI2_OWNPV;
  Float_t         lab2_FD_OWNPV;
  Float_t         lab2_FDCHI2_OWNPV;
  Float_t         lab2_DIRA_OWNPV;

  Float_t         lab2_ORIVX_X;
  Float_t         lab2_ORIVX_Y;
  Float_t         lab2_ORIVX_Z;
  Float_t         lab2_ORIVX_XERR;
  Float_t         lab2_ORIVX_YERR;
  Float_t         lab2_ORIVX_ZERR;
  Float_t         lab2_ORIVX_CHI2;
  Int_t           lab2_ORIVX_NDOF;
  Float_t         lab2_ORIVX_COV_[3][3];
  Float_t         lab2_FD_ORIVX;
  Float_t         lab2_FDCHI2_ORIVX;
  Float_t         lab2_DIRA_ORIVX;

  Float_t         lab2_ENDVERTEX_X;
  Float_t         lab2_ENDVERTEX_Y;
  Float_t         lab2_ENDVERTEX_Z;
  Float_t         lab2_ENDVERTEX_XERR;
  Float_t         lab2_ENDVERTEX_YERR;
  Float_t         lab2_ENDVERTEX_ZERR;
  Float_t         lab2_ENDVERTEX_CHI2;
  Int_t           lab2_ENDVERTEX_NDOF;
  Float_t         lab2_ENDVERTEX_COV_[3][3];

  // kinematic variables
  Float_t         lab2_P;
  Float_t         lab2_PT;
  Float_t         lab2_PE;
  Float_t         lab2_PX;
  Float_t         lab2_PY;
  Float_t         lab2_PZ;
  Float_t         lab2_MM;
  Float_t         lab2_MMERR;
  Float_t         lab2_M;
  Int_t           lab2_BKGCAT;

  // MC truth
  Int_t           lab2_TRUEID;
  Float_t         lab2_TRUEP_E;
  Float_t         lab2_TRUEP_X;
  Float_t         lab2_TRUEP_Y;
  Float_t         lab2_TRUEP_Z;
  Float_t         lab2_TRUEPT;
  Float_t         lab2_TRUEORIGINVERTEX_X;
  Float_t         lab2_TRUEORIGINVERTEX_Y;
  Float_t         lab2_TRUEORIGINVERTEX_Z;
  Float_t         lab2_TRUEENDVERTEX_X;
  Float_t         lab2_TRUEENDVERTEX_Y;
  Float_t         lab2_TRUEENDVERTEX_Z;
  Int_t           lab2_TRUEISSTABLE;
  Float_t         lab2_TRUETAU;

  // lifetime
  Int_t           lab2_OSCIL;
  Int_t           lab2_ID;
  Float_t         lab2_TAU;
  Float_t         lab2_TAUERR;
  Float_t         lab2_TAUCHI2;

  /**
   * Declaration of leaf types for the K (lab3_*)
   *
   */

  // what is mini?
  Float_t         lab3_CosTheta;

  Float_t         lab3_MINIP;
  Float_t         lab3_MINIPCHI2;

  Float_t         lab3_OWNPV_X;
  Float_t         lab3_OWNPV_Y;
  Float_t         lab3_OWNPV_Z;
  Float_t         lab3_OWNPV_XERR;
  Float_t         lab3_OWNPV_YERR;
  Float_t         lab3_OWNPV_ZERR;
  Float_t         lab3_OWNPV_CHI2;
  Int_t           lab3_OWNPV_NDOF;
  Float_t         lab3_OWNPV_COV_[3][3];
  Float_t         lab3_IP_OWNPV;
  Float_t         lab3_IPCHI2_OWNPV;

  Float_t         lab3_ORIVX_X;
  Float_t         lab3_ORIVX_Y;
  Float_t         lab3_ORIVX_Z;
  Float_t         lab3_ORIVX_XERR;
  Float_t         lab3_ORIVX_YERR;
  Float_t         lab3_ORIVX_ZERR;
  Float_t         lab3_ORIVX_CHI2;
  Int_t           lab3_ORIVX_NDOF;
  Float_t         lab3_ORIVX_COV_[3][3];

  // kinematic variables
  Float_t         lab3_P;
  Float_t         lab3_PT;
  Float_t         lab3_PE;
  Float_t         lab3_PX;
  Float_t         lab3_PY;
  Float_t         lab3_PZ;
  Float_t         lab3_M;

  // MC truth
  Int_t           lab3_TRUEID;
  Float_t         lab3_TRUEP_E;
  Float_t         lab3_TRUEP_X;
  Float_t         lab3_TRUEP_Y;
  Float_t         lab3_TRUEP_Z;
  Float_t         lab3_TRUEPT;
  Float_t         lab3_TRUEORIGINVERTEX_X;
  Float_t         lab3_TRUEORIGINVERTEX_Y;
  Float_t         lab3_TRUEORIGINVERTEX_Z;
  Float_t         lab3_TRUEENDVERTEX_X;
  Float_t         lab3_TRUEENDVERTEX_Y;
  Float_t         lab3_TRUEENDVERTEX_Z;
  Int_t           lab3_TRUEISSTABLE;
  Float_t         lab3_TRUETAU;

  Int_t           lab3_OSCIL;
  Int_t           lab3_ID;
  Float_t         lab3_PIDe;
  Float_t         lab3_PIDmu;
  Float_t         lab3_PIDK;
  Float_t         lab3_PIDp;
  Float_t         lab3_ProbNNe;
  Float_t         lab3_ProbNNk;
  Float_t         lab3_ProbNNp;
  Float_t         lab3_ProbNNpi;
  Float_t         lab3_ProbNNmu;
  Float_t         lab3_ProbNNghost;
  Float_t         lab3_CaloEcalE;
  Float_t         lab3_CaloHcalE;
  Int_t           lab3_hasMuon;
  Int_t           lab3_isMuon;
  Int_t           lab3_hasRich;
  Int_t           lab3_hasCalo;

  // tracking
  Int_t           lab3_TRACK_Type;
  Int_t           lab3_TRACK_Key;
  Float_t         lab3_TRACK_CHI2NDOF;
  Float_t         lab3_TRACK_PCHI2;
  Float_t         lab3_TRACK_GhostProb;
  Float_t         lab3_TRACK_CloneDist;

  /**
   * Declaration of leaf types for the K (lab4_*)
   *
   */

  Float_t         lab4_CosTheta;

  Float_t         lab4_MINIP;
  Float_t         lab4_MINIPCHI2;

  Float_t         lab4_OWNPV_X;
  Float_t         lab4_OWNPV_Y;
  Float_t         lab4_OWNPV_Z;
  Float_t         lab4_OWNPV_XERR;
  Float_t         lab4_OWNPV_YERR;
  Float_t         lab4_OWNPV_ZERR;
  Float_t         lab4_OWNPV_CHI2;
  Int_t           lab4_OWNPV_NDOF;
  Float_t         lab4_OWNPV_COV_[3][3];
  Float_t         lab4_IP_OWNPV;
  Float_t         lab4_IPCHI2_OWNPV;

  Float_t         lab4_ORIVX_X;
  Float_t         lab4_ORIVX_Y;
  Float_t         lab4_ORIVX_Z;
  Float_t         lab4_ORIVX_XERR;
  Float_t         lab4_ORIVX_YERR;
  Float_t         lab4_ORIVX_ZERR;
  Float_t         lab4_ORIVX_CHI2;
  Int_t           lab4_ORIVX_NDOF;
  Float_t         lab4_ORIVX_COV_[3][3];

  Float_t         lab4_P;
  Float_t         lab4_PT;
  Float_t         lab4_PE;
  Float_t         lab4_PX;
  Float_t         lab4_PY;
  Float_t         lab4_PZ;
  Float_t         lab4_M;

  // MC truth
  Int_t           lab4_TRUEID;
  Float_t         lab4_TRUEP_E;
  Float_t         lab4_TRUEP_X;
  Float_t         lab4_TRUEP_Y;
  Float_t         lab4_TRUEP_Z;
  Float_t         lab4_TRUEPT;
  Float_t         lab4_TRUEORIGINVERTEX_X;
  Float_t         lab4_TRUEORIGINVERTEX_Y;
  Float_t         lab4_TRUEORIGINVERTEX_Z;
  Float_t         lab4_TRUEENDVERTEX_X;
  Float_t         lab4_TRUEENDVERTEX_Y;
  Float_t         lab4_TRUEENDVERTEX_Z;
  Int_t           lab4_TRUEISSTABLE;
  Float_t         lab4_TRUETAU;

  // lifetime?
  Int_t           lab4_OSCIL;
  Int_t           lab4_ID;
  Float_t         lab4_PIDe;
  Float_t         lab4_PIDmu;
  Float_t         lab4_PIDK;
  Float_t         lab4_PIDp;
  Float_t         lab4_ProbNNe;
  Float_t         lab4_ProbNNk;
  Float_t         lab4_ProbNNp;
  Float_t         lab4_ProbNNpi;
  Float_t         lab4_ProbNNmu;
  Float_t         lab4_ProbNNghost;
  Float_t         lab4_CaloEcalE;
  Float_t         lab4_CaloHcalE;
  Int_t           lab4_hasMuon;
  Int_t           lab4_isMuon;
  Int_t           lab4_hasRich;
  Int_t           lab4_hasCalo;

  // tracking
  Int_t           lab4_TRACK_Type;
  Int_t           lab4_TRACK_Key;
  Float_t         lab4_TRACK_CHI2NDOF;
  Float_t         lab4_TRACK_PCHI2;
  Float_t         lab4_TRACK_GhostProb;
  Float_t         lab4_TRACK_CloneDist;

  /**
   * Declaration of leaf types for the pi (lab5_*)
   *
   */

  Float_t         lab5_CosTheta;

  Float_t         lab5_MINIP;
  Float_t         lab5_MINIPCHI2;

  Float_t         lab5_OWNPV_X;
  Float_t         lab5_OWNPV_Y;
  Float_t         lab5_OWNPV_Z;
  Float_t         lab5_OWNPV_XERR;
  Float_t         lab5_OWNPV_YERR;
  Float_t         lab5_OWNPV_ZERR;
  Float_t         lab5_OWNPV_CHI2;
  Int_t           lab5_OWNPV_NDOF;
  Float_t         lab5_OWNPV_COV_[3][3];
  Float_t         lab5_IP_OWNPV;
  Float_t         lab5_IPCHI2_OWNPV;

  Float_t         lab5_ORIVX_X;
  Float_t         lab5_ORIVX_Y;
  Float_t         lab5_ORIVX_Z;
  Float_t         lab5_ORIVX_XERR;
  Float_t         lab5_ORIVX_YERR;
  Float_t         lab5_ORIVX_ZERR;
  Float_t         lab5_ORIVX_CHI2;
  Int_t           lab5_ORIVX_NDOF;
  Float_t         lab5_ORIVX_COV_[3][3];

  Float_t         lab5_P;
  Float_t         lab5_PT;
  Float_t         lab5_PE;
  Float_t         lab5_PX;
  Float_t         lab5_PY;
  Float_t         lab5_PZ;
  Float_t         lab5_M;

  Int_t           lab5_TRUEID;
  Float_t         lab5_TRUEP_E;
  Float_t         lab5_TRUEP_X;
  Float_t         lab5_TRUEP_Y;
  Float_t         lab5_TRUEP_Z;
  Float_t         lab5_TRUEPT;
  Float_t         lab5_TRUEORIGINVERTEX_X;
  Float_t         lab5_TRUEORIGINVERTEX_Y;
  Float_t         lab5_TRUEORIGINVERTEX_Z;
  Float_t         lab5_TRUEENDVERTEX_X;
  Float_t         lab5_TRUEENDVERTEX_Y;
  Float_t         lab5_TRUEENDVERTEX_Z;
  Int_t           lab5_TRUEISSTABLE;
  Float_t         lab5_TRUETAU;

  Int_t           lab5_OSCIL;
  Int_t           lab5_ID;
  Float_t         lab5_PIDe;
  Float_t         lab5_PIDmu;
  Float_t         lab5_PIDK;
  Float_t         lab5_PIDp;
  Float_t         lab5_ProbNNe;
  Float_t         lab5_ProbNNk;
  Float_t         lab5_ProbNNp;
  Float_t         lab5_ProbNNpi;
  Float_t         lab5_ProbNNmu;
  Float_t         lab5_ProbNNghost;
  Float_t         lab5_CaloEcalE;
  Float_t         lab5_CaloHcalE;
  Int_t           lab5_hasMuon;
  Int_t           lab5_isMuon;
  Int_t           lab5_hasRich;
  Int_t           lab5_hasCalo;

  // tracking
  Int_t           lab5_TRACK_Type;
  Int_t           lab5_TRACK_Key;
  Float_t         lab5_TRACK_CHI2NDOF;
  Float_t         lab5_TRACK_PCHI2;
  Float_t         lab5_TRACK_GhostProb;
  Float_t         lab5_TRACK_CloneDist;

  /**
   * Declaration of leaf types not related to particles
   *
   */

  // others
  Int_t           nCandidate;
  Int_t           totCandidates;
  Int_t           EventInSequence;
  Int_t           runNumber;
  Int_t           eventNumber;
  Int_t           BCID;
  Int_t           BCType;
  Int_t           OdinTCK;
  Int_t           L0DUTCK;
  Int_t           HLTTCK;
  Float_t         GpsTime;
  Int_t           Primaries;
  Int_t           nPV;
  Float_t         PVX[100];   //[nPV]
  Float_t         PVY[100];   //[nPV]
  Float_t         PVZ[100];   //[nPV]
  Float_t         PVXERR[100];   //[nPV]
  Float_t         PVYERR[100];   //[nPV]
  Float_t         PVZERR[100];   //[nPV]
  Float_t         PVCHI2[100];   //[nPV]
  Float_t         PVNDOF[100];   //[nPV]
  Float_t         PVNTRACKS[100];   //[nPV]

  Int_t           nPVs;
  Int_t           nTracks;
  Int_t           nLongTracks;
  Int_t           nDownstreamTracks;
  Int_t           nUpstreamTracks;
  Int_t           nVeloTracks;
  Int_t           nTTracks;
  Int_t           nBackTracks;
  Int_t           nRich1Hits;
  Int_t           nRich2Hits;
  Float_t         BDTGResponse_1;

  /**
   * Declaration of branches
   *
   */

  // TODO: what is mini?
  TBranch         *b_lab0_MINIP;
  TBranch         *b_lab0_MINIPCHI2;

  TBranch         *b_lab0_OWNPV_X;
  TBranch         *b_lab0_OWNPV_Y;
  TBranch         *b_lab0_OWNPV_Z;
  TBranch         *b_lab0_OWNPV_XERR;
  TBranch         *b_lab0_OWNPV_YERR;
  TBranch         *b_lab0_OWNPV_ZERR;
  TBranch         *b_lab0_OWNPV_CHI2;
  TBranch         *b_lab0_OWNPV_NDOF;
  TBranch         *b_lab0_OWNPV_COV_;
  TBranch         *b_lab0_IP_OWNPV;
  TBranch         *b_lab0_IPCHI2_OWNPV;
  TBranch         *b_lab0_FD_OWNPV;
  TBranch         *b_lab0_FDCHI2_OWNPV;
  TBranch         *b_lab0_DIRA_OWNPV;

  TBranch         *b_lab0_ENDVERTEX_X;
  TBranch         *b_lab0_ENDVERTEX_Y;
  TBranch         *b_lab0_ENDVERTEX_Z;
  TBranch         *b_lab0_ENDVERTEX_XERR;
  TBranch         *b_lab0_ENDVERTEX_YERR;
  TBranch         *b_lab0_ENDVERTEX_ZERR;
  TBranch         *b_lab0_ENDVERTEX_CHI2;
  TBranch         *b_lab0_ENDVERTEX_NDOF;
  TBranch         *b_lab0_ENDVERTEX_COV_;

  // kinematic variables
  TBranch         *b_lab0_P;
  TBranch         *b_lab0_PT;
  TBranch         *b_lab0_PE;
  TBranch         *b_lab0_PX;
  TBranch         *b_lab0_PY;
  TBranch         *b_lab0_PZ;
  TBranch         *b_lab0_MM;
  TBranch         *b_lab0_MMERR;
  TBranch         *b_lab0_M;
  TBranch         *b_lab0_BKGCAT;

  // BDTG variables
  TBranch        *b_lab0_MassFitConsD_nPV;   //!
  TBranch        *b_lab0_MassFitConsD_M;   //!
  TBranch        *b_lab0_MassFitConsD_MERR;   //!
  TBranch        *b_lab0_MassFitConsD_P;   //!
  TBranch        *b_lab0_MassFitConsD_PERR;   //!
  TBranch        *b_lab0_MassFitConsD_chi2_B;   //!
  TBranch        *b_lab0_MassFitConsD_nDOF;   //!
  TBranch        *b_lab0_MassFitConsD_nIter;   //!
  TBranch        *b_lab0_MassFitConsD_status;   //!

  // MC truth
  TBranch         *b_lab0_TRUEID;
  TBranch         *b_lab0_TRUEP_E;
  TBranch         *b_lab0_TRUEP_X;
  TBranch         *b_lab0_TRUEP_Y;
  TBranch         *b_lab0_TRUEP_Z;
  TBranch         *b_lab0_TRUEPT;
  TBranch         *b_lab0_TRUEORIGINVERTEX_X;
  TBranch         *b_lab0_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab0_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab0_TRUEENDVERTEX_X;
  TBranch         *b_lab0_TRUEENDVERTEX_Y;
  TBranch         *b_lab0_TRUEENDVERTEX_Z;
  TBranch         *b_lab0_TRUEISSTABLE;
  TBranch         *b_lab0_TRUETAU;

  // lifetime
  TBranch         *b_lab0_OSCIL;
  TBranch         *b_lab0_ID;
  TBranch         *b_lab0_TAU;
  TBranch         *b_lab0_TAUERR;
  TBranch         *b_lab0_TAUCHI2;

  // L0 trigger
  TBranch         *b_lab0L0Global_Dec;
  TBranch         *b_lab0L0Global_TIS;
  TBranch         *b_lab0L0Global_TOS;

  TBranch         *b_lab0L0HadronDecision_Dec;
  TBranch         *b_lab0L0HadronDecision_TIS;
  TBranch         *b_lab0L0HadronDecision_TOS;

  // HLT1 trigger
  TBranch         *b_lab0Hlt1Global_Dec;
  TBranch         *b_lab0Hlt1Global_TIS;
  TBranch         *b_lab0Hlt1Global_TOS;

  TBranch         *b_lab0Hlt1TrackAllL0Decision_Dec;
  TBranch         *b_lab0Hlt1TrackAllL0Decision_TIS;
  TBranch         *b_lab0Hlt1TrackAllL0Decision_TOS;

  // HLT2 trigger
  TBranch         *b_lab0Hlt2Global_Dec;
  TBranch         *b_lab0Hlt2Global_TIS;
  TBranch         *b_lab0Hlt2Global_TOS;

  TBranch         *b_lab0Hlt2Topo2BodyBBDTDecision_Dec;
  TBranch         *b_lab0Hlt2Topo2BodyBBDTDecision_TIS;
  TBranch         *b_lab0Hlt2Topo2BodyBBDTDecision_TOS;
  TBranch         *b_lab0Hlt2Topo3BodyBBDTDecision_Dec;
  TBranch         *b_lab0Hlt2Topo3BodyBBDTDecision_TIS;
  TBranch         *b_lab0Hlt2Topo3BodyBBDTDecision_TOS;
  TBranch         *b_lab0Hlt2Topo4BodyBBDTDecision_Dec;
  TBranch         *b_lab0Hlt2Topo4BodyBBDTDecision_TIS;
  TBranch         *b_lab0Hlt2Topo4BodyBBDTDecision_TOS;
  TBranch         *b_lab0Hlt2IncPhiDecision_Dec;
  TBranch         *b_lab0Hlt2IncPhiDecision_TIS;
  TBranch         *b_lab0Hlt2IncPhiDecision_TOS;

  /**
   * Declaration of branches for the bachelor (h, lab1_*)
   *
   */

  // TODO: what is mini?
  TBranch         *b_lab1_CosTheta;

  TBranch         *b_lab1_MINIP;
  TBranch         *b_lab1_MINIPCHI2;

  TBranch         *b_lab1_OWNPV_X;
  TBranch         *b_lab1_OWNPV_Y;
  TBranch         *b_lab1_OWNPV_Z;
  TBranch         *b_lab1_OWNPV_XERR;
  TBranch         *b_lab1_OWNPV_YERR;
  TBranch         *b_lab1_OWNPV_ZERR;
  TBranch         *b_lab1_OWNPV_CHI2;
  TBranch         *b_lab1_OWNPV_NDOF;
  TBranch         *b_lab1_OWNPV_COV_;
  TBranch         *b_lab1_IP_OWNPV;
  TBranch         *b_lab1_IPCHI2_OWNPV;

  TBranch         *b_lab1_ORIVX_X;
  TBranch         *b_lab1_ORIVX_Y;
  TBranch         *b_lab1_ORIVX_Z;
  TBranch         *b_lab1_ORIVX_XERR;
  TBranch         *b_lab1_ORIVX_YERR;
  TBranch         *b_lab1_ORIVX_ZERR;
  TBranch         *b_lab1_ORIVX_CHI2;
  TBranch         *b_lab1_ORIVX_NDOF;
  TBranch         *b_lab1_ORIVX_COV_;

  // kinematic variables
  TBranch         *b_lab1_P;
  TBranch         *b_lab1_PT;
  TBranch         *b_lab1_PE;
  TBranch         *b_lab1_PX;
  TBranch         *b_lab1_PY;
  TBranch         *b_lab1_PZ;
  TBranch         *b_lab1_M;

  // MC truth
  TBranch         *b_lab1_TRUEID;
  TBranch         *b_lab1_TRUEP_E;
  TBranch         *b_lab1_TRUEP_X;
  TBranch         *b_lab1_TRUEP_Y;
  TBranch         *b_lab1_TRUEP_Z;
  TBranch         *b_lab1_TRUEPT;
  TBranch         *b_lab1_TRUEORIGINVERTEX_X;
  TBranch         *b_lab1_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab1_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab1_TRUEENDVERTEX_X;
  TBranch         *b_lab1_TRUEENDVERTEX_Y;
  TBranch         *b_lab1_TRUEENDVERTEX_Z;
  TBranch         *b_lab1_TRUEISSTABLE;
  TBranch         *b_lab1_TRUETAU;

  TBranch         *b_lab1_OSCIL;
  TBranch         *b_lab1_ID;
  TBranch         *b_lab1_PIDe;
  TBranch         *b_lab1_PIDmu;
  TBranch         *b_lab1_PIDK;
  TBranch         *b_lab1_PIDp;
  TBranch         *b_lab1_ProbNNe;
  TBranch         *b_lab1_ProbNNk;
  TBranch         *b_lab1_ProbNNp;
  TBranch         *b_lab1_ProbNNpi;
  TBranch         *b_lab1_ProbNNmu;
  TBranch         *b_lab1_ProbNNghost;
  TBranch         *b_lab1_CaloEcalE;      /**< Calibrated EM energy? */
  TBranch         *b_lab1_CaloHcalE;      /**< Calibrated Hadronic energy? */
  TBranch         *b_lab1_hasMuon;
  TBranch         *b_lab1_isMuon;
  TBranch         *b_lab1_hasRich;
  TBranch         *b_lab1_hasCalo;

  // tracking
  TBranch         *b_lab1_TRACK_Type;
  TBranch         *b_lab1_TRACK_Key;
  TBranch         *b_lab1_TRACK_CHI2NDOF;
  TBranch         *b_lab1_TRACK_PCHI2;
  TBranch         *b_lab1_TRACK_GhostProb;
  TBranch         *b_lab1_TRACK_CloneDist;

  /**
   * Declaration of branches for the Ds (lab2_*)
   *
   */

  TBranch         *b_lab2_CosTheta;

  TBranch         *b_lab2_MINIP;
  TBranch         *b_lab2_MINIPCHI2;

  TBranch         *b_lab2_OWNPV_X;
  TBranch         *b_lab2_OWNPV_Y;
  TBranch         *b_lab2_OWNPV_Z;
  TBranch         *b_lab2_OWNPV_XERR;
  TBranch         *b_lab2_OWNPV_YERR;
  TBranch         *b_lab2_OWNPV_ZERR;
  TBranch         *b_lab2_OWNPV_CHI2;
  TBranch         *b_lab2_OWNPV_NDOF;
  TBranch         *b_lab2_OWNPV_COV_;
  TBranch         *b_lab2_IP_OWNPV;
  TBranch         *b_lab2_IPCHI2_OWNPV;
  TBranch         *b_lab2_FD_OWNPV;
  TBranch         *b_lab2_FDCHI2_OWNPV;
  TBranch         *b_lab2_DIRA_OWNPV;

  TBranch         *b_lab2_ORIVX_X;
  TBranch         *b_lab2_ORIVX_Y;
  TBranch         *b_lab2_ORIVX_Z;
  TBranch         *b_lab2_ORIVX_XERR;
  TBranch         *b_lab2_ORIVX_YERR;
  TBranch         *b_lab2_ORIVX_ZERR;
  TBranch         *b_lab2_ORIVX_CHI2;
  TBranch         *b_lab2_ORIVX_NDOF;
  TBranch         *b_lab2_ORIVX_COV_;
  TBranch         *b_lab2_FD_ORIVX;
  TBranch         *b_lab2_FDCHI2_ORIVX;
  TBranch         *b_lab2_DIRA_ORIVX;

  TBranch         *b_lab2_ENDVERTEX_X;
  TBranch         *b_lab2_ENDVERTEX_Y;
  TBranch         *b_lab2_ENDVERTEX_Z;
  TBranch         *b_lab2_ENDVERTEX_XERR;
  TBranch         *b_lab2_ENDVERTEX_YERR;
  TBranch         *b_lab2_ENDVERTEX_ZERR;
  TBranch         *b_lab2_ENDVERTEX_CHI2;
  TBranch         *b_lab2_ENDVERTEX_NDOF;
  TBranch         *b_lab2_ENDVERTEX_COV_;

  // kinematic variables
  TBranch         *b_lab2_P;
  TBranch         *b_lab2_PT;
  TBranch         *b_lab2_PE;
  TBranch         *b_lab2_PX;
  TBranch         *b_lab2_PY;
  TBranch         *b_lab2_PZ;
  TBranch         *b_lab2_MM;
  TBranch         *b_lab2_MMERR;
  TBranch         *b_lab2_M;
  TBranch         *b_lab2_BKGCAT;

  // MC truth
  TBranch         *b_lab2_TRUEID;
  TBranch         *b_lab2_TRUEP_E;
  TBranch         *b_lab2_TRUEP_X;
  TBranch         *b_lab2_TRUEP_Y;
  TBranch         *b_lab2_TRUEP_Z;
  TBranch         *b_lab2_TRUEPT;
  TBranch         *b_lab2_TRUEORIGINVERTEX_X;
  TBranch         *b_lab2_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab2_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab2_TRUEENDVERTEX_X;
  TBranch         *b_lab2_TRUEENDVERTEX_Y;
  TBranch         *b_lab2_TRUEENDVERTEX_Z;
  TBranch         *b_lab2_TRUEISSTABLE;
  TBranch         *b_lab2_TRUETAU;

  // lifetime
  TBranch         *b_lab2_OSCIL;
  TBranch         *b_lab2_ID;
  TBranch         *b_lab2_TAU;
  TBranch         *b_lab2_TAUERR;
  TBranch         *b_lab2_TAUCHI2;

  /**
   * Declaration of branches for the K (lab3_*)
   *
   */

  // what is mini?
  TBranch         *b_lab3_CosTheta;

  TBranch         *b_lab3_MINIP;
  TBranch         *b_lab3_MINIPCHI2;

  TBranch         *b_lab3_OWNPV_X;
  TBranch         *b_lab3_OWNPV_Y;
  TBranch         *b_lab3_OWNPV_Z;
  TBranch         *b_lab3_OWNPV_XERR;
  TBranch         *b_lab3_OWNPV_YERR;
  TBranch         *b_lab3_OWNPV_ZERR;
  TBranch         *b_lab3_OWNPV_CHI2;
  TBranch         *b_lab3_OWNPV_NDOF;
  TBranch         *b_lab3_OWNPV_COV_;
  TBranch         *b_lab3_IP_OWNPV;
  TBranch         *b_lab3_IPCHI2_OWNPV;

  TBranch         *b_lab3_ORIVX_X;
  TBranch         *b_lab3_ORIVX_Y;
  TBranch         *b_lab3_ORIVX_Z;
  TBranch         *b_lab3_ORIVX_XERR;
  TBranch         *b_lab3_ORIVX_YERR;
  TBranch         *b_lab3_ORIVX_ZERR;
  TBranch         *b_lab3_ORIVX_CHI2;
  TBranch         *b_lab3_ORIVX_NDOF;
  TBranch         *b_lab3_ORIVX_COV_;

  // kinematic variables
  TBranch         *b_lab3_P;
  TBranch         *b_lab3_PT;
  TBranch         *b_lab3_PE;
  TBranch         *b_lab3_PX;
  TBranch         *b_lab3_PY;
  TBranch         *b_lab3_PZ;
  TBranch         *b_lab3_M;

  // MC truth
  TBranch         *b_lab3_TRUEID;
  TBranch         *b_lab3_TRUEP_E;
  TBranch         *b_lab3_TRUEP_X;
  TBranch         *b_lab3_TRUEP_Y;
  TBranch         *b_lab3_TRUEP_Z;
  TBranch         *b_lab3_TRUEPT;
  TBranch         *b_lab3_TRUEORIGINVERTEX_X;
  TBranch         *b_lab3_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab3_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab3_TRUEENDVERTEX_X;
  TBranch         *b_lab3_TRUEENDVERTEX_Y;
  TBranch         *b_lab3_TRUEENDVERTEX_Z;
  TBranch         *b_lab3_TRUEISSTABLE;
  TBranch         *b_lab3_TRUETAU;

  TBranch         *b_lab3_OSCIL;
  TBranch         *b_lab3_ID;
  TBranch         *b_lab3_PIDe;
  TBranch         *b_lab3_PIDmu;
  TBranch         *b_lab3_PIDK;
  TBranch         *b_lab3_PIDp;
  TBranch         *b_lab3_ProbNNe;
  TBranch         *b_lab3_ProbNNk;
  TBranch         *b_lab3_ProbNNp;
  TBranch         *b_lab3_ProbNNpi;
  TBranch         *b_lab3_ProbNNmu;
  TBranch         *b_lab3_ProbNNghost;
  TBranch         *b_lab3_CaloEcalE;
  TBranch         *b_lab3_CaloHcalE;
  TBranch         *b_lab3_hasMuon;
  TBranch         *b_lab3_isMuon;
  TBranch         *b_lab3_hasRich;
  TBranch         *b_lab3_hasCalo;

  // tracking
  TBranch         *b_lab3_TRACK_Type;
  TBranch         *b_lab3_TRACK_Key;
  TBranch         *b_lab3_TRACK_CHI2NDOF;
  TBranch         *b_lab3_TRACK_PCHI2;
  TBranch         *b_lab3_TRACK_GhostProb;
  TBranch         *b_lab3_TRACK_CloneDist;

  /**
   * Declaration of branches for the K (lab4_*)
   *
   */

  TBranch         *b_lab4_CosTheta;

  TBranch         *b_lab4_MINIP;
  TBranch         *b_lab4_MINIPCHI2;

  TBranch         *b_lab4_OWNPV_X;
  TBranch         *b_lab4_OWNPV_Y;
  TBranch         *b_lab4_OWNPV_Z;
  TBranch         *b_lab4_OWNPV_XERR;
  TBranch         *b_lab4_OWNPV_YERR;
  TBranch         *b_lab4_OWNPV_ZERR;
  TBranch         *b_lab4_OWNPV_CHI2;
  TBranch         *b_lab4_OWNPV_NDOF;
  TBranch         *b_lab4_OWNPV_COV_;
  TBranch         *b_lab4_IP_OWNPV;
  TBranch         *b_lab4_IPCHI2_OWNPV;

  TBranch         *b_lab4_ORIVX_X;
  TBranch         *b_lab4_ORIVX_Y;
  TBranch         *b_lab4_ORIVX_Z;
  TBranch         *b_lab4_ORIVX_XERR;
  TBranch         *b_lab4_ORIVX_YERR;
  TBranch         *b_lab4_ORIVX_ZERR;
  TBranch         *b_lab4_ORIVX_CHI2;
  TBranch         *b_lab4_ORIVX_NDOF;
  TBranch         *b_lab4_ORIVX_COV_;

  TBranch         *b_lab4_P;
  TBranch         *b_lab4_PT;
  TBranch         *b_lab4_PE;
  TBranch         *b_lab4_PX;
  TBranch         *b_lab4_PY;
  TBranch         *b_lab4_PZ;
  TBranch         *b_lab4_M;

  // MC truth
  TBranch         *b_lab4_TRUEID;
  TBranch         *b_lab4_TRUEP_E;
  TBranch         *b_lab4_TRUEP_X;
  TBranch         *b_lab4_TRUEP_Y;
  TBranch         *b_lab4_TRUEP_Z;
  TBranch         *b_lab4_TRUEPT;
  TBranch         *b_lab4_TRUEORIGINVERTEX_X;
  TBranch         *b_lab4_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab4_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab4_TRUEENDVERTEX_X;
  TBranch         *b_lab4_TRUEENDVERTEX_Y;
  TBranch         *b_lab4_TRUEENDVERTEX_Z;
  TBranch         *b_lab4_TRUEISSTABLE;
  TBranch         *b_lab4_TRUETAU;

  // lifetime?
  TBranch         *b_lab4_OSCIL;
  TBranch         *b_lab4_ID;
  TBranch         *b_lab4_PIDe;
  TBranch         *b_lab4_PIDmu;
  TBranch         *b_lab4_PIDK;
  TBranch         *b_lab4_PIDp;
  TBranch         *b_lab4_ProbNNe;
  TBranch         *b_lab4_ProbNNk;
  TBranch         *b_lab4_ProbNNp;
  TBranch         *b_lab4_ProbNNpi;
  TBranch         *b_lab4_ProbNNmu;
  TBranch         *b_lab4_ProbNNghost;
  TBranch         *b_lab4_CaloEcalE;
  TBranch         *b_lab4_CaloHcalE;
  TBranch         *b_lab4_hasMuon;
  TBranch         *b_lab4_isMuon;
  TBranch         *b_lab4_hasRich;
  TBranch         *b_lab4_hasCalo;

  // tracking
  TBranch         *b_lab4_TRACK_Type;
  TBranch         *b_lab4_TRACK_Key;
  TBranch         *b_lab4_TRACK_CHI2NDOF;
  TBranch         *b_lab4_TRACK_PCHI2;
  TBranch         *b_lab4_TRACK_GhostProb;
  TBranch         *b_lab4_TRACK_CloneDist;

  /**
   * Declaration of branches for the pi (lab5_*)
   *
   */

  TBranch         *b_lab5_CosTheta;

  TBranch         *b_lab5_MINIP;
  TBranch         *b_lab5_MINIPCHI2;

  TBranch         *b_lab5_OWNPV_X;
  TBranch         *b_lab5_OWNPV_Y;
  TBranch         *b_lab5_OWNPV_Z;
  TBranch         *b_lab5_OWNPV_XERR;
  TBranch         *b_lab5_OWNPV_YERR;
  TBranch         *b_lab5_OWNPV_ZERR;
  TBranch         *b_lab5_OWNPV_CHI2;
  TBranch         *b_lab5_OWNPV_NDOF;
  TBranch         *b_lab5_OWNPV_COV_;
  TBranch         *b_lab5_IP_OWNPV;
  TBranch         *b_lab5_IPCHI2_OWNPV;

  TBranch         *b_lab5_ORIVX_X;
  TBranch         *b_lab5_ORIVX_Y;
  TBranch         *b_lab5_ORIVX_Z;
  TBranch         *b_lab5_ORIVX_XERR;
  TBranch         *b_lab5_ORIVX_YERR;
  TBranch         *b_lab5_ORIVX_ZERR;
  TBranch         *b_lab5_ORIVX_CHI2;
  TBranch         *b_lab5_ORIVX_NDOF;
  TBranch         *b_lab5_ORIVX_COV_;

  TBranch         *b_lab5_P;
  TBranch         *b_lab5_PT;
  TBranch         *b_lab5_PE;
  TBranch         *b_lab5_PX;
  TBranch         *b_lab5_PY;
  TBranch         *b_lab5_PZ;
  TBranch         *b_lab5_M;

  TBranch         *b_lab5_TRUEID;
  TBranch         *b_lab5_TRUEP_E;
  TBranch         *b_lab5_TRUEP_X;
  TBranch         *b_lab5_TRUEP_Y;
  TBranch         *b_lab5_TRUEP_Z;
  TBranch         *b_lab5_TRUEPT;
  TBranch         *b_lab5_TRUEORIGINVERTEX_X;
  TBranch         *b_lab5_TRUEORIGINVERTEX_Y;
  TBranch         *b_lab5_TRUEORIGINVERTEX_Z;
  TBranch         *b_lab5_TRUEENDVERTEX_X;
  TBranch         *b_lab5_TRUEENDVERTEX_Y;
  TBranch         *b_lab5_TRUEENDVERTEX_Z;
  TBranch         *b_lab5_TRUEISSTABLE;
  TBranch         *b_lab5_TRUETAU;

  TBranch         *b_lab5_OSCIL;
  TBranch         *b_lab5_ID;
  TBranch         *b_lab5_PIDe;
  TBranch         *b_lab5_PIDmu;
  TBranch         *b_lab5_PIDK;
  TBranch         *b_lab5_PIDp;
  TBranch         *b_lab5_ProbNNe;
  TBranch         *b_lab5_ProbNNk;
  TBranch         *b_lab5_ProbNNp;
  TBranch         *b_lab5_ProbNNpi;
  TBranch         *b_lab5_ProbNNmu;
  TBranch         *b_lab5_ProbNNghost;
  TBranch         *b_lab5_CaloEcalE;
  TBranch         *b_lab5_CaloHcalE;
  TBranch         *b_lab5_hasMuon;
  TBranch         *b_lab5_isMuon;
  TBranch         *b_lab5_hasRich;
  TBranch         *b_lab5_hasCalo;

  // tracking
  TBranch         *b_lab5_TRACK_Type;
  TBranch         *b_lab5_TRACK_Key;
  TBranch         *b_lab5_TRACK_CHI2NDOF;
  TBranch         *b_lab5_TRACK_PCHI2;
  TBranch         *b_lab5_TRACK_GhostProb;
  TBranch         *b_lab5_TRACK_CloneDist;

  /**
   * Declaration of branches not related to particles
   *
   */

  // others
  TBranch         *b_nCandidate;
  TBranch         *b_totCandidates;
  TBranch         *b_EventInSequence;
  TBranch         *b_runNumber;
  TBranch         *b_eventNumber;
  TBranch         *b_BCID;
  TBranch         *b_BCType;
  TBranch         *b_OdinTCK;
  TBranch         *b_L0DUTCK;
  TBranch         *b_HLTTCK;
  TBranch         *b_GpsTime;
  TBranch         *b_Primaries;
  TBranch         *b_nPV;
  TBranch         *b_PVX;   //[nPV]
  TBranch         *b_PVY;   //[nPV]
  TBranch         *b_PVZ;   //[nPV]
  TBranch         *b_PVXERR;   //[nPV]
  TBranch         *b_PVYERR;   //[nPV]
  TBranch         *b_PVZERR;   //[nPV]
  TBranch         *b_PVCHI2;   //[nPV]
  TBranch         *b_PVNDOF;   //[nPV]
  TBranch         *b_PVNTRACKS;   //[nPV]

  TBranch        *b_nPVs;
  TBranch        *b_nTracks;
  TBranch        *b_nLongTracks;
  TBranch        *b_nDownstreamTracks;
  TBranch        *b_nUpstreamTracks;
  TBranch        *b_nVeloTracks;
  TBranch        *b_nTTracks;
  TBranch        *b_nBackTracks;
  TBranch        *b_nRich1Hits;
  TBranch        *b_nRich2Hits;
  TBranch        *b_BDTGResponse_1;

};

#endif // #ifndef __READMCTREE_HXX
