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
ROOTCINT     := rootcint

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
ACCSRC       += ErfAcceptance.cxx

# linkdef files for dictionaries
LINKDEFS     =
LINKDEFS     += readTreeLinkDef.h
LINKDEFS     += utilsLinkDef.h

# binaries
BINSRC        =
BINSRC       += accept.cc
BINSRC       += resolution.cc

BINS          = $(BINSRC:%.cc=%)
BINFILES      = $(BINSRC:%.cc=$(BINDIR)/%)

#-----------------------------------------------------
# canned recipes
#-----------------------------------------------------
define LINK-LIBS =
$(LD) $(LDFLAGS) $(SOFLAGS) $(ROOTLIBS)
endef

define DICTNAMES =
$(foreach NAME,$(LIBS),$(NAME:lib%.so=$(DICTDIR)/%Dict.cxx))
endef

# getting linkdef name $(patsubst %Dict.cxx,%LinkDef.h,$@)
define MAKE-DICT =
	$(ROOTCINT) -f $@ -c -p $^
	@echo "Generated $@ from $^"
endef

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
	$(LINK-LIBS) $^ -o $@

$(LIBDIR)/libutils.so:		$(LIBDIR)/utils.o | $(LIBDIR)
	$(LINK-LIBS) $^ -o $@

$(LIBDIR)/libacceptance.so:	$(ACCSRC:%.cxx=$(LIBDIR)/%.o) $(DICTDIR)/acceptanceDict.o | $(LIBDIR)
	$(LINK-LIBS) $(ROOFITLIBS) $^ -o $@

$(LIBDIR)/%.o:	$(SRCDIR)/%.cxx | $(LIBDIR)
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	mkdir -p $(LIBDIR)

# Dictionaries
$(DICTDIR)/readTreeDict.cxx:	$(TREESRC:%.cxx=$(INCDIR)/%.hxx) $(DICTDIR)/readTreeLinkDef.h
	$(MAKE-DICT)

$(DICTDIR)/acceptanceDict.cxx:	$(ACCSRC:%.cxx=$(INCDIR)/%.hxx) $(DICTDIR)/acceptanceLinkDef.h
	$(MAKE-DICT)

# $(DICTDIR)/utilsDict.cxx:	$(INCDIR)/utils.hxx $(DICTDIR)/utilsLinkDef.h
# 	$(MAKE-DICT)

$(DICTDIR)/%.o:	$(DICTDIR)/%.cxx
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(PROJROOT) $< -o $@

# Binaries
$(BINS): %:	$(SRCDIR)/%.cc $(LIBS) | $(BINDIR)
	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lreadTree -lutils $< -o $(BINDIR)/$@

$(BINDIR):
	mkdir -p $(BINDIR)

cleanall:	obj-clean so-clean bin-clean

clean:		obj-clean

bin-clean:
	rm -f $(foreach FILE,$(BINS),$(BINDIR)/$(FILE))

obj-clean:
	rm -f $(LIBDIR)/*.o

so-clean:
	rm -f $(LIBDIR)/*.so


# ###
# Event.$(ObjSuf): Event.h
# EventMT.$(ObjSuf): EventMT.h
# MainEvent.$(ObjSuf): Event.h

# EventDict.$(SrcSuf): Event.h EventLinkDef.h
# 	@echo "Generating dictionary $@..."
# 	$(ROOTCINT) -f $@ -c $^

# EventMTDict.$(SrcSuf): EventMT.h EventLinkDef.h
# 	@echo "Generating dictionary $@..."
# 	$(ROOTCINT) -f $@ -c $^

# Hello.$(ObjSuf): Hello.h
# HelloDict.$(SrcSuf): Hello.h
# 	@echo "Generating dictionary $@..."
# 	$(ROOTCINT) -f $@ -c $^

# .$(SrcSuf).$(ObjSuf):
# 	$(CXX)  $(CXXFLAGS) -c $<
