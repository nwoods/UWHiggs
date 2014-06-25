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

if [ -e HZZ_all_official.txt ]
then
	rm HZZ_all_official.txt
fi

export jobid=$jobid8
rake analyzeZZ

#bash combine.sh
