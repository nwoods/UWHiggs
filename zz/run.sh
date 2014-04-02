#!/bin/bash
# Run all of the analysis

set -o nounset
set -o errexit

source jobid.sh

#export jobid=$jobid7
#rake analyzebprime

export jobid=$jobid8
rake analyzeZZ

#bash combine.sh
