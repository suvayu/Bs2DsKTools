# Makefile notes: `:=' is evaluated immediately but `=' is not. So if
# a variable contains parameters which are to be expanded later, then
# use `='.

SHELL        := /bin/bash
ROOTCONFIG   := $(shell which root-config)
ROOTCINT     := $(shell which rootcint)

# compiler flags and options
OPTS	     := -g -Wall

# compile with g++
CXX          := $(shell $(ROOTCONFIG) --cxx)
CXXFLAGS     := -fPIC $(shell $(ROOTCONFIG) --cflags)

# link
LD           := $(shell $(ROOTCONFIG) --ld)
LDFLAGS      := $(shell $(ROOTCONFIG) --ldflags)
# SOFLAGS       = -shared -Wl,-soname,$@ # not needed, default is fine

# linking to ROOT
ROOTLIBS     := $(shell $(ROOTCONFIG) --libs)
ROOFITLIBS   := -lRooFitCore -lRooFit
ROOTGLIBS    := $(shell $(ROOTCONFIG) --glibs)

LIBS          = libreadTree.so libacceptance.so
LINKDEFS      = $(wildcard dict/*LinkDef.h)
LIBSRC        = $(wildcard src/*.cxx)
ACCSRC        = $(wildcard src/*Acceptance*.cxx)
TREESRC       = $(filter-out $(ACCSRC),$(LIBSRC))
BINSRC        = $(wildcard src/*.cc)
BINS          = $(BINSRC:src/%.cc=%)
TESTDIR       = tests

# rules
.PHONY:		all $(LIBS) $(BINS) clean cleanall

all:		$(LIBS) $(BINS)

# dicts
dict/readTreeDict.cxx:	$(TREESRC:%.cxx=%.hxx) dict/readTreeLinkDef.h
	$(ROOTCINT) -f $@ -c -p $^

dict/acceptanceDict.cxx:	$(ACCSRC:%.cxx=%.hxx) dict/acceptanceLinkDef.h
	$(ROOTCINT) -f $@ -c -p $^

dict/%.o:	dict/%.cxx
	$(CXX) -c $(OPTS) $(CXXFLAGS) -Idict -I. $< -o $@

# sources
src/%.o:	src/%.cxx
	$(CXX) -c $(OPTS) $(CXXFLAGS) -Isrc $< -o $@

# link
libreadTree.so:	$(TREESRC:%.cxx=%.o) dict/readTreeDict.o
	$(LD) -shared $(OPTS) $(LDFLAGS) $(ROOTLIBS) $^ -o $@

libacceptance.so:	$(ACCSRC:%.cxx=%.o) dict/acceptanceDict.o
	$(LD) -shared $(OPTS) $(LDFLAGS) $(ROOTLIBS) $(ROOFITLIBS) $^ -o $@

# binaries
$(BINS):%:	src/%.cc $(LIBS)
	$(CXX) $(OPTS) $(CXXFLAGS) -Isrc $(ROOTLIBS) $(ROOFITLIBS) -L. -lreadTree -lacceptance src/utils.cc $< -o $@

# FIXME: test binaries
tests/%:%:	%.cc $(LIBS)
	$(CXX) $(OPTS) $(CXXFLAGS) -Isrc -Itests $(ROOTLIBS) $(ROOFITLIBS) -L. -lreadTree -lacceptance src/utils.cc $< -o $@

cleanall:	clean
	rm -f {dict,src}/*.o dict/*Dict.*

clean:
	rm -f $(LIBS) $(BINS)
