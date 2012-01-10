#ifndef __UTILS_HH
#define __UTILS_HH

#include <TString.h>
#include <TStyle.h>

using namespace std;

namespace Parsers {

  bool PrintOpts(TString&, TString&);

}

namespace Style {

  TStyle* setStyle();

}

#endif	// __UTILS_HH
