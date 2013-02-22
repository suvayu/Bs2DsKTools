# Makefile notes: `:=' is evaluated immediately but `=' is not. So if
# a variable contains parameters which are to be expanded later, then
# use `='.

#-----------------------------------------------------
# shell utilities
#-----------------------------------------------------
SHELL        := /bin/bash
ROOTCONFIG   := root-config
PKGCONFIG    := pkg-config

#-----------------------------------------------------
# compiler flags and options
#-----------------------------------------------------
# debug
ifneq ($(findstring debug, $(strip $(shell $(ROOTCONFIG) --config))),)
OPT           = -g
endif

# compile with g++
CXX          := $(shell $(ROOTCONFIG) --cxx)
OPT          += -Wall -fPIC $(DEBUG)
CXXFLAGS     := -c $(OPT)

# link
LD           := $(shell $(ROOTCONFIG) --ld)
LDFLAGS      := $(shell $(ROOTCONFIG) --ldflags) $(OPT)
SOFLAGS       = -shared
# SOFLAGS       = -shared -Wl,-soname,$@ # not needed, default is fine

# ROOT compile flags
ROOTCFLAGS   := $(shell $(ROOTCONFIG) --cflags)

# linking to ROOT
ROOTLIBS     := $(shell $(ROOTCONFIG) --libs)
ROOFITLIBS   := -lRooFitCore -lRooFit
ROOTGLIBS    := $(shell $(ROOTCONFIG) --glibs)

# others
HASTHREAD    := $(shell $(ROOTCONFIG) --has-thread)
ROOTDICTTYPE := $(shell $(ROOTCONFIG) --dicttype)
ROOTCINT     := $(shell $(ROOTCONFIG) --bindir)/rootcint

#-----------------------------------------------------
# directories
#-----------------------------------------------------
# PROJROOT      = $(PWD)
PROJROOT      = .
INCDIR        = $(PROJROOT)/include
SRCDIR        = $(PROJROOT)/src
LIBDIR        = $(PROJROOT)/lib
DICTDIR       = $(PROJROOT)/dict
DOCDIR        = $(PROJROOT)/docs
BINDIR        = $(PROJROOT)/bin
PYDIR         = $(PROJROOT)/python
TESTDIR       = $(PROJROOT)/tests

#-----------------------------------------------------
# project source, object, dictionary and lib filenames
#-----------------------------------------------------
# libraries
LIBS          =
LIBS         += libreadTree.so
LIBS         += libutils.so
LIBS         += libacceptance.so

# libraries with multiple source files need special handling
# libreadTree.so
TREESRC       =
TREESRC      += readMCTree.cxx
TREESRC      += readDataTree.cxx
TREESRC      += lifetime.cxx

# libacceptance.so
ACCSRC        =
ACCSRC       += PowLawAcceptance.cxx
ACCSRC       += AcceptanceRatio.cxx
# ACCSRC       += ErfAcceptance.cxx
# ACCSRC       += BdPTAcceptance.cxx

# linkdef files for dictionaries
LINKDEFS     =
LINKDEFS     += readTreeLinkDef.h
LINKDEFS     += utilsLinkDef.h

# binaries
BINSRC        =
BINSRC       += accept.cc
BINSRC       += resolution.cc
BINSRC       += addTreeBranch.cc

BINS          = $(BINSRC:%.cc=%)
BINFILES      = $(BINSRC:%.cc=$(BINDIR)/%)

#-----------------------------------------------------
# canned recipes
#-----------------------------------------------------
LINKLIBS = $(LD) $(LDFLAGS) $(SOFLAGS) $(ROOTLIBS)

define DICTNAMES =
$(foreach NAME,$(LIBS),$(NAME:lib%.so=$(DICTDIR)/%Dict.cxx))
endef

# getting linkdef name $(patsubst %Dict.cxx,%LinkDef.h,$@)
MAKEDICT = $(ROOTCINT) -f $@ -c -p $^

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY:		all libs $(LIBS) $(BINS) cleanall clean bin-clean so-clean obj-clean docs

all:		libs $(BINS)

# Libraries
libs:		$(LIBS)

$(LIBS): %:	$(LIBDIR)/%
	@echo "$@ done"

$(LIBDIR)/libreadTree.so:	$(TREESRC:%.cxx=$(LIBDIR)/%.o) $(DICTDIR)/readTreeDict.o | $(LIBDIR)
	$(LINKLIBS) $^ -o $@

$(LIBDIR)/libutils.so:		$(LIBDIR)/utils.o | $(LIBDIR)
	$(LINKLIBS) $^ -o $@

$(LIBDIR)/libacceptance.so:	$(ACCSRC:%.cxx=$(LIBDIR)/%.o) $(DICTDIR)/acceptanceDict.o | $(LIBDIR)
	$(LINKLIBS) $(ROOFITLIBS) $^ -o $@

$(LIBDIR)/%.o:	$(SRCDIR)/%.cxx | $(LIBDIR)
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	mkdir -p $(LIBDIR)

# Dictionaries
$(DICTDIR)/readTreeDict.cxx:	$(TREESRC:%.cxx=$(INCDIR)/%.hxx) $(DICTDIR)/readTreeLinkDef.h
	$(MAKEDICT)

$(DICTDIR)/acceptanceDict.cxx:	$(ACCSRC:%.cxx=$(INCDIR)/%.hxx) $(DICTDIR)/acceptanceLinkDef.h
	$(MAKEDICT)

# $(DICTDIR)/utilsDict.cxx:	$(INCDIR)/utils.hxx $(DICTDIR)/utilsLinkDef.h
# 	$(MAKEDICT)

$(DICTDIR)/%.o:	$(DICTDIR)/%.cxx
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(PROJROOT) $< -o $@

# Binaries
$(BINS): %:	$(SRCDIR)/%.cc $(LIBS) | $(BINDIR)
	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) $(ROOFITLIBS) -L$(LIBDIR) -lreadTree -lutils $< -o $(BINDIR)/$@

$(BINDIR):
	mkdir -p $(BINDIR)

# generic rule to build a test binary
# $(TESTDIR)/%: %:	%.cc
# 	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lreadTree -lutils $< -o $(TESTDIR)/$@

$(TESTDIR)/acctest:	$(TESTDIR)/acctest.cc $(LIBDIR)/libacceptance.so
	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lacceptance $< -o $@

$(TESTDIR)/treetest:	$(TESTDIR)/treetest.cc
	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) $(ROOFITLIBS) $< -o $@

cleanall:	obj-clean so-clean dict-clean bin-clean

clean:		obj-clean so-clean

bin-clean:
	rm -f $(foreach FILE,$(BINS),$(BINDIR)/$(FILE))

obj-clean:
	rm -f $(LIBDIR)/*.o

dict-clean:
	rm -f $(DICTDIR)/*.cxx
	rm -f $(DICTDIR)/*.o

so-clean:
	rm -f $(LIBDIR)/*.so
