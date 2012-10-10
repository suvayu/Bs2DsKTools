TARGETS = readTreeDict.cxx libreadTree.so accept

alldicts += readTreeDict.cxx

include Rules.mk

libreadTree.so: $(patsubst %.cxx,%.os,$(filter-out accept.cc,$(ccsrc)))

readTreeDict.cxx: readTree.hxx readMCTree.hxx lifetime.hxx readTreeLinkDef.h

accept: libreadTree.so
accept:	LDLIBS+=-lstdc++ $(ROOTLIBS)
