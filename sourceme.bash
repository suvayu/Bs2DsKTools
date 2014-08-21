#!/bin/bash

# set -o xtrace

[[ $0 == sourceme.bash ]] && {
    echo "This script should be sourced, not executed.";
    exit -1;
}

which root-config &> /dev/null

if [[ $? == 0 ]]; then
    declare srcdir=${BASH_SOURCE%/*}
    [[ -n $LD_LIBRARY_PATH ]] && \
	export LD_LIBRARY_PATH=${srcdir}/lib:$LD_LIBRARY_PATH || \
	export LD_LIBRARY_PATH=${srcdir}/lib
else
    echo "No ROOT installation found."
fi

# set +o xtrace
