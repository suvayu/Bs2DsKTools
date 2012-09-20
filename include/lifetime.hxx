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
#include <map>

#include <TEntryList.h>

#include "readMCTree.hxx"

using namespace std;

class lifetime : public readMCTree {

private:

  std::map<unsigned int, long> _cutflow;

public :

  // constructor & destructor
  lifetime(TTree *tree=0);
  virtual ~lifetime();

  // overloaded virtual methods
  virtual void  Loop();
  virtual void  Loop(TNtuple &) {}
  virtual void  Loop(TTree &);
  virtual void  Loop(TTree &, TEntryList &, bool DsK);

  // overloaded non-virtual methods
  bool  CommonSelection(bool DsK=true);
  bool  UnbiasedSelection();
  bool  OfflineSelection(bool DsK=true);
};

#endif // #ifndef __LIFETIME_HXX
