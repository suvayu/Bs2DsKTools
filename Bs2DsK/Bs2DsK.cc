#define Bs2DsK_cc
#include <cstdio>
#include <iostream>

#include "Bs2DsK.hh"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <TMath.h>

void Bs2DsK::Loop(TH1D &hBsM, TH2D &h2oangle)
{
//   In a ROOT session, you can do:
//      Root > .L Bs2DsK.C
//      Root > Bs2DsK t
//      Root > t.GetEntry(12); // Fill t data members with entry number 12
//      Root > t.Show();       // Show values of entry 12
//      Root > t.Show(16);     // Read and show values of entry 16
//      Root > t.Loop();       // Loop on all entries
//

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

   Double_t BsM(0.0), DsM(0.0);
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
       if ( lab1_PIDK[0] < 5 ) continue;
       if ( pPIDcut[0] != 1) continue;

       Pi3P.SetXYZM( lab3_PX[0], lab3_PY[0], lab3_PZ[0], lab3_M[0]);
       K4P .SetXYZM( lab4_PX[0], lab4_PY[0], lab4_PZ[0], lab4_M[0]);
       K5P .SetXYZM( lab5_PX[0], lab5_PY[0], lab5_PZ[0], lab5_M[0]);
       hP  .SetXYZM( lab1_PX[0], lab1_PY[0], lab1_PZ[0], lab1_M[0]);

       DsP = Pi3P + K4P + K5P;
       BsP = DsP + hP;

       DsM = DsP.M();
       BsM = BsP.M();

       hBsM.Fill(lab0_MM[0]);

       boost = - BsP.BoostVector();
       //       DsP.Boost(boost(0), boost(1), boost(2));
       hP .Boost(boost(0), boost(1), boost(2));

       h2oangle.Fill( TMath::Cos((hP.Angle(boost))), lab0_MM[0]);

       // printf("DsM: %.2f, %.2f, %.2f\n", DsM, lab2_MM[0], DsM - lab2_MM[0]);
       // printf("BsM: %.2f, %.2f, %.2f\n", BsM, lab0_MM[0], BsM - lab0_MM[0]);
     }

   // hBsM.Draw();
   // gPad->Print("BsMass.png");
   std::cout << "Read " << nbytes << " bytes." << std::endl;
}
