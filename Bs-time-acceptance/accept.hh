#ifndef __ACCEPT_HH
#define __ACCEPT_HH

#include <TTree.h>

#include "readTree.hxx"


/** 
 * Main method to get acceptance
 *
 * @param doSelect Select from ntuples or read from file
 *
 * @return 
 */
int accept(bool doSelect=false);

/** 
 * Plot histograms from tree
 *
 * @param ftree Event tree
 */
void plotHistos(TTree* ftree);

/** 
 * Loop over ntuple and return selected events in a tree
 *
 * @param sample MC tree reader
 *
 * @return Tree with selected events
 */
TTree* selAccTree(readTree& sample);

/** 
 * Return histogram from tree
 *
 * @param ftree Event tree
 * @param doAcc Weight for acceptance of lifetime
 *
 * @return Acceptance/lifetime histogram
 */
TH1D* getLifetime(TTree* ftree, bool doAcc=false);

#endif  // __ACCEPT_HH
