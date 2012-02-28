void rootlogon()
{
  gSystem->AddIncludePath(" -I./include");
  cout << "Include path = " << gSystem->GetIncludePath() << endl;

  gSystem->AddDynamicPath("./lib");
  cout << "Dynamic path = " << gSystem->GetDynamicPath() << endl;
}
