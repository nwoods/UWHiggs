#!/bin/bash
# Setup the UWHiggs dependencies in this working area 
# 
#  Usage: ./install.sh
#  
#  Author: Evan K. Friis, UW Madison

${CMSSW_BASE:?"Please run cmsenv before running install.sh"}

set -o errexit
set -o nounset

# Check CMSSW version
export MAJOR_VERSION=`echo $CMSSW_VERSION | sed "s|CMSSW_\([0-9]\)_.*|\1|"`
export MINOR_VERSION=`echo $CMSSW_VERSION | sed "s|CMSSW_\([0-9]\)_\([0-9]\)_.*|\2|"`

echo "Symlinking FinalStateAnalysis into working area"

pushd $CMSSW_BASE/src
if ! [ -L FinalStateAnalysis ]; then
  if ! [ -d FinalStateAnalysis ]; then
    ln -s UWHiggs/dependencies/FinalStateAnalysis FinalStateAnalysis
  fi
fi

echo "Selectring FSA version..."
pushd FinalStateAnalysis
if [ `git remote -v | grep upstream | grep uwcms | wc -l` = 2 ];
then
    echo 'Upstream detected'
else
    echo 'Adding upstream'
    git remote add upstream git@github.com:uwcms/FinalStateAnalysis.git
fi
git fetch upstream
if [ "$MAJOR_VERSION" -eq "7" ];
then
    echo "Selecting recipe for 13TeV miniAOD"
    git checkout -b miniAOD upstream/miniAOD_dev
elif [ "$MAJOR_VERSION" -eq "5" ];
then
    echo "Selecting recipe for 8TeV"
    git checkout -b uwcms_master upstream/master
fi
popd

echo "Checking out FSA dependencies"
pushd FinalStateAnalysis/recipe
# Do no do this - make sure you first run the FSA installation
#source environment.sh
#LUMI=1 LIMITS=1 PATPROD=${PATPROD:-0} ./recipe.sh

# The Nuke idea is great, but it needs fixing now...
#echo "Deleting unneeded PAT dependencies"
#FORCENUKE=1 ./nuke_pat_tools.sh

echo "Manually creating FinalStateAnalysis python symlinks"
./symlink_python.sh

echo "Installing python tools"
./install_python.sh

popd
popd

echo "Now run scram b -j 8 to compile"
