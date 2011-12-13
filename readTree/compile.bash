#!/bin/bash
# compile tree reader

# NOTE: compiling in same session links the 2nd library with the 1st.
# Make sure to avoid that.

if [[ $1 = MC ]]; then
    root -l -b <<EOF
.L readMCTree.cxx++
.q
EOF
elif [[ $1 = Data ]]; then
    root -l -b <<EOF
.L readDataTree.cxx++
.q
EOF
fi

exit $?
