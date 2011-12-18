#ifndef __OANGLEPID_HXX
#define __OANGLEPID_HXX

#include <string>

#include <TH2D.h>

using namespace std;

class oanglePID {
public:

  /**
   * Constructor for kinematic variable based PID
   *
   * @param wt Relative weight
   * @param dsk Pointer to DsK histogram
   * @param dspi Pointer to Dspi histogram
   */
  oanglePID(double wt, TH2D *dsk, TH2D *dspi) : weight(wt), hDsK(dsk), hDspi(dspi) {}
  oanglePID(double wt, string sDsK="hDsK", string sDspi="hDspi", string fname="histos.root");
  ~oanglePID() {}

  /**
   * Return PID delta log likelihood based on kinematics variables for
   * DsK and Dspi events
   *
   * @param Bsmass Bs mass
   * @param oangleCosine Cosine of the opening angle
   *
   * @return delta log likelihood
   */
  double GetoangleDLL(double Bsmass, double oangleCosine);

private:

  double weight;                /**< Relative weight between DsK and Dspi probabilities */
  TH2D  *hDsK;                  /**< Normalised 2-D DsK histogram */
  TH2D  *hDspi;                 /**< Normalised 2-D Dspi histogram */

};

#endif	// __OANGLEPID_HXX
