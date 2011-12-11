int oangle_MC()
{
  // make chain
  TChain MCChain("MCChain");
  MCChain.Add("../../ntuples/MC/Merged_Bs2Ds*.root/DecayTree");

  readMCTree MCsample(&MCChain);

  // ntuple with mass, cos(oangle) and species from MC truth
  TNtuple noangle("noangle", "Opening angle", "mass:cos_oangle:hID");

  gROOT->LoadMacro("rootlogon.cc");

  MCsample.Loop(noangle);
  cout << noangle.GetEntries() << " entries filled!" << endl;

  gROOT->LoadMacro("plot_MC.cc");
  plot_MC(noangle);
  noangle.SaveAs("dump.root");

  return 0;
}
