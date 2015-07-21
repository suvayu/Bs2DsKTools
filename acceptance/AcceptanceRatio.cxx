/**
 * @file   AcceptanceRatio.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Thu Nov 30 12:46:42 2012
 *
 * @brief  This class implements acceptance ratio function.
 *
 */

#include <cmath>

#include <TMath.h>
#include <Riostream.h>

#include <RooAbsReal.h>
#include <RooAbsCategory.h>

#include "AcceptanceRatio.hxx"


/**
 * Default constructor, used during ROOT I/O.  Ensures objects are
 * consistent when reading instances of older version of the class.
 *
 */
AcceptanceRatio::AcceptanceRatio()
{
}


AcceptanceRatio::AcceptanceRatio(const char *name, const char *title,
				 RooAbsReal& time, RooAbsReal& turnon,
				 RooAbsReal& offset, RooAbsReal& beta) :
  RooAbsReal(name, title),
  _time("time", "time", this, time),
  _turnon("turnon", "turnon", this, turnon),
  _offset("offset", "offset", this, offset),
  _beta("beta", "beta", this, beta)
{
}


AcceptanceRatio::AcceptanceRatio(const AcceptanceRatio& other,
				 const char* name) :
  RooAbsReal(other, name),
  _time("time", this, other._time),
  _turnon("turnon", this, other._turnon),
  _offset("offset", this, other._offset),
  _beta("beta", this, other._beta)
{
}


AcceptanceRatio::~AcceptanceRatio() {}


TObject* AcceptanceRatio::clone(const char* newname) const
{
  return new AcceptanceRatio(*this, newname);
}


AcceptanceRatio& AcceptanceRatio::operator=(const AcceptanceRatio& other)
{
  if (&other == this)
    return *this;

  RooAbsReal::operator=(other);
  _time = RooRealProxy("time", this, other._time);
  _turnon = RooRealProxy("turnon", this, other._turnon);
  _offset = RooRealProxy("offset", this, other._offset);
  _beta = RooRealProxy("beta", this, other._beta);

  return *this;
}


Double_t AcceptanceRatio::evaluate() const
{
  Double_t time((Double_t)_time), turnon((Double_t)_turnon),
    offset((Double_t)_offset), beta((Double_t)_beta);

  if (time < 0.2) return 0.;	// selection in stripping
  if (time - offset < 0.) return 0.; // exponent should be +ve
  if (beta*time > 1.0) return 0.0; // 1-βt > 0
  Double_t exponential = std::exp(-1.0 * turnon * (time - offset));

  if (1.0 <= exponential) {
    return 0.0;
  } else {
    return ((1.0 - exponential) * (1.0 - beta*time));
  }
}
