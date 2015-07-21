# ROOT
ROOTCONFIG	:= $(shell which root-config)
ROOTCLING    	:= $(shell which rootcling)

# compiler flags and options
CC           	:= $(shell $(ROOTCONFIG) --cc)
CXX 	     	:= $(shell $(ROOTCONFIG) --cxx)
LD           	:= $(shell $(ROOTCONFIG) --ld)

OPTS	     	:= -g -Wall
CXXFLAGS     	:= $(OPTS) -fPIC $(shell $(ROOTCONFIG) --cflags)
LDFLAGS      	:= $(OPTS) -shared $(shell $(ROOTCONFIG) --ldflags)

# linking to ROOT
ROOTLIBS     	:= $(shell $(ROOTCONFIG) --libs)
ROOFITLIBS   	:= -lRooFitCore -lRooFit

SRCS	     	:= $(wildcard *.cxx)

dict/%Dict.cxx:	$(wildcard *.hxx) $(wildcard dict/*LinkDef.h)
	$(ROOTCLING) -f $@ $^

dict/%.o:	dict/%.cxx
	$(CXX) -c $(CXXFLAGS) -Idict -I. $< -o $@

%.o:	%.cxx
	$(CXX) -c $(CXXFLAGS) -I. $< -o $@

clean:
	rm -f *.o *.so

cleanall:	clean
	rm -f dict/*.cxx
