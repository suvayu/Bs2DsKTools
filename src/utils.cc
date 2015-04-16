#include "utils.hh"


TStyle* setStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette
  gStyle->SetTitleOffset( 1.2, "xy");
  gStyle->SetCanvasPreferGL(true);
  return gStyle;
}


void rescale(TH1 *h, Double_t factor)
{
  // change X scale
  Double_t xmin = h->GetXaxis()->GetXmin();
  Double_t xmax = h->GetXaxis()->GetXmax();
  h->GetXaxis()->SetLimits(xmin*factor,xmax*factor);
  return;
}
