#!/bin/bash
# plot ZZ mass spectrum

set -o nounset
set -o errexit

source jobid.sh

#export jobid=$jobid7

export jobid=$jobid8

python plotZZ.py
