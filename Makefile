SHELL        := /bin/bash
ROOTCONFIG   := root-config

# ifneq ($(findstring debug, $(strip $(shell $(ROOTCONFIG) --config))),)
# OPT           = -g
# OPT2          = -g
# endif

# compile with g++ 
CXX          := $(shell $(ROOTCONFIG) --cxx)
CXXFLAGS     := -c $(OPT) -Wall -fPIC

# link
LD           := $(shell $(ROOTCONFIG) --ld)
LDFLAGS      := $(OPT) -fPIC
SOFLAGS      := -shared

# ROOT compile flags
ROOTCFLAGS   := $(shell $(ROOTCONFIG) --cflags)

# linking to ROOT 
ROOTLIBS     := $(shell $(ROOTCONFIG) --libs)
ROOFITLIBS   := -lRooFitCore -lRooFit
ROOTGLIBS    := $(shell $(ROOTCONFIG) --glibs)
ROOTLDFLAGS  := $(shell $(ROOTCONFIG) --ldflags)

# others
HASTHREAD    := $(shell $(ROOTCONFIG) --has-thread)
ROOTDICTTYPE := $(shell $(ROOTCONFIG) --dicttype)
ROOTCINT     := rootcint

# directories
PROJROOT     =  $(PWD)
INCDIR       =  $(PROJROOT)/include
SRCDIR       =  $(PROJROOT)/src
LIBDIR       =  $(PROJROOT)/lib
DICTDIR      =  $(PROJROOT)/dict
DOCDIR       =  $(PROJROOT)/docs
OBJDIR       =  $(LIBDIR)
TESTDIR      =  $(PROJROOT)/tests

# library sources
LIBSRC       =
LIBSRC       += readMCTree.cxx
LIBSRC       += readDataTree.cxx
LIBSRC       += lifetime.cxx

# BINSRC       += accept.cc
# BINSRC       += oangle.cc
# BINSRC       += PIDsel.cc

OBJS         =  $(LIBSRC:%.cxx=%.o)

LIBS         =
LIBS         += libreadTree.so

SRCFILES     =  $(LIBSRC:%=$(SRCDIR)/%)
OBJFILES     =  $(OBJS:%=$(OBJDIR)/%)
LIBFILES     =  $(LIBS:%=$(LIBDIR)/%)

#------------------------------------------------------------------------------

# .SUFFIXES: .$(SrcSuf) .$(ObjSuf) .$(DllSuf)
# .PHONY:    Aclock Hello Tetris

all:		$(LIBFILES)

$(LIBFILES):	$(OBJFILES) | $(LIBDIR)
	$(LD) $(SOFLAGS) $(LDFLAGS) $(ROOTLIBS) $^ -o $@
	@echo "$@ done"

$(OBJDIR)/%.o:	$(SRCDIR)/%.cxx | $(OBJDIR)
	$(CXX) $(CXXFLAGS) -I$(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	@mkdir -p $(LIBDIR)

# Binaries
%:     src/%.cc
	$(CXX) -Wall -fPIC $(ROOTCFLAGS) -I$(INCDIR) $(ROOTLIBS) -L$(LIBDIR) -lreadTree $< -o $@

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
