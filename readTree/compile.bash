#!/bin/bash
# compile tree reader

# NOTE: compiling in same session links the 2nd library with the 1st.
# Make sure to avoid that.

root -l -b <<EOF
.L readMCTree.cxx++
.q
EOF

root -l -b <<EOF
.L readDataTree.cxx++
.q
EOF
