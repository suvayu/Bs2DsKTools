void rootlogon()
{
  gSystem->AddIncludePath(" -I../readTree -I../oangle");
  cout << "Include path = " << gSystem->GetIncludePath() << endl;

  // gSystem->Load("../readTree/readDataTree_cxx.so");
  gSystem->Load("../readTree/readMCTree_cxx.so");
}
