#include <TMath.h>
#include <TFile.h>

#include "oanglePID.hxx"


oanglePID::oanglePID(double wt, string sDsK, string sDspi, string fname)
  : weight(wt)
{
  TFile fhisto( fname.c_str(), "read"); // FIXME: Does this have to be a member?

  hDsK  = (TH2D*) fhisto.Get(sDsK.c_str());
  hDspi = (TH2D*) fhisto.Get(sDspi.c_str());
}


double oanglePID::GetoangleDLL(double Bsmass, double oangleCosine)
{
  int gBinDsK(0), gBinDspi(0);
  double pDsK(0.), pDspi(0.), deltaLogL(0.);

  gBinDsK   = hDsK ->FindBin( Bsmass, oangleCosine);
  gBinDspi  = hDspi->FindBin( Bsmass, oangleCosine);
  pDsK      = weight     * hDsK ->GetBinContent(gBinDsK);
  pDspi     = (1-weight) * hDspi->GetBinContent(gBinDspi);
  deltaLogL = TMath::Log(pDsK / pDspi);
  return deltaLogL;
}
