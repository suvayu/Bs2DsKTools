# Makefile notes: `:=' is evaluated immediately but `=' is not. So if
# a variable contains parameters which are to be expanded later, then
# use `='.

LIBS	:= readTree acceptance
BINS    := $(patsubst src/%.cc,bin/%,$(wildcard src/*.cc))

# rules
.PHONY:		all libs $(LIBS) bins clean cleanall

all:		libs bins

libs:	$(LIBS)

$(LIBS):%:	| lib inc
	make -C $@ lib$@.so
	cp -f $@/*.{so,pcm} lib/
	cd inc && ln -sf ../$@/*.hxx .

lib inc bin:%:
	mkdir -p $@

# # binaries
# $(BINS):%:	src/%.cc $(LIBS)
# 	$(CXX) $(OPTS) $(CXXFLAGS) -Isrc $(ROOTLIBS) $(ROOFITLIBS) -L. -lreadTree -lacceptance src/utils.cc $< -o $@

# # FIXME: test binaries
# tests/%:%:	%.cc $(LIBS)
# 	$(CXX) $(OPTS) $(CXXFLAGS) -Isrc -Itests $(ROOTLIBS) $(ROOFITLIBS) -L. -lreadTree -lacceptance src/utils.cc $< -o $@

cleanall clean:%:
	rm -r lib/*
	@for dir in $(LIBS); do make -C $$dir $@; done
