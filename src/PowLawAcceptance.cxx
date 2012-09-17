/**
 * @file   PowLawAcceptance.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Thu May 17 21:46:42 2012
 *
 * @brief  This class implements a power law acceptance function.
 *
 */

#include <iostream>
#include <list>

#include "Riostream.h"

#include "PowLawAcceptance.hxx"
#include "RooCustomizer.h"
#include "RooAbsReal.h"
#include "RooRealVar.h"
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

  // check if underlying data type is valid and is binned

  if (_correction.absArg()) {
    const RooAbsReal *correction = &_correction.arg();
    std::cout << __func__ << ": isBinnedDistribution = "
	      << correction->isBinnedDistribution(RooArgSet())
              << ", allVars = " << allVars << ", analVars = " << analVars
	      << std::endl;
    if (correction->isBinnedDistribution(RooArgSet()) and
	matchArgs(allVars, analVars, _time)) {
      std::cout << __func__ << ": PowLawAcceptance analytical integral supported" << std::endl;
      return 1;
    }
  }

  return 0;
}


Double_t PowLawAcceptance::analyticalIntegral(Int_t code,
					      const char* rangeName) const
{
  // return analytical integral defined by return code assigned by
  // getAnalyticalIntegral(..) the member function x.min(rangename)
  // and x.max(rangename) will return the integration boundaries for
  // each observable x

  std::cout << __func__ << ": Calculating PowLawAcceptance analytical integral" << std::endl;

  assert(code==1);

  double turnon((Double_t)_turnon), offset((Double_t)_offset),
    exponent((Double_t)_exponent), beta((Double_t)_beta), ratio(1.0);

  std::string name(_time.GetName());
  name += "_tmp";
  RooRealVar *time =
    dynamic_cast<RooRealVar*>(_time.absArg()->clone(name.c_str()));
  RooCustomizer custom(_correction.arg(), "_tmp");
  custom.replaceArg(*(_time.absArg()), *time);
  RooAbsReal *correction = dynamic_cast<RooAbsReal*>(custom.build(true));
  correction->addOwnedComponents(*time);

  double tmax(_time.max(rangeName)), tmin(_time.min(rangeName));
  std::list<double> *binedges(correction->binBoundaries(*time, tmin, tmax));

  double imin(0.0), imax(0.0), prefactor(1 / (2 * (offset - 1))),
    a_2F1(0.0), b_2F1(0.0), c_2F1(0.0), x_2F1(0.0),
    term1(0.0), term2(0.0), term3(0.0), integral(0.0);

  if (tmin < 0.2) return 0.;
  if (beta < -0.0) return 0.0;
  if (beta*tmin > 1.0) return 0.0;

  std::list<double>::const_iterator bitrE(binedges->end());
  for (std::list<double>::const_iterator bitr = binedges->begin();
       bitr != bitrE; ++bitr) {
    // bin low edges - binedges[i]
    // bin high edges - binedges[i+1]

    std::list<double>::const_iterator bitrcopy = bitr;
    ++bitrcopy;
    double tlo(*bitr), thi(*bitrcopy);

    time->setVal((tlo + thi) / 2.0);
    ratio = correction->getVal();

    a_2F1 = 1.0;
    b_2F1 = 2 / exponent;
    c_2F1 = 1 + 2/exponent;
    x_2F1 = std::pow(turnon * thi, exponent) / (offset - 1);
    term1 = beta * thi * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

    b_2F1 /= 2;
    c_2F1 -= 1/exponent;
    term2 = 2 * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

    term3 = (offset - 1) * (beta * thi - 2);
    imax = -prefactor * thi * (term1 - term2 + term3);

    b_2F1 = 2 / exponent;
    c_2F1 = 1 + 2/exponent;
    x_2F1 = std::pow(turnon * tlo, exponent) / (offset - 1);
    term1 = beta * tlo * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

    b_2F1 /= 2;
    c_2F1 -= 1/exponent;
    term2 = 2 * gsl_sf_hyperg_2F1(a_2F1, b_2F1, c_2F1, x_2F1);

    term3 = (offset - 1) * (beta * tlo - 2);
    imin = -prefactor * tlo * (term1 - term2 + term3);

    integral += ratio * (imax - imin);
  }

  return integral;
}
