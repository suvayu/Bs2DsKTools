/**
 * @file   PowLawAcceptance.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Thu May 17 21:46:42 2012
 * 
 * @brief  This class implements a power law acceptance function.
 *
 */

#include "Riostream.h"

#include "PowLawAcceptance.hxx"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include <cmath>
#include "TMath.h"


// ClassImp(PowLawAcceptance)


PowLawAcceptance::PowLawAcceptance(const char *name, const char *title,
				   RooAbsReal& turnon, RooAbsReal& time,
				   RooAbsReal& offset, RooAbsReal& exponent) :
  RooAbsReal(name, title),
  _turnon("turnon", "turnon", this, turnon),
  _time("time", "time", this, time),
  _offset("offset", "offset", this, offset),
  _exponent("exponent", "exponent", this, exponent)
{
}


PowLawAcceptance::PowLawAcceptance(const PowLawAcceptance& other, const char* name) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset),
  _exponent("exponent", this, other._exponent)
{
}


PowLawAcceptance::~PowLawAcceptance() {}


TObject* PowLawAcceptance::clone(const char* newname) const
{
  return new PowLawAcceptance(*this, newname);
}


Double_t PowLawAcceptance::evaluate() const
{
  Double_t turnon((Double_t)_turnon), time((Double_t)_time),
    offset((Double_t)_offset), exponent((Double_t)_exponent);

  if ((time - offset > -0.) and time > 2E-4) {
    Double_t denom(1. + pow(turnon*(time - offset), exponent));
    return (1. - 1./denom);
  }

  return 0.;
}


/* // disable analytical integral
Int_t PowLawAcceptance::getAnalyticalIntegral(RooArgSet& allVars,
					      RooArgSet& analVars,
					      const char* rangeName) const
{
  // LIST HERE OVER WHICH VARIABLES ANALYTICAL INTEGRATION IS
  // SUPPORTED, ASSIGN A NUMERIC CODE FOR EACH SUPPORTED (SET OF)
  // PARAMETERS THE EXAMPLE BELOW ASSIGNS CODE 1 TO INTEGRATION OVER
  // VARIABLE X YOU CAN ALSO IMPLEMENT MORE THAN ONE ANALYTICAL
  // INTEGRAL BY REPEATING THE matchArgs EXPRESSION MULTIPLE TIMES

  // if (matchArgs(allVars,analVars,x)) return 1;
  return 0;
}


Double_t PowLawAcceptance::analyticalIntegral(Int_t code,
					      const char* rangeName) const
{
  // RETURN ANALYTICAL INTEGRAL DEFINED BY RETURN CODE ASSIGNED BY
  // getAnalyticalIntegral THE MEMBER FUNCTION x.min(rangeName) AND
  // x.max(rangeName) WILL RETURN THE INTEGRATION BOUNDARIES FOR EACH
  // OBSERVABLE x

  // assert(code==1);
  // return (x.max(rangeName)-x.min(rangeName));
  return 0;
}
*/
