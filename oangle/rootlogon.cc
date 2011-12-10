void rootlogon()
{
  gSystem->SetIncludePath(" -I../read-data/ -I../read-MC/");
  cout << "Include path = " << gSystem->GetIncludePath() << endl;

  gSystem->Load("../read-data/Bs2DsK_cc.so");
  gSystem->Load("../read-MC/readTree_cxx.so");
}
