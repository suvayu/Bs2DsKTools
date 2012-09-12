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

#include <gsl/gsl_sf_hyperg.h>


/**
 * Static data member for acceptance with no correction
 *
 */
RooConstVar PowLawAcceptance::_one(
    "PowLawAcceptance::_one", "PowLawAcceptance::_one", 1.0);


/**
 * Default constructor, used during ROOT I/O.  Ensures objects are
 * consistent when reading instances of older version of the class.
 *
 */
PowLawAcceptance::PowLawAcceptance()
{
}


PowLawAcceptance::PowLawAcceptance(const char *name, const char *title,
				   RooAbsReal& turnon, RooAbsReal& time,
				   RooAbsReal& offset, RooAbsReal& exponent,
				   RooAbsReal& beta, RooAbsReal* correction) :
  RooAbsReal(name, title),
  _turnon("turnon", "turnon", this, turnon),
  _time("time", "time", this, time),
  _offset("offset", "offset", this, offset),
  _exponent("exponent", "exponent", this, exponent),
  _beta("beta", "beta", this, beta),
  _correction("correction", "correction", this,
	      correction ? *correction : _one)
{
}


PowLawAcceptance::PowLawAcceptance(const PowLawAcceptance& other,
				   const char* name) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset),
  _exponent("exponent", this, other._exponent),
  _beta("beta", this, other._beta),
  _correction("correction", this, other._correction)
{
}


/**
 * This version of the copy constructor allows you to change the
 * acceptance correction to something new or back to unity.
 *
 * @param other PowLawAcceptance instance copied from
 * @param name New name
 * @param correction New correction factor
 */
PowLawAcceptance::PowLawAcceptance(const PowLawAcceptance& other,
				   const char* name,
				   RooAbsReal* correction) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset),
  _exponent("exponent", this, other._exponent),
  _beta("beta", this, other._beta),
  _correction("correction", "correction", this,
	      correction ? *correction : _one)
{
}


PowLawAcceptance::~PowLawAcceptance() {}


TObject* PowLawAcceptance::clone(const char* newname) const
{
  return new PowLawAcceptance(*this, newname);
}


PowLawAcceptance& PowLawAcceptance::operator=(const PowLawAcceptance& other)
{
  if (&other == this)
    return *this;

  RooAbsReal::operator=(other);
  _turnon = RooRealProxy("turnon", this, other._turnon);
  _time = RooRealProxy("time", this, other._time);
  _offset = RooRealProxy("offset", this, other._offset);
  _exponent = RooRealProxy("exponent", this, other._exponent);
  _beta = RooRealProxy("beta", this, other._beta);
  _correction = RooRealProxy("correction", this, other._correction);

  return *this;
}


Double_t PowLawAcceptance::evaluate() const
{
  Double_t turnon((Double_t)_turnon), time((Double_t)_time),
    offset((Double_t)_offset), exponent((Double_t)_exponent),
    beta((Double_t)_beta), ratio(1.0);

  // check if underlying data type is valid
  if (_correction.absArg()) ratio = (Double_t)_correction;

  if (time < 0.2) return 0.;
  if (beta < -0.0) return 0.0;
  if (beta*time > 1.0) return 0.0;
  Double_t expnoff = std::pow(turnon*time, exponent) - offset;

  if (expnoff <= 0.0) {
    return 0.0;
  } else {
    Double_t denominator(1.0 + expnoff);
    return (ratio * (1.0 - 1.0/denominator) * (1.0 - beta*time));
  }
}


Int_t PowLawAcceptance::getAnalyticalIntegral(RooArgSet& allVars,
					      RooArgSet& analVars,
					      const char* rangeName) const
{
  // List here over which variables analytical integration is
  // supported, assign a numeric code for each supported (set of)
  // parameters the example below assigns code 1 to integration over
  // variable x you can also implement more than one analytical
  // integral by repeating the matchArgs(..) expression multiple times

  if (matchArgs(allVars, analVars, _time)) return 1;
  return 0;
}


Double_t PowLawAcceptance::analyticalIntegral(Int_t code,
					      const char* rangeName) const
{
  // return analytical integral defined by return code assigned by
  // getAnalyticalIntegral(..) the member function x.min(rangename)
  // and x.max(rangename) will return the integration boundaries for
  // each observable x

  assert(code==1);

  Double_t tmax(_time.max(rangeName)), tmin(_time.min(rangeName)),
    turnon((Double_t)_turnon), offset((Double_t)_offset),
    exponent((Double_t)_exponent), beta((Double_t)_beta), ratio(1.0);

  if (tmin < 0.2) return 0.;
  if (beta < -0.0) return 0.0;
  if (beta*tmin > 1.0) return 0.0;

  // check if underlying data type is valid
  if (_correction.absArg()) ratio = (Double_t)_correction;

  double imin(0.0), imax(0.0), prefactor(1 / (2 * (offset - 1))),
    a_2F1(0.0), b_2F1(0.0), c_2F1(0.0), x_2F1(0.0),
    term1(0.0), term2(0.0), term3(0.0);

  a_2F1 = 1.0;
  b_2F1 = 2 / exponent;
  c_2F1 = 1 + 2/exponent;
  x_2F1 = std::pow(turnon * tmax, exponent) / (offset - 1);
  term1 = beta * tmax * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

  b_2F1 /= 2;
  c_2F1 -= 1/exponent;
  term2 = 2 * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

  term3 = (offset - 1) * (beta * tmax - 2);
  imax = -prefactor * tmax * (term1 - term2 + term3);

  b_2F1 = 2 / exponent;
  c_2F1 = 1 + 2/exponent;
  x_2F1 = std::pow(turnon * tmin, exponent) / (offset - 1);
  term1 = beta * tmin * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

  b_2F1 /= 2;
  c_2F1 -= 1/exponent;
  term2 = 2 * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

  term3 = (offset - 1) * (beta * tmin - 2);
  imin = -prefactor * tmin * (term1 - term2 + term3);

  return (ratio * (imax - imin));
}
