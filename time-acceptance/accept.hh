#ifndef __ACCEPT_HH
#define __ACCEPT_HH

#include <string>

#include <TFile.h>
#include <TChain.h>
#include <TTree.h>
#include <TEntryList.h>
#include <TH1D.h>
#include <TString.h>

#include "readTree.hxx"

/** 
 * Main method to get acceptance
 *
 * @param doSelect Select from ntuples or read from file
 *
 * @return 
 */
int accept(bool doSelect=false);


TChain* initChain(std::string name, std::string fileglob);

/** 
 * Loop over ntuple and return selected events in a tree
 *
 * @param sample MC tree reader
 * @param ftree Tree with selected events
 * @param felist Selected entry list
 *
 * @return Total events selected
 */
int selAccTree(readTree &sample, TTree *& ftree, TEntryList *& felist);


void plotHistos(TEntryList* felist);

/** 
 * Plot histograms from tree
 *
 * @param ftree Event tree
 */
void plotHistos(TTree* ftree);

/** 
 * Return histogram from tree
 *
 * @param ftree Event tree
 * @param doAcc Weight for acceptance of lifetime
 *
 * @return Acceptance/lifetime histogram
 */
TH1D* getLifetime(TTree* ftree, bool doAcc=false);


TH1D* getLifetime(TEntryList* felist, TString cuts, bool doAcc=false);


void getTriggers(std::vector<TString> &triggers);


void plotHistoPanel(TEntryList *felist);

#endif  // __ACCEPT_HH
