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

#include <TNtuple.h>

int oangle(bool select=false);

int oangleHisto();

int oangleNtuple(TNtuple &noangle);

#endif // __OANGLE_HH
