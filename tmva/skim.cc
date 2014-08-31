#include <string>
#include <vector>
#include <iostream>
#include <cassert>

#include <TFile.h>
#include <TTree.h>
#include <TCut.h>


int main (int argc, char **argv)
{
  std::vector<std::string> args;
  args.reserve(argc);
  for (unsigned i = 0; i < unsigned(argc); ++i) {
    args.push_back(std::string(argv[i]));
  }

  // invocation line
  std::cout << "Invoked as:";
  for (auto arg : args) {
    std::cout << " " << arg;
  }
  std::cout << std::endl;

  assert(4 == args.size());
  std::string ofilen(args[2]), ifilen(args[3]); // skim -o out.root in.root

  TCut dtau("lab2_TAU>0");
  TCut dchi2("lab2_ENDVERTEX_CHI2>2"); // FIXME: disable cut, first investigate if right variable
  TCut hlt1("lab0_Hlt1TrackAllL0Decision_TOS");
  TCut hlt2topo2body("lab0_Hlt2Topo2BodyBBDTDecision_TOS");
  TCut hlt2topo3body("lab0_Hlt2Topo3BodyBBDTDecision_TOS");
  TCut hlt2topo4body("lab0_Hlt2Topo4BodyBBDTDecision_TOS");
  TCut hlt2incphi("lab0_Hlt2IncPhiDecision_TOS");
  TCut hlt2 = hlt2topo2body || hlt2topo3body || hlt2topo4body || hlt2incphi;
  TCut cut = dtau && hlt1 && hlt2;

  TFile *ifile = TFile::Open(ifilen.c_str());
  TTree *itree = dynamic_cast<TTree*>(ifile->Get("DecayTree"));
  unsigned long nentries(itree->GetEntries());

  TFile *ofile = TFile::Open(ofilen.c_str(), "recreate");
  // For one of MU/MD, data: 67798586L, MC (Dsπ): 67837L
  TTree *otree = itree->CopyTree(cut, "", nentries/120);
  otree->Write();
  ofile->Write();
  ofile->Close();
  return 0;
}
