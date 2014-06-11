

lumiFiles = ['inputs/2014-03-03-8TeV/data_MuEG_Run2012A_22Jan2013_v1.lumicalc.sum',\
                 'inputs/2014-03-03-8TeV/data_MuEG_Run2012B_22Jan2013_v1.lumicalc.sum',\
                 'inputs/2014-03-03-8TeV/data_MuEG_Run2012C_22Jan2013_v1.lumicalc.sum',\
                 'inputs/2014-03-03-8TeV/data_MuEG_Run2012D_22Jan2013_v1.lumicalc.sum']
#'inputs/2014-03-03-8TeV/_data_DoubleMuParked_Run2012A_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleElectron_Run2012A_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleElectron_Run2012B_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleElectron_Run2012C_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleElectron_Run2012D_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleMuParked_Run2012B_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleMuParked_Run2012C_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleMuParked_Run2012D_22Jan2013_v1.lumicalc.sum',\
#                  'inputs/2014-03-03-8TeV/data_DoubleMu_Run2012A_22Jan2013_v1.lumicalc.sum',\


lumiSum = 0.

for fileName in lumiFiles:
    with open(fileName,'r') as f:
        thisLumi = float(f.read())
        lumiSum += thisLumi
        print fileName + ': ' + str(thisLumi)
        

print "Total Lumi = " + str(lumiSum/3)
