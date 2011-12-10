#include <string>

using namespace std;

int plot_MC(TNtuple &noangle)
{
  gStyle->SetOptStat(0);
  // gStyle->SetOptTitle(0);
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

  // Manuel wrote:
  //
  // I think that would be useful to have. On MC, maybe you could make a plot
  // which shows how much you can gain in purity as a function of a suitable
  // cut in the (m, cos(theta*)) plane, relative to the signal selection we
  // already have. The optimal plot would be signal purity versus signal
  // efficiency, so you should get a curve which tells you how you can trade
  // increased purity for some (hopefully little) loss.
