%Dict.cxx:	$(wildcard *.hxx) $(wildcard *LinkDef.h)
	$(ROOTCLING) -f $@ $^

%.o:	%.cxx
	$(CXX) -c $(CXXFLAGS) -I. $< -o $@

clean:
	rm -f *.o *.so

cleanall:	clean
	rm -f *Dict.{h,cxx}
