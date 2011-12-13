#!/bin/bash


if [[ $1 = lt ]]; then
    root -l << EOF
.L lifetime.cxx++
.q
EOF
elif [[ $1 = macros ]]; then
    root -l -b <<EOF
.L lifetime_cxx.so
.L accept.cc++
.q
EOF
fi

exit $?
