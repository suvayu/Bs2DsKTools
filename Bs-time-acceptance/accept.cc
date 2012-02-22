#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cassert>
#include <string>

#include <TChain.h>
#include <TCanvas.h>
#include <TH1D.h>

#include "utils.hh"
#include "lifetime.hxx"
#include "accept.hh"


int accept(bool doSelect)
{
  TChain MCChain("MCChain");
  TTree *ftree = NULL;

  string fileaccess((doSelect) ? "recreate" : "read");
  TFile rfile("smalltree.root", fileaccess.c_str());

  // select
  if (doSelect) {
    MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
    lifetime MCsample(&MCChain);
    ftree = selAccTree(MCsample); // remember to delete ftree
  }
  else ftree = (TTree*) rfile.Get("ftree");;

  std::cout << "Entries: " << ftree->GetEntries() << std::endl;
  plotHistos(ftree);

  if (doSelect) {
    rfile.cd();
    ftree->Write();
  }

  // housekeeping
  delete ftree;
  return 0;
}


void plotHistos(TTree* ftree)
{
  Style::setStyle();
  TH1D *hlaccept = getLifetime(ftree, true); // remember to delete
  TH1D *hltime   = getLifetime(ftree);	     // remember to delete

  hlaccept->SetLineColor(kAzure);
  hltime  ->SetLineColor(kAzure);
  hlaccept->SetXTitle("Bs lifetime in ps");
  hltime  ->SetXTitle("Bs lifetime in ps");

  TCanvas *canvas = new TCanvas("canvas", "", 1200, 450);
  canvas->Divide(2,1);
  canvas->cd(1);
  hlaccept->Draw("hist");
  canvas->cd(2);
  hltime->Draw("hist");
  canvas->Print(".png");

  delete hlaccept; delete hltime;
  return;
}


TTree* selAccTree(readTree &sample)
{
  TTree *ftree = new TTree("ftree", "Selected events for lifetime acceptance");
  sample.Loop(*ftree);
  return ftree;
}


// hlifetimew.Fill(lab0_TRUETAU, TMath::Exp(lab0_TRUETAU*1e3/1.472)); // time in ns / lifetime in ps
TH1D* getLifetime(TTree* ftree, bool doAcc)
{
  TString name, title, select, trigger, weight;

  if (doAcc) {
    title = "B_{s} lifetime acceptance";
    name  = "hlaccept";
  }
  else {
    title = "B_{s} lifetime";
    name  = "hltime";
  }

  if (doAcc) weight  = "*exp(tau*1e3/1.472)";
  trigger = "(HLT2Topo4Body>0)";
  select  = trigger + weight;

  // binning for ps, tree has lifetimes in ns
  TH1D* hist = new TH1D(name.Data(), title.Data(), 100, 0, 10);
  ftree->Draw("tau*1e3>>" + name, select.Data());
  return hist;
}
