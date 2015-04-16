/**
 * @file   oangle.hh
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Wed Dec 14 01:28:52 2011
 *
 * @brief  Definitions for opening angle study utilities
 *
 *
 */

#ifndef __OANGLE_HH
#define __OANGLE_HH

#include <TTree.h>
#include <TNtuple.h>
#include <TString.h>

#include "readTree.hxx"

int setStyle();

int oangle(bool select=false);

// deprecated retain temporarily for record
int oangleHisto();

void oangleProject(TString);

TTree* oangleTree_get(readTree&);

TNtuple* oangleNtuple_get(readTree&);

int makeTemplates(TTree&);

int test_oangle();

#endif // __OANGLE_HH
