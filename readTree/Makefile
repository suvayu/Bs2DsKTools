include ../common.mk

libreadTree.so:	$(SRCS:%.cxx=%.o) dict/readTreeDict.o
	$(LD) $(LDFLAGS) $(ROOTLIBS) $^ -o $@
