#ifndef __UTILS_HXX
#define __UTILS_HXX

#include <TStyle.h>
#include <TH1.h>


/** 
 * Set global ROOT style and return the TStyle object.
 *
 * @return 
 */
TStyle* setStyle();


/**
 * Rescale X-axis of the passed histogram.
 *
 * @param h Pointer to histogram
 * @param factor Scale factor. (default = 0.001, corresponds to GeV/MeV -> TeV/GeV)
 */
void rescale(TH1 *h, Double_t factor);

#endif	// __UTILS_HXX
