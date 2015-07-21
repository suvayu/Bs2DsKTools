include ../common.mk

libacceptance.so:	$(SRCS:%.cxx=%.o) dict/acceptanceDict.o
	$(LD) $(LDFLAGS) $(ROOTLIBS) $(ROOFITLIBS) $^ -o $@
