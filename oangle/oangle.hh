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

#include "readTree.hxx"

int oangle(bool select=false);

int oangleHisto();

TNtuple* oangleNtuple_get(readTree&);

int oangleNtuple_plot(TNtuple &noangle);

#endif // __OANGLE_HH
