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
#include <TCutG.h>
#include <TPad.h>
#include <TCanvas.h>

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


int setStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette
  gStyle->SetTitleOffset( 1.2, "xy");
  return 0;
}


int oangle(bool doSelect)
{
  // make chain
  TChain MCChain("MCChain");
  // TNtuple *noangle = NULL;
  TTree *noangle = NULL;

  string fileaccess((doSelect) ? "recreate" : "read");
  TFile treedump("treedump.root", fileaccess.c_str());

  if (doSelect) {
    MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
    readMCTree MCsample(&MCChain);
    // noangle = oangleNtuple_get(MCsample);
    noangle = oangleTree_get(MCsample);
  } else {
    noangle = (TTree*) treedump.Get("noangle");
  }

  makeTemplates(*noangle);

  if (doSelect) {
    treedump.cd();
    noangle->Write();
  }

  return 0;
}


void oangleProject(TString opt)
{
  setStyle();
  opt.ToLower();

  bool doPrint(false);
  TString format;
  if ( opt.Contains("print") ) {
    doPrint = true;
    if ( opt.Contains("png") )          format = "png";
    else if ( opt.Contains("jpg") )     format = "jpg";
    else if ( opt.Contains("ps") )      format = "ps";
    else if ( opt.Contains("pdf") )     format = "pdf";
    else if ( opt.Contains("cscript") ) format = "C";
    else {
      cout << "Error oangleProject(): Bad print option! No recognised formats found.\n"
	   << "Warning oangleProject(): Skipping canvas printing." << endl;
      doPrint = false;
    }
  }

  TFile *fhisto = new TFile( "templates.root", "read");

  TH2D *hDsK  = dynamic_cast<TH2D*> (fhisto->Get("hDsK" )->Clone());
  TH2D *hDspi = dynamic_cast<TH2D*> (fhisto->Get("hDspi")->Clone());

  hDsK ->SetLineColor(kAzure);
  hDspi->SetLineColor(kRed);

  // project full range
  TH1D *hDsKcosoangle  = hDsK ->ProjectionY("hDsKcosoangle" );
  TH1D *hDspicosoangle = hDspi->ProjectionY("hDspicosoangle");

  hDsKcosoangle ->SetTitle("cos(#theta*) distrib for Bs mass range #in (5 GeV, 5.8 GeV)");
  hDspicosoangle->SetTitle("cos(#theta*) distrib for Bs mass range #in (5 GeV, 5.8 GeV)");

  TH1D *hDsKBsmass  = hDsK ->ProjectionX("hDsKBsmass" );
  TH1D *hDspiBsmass = hDspi->ProjectionX("hDspiBsmass");

  hDsKBsmass ->SetTitle("Bs mass distrib for entire cos(#theta*) range");
  hDspiBsmass->SetTitle("Bs mass distrib for entire cos(#theta*) range");

  // graphical cuts
  TCutG *topcutg = new TCutG("topcutg",4);
  topcutg->SetPoint(0, 5200, 0);
  topcutg->SetPoint(1, 5600, 0);
  topcutg->SetPoint(2, 5600, 1);
  topcutg->SetPoint(3, 5200, 1);

  TCutG *botcutg = new TCutG("botcutg",4);
  botcutg->SetPoint(0, 5200, -1);
  botcutg->SetPoint(1, 5600, -1);
  botcutg->SetPoint(2, 5600, 0);
  botcutg->SetPoint(3, 5200, 0);

  // project with cuts
  TH1D *hDsKcosoangle1  = hDsK ->ProjectionY("hDsKcosoangle1" ,0,-1,"[topcutg]");
  TH1D *hDspicosoangle1 = hDspi->ProjectionY("hDspicosoangle1",0,-1,"[topcutg]");

  hDsKcosoangle1 ->SetTitle("cos(#theta*) distrib for Bs mass range #in (5.2 GeV, 5.6 GeV)");
  hDspicosoangle1->SetTitle("cos(#theta*) distrib for Bs mass range #in (5.2 GeV, 5.6 GeV)");

  TH1D *hDsKcosoangle2  = hDsK ->ProjectionY("hDsKcosoangle2" ,0,-1,"[botcutg]");
  TH1D *hDspicosoangle2 = hDspi->ProjectionY("hDspicosoangle2",0,-1,"[botcutg]");

  hDsKcosoangle2 ->SetTitle("cos(#theta*) distrib for Bs mass range #in (5.2 GeV, 5.6 GeV)");
  hDspicosoangle2->SetTitle("cos(#theta*) distrib for Bs mass range #in (5.2 GeV, 5.6 GeV)");

  // plot w/o cuts
  TCanvas *canvas = new TCanvas("canvas", "", 1200, 800);
  canvas->Divide(2,2);

  canvas->cd(1);
  hDsKcosoangle ->Draw("hist");
  hDspicosoangle->Draw("hist same");

  TLegend *oleg = new TLegend( 0.4, 0.2, 0.7, 0.35);
  oleg->SetFillColor(4000); // transparent
  oleg->SetBorderSize(0);
  oleg->AddEntry( hDsKcosoangle,  "DsK - correct hypo", "l");
  oleg->AddEntry( hDspicosoangle, "Ds#pi - wrong hypo", "l");
  oleg->Draw();
  if (doPrint) gPad->Print(TString::Format("%s.%s", "oangle-projn", format.Data()));

  canvas->cd(2);
  hDsKBsmass ->Draw("hist");
  hDspiBsmass->Draw("hist same");

  TLegend *mleg = new TLegend( 0.2, 0.45, 0.5, 0.6);
  mleg->SetFillColor(4000); // transparent
  mleg->SetBorderSize(0);
  mleg->AddEntry( hDsKBsmass,  "DsK - correct hypo", "l");
  mleg->AddEntry( hDspiBsmass, "Ds#pi - wrong hypo", "l");
  mleg->Draw();
  if (doPrint) gPad->Print(TString::Format("%s.%s", "Bs-mass-projn", format.Data()));

  // plot with cuts
  canvas->cd(3);
  hDsKcosoangle1 ->Draw("hist");
  hDspicosoangle1->Draw("hist same");

  TLegend *oleg1 = new TLegend( 0.2, 0.2, 0.4, 0.35);
  oleg1->SetFillColor(4000); // transparent
  oleg1->SetBorderSize(0);
  oleg1->AddEntry( hDsKcosoangle1,  "DsK",   "l");
  oleg1->AddEntry( hDspicosoangle1, "Ds#pi", "l");
  oleg1->Draw();

  canvas->cd(4);
  hDsKcosoangle2 ->Draw("hist");
  hDspicosoangle2->Draw("hist same");

  TLegend *oleg2 = new TLegend( 0.6, 0.2, 0.8, 0.35);
  oleg2->SetFillColor(4000); // transparent
  oleg2->SetBorderSize(0);
  oleg2->AddEntry( hDsKcosoangle2,  "DsK",   "l");
  oleg2->AddEntry( hDspicosoangle2, "Ds#pi", "l");
  oleg2->Draw();

  return;
}


TTree* oangleTree_get(readTree &sample)
{
  TTree *ftree = new TTree("noangle", "dump tree with opening angle");
  sample.Loop(*ftree);
  cout << ftree->GetEntries() << " entries filled!" << endl;
  return ftree;
}


TNtuple* oangleNtuple_get(readTree &sample)
{
  // ntuple with mass, cos(oangle) and species from MC truth
  TNtuple *ntpoangle = new TNtuple("noangle", "Opening angle", "mass:cos_oangle:hID");
  sample.Loop(*ntpoangle);
  cout << ntpoangle->GetEntries() << " entries filled!" << endl;
  return ntpoangle;
}


int makeTemplates(TTree &noangle)
{
  setStyle();
  // noangle.Scan("*", "abs(hID)==211");

  TFile fhisto("templates.root", "recreate");
  fhisto.cd();

  // // invariant mass
  // TH1D hBsM ("hBsM", "B_{s} mass", 150, 4500, 6000);
  // hBsM.SetLineColor(kAzure);
  // hBsM.SetXTitle("Mass[MeV]");
  // hBsM.SetYTitle("Events");

  // // noangle.Draw("mass>>hBsM", "abs(hID)==321", "hist"); // K
  // noangle.Draw("mass>>hBsM", "1", "hist"); // K
  // hBsM.Write();
  // gPad->Print("Bs-mass-MC.png");

  // opening angle
  TH2D hDsK ("hDsK", "#it{B_{s}} mass vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
	     150, 4500, 6000, 25, -1, 1);
  hDsK.SetYTitle("Cosine of the opening angle[deg]");
  hDsK.SetXTitle("Mass[MeV]");
  hDsK.Sumw2();

  TH2D hDspi ("hDspi", "#it{B_{s}} mass vs #it{#vec{#beta}} #angle #it{h} in #it{B_{s}} rest frame",
	      150, 4500, 6000, 25, -1, 1);
  hDspi.SetYTitle("Cosine of the opening angle[deg]");
  hDspi.SetXTitle("Mass[MeV]");
  hDspi.Sumw2();

  // gPad->Clear(); // uncomment when also plotting invariant mass
  noangle.Draw("cosangle:Bsmass>>hDsK", "abs(hID)==321", "COLZ"); // K
  gPad->Print("Bs-opening-angle-w-MC-K.png");
  hDsK.Scale(1./hDsK.Integral());
  hDsK.Draw("COLZ");
  hDsK.Write();

  gPad->Clear();
  noangle.Draw("cosangle:Bsmass>>hDspi", "abs(hID)==211", "COLZ"); // pi
  gPad->Print("Bs-opening-angle-w-MC-pi.png");
  hDspi.Scale(1./hDspi.Integral());
  hDspi.Draw("COLZ");
  hDspi.Write();

  fhisto.Close();
  return 0;
}


// deprecated retain temporarily for record
int oangleHisto()
{
  cout << "oangleHisto(): This method is deprecated, quitting." << endl;
  return 0;

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

  // ch_pi.Loop(hBsM_Pi, h2oangle_Pi);
  // ch_K .Loop(hBsM_K , h2oangle_K);

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


int test_oangle()
{
  // make chain
  TChain MCChain("MCChain");
  MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
  readMCTree MCsample(&MCChain);
  oangleNtuple_get(MCsample);
  return 0;
}
