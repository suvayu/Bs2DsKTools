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
   TProfile hAccept  ("hAccept"   , "Acceptance function", 100, 0, 0.01);
   TH1D     hlifetime ("hlifetime"  , "hlifetime"           , 100, 0, 0.01);
   TH1D     hlifetimet("hlifetimet" , "hlifetime"           , 100, 0, 0.01);
   TH1D     hlifetimew("hlifetimew" , "hlifetime"           , 100, 0, 0.01);

   hAccept  .SetLineColor(kAzure);
   hlifetime .SetLineColor(kAzure);
   hlifetimet.SetLineColor(kRed);
   hlifetimew.SetLineColor(kGreen);

   hAccept  .SetXTitle("Bs lifetime in ns");
   hlifetime .SetXTitle("Bs lifetime in ns");
   hlifetimet.SetXTitle("Bs lifetime in ns");
   hlifetimew.SetXTitle("Bs lifetime in ns");

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

       if (( lab0Hlt2TopoOSTF4BodyDecision_TOS == false )
       // if (( lab0Hlt2TopoOSTF2BodyDecision_TOS == false )
       // if (( lab0Hlt2IncPhiDecision_TOS == false )
	   or ( CommonSelection() == false ) or ( lab1_PIDK < 5 )) {
	 // off so that you can apply later
	 hAccept.Fill(lab0_TRUETAU, 0);
	 continue;
       }
       // if ( pPIDcut != 1) continue; // not in TTree,  pPIDcut = (lab5_PIDK - lab5PIDp > 0)

       hAccept  .Fill(lab0_TRUETAU, 1);
       hlifetime .Fill(lab0_TAU);
       hlifetimet.Fill(lab0_TRUETAU);
       hlifetimew.Fill(lab0_TAU, TMath::Exp(lab0_TAU*1e3/1.472)); // time in ns / lifetime in ps
     }

   TCanvas *canvas = new TCanvas("canvas", "", 1200, 450);
   canvas->Divide(2,1);

   canvas->cd(1);
   hAccept   .DrawNormalized("hist");
   hlifetimew.DrawNormalized("hist same");
   canvas->cd(2);
   hlifetimet.Draw("hist");
   hlifetime .Draw("hist same");

   TLegend *leg = new TLegend( 0.6, 0.45, 0.9, 0.7);
   leg->SetFillColor(4000); // transparent
   leg->SetBorderSize(0);
   leg->SetHeader("Bs lifetime (#tau)");
   leg->AddEntry( &hlifetime , "Reconstructed", "l");
   leg->AddEntry( &hlifetimet, "MC true"      , "l");
   leg->Draw();
   canvas->Print(".png");

   // hAccept  .Print("all");
   hlifetime .Print("all");
   hlifetimew.Print("all");
   // hlifetimet.Print("all");

   delete canvas;
   cout << "lifetime::Loop(): Read " << nbytes << " bytes." << std::endl;
}


bool lifetime::CommonSelection()
{
  // selecting only "true" Bs2DsK and Bs2Dsπ events
  if ( fabs(lab0_TRUEID) == 531 and fabs(lab2_TRUEID) == 431 and
       ( fabs(lab1_TRUEID) == 321 or fabs(lab1_TRUEID) == 211 ) and
       ( 5000 < lab0_MM and lab0_MM < 5800 ) and // Bs mass
       ( 1944 < lab2_MM and lab2_MM < 1990 ) and // Ds mass
       ( lab1_P < 100000 )) return true;
  else return false;
}
