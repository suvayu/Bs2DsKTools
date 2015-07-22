include ../common.mk

libacceptance.so:	$(SRCS:%.cxx=%.o) acceptanceDict.o
	$(LD) $(LDFLAGS) $(ROOTLIBS) $(ROOFITLIBS) $^ -o $@

include ../targets.mk
