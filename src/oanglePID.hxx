#ifndef __OANGLEPID_HXX
#define __OANGLEPID_HXX

#include <string>
#include <limits>

#include <TMath.h>
#include <TH2D.h>

using namespace std;

class oanglePID {
public:

  /**
   * Constructor for kinematic variable based PID
   *
   * @param dsk Pointer to DsK histogram
   * @param dspi Pointer to Dspi histogram
   */
  oanglePID(TH2D* dsk, TH2D* dspi) : hDsK(dsk), hDspi(dspi) {}

  oanglePID(const oanglePID& other) : hDsK(other.hDsK), hDspi(other.hDspi) {}

  // // FIXME: Do not use, doesn't work. Histograms go out of scope and segfaults later
  // oanglePID(string sDsK="hDsK", string sDspi="hDspi", string fname="histos.root") {}

  ~oanglePID() {}

  oanglePID& operator=(const oanglePID& other) {
    if (&other == this) return *this;
    hDsK  = other.hDsK;
    hDspi = other.hDspi;
  }

  /**
   * Return PID delta log likelihood based on kinematics variables for
   * DsK and Dspi events.
   *
   * @param Bsmass Bs mass
   * @param oangleCosine Cosine of the opening angle
   *
   * @return delta log likelihood (DLL = ln[pDsK/pDspi])
   */
  double GetoangleDLL(double Bsmass, double oangleCosine) const {
    // same binning for DsK and Dspi
    return GetoangleDLL( hDsK->FindBin( Bsmass, oangleCosine) );
  }

  /** 
   * Return PID delta log likelihood based on kinematics variables for
   * DsK and Dspi events.
   *
   * @param gBin Global histogram bin number
   *
   * @return delta log likelihood (DLL = ln[pDsK/pDspi])
   */
  double GetoangleDLL(int gBin) const { // same binning for DsK and Dspi
    // normalise the bin content before getting the DLL
    double pDsK ((hDsK ->GetBinContent(gBin) + numeric_limits<double>::epsilon()));
    double pDspi((hDspi->GetBinContent(gBin) + numeric_limits<double>::epsilon()));
    return DLL( pDsK, pDspi );
  }

  /** 
   * Return delta log likelihood for given numerator and denominator.
   *
   * @param num numerator
   * @param denom denominator
   *
   * @return delta log likelihood (DLL = ln[pDsK/pDspi])
   */
  static double DLL(double num, double denom) { return TMath::Log(num/denom); }

  /** 
   * Print reference histograms.
   *
   * @param opt Print options for TH2::Print()
   */
  void   PrintHistos (const char* opt="") const {
    hDsK ->Print(opt);
    hDspi->Print(opt);
  }

private:

  TH2D  *hDsK;                  /**< Normalised 2-D DsK histogram */
  TH2D  *hDspi;                 /**< Normalised 2-D Dspi histogram */

};

#endif	// __OANGLEPID_HXX
