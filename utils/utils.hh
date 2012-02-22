#ifndef __UTILS_HH
#define __UTILS_HH

#include <string>

#include <TString.h>
#include <TStyle.h>
#include <TH1.h>


namespace Style {

  /** 
   * Set global ROOT style and return the TStyle object.
   *
   * @return 
   */
  TStyle* setStyle();
}

namespace Hist {

  /**
   * Rescale X-axis of the passed histogram.
   *
   * @param h Pointer to histogram
   * @param factor Scale factor. (default = 0.001, corresponds to GeV/MeV -> TeV/GeV)
   */
  void rescale(TH1 *h, Double_t factor);
}

namespace Parsers {

  /** 
   * Parse print options and return output file format
   *
   * @param opt Print options
   * @param format output file format
   *
   * @return 
   */
  bool PrintOpts(TString& opt, TString& format);

  /**
   * Parse the passed file to initialise variables.
   *
   * @param var Vector of TString for variable names.
   * @param val Vector of TString for variable values.
   * @param fname Configuration file to parse.
   */
  void readconf(std::vector<TString> &var, std::vector<TString> &val, std::string fname);

  /**
   * Search and replace string within provided string
   *
   * @param context Original string
   * @param from Search string
   * @param to Replacement string
   *
   * @return Return original string after replacement
   */
  std::string& replaceAll(std::string& context, const std::string& from, const std::string& to);
}

#endif	// __UTILS_HH
