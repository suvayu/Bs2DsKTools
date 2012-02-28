#ifndef __PIDSEL__HH
#define __PIDSEL__HH

#include <TString.h>

#include "oanglePID.hxx"

using namespace std;

// deprecated retain temporarily for record
int PIDsel();

int PIDperf(TString);

oanglePID init_oanglePID();

int test_oanglePID();

#endif	// __PIDSEL__HH
