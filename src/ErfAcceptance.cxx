/**
 * @file   ErfAcceptance.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Fri May 18 04:01:57 2012
 * 
 * @brief  This class implements an error function acceptance.
 *
 */

#include "Riostream.h"

#include "ErfAcceptance.hxx"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include <cmath>
#include "TMath.h"


// ClassImp(ErfAcceptance)


ErfAcceptance::ErfAcceptance(const char *name, const char *title,
			     RooAbsReal& turnon, RooAbsReal& time,
			     RooAbsReal& offset) :
  RooAbsReal(name, title),
  _turnon("turnon", "turnon", this, turnon),
  _time("time", "time", this, time),
  _offset("offset", "offset", this, offset)
{
}


ErfAcceptance::ErfAcceptance(const ErfAcceptance& other, const char* name) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset)
{
}


ErfAcceptance::~ErfAcceptance() {}


TObject* ErfAcceptance::clone(const char* newname) const
{
  return new ErfAcceptance(*this, newname);
}


Double_t ErfAcceptance::evaluate() const
{
  Double_t turnon((Double_t)_turnon), time((Double_t)_time),
    offset((Double_t)_offset);

  if (time > 2E-4) {
    Double_t error_fn(erf((time - offset)/turnon));
    return (0.5*error_fn + 0.5);
  }

  return 0.;
}


Int_t ErfAcceptance::getAnalyticalIntegral(RooArgSet& allVars,
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


Double_t ErfAcceptance::analyticalIntegral(Int_t code,
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
