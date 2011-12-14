/**
 * @file   oangle.cc
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Wed Dec 14 01:25:40 2011
 *
 * @brief  Opening angle study utilities
 *
 *
 */

#include <string>
#include <iostream>
#include <string>

#include <TROOT.h>
#include <TStyle.h>
#include <TChain.h>
#include <TNtuple.h>
#include <TH2D.h>
#include <TLegend.h>
#include <TPad.h>

#include "oangle.hh"

#include "readDataTree.hxx"
#include "readMCTree.hxx"

using namespace std;

  // Manuel wrote:
  //
  // I think that would be useful to have. On MC, maybe you could make a plot
  // which shows how much you can gain in purity as a function of a suitable
  // cut in the (m, cos(theta*)) plane, relative to the signal selection we
  // already have. The optimal plot would be signal purity versus signal
  // efficiency, so you should get a curve which tells you how you can trade
  // increased purity for some (hopefully little) loss.


int oangle(bool doSelect)
{
  // make chain
  TChain MCChain("MCChain");
  TNtuple *noangle = NULL;

  string fileaccess((doSelect) ? "recreate" : "read");
  TFile dump("dump.root", fileaccess.c_str());

  if (doSelect) {
    MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
    readMCTree MCsample(&MCChain);

    // ntuple with mass, cos(oangle) and species from MC truth
    noangle = new TNtuple("noangle", "Opening angle", "mass:cos_oangle:hID");
    MCsample.Loop(*noangle);
    cout << noangle->GetEntries() << " entries filled!" << endl;
  } else {
    noangle = (TNtuple*) dump.Get("noangle");
    // bla->Scan("cos_oangle:mass", "abs(hID)==211");
  }

  oangleNtuple(*noangle);
  if (doSelect) noangle->SaveAs("dump.root");

  return 0;
}


int oangleNtuple(TNtuple &noangle)
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette
  gStyle->SetTitleOffset( 1.2, "xy");

  // cout << noangle.GetEntries() << " entries filled! Lets draw." << endl;
  // noangle.Scan("*", "abs(hID)==211");

  // invariant mass
  TH1D hBsM ("hBsM", "B_{s} mass", 150, 4500, 6000);

  hBsM.SetLineColor(kAzure);
  hBsM.SetXTitle("Mass[MeV]");
  hBsM.SetYTitle("Events");

  // noangle.Draw("mass>>hBsM", "abs(hID)==321", "hist"); // K
  noangle.Draw("mass>>hBsM", "1", "hist"); // K
  gPad->Print("Bs-mass-MC.png");

  // opening angle
  TH2D h2oangle ("h2oangle", "#it{B_{s}} mass vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
		 150, 4500, 6000, 25, -1, 1);
  h2oangle.SetYTitle("Cosine of the opening angle[deg]");
  h2oangle.SetXTitle("Mass[MeV]");

  gPad->Clear();
  noangle.Draw("cos_oangle:mass>>h2oangle", "abs(hID)==321", "COLZ"); // K
  // noangle.Draw("cos_oangle:mass>>h2oangle", "1", "COLZ"); // K
  gPad->Print("Bs-opening-angle-w-MC-K.png");

  gPad->Clear();
  h2oangle.Reset("ICESM");
  noangle.Draw("cos_oangle:mass>>h2oangle", "abs(hID)==211", "COLZ"); // pi
  gPad->Print("Bs-opening-angle-w-MC-pi.png");

  return 0;
}


int oangleHisto()
{
  // make chain
  TChain pi_hypo("pi_hypo");
  pi_hypo.Add("../../ntuples/data/FitTuple_BsDs1Pi_Pi_*.root/MyOffSelTree");

  TChain K_hypo("K_hypo");
  K_hypo.Add("../../ntuples/data/FitTuple_BsDs1Pi_K_*.root/MyOffSelTree");

  readDataTree ch_pi(&pi_hypo);
  readDataTree ch_K (&K_hypo);

  // invariant mass
  TH1D hBsM_Pi ("hBsM_Pi", "B_{s} mass with #it{#pi} mass hypothesis", 150, 4500, 6000);
  TH1D hBsM_K  ("hBsM_K",  "B_{s} mass with #it{K} mass hypothesis",   150, 4500, 6000);

  hBsM_Pi.SetLineColor(kAzure);
  hBsM_K .SetLineColor(kRed);

  hBsM_Pi.SetXTitle("Mass[MeV]");
  hBsM_K .SetXTitle("Mass[MeV]");
  hBsM_Pi.SetYTitle("Events");
  hBsM_K .SetYTitle("Events");

  // opening angle
  TH2D h2oangle_Pi ("h2oangle_Pi", "#it{B_{s}} (#it{D_{s}#pi} hypothesis) vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
		    75, 4500, 6000, 20, -1, 1);
  TH2D h2oangle_K ("h2oangle_K", "#it{B_{s}} (#it{D_{s}K} hypothesis) vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
		   75, 4500, 6000, 20, -1, 1);

  h2oangle_Pi.SetYTitle("Cosine of the opening angle[deg]");
  h2oangle_K .SetYTitle("Cosine of the opening angle[deg]");
  h2oangle_Pi.SetXTitle("Mass[MeV]");
  h2oangle_K .SetXTitle("Mass[MeV]");

  ch_pi.Loop(hBsM_Pi, h2oangle_Pi);
  ch_K .Loop(hBsM_K , h2oangle_K);

  hBsM_Pi.Draw("hist");
  hBsM_K .Draw("hist same");

  TLegend leg( 0.2, 0.55, 0.5, 0.85);
  leg.SetFillColor(4000); // transparent
  leg.SetBorderSize(0);
  leg.SetHeader("#it{B_{s}} invariant mass");
  leg.AddEntry(&hBsM_Pi, "#it{D_{s}#pi} mass hypothesis", "l");
  leg.AddEntry(&hBsM_K,  "#it{D_{s}K} mass hypothesis",   "l");
  leg.Draw();

  gPad->Update();
  gPad->Print("Bs-mass-data.png");

  gPad->Clear();
  gStyle->SetOptTitle(1);
  h2oangle_Pi.Draw("COLZ");
  gPad->Print("Bs-opening-angle-pi-hypo.png");

  gPad->Clear();
  h2oangle_K.Draw("COLZ");
  gPad->Print("Bs-opening-angle-K-hypo.png");

  return 0;
}
