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
SOFLAGS       = -shared -Wl,-soname,$@

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

TREEOBJF      = $(TREESRC:%.cxx=$(LIBDIR)/%.o)

# libreadTree.so
ACCSRC        =
ACCSRC       += PowLawAcceptance.cxx

ACCOBJF       = $(ACCSRC:%.cxx=$(LIBDIR)/%.o)

# libraries with one source file
# other libraries
LIBSRC        =
LIBSRC       += readMCTree.cxx
LIBSRC       += readDataTree.cxx
LIBSRC       += lifetime.cxx
LIBSRC       += utils.cxx
LIBSRC       += PowLawAcceptance.cxx

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

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY:		all libs $(LIBS) $(BINS) clean bin-clean obj-clean docs

all:		libs $(BINS)

# libraries
libs:		$(LIBS)

$(LIBS): %:	$(LIBDIR)/%

$(LIBDIR)/libreadTree.so:	$(TREEOBJF) | $(LIBDIR)
	$(LINK-LIBS) $^ -o $@
	@echo "$@ done"

$(LIBDIR)/libutils.so:		$(LIBDIR)/utils.o | $(LIBDIR)
	$(LINK-LIBS) $^ -o $@
	@echo "$@ done"

$(LIBDIR)/libacceptance.so:	$(ACCOBJF) | $(LIBDIR)
	$(LINK-LIBS) $(ROOFITLIBS) $^ -o $@
	@echo "$@ done"

$(LIBDIR)/%.o:	$(SRCDIR)/%.cxx | $(LIBDIR)
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	mkdir -p $(LIBDIR)

# Binaries
$(BINS): %:	$(SRCDIR)/%.cc $(LIBFILES) | $(BINDIR)
	$(CXX) $(OPT) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lreadTree -lutils $< -o $(BINDIR)/$@

$(BINDIR):
	mkdir -p $(BINDIR)

clean:		obj-clean bin-clean

bin-clean:
	rm -f $(foreach FILE,$(BINS),$(BINDIR)/$(FILE))

obj-clean:
	rm -f $(LIBDIR)/*.o
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
