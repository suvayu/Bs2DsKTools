/**
 * @file   lifetime.hxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Sun Dec 11 01:25:13 2011
 * 
 * @brief  
 * 
 * 
 */

#ifndef __LIFETIME_HXX
#define __LIFETIME_HXX

#include <vector>

#include <TEntryList.h>

#include "readMCTree.hxx"

using namespace std;

class lifetime : public readMCTree {

public :

  // constructor & destructor
  lifetime(TTree *tree=0);
  virtual ~lifetime();

  // overloaded virtual methods
  virtual void  Loop();
  virtual void  Loop(TNtuple &) {}
  virtual void  Loop(TTree &);
  virtual void  Loop(TTree &, TEntryList &);

  // overloaded non-virtual methods
  bool  CommonSelection();
  bool  UnbiasedSelection();
};

#endif // #ifndef __LIFETIME_HXX
