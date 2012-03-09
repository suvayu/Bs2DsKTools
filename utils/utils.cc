#include <iostream>
#include <vector>
#include <fstream>

#include "utils.hh"


TStyle* Style::setStyle()
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetPalette(1); // "rainbow" color palette
  gStyle->SetNumberContours(256); // smooth color palette
  gStyle->SetTitleOffset( 1.2, "xy");
  gStyle->SetCanvasPreferGL(true);
  return gStyle;
}


void Hist::rescale(TH1 *h, Double_t factor)
{
  // change X scale
  Double_t xmin = h->GetXaxis()->GetXmin();
  Double_t xmax = h->GetXaxis()->GetXmax();
  h->GetXaxis()->SetLimits(xmin*factor,xmax*factor);
  return;
}


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
      std::cout << "Error   Parsers::PrintOpts(): Bad print option!"
		<< " No known formats found.\n"
		<< "Warning Parsers::PrintOpts(): Printing will be skipped."
		<< std::endl;
      doPrint = false;
    }
  }
  return doPrint;
}


void Parsers::readconf(std::vector<TString> &var, std::vector<TString> &val, std::string fname)
{
  ifstream inFile(fname.c_str());

  while (! inFile.eof()) {
    TString tmp;
    tmp.ReadToken(inFile);
    if (tmp.BeginsWith("#") or tmp.IsWhitespace()) {
      tmp.ReadLine(inFile);
      continue;
    }
    var.push_back(tmp);
    tmp.ReadToken(inFile);
    val.push_back(tmp);
  }
  return;
}


void Parsers::readlist(std::vector<TString> &var, std::string fname)
{
  ifstream inFile(fname.c_str());

  while (! inFile.eof())
    {
      TString tmp;
      tmp.ReadToken(inFile);
      if (tmp.BeginsWith("#") or tmp.IsWhitespace())
        {
          tmp.ReadLine(inFile);
          continue;
        }
      var.push_back(tmp);
    }
  return;
}


std::string& Parsers::replaceAll(std::string& context, const std::string& from, const std::string& to)
{
  size_t lookHere = 0;
  size_t foundHere;
  while((foundHere = context.find(from, lookHere)) != string::npos) {
    context.replace(foundHere, from.size(), to);
    lookHere = foundHere + to.size();
  }
  return context;
}
