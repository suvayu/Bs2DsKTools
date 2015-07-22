include ../common.mk

libreadTree.so:	$(SRCS:%.cxx=%.o) readTreeDict.o
	$(LD) $(LDFLAGS) $(ROOTLIBS) $^ -o $@

include ../targets.mk
