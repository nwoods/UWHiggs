#!/bin/bash
# Run all of the analysis

set -o nounset
set -o errexit

source jobid.sh

#export jobid=$jobid7
#rake analyzebprime

if [ -e results/2014-03-03-8TeV/ZZAnalyzerEEEE/data_Run2012A.json ]
then
	rm results/*/*/*.json
fi

if [ -e HZZ_passed.txt ]
then
	rm HZZ_passed.txt
fi

if [ -e results/2014-03-03-8TeV/ZZAnalyzerMMMM/data_DoubleMuParked_Run2012B_22Jan2013_v1.root ]
then
    rm results/*/*/*data*
fi

export jobid=$jobid8
rake analyzeZZ_dataonly

#bash combine.sh
