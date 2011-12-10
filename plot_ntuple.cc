{
  TNtuple *bla = (TTree*) _file0->Get("noangle");
  // bla->Scan("cos_oangle:mass", "abs(hID)==211");
  gROOT->LoadMacro("plot_MC.cc");
  plot_MC(*bla);
}
