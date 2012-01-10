#include <iostream>

#include "utils.hh"

using namespace std;

bool Parsers::PrintOpts(TString& opt, TString& format)
{
  opt.ToLower();
  bool doPrint(false);

  if ( opt.Contains("print") ) {
    doPrint = true;
    if ( opt.Contains("png") )          format = "png";
    else if ( opt.Contains("jpg") )     format = "jpg";
    else if ( opt.Contains("ps") )      format = "ps";
    else if ( opt.Contains("pdf") )     format = "pdf";
    else if ( opt.Contains("cscript") ) format = "C";
    else {
      cout << "Error   Parsers::PrintOpts(): Bad print option!"
	   << " No known formats found.\n"
	   << "Warning Parsers::PrintOpts(): Printing will be skipped."
	   << endl;
      doPrint = false;
    }
  }

  return doPrint;
}


TStyle* Style::setStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette
  gStyle->SetTitleOffset( 1.2, "xy");
  return gStyle;
}
