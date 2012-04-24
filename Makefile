#-----------------------------------------------------
# shell utilities
#-----------------------------------------------------
SHELL        := /bin/bash
ROOTCONFIG   := root-config

#-----------------------------------------------------
# compiler flags and options
#-----------------------------------------------------
# debug
ifneq ($(findstring debug, $(strip $(shell $(ROOTCONFIG) --config))),)
OPT           = -g
endif

# compile with g++ 
CXX          := $(shell $(ROOTCONFIG) --cxx) -Wall -fPIC
CXXFLAGS     := -c $(OPT)

# link
LD           := $(shell $(ROOTCONFIG) --ld) -Wall -fPIC
LDFLAGS      := $(shell $(ROOTCONFIG) --ldflags) $(OPT)
SOFLAGS      := -shared

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
PROJROOT     =  $(PWD)
INCDIR       =  $(PROJROOT)/include
SRCDIR       =  $(PROJROOT)/src
LIBDIR       =  $(PROJROOT)/lib
DICTDIR      =  $(PROJROOT)/dict
DOCDIR       =  $(PROJROOT)/docs
BINDIR       =  $(PROJROOT)/bin
TESTDIR      =  $(PROJROOT)/tests

#-----------------------------------------------------
# project source, object, dictionary and lib filenames
#-----------------------------------------------------
# libraries
LIBS         =  
LIBS         += libreadTree.so
LIBS         += libutils.so

LIBFILES     =  $(LIBS:%=$(LIBDIR)/%)

# libraries with multiple source files need special handling
# libreadTree.so
TREESRC      =
TREESRC      += readMCTree.cxx
TREESRC      += readDataTree.cxx
TREESRC      += lifetime.cxx

TREEOBJF     =  $(TREESRC:%.cxx=$(LIBDIR)/%.o)

# libraries with one source file
# other libraries
LIBSRC       =
LIBSRC       += readMCTree.cxx
LIBSRC       += readDataTree.cxx
LIBSRC       += lifetime.cxx
LIBSRC       += utils.cxx

OBJFILES     =  $(SRCDIR)/%.o

# binaries
BINSRC       =
BINSRC       += accept.cc
BINSRC       += resolution.cc

BINFILES     =  $(BINSRC:%.cc=$(BINDIR)/%)

#-----------------------------------------------------
# canned recipes
#-----------------------------------------------------
define LINK-LIBS =
$(LD) $(LDFLAGS) $(SOFLAGS) $(ROOTLIBS) $^ -o $@
@echo "$@ done"
endef

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY:		all clean clean-obj clean-so docs

all:		$(LIBFILES) $(BINFILES)

# libraries
$(LIBDIR)/libreadTree.so:	$(TREEOBJF) | $(LIBDIR)
	$(LINK-LIBS)

$(LIBDIR)/libutils.so:		$(LIBDIR)/utils.o | $(LIBDIR)
	$(LINK-LIBS)

$(LIBDIR)/%.o:	$(SRCDIR)/%.cxx | $(LIBDIR)
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	mkdir -p $(LIBDIR)

# Binaries
$(BINFILES): $(BINDIR)/%:	$(SRCDIR)/%.cc $(LIBFILES) | $(BINDIR)
	$(CXX) $(CXXFLAGS) $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lreadTree -lutils $< -o $@

$(BINDIR):
	mkdir -p $(BINDIR)

clean:		clean-obj clean-so

clean-obj:
	rm -f $(OBJDIR)/*.o

clean-so:
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
