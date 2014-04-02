#!/bin/bash

# Setup the cython proxies, find input ntuple files, and compute luminosity.
source jobid.sh
#export datasrc=/scratch/dntaylor/data
export datasrc=/hdfs/store/user/nwoods
#export datasrc=/hdfs/store/user/dntaylor/data
export jobid=$jobid8
export afile=`find $datasrc/$jobid | grep root | head -n 1`

echo "Building cython wrappers from file: $afile"

# rake "make_wrapper[$afile, mmm/final/Ntuple, MuMuMuTree]"
# rake "make_wrapper[$afile, eem/final/Ntuple, ElecElecMuTree]"
# rake "make_wrapper[$afile, mme/final/Ntuple, ElecMuMuTree]"
# rake "make_wrapper[$afile, eee/final/Ntuple, ElecElecElecTree]"
rake "make_wrapper[$afile, mmmm/final/Ntuple, MuMuMuMuTree]"
rake "make_wrapper[$afile, eemm/final/Ntuple, ElecElecMuMuTree]"
rake "make_wrapper[$afile, eeee/final/Ntuple, ElecElecElecElecTree]"

ls *pyx | sed "s|pyx|so|" | xargs rake 

echo "getting meta info"

# echo "rake meta:getinputs[$jobid, $datasrc, mmmmjj/metaInfo]"
# rake "meta:getinputs[$jobid, $datasrc, mmmmjj/metaInfo]"
# rake "meta:getmeta[inputs/$jobid, mmmmjj/metaInfo, 8]"
# 
# echo "rake meta:getinputs[$jobid, $datasrc, eemmjj/metaInfo]"
# rake "meta:getinputs[$jobid, $datasrc, eemmjj/metaInfo]"
# rake "meta:getmeta[inputs/$jobid, eemmjj/metaInfo, 8]"
# 
# echo "rake meta:getinputs[$jobid, $datasrc, eeeejj/metaInfo]"
# rake "meta:getinputs[$jobid, $datasrc, eeeejj/metaInfo]"
# rake "meta:getmeta[inputs/$jobid, eeeejj/metaInfo, 8]"

echo "rake meta:getinputs[$jobid, $datasrc, mmmm/metaInfo]"
rake "meta:getinputs[$jobid, $datasrc, mmmm/metaInfo]"
rake "meta:getmeta[inputs/$jobid, mmmm/metaInfo, 8]"

echo "rake meta:getinputs[$jobid, $datasrc, eemm/metaInfo]"
rake "meta:getinputs[$jobid, $datasrc, eemm/metaInfo]"
rake "meta:getmeta[inputs/$jobid, eemm/metaInfo, 8]"

echo "rake meta:getinputs[$jobid, $datasrc, eeee/metaInfo]"
rake "meta:getinputs[$jobid, $datasrc, eeee/metaInfo]"
rake "meta:getmeta[inputs/$jobid, eeee/metaInfo, 8]"

#export jobid=$jobid7
#rake "meta:getinputs[$jobid, $datasrc]"
#pushd inputs/$jobid/
#ls ../../inputs/$jobid8/WH_*HWW* | grep -v lumicalc | xargs -n 1 ln -s 
#popd
#rake "meta:getmeta[inputs/$jobid, mm/metaInfo, 7]"
