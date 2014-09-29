BOOST		:= /cvmfs/lhcb.cern.ch/lib/lcg/releases/LCG_68/Boost/1.55.0_python2.7/x86_64-slc6-gcc48-opt
BOOSTCFLAGS     := -I$(BOOST)/include/boost-1_55
BOOSTLIBS	:= -L$(BOOST)/lib -lboost_regex-gcc48-mt-1_55
BOOSTLIBS.CLI   := -L$(BOOST)/lib -lboost_program_options-gcc48-mt-1_55

# targets
$(SRCS:%.cc=%):%:	%.cc
	$(CXX) $(OPT) $(BOOSTCFLAGS) $(BOOSTLIBS.CLI) $(ROOTCFLAGS) $(ROOTLIBS) -o $@ $<

$(SRCS:%.cc=run-%):run-%:	%
	LD_LIBRARY_PATH=$(BOOST)/lib:$$LD_LIBRARY_PATH ./$< $(ARGS)
