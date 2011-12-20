#!/bin/bash

# NOTE: compiling in same session links the 2nd library with the 1st.
# Make sure to avoid that.

if [[ $1 = "PID" ]]; then
    root -l -b <<EOF
.L PIDsel.cc++
.q
EOF
else
    root -l -b <<EOF
.L oangle.cc++
.q
EOF
fi
