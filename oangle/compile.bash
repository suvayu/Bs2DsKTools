#!/bin/bash

# NOTE: compiling in same session links the 2nd library with the 1st.
# Make sure to avoid that.

root -l -b <<EOF
.L oangle.cc++
.q
EOF
