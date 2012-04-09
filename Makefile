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

PROJROOT     = $(PWD)
INCDIR       = $(PROJROOT)/include
SRCDIR       = $(PROJROOT)/src
LIBDIR       = $(PROJROOT)/lib
DICTDIR      = $(PROJROOT)/dict
DOCDIR       = $(PROJROOT)/docs
OBJDIR       = $(SRCDIR)

SRC          =
SRC          += $(SRCDIR)/readMCTree.cxx
SRC          += $(SRCDIR)/readDataTree.cxx
SRC          += $(SRCDIR)/lifetime.cxx
# SRC          += $(SRCDIR)/accept.cc

OBJS     =  $(SRC:%.cxx=%.o)


#------------------------------------------------------------------------------

# .SUFFIXES: .$(SrcSuf) .$(ObjSuf) .$(DllSuf)
# .PHONY:    Aclock Hello Tetris

all:		libreadTree.so

libreadTree.so:	$(OBJS) | $(LIBDIR)
	$(LD) $(SOFLAGS) $(LDFLAGS) $(ROOTLIBS) $^ -o $(LIBDIR)/$@
	@echo "$@ done"

# accept.so:		$()

$(SRCDIR)/%.o:	$(SRCDIR)/%.cxx
	$(CXX) $(CXXFLAGS) -I$(ROOTCFLAGS) -I$(INCDIR) $< -o $@

$(LIBDIR):
	@mkdir -p $(LIBDIR)

clean:		clean-obj
	@rm -f $(LIBDIR)/*

clean-obj:
	@rm -f $(OBJDIR)/*.o

# distclean:      clean
# 		@rm -f $(PROGRAMS) $(EVENTSO) $(EVENTLIB) *Dict.* *.def *.exp \
# 		   *.root *.ps *.so *.lib *.dll *.d *.log .def so_locations \
# 		   files/*
# 		@rm -rf cxx_repository
# 		-@cd RootShower && $(MAKE) distclean
# 		-@cd rhtml && $(MAKE) distclean
# 		-@cd RootIDE && $(MAKE) distclean
# 		-@cd periodic && $(MAKE) distclean
# 		-@cd histviewer && $(MAKE) distclean

# .SUFFIXES: .$(SrcSuf)

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
