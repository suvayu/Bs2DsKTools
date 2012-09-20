/**
 * @file   lifetime.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Sun Dec 11 01:27:13 2011
 *
 * @brief
 *
 *
 */

#include <iostream>
#include <iomanip>

#include "lifetime.hxx"
// #include "Event.h"

#include <Rtypes.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TVector3.h>
#include <TProfile.h>
#include <TLegend.h>
#include <TMath.h>

using namespace std;


lifetime::lifetime(TTree *tree) : readMCTree(tree) {}


lifetime::~lifetime() {}


void lifetime::Loop()
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();

   std::cout << nentries << " entries!" << std::endl;

   // double gamma(0), tau(0);
   // TLorentzVector BsP(0,0,0,0), DsP(0,0,0,0), hP(0,0,0,0),
   //   Pi3P(0,0,0,0), K4P(0,0,0,0), K5P(0,0,0,0);

   // TVector3 PV(0,0,0), DecVx(0,0,0), flight(0,0,0);
   TProfile hAccept  ("hAccept"    , "Acceptance function", 100, 0, 0.01);
   TH1D     hlifetimew("hlifetimew", "Weighted lifetime"  , 100, 0, 0.01);
   TH1D     hlifetime ("hlifetime" , "Lifetime"           , 100, 0, 0.01);

   hAccept   .SetLineColor(kAzure);
   hlifetimew.SetLineColor(kGreen);
   hlifetime .SetLineColor(kAzure);

   hAccept   .SetXTitle("Bs lifetime in ns");
   hlifetimew.SetXTitle("Bs lifetime in ns");
   hlifetime .SetXTitle("Bs lifetime in ns");

   // cout << setw(20) << "true τ" << endl;

   Long64_t nbytes = 0, nb = 0;
   // for (Long64_t jentry=0; jentry<nentries;jentry+=10) // for testing
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       // Pi3P.SetXYZM( lab3_PX, lab3_PY, lab3_PZ, lab3_M);
       // K4P .SetXYZM( lab4_PX, lab4_PY, lab4_PZ, lab4_M);
       // K5P .SetXYZM( lab5_PX, lab5_PY, lab5_PZ, lab5_M);
       // hP  .SetXYZM( lab1_PX, lab1_PY, lab1_PZ, lab1_M);

       // DsP = Pi3P + K4P + K5P;
       // BsP = DsP + hP;

       // gamma = BsP.Gamma();
       // PV   .SetXYZ(lab0_OWNPV_X, lab0_OWNPV_Y, lab0_OWNPV_Z);
       // DecVx.SetXYZ(lab0_ENDVERTEX_X, lab0_ENDVERTEX_Y, lab0_ENDVERTEX_Z);
       // flight = DecVx - PV;
       // tau = flight.Mag() * lab0_MM / (lab0_P * gamma);

       // cout << setw(20) << lab0_TRUETAU << endl;

       if (( lab0Hlt2Topo4BodyBBDTDecision_TOS == false )
       // if (( lab0Hlt2Topo2BodyBBDTDecision_TOS == false )
       // if (( lab0Hlt2IncPhiDecision_TOS == false )
	   or ( CommonSelection() == false ) or ( lab1_PIDK < 5 )) {
	 // off so that you can apply later
	 hAccept.Fill(lab0_TRUETAU, 0);
	 continue;
       }
       // if ( pPIDcut != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       hAccept   .Fill(lab0_TRUETAU, 1);
       hlifetimew.Fill(lab0_TRUETAU, TMath::Exp(lab0_TRUETAU*1e3/1.472)); // time in ns / lifetime in ps
       hlifetime .Fill(lab0_TAU);
     }

   TCanvas *canvas = new TCanvas("canvas", "", 1200, 450);
   canvas->Divide(2,1);

   canvas->cd(1);
   hAccept   .DrawNormalized("hist");
   hlifetimew.DrawNormalized("hist same");
   canvas->cd(2);
   hlifetime .Draw("hist");

   TLegend *leg = new TLegend( 0.6, 0.45, 0.9, 0.7);
   leg->SetFillColor(4000); // transparent
   leg->SetBorderSize(0);
   leg->SetHeader("Bs lifetime (#tau)");
   leg->AddEntry( &hlifetime , "Reconstructed", "l");
   leg->Draw();
   canvas->Print(".png");

   // hAccept  .Print("all");
   // hlifetime .Print("all");
   // hlifetimew.Print("all");

   delete canvas;
   cout << "lifetime::Loop(): Read " << nbytes << " bytes." << std::endl;
}


void lifetime::Loop(TTree &ftree)
{
   if (fChain == 0) return;
   Long64_t nentries = fChain->GetEntries();
   std::cout << nentries << " entries!" << std::endl;

   TLorentzVector BsMom(0,0,0,0);
   TVector3 OWNPV(0,0,0), ENDVX(0,0,0);
   double wt(0), truewt(0);

   ftree.Branch("Bsmass" , &lab0_MM);
   ftree.Branch("BsMom"  , &BsMom);
   ftree.Branch("hID"    , &lab1_TRUEID);
   ftree.Branch("time"   , &lab0_TAU);
   ftree.Branch("truetime", &lab0_TRUETAU);
   ftree.Branch("wt"     , &wt);
   ftree.Branch("truewt" , &truewt);
   ftree.Branch("oscil"  , &lab0_OSCIL);
   ftree.Branch("OWNPV"  , &OWNPV);
   ftree.Branch("ENDVX"  , &ENDVX);

   ftree.Branch("HLT1TrackAllL0TOS", &lab0Hlt1TrackAllL0Decision_TOS);
   ftree.Branch("HLT2Topo4BodyTOS" , &lab0Hlt2Topo4BodyBBDTDecision_TOS);
   ftree.Branch("HLT2Topo3BodyTOS" , &lab0Hlt2Topo3BodyBBDTDecision_TOS);
   ftree.Branch("HLT2Topo2BodyTOS" , &lab0Hlt2Topo2BodyBBDTDecision_TOS);
   ftree.Branch("HLT2TopoIncPhiTOS", &lab0Hlt2IncPhiDecision_TOS);

   Long64_t nbytes = 0, nb = 0;
   // for (Long64_t jentry=0; jentry<nentries;jentry+=10) // for testing
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       // if (( UnbiasedSelection() == false ) or ( lab1_PIDK < 5 )) continue;
       if (CommonSelection() == false) continue;
       // if ( pPIDcut != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       wt       = TMath::Exp(lab0_TAU*1e3/1.472);
       truewt   = TMath::Exp(lab0_TRUETAU*1e3/1.472);
       BsMom.SetPxPyPzE(lab0_PX, lab0_PY, lab0_PZ, lab0_MM);
       OWNPV.SetXYZ(lab0_OWNPV_X, lab0_OWNPV_Y, lab0_OWNPV_Z);
       ENDVX.SetXYZ(lab0_ENDVERTEX_X, lab0_ENDVERTEX_Y, lab0_ENDVERTEX_Z);
       ftree.Fill();
     }

   std::cout << "lifetime::Loop(TTree&): Read " << nbytes << " bytes." << std::endl;
}


void lifetime::Loop(TTree &ftree, TEntryList &felist, bool DsK)
{
   if (fChain == 0) return;
   Long64_t nentries = fChain->GetEntries();
   std::cout << nentries << " entries!" << std::endl;

   TLorentzVector BsMom(0,0,0,0);
   TVector3 OWNPV(0,0,0), ENDVX(0,0,0);
   double wt(0.0), truewt(0.0), time(0.0), dt(0.0), truetime(0.0);

   ftree.Branch("Bsmass" , &lab0_MM);
   ftree.Branch("BsMom"  , &BsMom);
   ftree.Branch("hID"    , &lab1_TRUEID);
   ftree.Branch("time"   , &time);
   ftree.Branch("dt"     , &dt);
   ftree.Branch("tchi2"  , &lab0_TAUCHI2);
   ftree.Branch("truetime", &truetime);
   ftree.Branch("wt"     , &wt);
   ftree.Branch("truewt" , &truewt);
   ftree.Branch("oscil"  , &lab0_OSCIL);
   ftree.Branch("OWNPV"  , &OWNPV);
   ftree.Branch("ENDVX"  , &ENDVX);

   ftree.Branch("HLT1TrackAllL0TOS", &lab0Hlt1TrackAllL0Decision_TOS);
   ftree.Branch("HLT2Topo4BodyTOS" , &lab0Hlt2Topo4BodyBBDTDecision_TOS);
   ftree.Branch("HLT2Topo3BodyTOS" , &lab0Hlt2Topo3BodyBBDTDecision_TOS);
   ftree.Branch("HLT2Topo2BodyTOS" , &lab0Hlt2Topo2BodyBBDTDecision_TOS);
   ftree.Branch("HLT2TopoIncPhiTOS", &lab0Hlt2IncPhiDecision_TOS);

   unsigned long rdskcount(0), rdspicount(0);
   unsigned long dskcount(0), dspicount(0);

   Long64_t nbytes = 0, nb = 0;
   // for (Long64_t jentry=0; jentry<nentries;jentry+=10) // for testing
   for (Long64_t jentry=0; jentry<nentries;jentry++)
     {
       Long64_t ientry = LoadTree(jentry);
       if (ientry < 0) break;
       nb = fChain->GetEntry(jentry);   nbytes += nb;

       if (std::abs(lab1_TRUEID) == 321) rdskcount++;
       else if (std::abs(lab1_TRUEID) == 211) rdspicount++;

       // if (( UnbiasedSelection() == false ) or ( lab1_PIDK < 5 )) continue;
       if (CommonSelection(DsK) == false) continue;
       if (OfflineSelection(DsK) == false) continue;

       if (lab0_TAUERR <= 0 or lab0_TAUERR >= 0.0002 or
	   lab0_TAUERR != lab0_TAUERR) continue;

       time     = lab0_TAU * 1E3;
       dt       = lab0_TAUERR * 1E3;
       truetime = lab0_TRUETAU * 1E3;
       wt       = TMath::Exp(lab0_TAU*1e3/1.472);
       truewt   = TMath::Exp(lab0_TRUETAU*1e3/1.472);
       BsMom.SetPxPyPzE(lab0_PX, lab0_PY, lab0_PZ, lab0_MM);
       OWNPV.SetXYZ(lab0_OWNPV_X, lab0_OWNPV_Y, lab0_OWNPV_Z);
       ENDVX.SetXYZ(lab0_ENDVERTEX_X, lab0_ENDVERTEX_Y, lab0_ENDVERTEX_Z);
       ftree.Fill();
       felist.Enter(jentry, fChain);
       if (std::abs(lab1_TRUEID) == 321) dskcount++;
       else if (std::abs(lab1_TRUEID) == 211) dspicount++;
     }

   std::cout << "Cutflow: ";
   for (std::map<unsigned int,long>::const_iterator itr = _cutflow.begin();
	itr != _cutflow.end(); ++itr) {
     std::cout << "(" << itr->first << "," << itr->second << "), ";
   }
   std::cout << std::endl;

   std::cout << "Entry list: " << felist.GetN() << " DsK: " << dskcount
	     << " DsPi: " << dspicount << std::endl;
   std::cout << "Rejected DsK: " << rdskcount - dskcount
	     << " DsPi: " << rdspicount - dspicount << std::endl;
   std::cout << "lifetime::Loop(TTree&,TEntryList&): Read " << nbytes << " bytes." << std::endl;
}


bool lifetime::OfflineSelection(bool DsK)
{
  if (not (lab1_P > 0.0 and lab1_P < 1.0E11)) {
    _cutflow[0]++;
    return false;
  }
  if (not (BDTGResponse_1 > 0.5)) {
    _cutflow[1]++;
    return false;
  }
  if (not (lab2_FDCHI2_ORIVX > 2.0)) {
    _cutflow[2]++;
    return false;
  }
  if (not ((DsK and lab1_M > 200.0) or
	   ((not DsK) and lab1_M < 200.0))) {
    _cutflow[3]++;
    return false;
  }
  if (not (lab3_M < 200.0 and lab4_M > 200.0 and lab5_M > 200.0)) {
    _cutflow[4]++;
    return false;
  }
  if (not (lab4_PIDK > 5.0 and lab3_PIDK < 0.0 and lab5_PIDK > 5.0)) {
    _cutflow[5]++;
    return false;
  }
  if (not (5000.0 < lab0_MassFitConsD_M[0] and lab0_MassFitConsD_M[0] < 5500.0)) {
    _cutflow[6]++;
    return false;
  }
  if (not (1948.0 < lab2_MM and lab2_MM < 1990.0)) {
    _cutflow[7]++;
    return false;
  }
  if (not (lab0_BKGCAT < 60)) {
    _cutflow[8]++;
    return false;
  }
  if (not (lab2_BKGCAT < 30. or std::abs(lab2_BKGCAT -50.) < 1e-4)) {
    _cutflow[9]++;
    return false;
  }
  if (not ((DsK and lab1_PIDK > 10.0) or 
	   ((not DsK) and lab1_PIDK < 10.0))) {
    _cutflow[10]++;
    return false;
  }
  return true;
}


bool lifetime::CommonSelection(bool DsK)
{
  // selecting only "true" Bs2DsK and Bs2Dsπ events
  if (lab0_TRUEID*lab0_TRUEID == 531*531 and
      lab2_TRUEID*lab2_TRUEID == 431*431 and
      lab3_TRUEID*lab3_TRUEID == 211*211 and
      lab4_TRUEID*lab4_TRUEID == 321*321 and
      lab5_TRUEID*lab5_TRUEID == 321*321 and
      ((DsK and lab1_TRUEID*lab1_TRUEID == 321*321) or
       ((not DsK) and lab1_TRUEID*lab1_TRUEID == 211*211)))
    return true;
  else return false;
}


bool lifetime::UnbiasedSelection()
{
  if (lab1_TRACK_PCHI2 < 4. and lab1_P > 5000. and lab1_PT > 500. and
      lab1_MINIPCHI2 > 0. and 1918. < lab2_MM and lab2_MM < 2018. and // 100 MeV Ds mass window
      lab0_ENDVERTEX_CHI2 < 9. and lab0_IPCHI2_OWNPV < 250. and
      -1000. < lab0_FDCHI2_OWNPV and -1. < lab0_DIRA_OWNPV and
      5116. < lab0_MM and lab0_MM < 5616.) return true; // 500 MeV Bs mass window
  else return false;
}
