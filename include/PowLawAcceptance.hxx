/**
 * @file   PowLawAcceptance.hxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Thu May 17 21:47:46 2012
 * 
 * @brief  This class implements a power law acceptance function.
 *
 *         This code is based on a skeleton code generated by
 *         RooClassFactory from RooFit. The functional form and the
 *         integral was coded in by hand.
 * 
 */


#ifndef __POWLAWACCEPTANCE_HXX
#define __POWLAWACCEPTANCE_HXX

#include "RooAbsReal.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"


class PowLawAcceptance : public RooAbsReal {
public:

  PowLawAcceptance() {};
  PowLawAcceptance(const char *name, const char *title,
		   RooAbsReal& turnon, RooAbsReal& time,
		   RooAbsReal& offset, RooAbsReal& exponent);
  PowLawAcceptance(const PowLawAcceptance& other, const char* name=0);
  virtual ~PowLawAcceptance();
  virtual TObject* clone(const char* newname) const;

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars,
			      const char* rangeName=0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

  Double_t evaluate() const;

  RooRealProxy _turnon;
  RooRealProxy _time;
  RooRealProxy _offset;
  RooRealProxy _exponent;

private:

  ClassDef(PowLawAcceptance,1);	// This class implements a power law
			        // acceptance function.
};

#endif	// __POWLAWACCEPTANCE_HXX
