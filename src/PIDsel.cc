#include <iostream>
#include <vector>

#include <TTree.h>
#include <TStyle.h>
#include <TFile.h>
#include <TH2D.h>
#include <TCanvas.h>
#include <TPad.h>
#include <TGraph.h>
#include <TLegend.h>
#include <TArrow.h>

#include "utils.hh"
#include "readMCTree.hxx"
#include "readDataTree.hxx"
#include "PIDsel.hh"

// DsK / Dsπ = 0.067 or 0.081
// DsK = 403, Dsπ = 6046

using namespace std;


// deprecated retain temporarily for record
int PIDsel()
{
  cout << "PIDsel(): This method is deprecated, quitting." << endl;
  return 0;

  Style::setStyle();

  TFile *fhisto = new TFile( "templates.root", "read");

  TH2D *hDsK  = dynamic_cast<TH2D*> (fhisto->Get("hDsK" )->Clone());
  TH2D *hDspi = dynamic_cast<TH2D*> (fhisto->Get("hDspi")->Clone());

  oanglePID kPID(hDsK, hDspi);

  // make and read chain
  TChain K_hypo("K_hypo");
  K_hypo.Add("../../ntuples/data/FitTuple_BsDs1Pi_K_*.root/MyOffSelTree");
  readDataTree ch_K (&K_hypo);

  // TChain pi_hypo("pi_hypo");
  // pi_hypo.Add("../../ntuples/data/FitTuple_BsDs1Pi_Pi_*.root/MyOffSelTree");
  // readDataTree ch_pi(&pi_hypo);

  // invariant mass
  TH1D hdataBsmK ("hdataBsmK", "B_{s} mass with #it{K} mass hypothesis", 75, 4500, 6000);
  // TH1D hdataBsmpi  ("hdataBsmpi",  "B_{s} mass with #it{#pi} mass hypothesis",   75, 4500, 6000);

  hdataBsmK.SetLineColor(kAzure);
  hdataBsmK.SetXTitle("Mass[MeV]");
  hdataBsmK.SetYTitle("Events");
  hdataBsmK.Sumw2();

  // opening angle
  TH2D hdataDsK ("hdataDsK", "#it{B_{s}} (#it{D_{s}#pi} hypothesis) vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
		 75, 4500, 6000, 20, -1, 1);
  // TH2D hdataDspi ("hdataDspi", "#it{B_{s}} (#it{D_{s}K} hypothesis) vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
  // 		  75, 4500, 6000, 20, -1, 1);

  hdataDsK.SetYTitle("Cosine of the opening angle[deg]");
  hdataDsK.SetXTitle("Mass[MeV]");
  hdataDsK.Sumw2();

  // ch_K.Loop(kPID, hdataBsmK, hdataDsK);

  hdataBsmK.Draw("hist");
  gPad->Print("Bs-mass-data-new-PID-K.png");
  gPad->Clear();
  hdataDsK.Draw("COLZ");
  gPad->Print("Bs-opening-angle-data-new-PID-K.png");

  hdataBsmK.Print("base");
  hdataDsK .Print("base");

  return 0;
}


int PIDperf(TString opt)
{
  Style::setStyle();
  gStyle->SetPadLeftMargin(2);
  gStyle->SetTitleYOffset(1.4);
  opt.ToLower();

  TString format;
  bool doPrint( Parsers::PrintOpts( opt, format ) );

  oanglePID oPID(init_oanglePID());
  double mass(0), coso(0);
  float pidK(0);
  int hID(0);

  TFile *file = new TFile("treedump.root", "read");
  TTree *ftree = dynamic_cast<TTree*> (file->Get("noangle"));
  ftree->SetBranchAddress("Bsmass", &mass);
  ftree->SetBranchAddress("cosangle", &coso);
  ftree->SetBranchAddress("hID", &hID);
  ftree->SetBranchAddress("hPIDK", &pidK);
  int entries(ftree->GetEntries());

  // histograms before RICH PID
  TH1D *DsKDLL  = new TH1D ("DsKDLL" , "DsK DLL before RICH PID"     , 1000, -50, 50);
  TH1D *DspiDLL = new TH1D ("DspiDLL", "Ds#pi DLL before RICH PID"   , 1000, -50, 50);
  TH1D *TotDLL  = new TH1D ("TotDLL" , "Combined DLL before RICH PID", 1000, -50, 50);

  DsKDLL ->SetLineColor(kGreen);
  DspiDLL->SetLineColor(kRed);
  TotDLL ->SetLineColor(kAzure);

  // histograms with RICH PID
  TH1D *DsKDLL2  = new TH1D ("DsKDLL2" , "DsK DLL after RICH PID"     , 1000, -50, 50);
  TH1D *DspiDLL2 = new TH1D ("DspiDLL2", "Ds#pi DLL after RICH PID"   , 1000, -50, 50);
  TH1D *TotDLL2  = new TH1D ("TotDLL2" , "Combined DLL after RICH PID", 1000, -50, 50);

  DsKDLL2 ->SetLineColor(kGreen);
  DspiDLL2->SetLineColor(kRed);
  TotDLL2 ->SetLineColor(kAzure);

  // RICH PID histograms
  TH1D *DsKDLL3  = new TH1D ("DsKDLL3" , "DsKDLL3" , 1000, -50, 50);
  TH1D *DspiDLL3 = new TH1D ("DspiDLL3", "DspiDLL3", 1000, -50, 50);
  TH1D *TotDLL3  = new TH1D ("TotDLL3" , "TotDLL3" , 1000, -50, 50);

  DsKDLL3 ->SetLineColor(kGreen);
  DspiDLL3->SetLineColor(kRed);
  TotDLL3 ->SetLineColor(kAzure);

  for (int i(0); i < entries; ++i) {
    ftree->GetEntry(i);
    // if ( oPID.GetoangleDLL(i,j) == 0 ) continue;
    TotDLL->Fill(oPID.GetoangleDLL( mass, coso));
    TotDLL3->Fill(pidK);
    if (fabs(hID) == 321) {	// K
      DsKDLL ->Fill(oPID.GetoangleDLL( mass, coso));
      DsKDLL3->Fill(pidK);
    }
    if (fabs(hID) == 211) {	// pi
      DspiDLL ->Fill(oPID.GetoangleDLL( mass, coso));
      DspiDLL3->Fill(pidK);
    }
    // after RICH PID
    if (pidK > 5) {
      TotDLL2->Fill(oPID.GetoangleDLL( mass, coso));
      if (fabs(hID) == 321) DsKDLL2 ->Fill(oPID.GetoangleDLL( mass, coso));
      if (fabs(hID) == 211) DspiDLL2->Fill(oPID.GetoangleDLL( mass, coso));
    }
  }

  // plot DLLs
  if ( opt.Contains("dll") ) {
    // new PID DLLs
    TCanvas *canvas = new TCanvas("canvas", "", 1200, 600);
    canvas->Divide(3,2);

    canvas->cd(1);
    TotDLL ->Draw("hist");
    canvas->cd(2);
    DsKDLL ->Draw("hist");
    if (doPrint) gPad->Print(TString::Format("%s.%s", "kin-PID-DsK-no-RICH", format.Data()));
    canvas->cd(3);
    DspiDLL->Draw("hist");
    if (doPrint) gPad->Print(TString::Format("%s.%s", "kin-PID-Dspi-no-RICH", format.Data()));

    canvas->cd(4);
    TotDLL2 ->Draw("hist");
    canvas->cd(5);
    DsKDLL2 ->Draw("hist");
    if (doPrint) gPad->Print(TString::Format("%s.%s", "kin-PID-DsK-w-RICH", format.Data()));
    canvas->cd(6);
    DspiDLL2->Draw("hist");
    if (doPrint) gPad->Print(TString::Format("%s.%s", "kin-PID-Dspi-w-RICH", format.Data()));

    // canvas->cd(7);
    // TotDLL3 ->Draw("hist");
    // canvas->cd(8);
    // DsKDLL3 ->Draw("hist");
    // canvas->cd(9);
    // DspiDLL3->Draw("hist");
  }

  // fill and plot performance
  if ( opt.Contains("perf") ) {

    /**
     *  purity     = nDsKsel / (nDsKsel + nDspisel)
     *  efficiency = nDsKsel / nDsKall
     *
     */

    double nDsKsel(0), nDsKall(0), nDspisel(0),
      nDsKsel2(0), nDsKall2(0), nDspisel2(0),
      nDsKsel3(0), nDsKall3(0), nDspisel3(0);
    int tbins(TotDLL->GetNbinsX());
    const double scaleKPi(0.067);

    nDsKall  = DsKDLL ->Integral(0,DsKDLL ->GetNbinsX()+1);
    nDsKall2 = DsKDLL2->Integral(0,DsKDLL2->GetNbinsX()+1);
    nDsKall3 = DsKDLL3->Integral(0,DsKDLL3->GetNbinsX()+1);

    vector<double> eff, eff2, eff3, pur, pur2, pur3;

    for (int i(0); i < tbins+2; ++i) {
      nDsKsel  = DsKDLL ->Integral(i,tbins+1);
      nDspisel = DspiDLL->Integral(i,tbins+1);

      if (nDsKsel + nDspisel != 0) {
          eff.push_back(nDsKsel / nDsKall);
          pur.push_back(nDsKsel / (nDsKsel + scaleKPi * nDspisel));
      }

      nDsKsel2  = DsKDLL2 ->Integral(i,tbins+1);
      nDspisel2 = DspiDLL2->Integral(i,tbins+1);

      if (nDsKsel2 + nDspisel2 != 0) {
          eff2.push_back(nDsKsel2 / nDsKall2);
          pur2.push_back(nDsKsel2 / (nDsKsel2 + scaleKPi * nDspisel2));
      }

      nDsKsel3  = DsKDLL3 ->Integral(i,tbins+1);
      nDspisel3 = DspiDLL3->Integral(i,tbins+1);

      if (nDsKsel3 + nDspisel3 != 0) {
          eff3.push_back(nDsKsel3 / nDsKall3);
          pur3.push_back(nDsKsel3 / (nDsKsel3 + scaleKPi * nDspisel3));
      }
    }

    // RICH cut
    double RICHeff(0), RICHpur(0), RICHDsKsel(0), RICHDspisel(0);
    RICHDsKsel  = DsKDLL3 ->Integral( DsKDLL3 ->FindBin(5), tbins+1 );
    RICHDspisel = DspiDLL3->Integral( DspiDLL3->FindBin(5), tbins+1 );

    if (RICHDsKsel + RICHDspisel != 0) {
      RICHeff = RICHDsKsel /  nDsKall3;
      RICHpur = RICHDsKsel / (RICHDsKsel + scaleKPi * RICHDspisel);
    }

    TArrow *RICHcut = new TArrow(RICHeff-0.2, RICHpur, RICHeff, RICHpur, 0.03, "|>");
    RICHcut->SetLineWidth(2);
    RICHcut->SetAngle(40);
    RICHcut->SetLineColor(kRed);
    RICHcut->SetFillColor(kRed);

    TGraph *gr1 = new TGraph( eff.size(), &eff[0], &pur[0]);
    gr1->SetLineColor(kRed);

    TGraph *gr2 = new TGraph( eff2.size(), &eff2[0], &pur2[0]);
    gr2->SetLineColor(kAzure);
    gr2->SetTitle("Kinematic PID (mass vs opening angle) performance");
    gr2->GetXaxis()->SetTitle("#varepsilon (n^{sel}_{DsK} / n^{all}_{DsK})");
    gr2->GetYaxis()->SetTitle("p (n^{sel}_{DsK} / n^{sel}_{DsK} + n^{sel}_{Ds#pi})");

    TGraph *gr3 = new TGraph( eff3.size(), &eff3[0], &pur3[0]);
    gr3->SetLineColor(kGreen);

    TCanvas *canvas2 = new TCanvas("canvas2", "", 800, 600);
    canvas2->cd();
    // gr1->Draw("AC");
    gr2->Draw("AC");
    gr3->Draw("C");

    RICHcut->Draw();

    TLegend *leg = new TLegend( 0.2, 0.2, 0.6, 0.45);
    leg->SetFillColor(4000); // transparent
    leg->SetBorderSize(0);
    // leg->AddEntry( gr1, "Kin PID before RICH", "l");
    leg->AddEntry( gr2, "Kin PID after RICH", "l");
    leg->AddEntry( gr3, "RICH PID", "l");
    leg->Draw();
    if (doPrint) gPad->Print(TString::Format("%s.%s", "kin-PID-perf", format.Data()));
  }

  return 0;
}


oanglePID init_oanglePID()
{
  TFile *fhisto = new TFile( "templates.root", "read");

  TH2D *hDsK  = dynamic_cast<TH2D*> (fhisto->Get("hDsK" )->Clone());
  TH2D *hDspi = dynamic_cast<TH2D*> (fhisto->Get("hDspi")->Clone());

  return oanglePID(hDsK, hDspi);
}


int test_oanglePID()
{
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette

  TFile *fhisto = new TFile( "templates.root", "read");

  TH2D *hDsK  = dynamic_cast<TH2D*> (fhisto->Get("hDsK" )->Clone());
  TH2D *hDspi = dynamic_cast<TH2D*> (fhisto->Get("hDspi")->Clone());

  oanglePID test(hDsK, hDspi);

  TH2D *hweight = dynamic_cast<TH2D*> (hDsK->Clone());
  hweight->Reset("ICESM");

  // TH2D binning - 150, 4500, 6000, 25, -1, 1);
  int gbin(0);
  for (double mass(4505.); mass < 6000; mass+=10) {
    for (double cosine(-0.98); cosine < 1; cosine+=0.08) {
      gbin = hweight->FindBin(mass, cosine);
      hweight->SetBinContent(gbin, test.GetoangleDLL(mass, cosine));
      // cout << "bin: " << gbin;
      // cout << ", DLL: " << test.GetoangleDLL(mass, cosine) << endl;
    }
  }

  TCanvas c("c", "template compare", 1500, 400);
  c.Divide(3,1);

  c.cd(1);
  hDsK->Draw("COLZ");

  c.cd(2);
  hDspi->Draw("COLZ");

  c.cd(3);
  hweight->Draw("COLZ");

  c.Print("new-PID-test.png");
  // hweight->Divide(hDsK, hDspi, 0.1, 0.9);
  // hweight->Draw("surf");

  return 0;
}
