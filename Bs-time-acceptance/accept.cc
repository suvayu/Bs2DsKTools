#include "lifetime.hxx"

int accept()
{
  TChain MCChain("MCChain");
  MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");
  lifetime MCsample(&MCChain);
  MCsample.Loop();
  return 0;
}
