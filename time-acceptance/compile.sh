#!/bin/bash


if [[ $1 = lt ]]; then
    root -l << EOF
.L lifetime.cxx++
.q
EOF
elif [[ $1 = mac ]]; then
    root -l -b <<EOF
.L lifetime_cxx.so
.L ../utils/utils_cc.so
.L accept.cc++
.q
EOF
elif [[ $1 = fit ]]; then
    root -l -b <<EOF
.L ltFit.cc++
.q
EOF
fi
# .L ../utils/utils_cc.so

exit $?
