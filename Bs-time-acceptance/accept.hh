#ifndef __ACCEPT_HH
#define __ACCEPT_HH

#include <TTree.h>

#include "readTree.hxx"

int accept(bool doSelect=false);

void plotHistos(TTree* ftree);

TTree* selAccTree(readTree& sample);

TH1D* getLifetime(TTree* ftree, bool doAcc=false);

#endif  // __ACCEPT_HH
