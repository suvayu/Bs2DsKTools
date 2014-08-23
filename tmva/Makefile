PKGCONFIG	:= pkg-config
ROOTCONFIG	:= root-config

CXX		:= $(shell $(ROOTCONFIG) --cxx)
OPT		:= -g -Wall -std=c++11
CXXFLAGS	:= -c $(OPT)

ROOTCFLAGS	:= $(shell $(ROOTCONFIG) --cflags)
ROOTLIBS	:= $(shell $(ROOTCONFIG) --libs)
ROOTGLIBS	:= $(shell $(ROOTCONFIG) --glibs)

SRCS	:= $(wildcard *.cc)

# targets
$(SRCS:%.cc=%):%:	%.cc
	$(CXX) $(OPT) $(ROOTCFLAGS) $(ROOTLIBS) -o $@ $<
