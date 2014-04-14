'''
Generic Base Class for SMP ZZ analysis

This class has 4 leptons

The subclasses must define the following functions:

    self.preselection

    self.event_weight(row) 

    self.book_histos(folder)              # books histograms in a given folder (region)
'''


from __future__ import division
from FinalStateAnalysis.PlotTools.MegaBase import MegaBase
import ROOT
import array
import os
import pprint
import itertools
import baseSelections as selections
import json

class ZZAnalyzerBase(MegaBase):
    def __init__(self, tree, outfile, wrapper, channel, **kwargs):
        super(ZZAnalyzerBase, self).__init__(tree, outfile, **kwargs)
        # Cython wrapper class must be passed
        self.tree = wrapper(tree)
        self.out = outfile
        self.jobid = os.environ['jobid']
        self.is7TeV = bool('7TeV' in self.jobid)
        self.histograms = {}
        self.channel = channel
        self.comboMap = {} # a dictionary to keep track of events that have been used
                           # format: self.combinatorics[EventNumber]=(Z1 mass of best found so far, Z2 pt sum of best found so far)
        self.jsonfile = self.getJsonFileName()
        self.hfunc   = { #maps the name of non-trivial histograms to a function to get the proper value, the function MUST have two args (evt and weight). Used in fill_histos later
            'nTruePU' : lambda row, weight: (row.nTruePU,None),
            'weight'  : lambda row, weight: (weight,None) if weight is not None else (1.,None),
            'Event_ID': lambda row, weight: (array.array("f", [row.run,row.lumi,int(row.evt)/10**5,int(row.evt)%10**5] ), None),
        }
        self.hfunc['Z1Mass']     = lambda row, weight: self.objectmap['Z1']['mass']
        self.hfunc['Z1Pt']       = lambda row, weight: self.objectmap['Z1']['pt']
        self.hfunc['Z1Eta']      = lambda row, weight: self.objectmap['Z1']['eta']
        self.hfunc['Z1Phi']      = lambda row, weight: self.objectmap['Z1']['phi']
        self.hfunc['Z2Mass']     = lambda row, weight: self.objectmap['Z2']['mass']
        self.hfunc['Z2Pt']       = lambda row, weight: self.objectmap['Z2']['pt']
        self.hfunc['Z2Eta']      = lambda row, weight: self.objectmap['Z2']['eta']
        self.hfunc['Z2Phi']      = lambda row, weight: self.objectmap['Z2']['phi']
#         self.hfunc['j1_Z1_dPhi'] = lambda row, weight: row.j1Phi-self.objectmap['Z1']['phi']
#         self.hfunc['j1_Z2_dPhi'] = lambda row, weight: row.j1Phi-self.objectmap['Z2']['phi']
#         self.hfunc['j2_Z1_dPhi'] = lambda row, weight: row.j2Phi-self.objectmap['Z1']['phi']
#         self.hfunc['j2_Z2_dPhi'] = lambda row, weight: row.j2Phi-self.objectmap['Z2']['phi']
#         self.hfunc['j1_Z1_Mass'] = lambda row, weight: self.getInvariant(row,'j1','Z1')['mass']
#         self.hfunc['j1_Z2_Mass'] = lambda row, weight: self.getInvariant(row,'j1','Z2')['mass']
#         self.hfunc['j2_Z1_Mass'] = lambda row, weight: self.getInvariant(row,'j2','Z1')['mass']
#         self.hfunc['j2_Z2_Mass'] = lambda row, weight: self.getInvariant(row,'j2','Z2')['mass']
        self.hfunc['Z1_Z2_Mass'] = lambda row, weight: self.getInvariant(row,'Z1','Z2')['mass']
#         self.hfunc['numberOSSF'] = lambda row, weight: selections.numberOSSF(row,channel)
        self.hfunc['numberOnZ']  = lambda row, weight: selections.numberOnZ(row,channel)
#         self.hfunc['numberBjet'] = lambda row, weight: selections.numberBjet(row)
        self.hfunc['numJets']    = lambda row, weight: row.jetVeto30 
#         self.hfunc['numBJets']   = lambda row, weight: row.bjetCSVVeto30 
        self.hfunc['Z1_Z2_Scatter'] = lambda row, weight: (self.objectmap['Z1']['mass'], self.objectmap['Z2']['mass'])
#        self.objects = []

    def build_zz_folder_structure(self):
        '''Builds a folder structure for the bprime histograms:
           /
           .../Signal
           ....../Preselection
           ....../OSSF#
           ........./onZ#
           .../Control
           ....../Zjets
           ....../WZ
           ....../ttbar
           ....../ZLep
        '''
        channel = self.channel
        self.controls = ["ZJets","WZ","ttbar","ZLep"]
        flag_map = {}
        #for ossf in range(0,3):
        for ossf in [2]:
            for onZ in range(0,ossf+1):
#                 for bjet in range(0,3):
                flag_map[(ossf,onZ)] = ("Signal",'OSSF'+str(ossf),'onZ'+str(onZ))
        flag_map["signal"] = ("Signal","Preselection")
        for control in self.controls:
            flag_map[control] = ("Control",control)
        return flag_map

    def begin(self):
        folder = self.channel
        for key, selection in self.build_zz_folder_structure().iteritems():
            folder = "/".join(selection)
            self.book_histos(folder)

    def jsonToDict(self):
        ''' Open (create) the used events file.'''
        if not os.path.exists(self.jsonfile):
            return self.generateJsonDict()
        jsondata = open(self.jsonfile)
        usedevents = json.load(jsondata)
        jsondata.close()
        return usedevents

    def dictToJson(self,dict):
        '''Write the dictionary to json'''
        jsonout = open(self.jsonfile,'w')
        json.dump(dict,jsonout)
        jsonout.close()

    def getJsonFileName(self):
        '''Return the filename of the json file'''
        [filedir, filename]  = os.path.split(os.environ['megatarget'])
        runname = 'Run2011' if self.is7TeV else 'Run2012'
        for letter in ['A','B','C','D']:
            if runname+letter in filename: runname += letter
        usedfilename = filedir+'/'+'data_'+runname+'.json'
        return usedfilename

    def generateJsonDict(self):
        '''Generate the dictionary for the used events'''
        dict = {}
        dict["Signal"] = {}
        dict["Control"] = {}
        dict["Signal"]["Preselection"] = []
#         for ossf in [2]: 
#             for onZ in range(0,ossf+1):
#                 for bjet in range(0,3):
#                     dictkey = "OSSF%i_onZ%i_b%i" % (ossf, onZ, bjet)
#                     dict["Signal"][dictkey] = []
        for control in self.controls:
            dict["Control"][control] = []
        return dict


    def process(self):
        histos       = self.histograms
        preselection = self.preselection
        fill_histos  = self.fill_histos
        event_weight = self.event_weight
        channel      = self.channel
        
#        if len(self.objects) == 4:
            # Find the right version of each event to deal with combinatorics issues
        for row in self.tree :
            ossfs = selections.getOSSF(row,channel,*self.objects)
            if len(ossfs) == 4 :
                mz1 = getattr(row, getVar2(ossfs[0], ossfs[1], 'Mass'))
                ptSum = getattr(row, getVar(ossfs[2], 'Pt')) + getattr(row,getVar(ossfs[3], 'Pt'))
                evNum = getattr(row, 'evt') 
                if evNum not in self.comboMap or (abs(91.1876 - self.comboMap[evNum][0]) > abs(91.1876 - mz1) and ptSum > self.comboMap[evNum][1]) :
                    self.comboMap[evNum] = (mz1, ptSum)

        self.cut_flow_init()
        usedEvents = self.jsonToDict()
        counter = 0
        for row in self.tree:
            self.cutmap["Initial"] += 1

            event = row.evt
            lumi = row.lumi
            run = row.run
            eventkey = [run, lumi, event]

            counter += 1
            self.ossf = selections.numberOSSF(row,channel)
            self.onZ = selections.numberOnZ(row,channel)
            self.objectmap = self.getObjectMap(row)
            for key, selection in self.build_zz_folder_structure().iteritems():
                # fill all events
                if key == "signal":
                    if preselection(row,"Signal"):
                        # check if we already used this event
                        if eventkey in usedEvents["Signal"]["Preselection"]: continue

                        self.cutmap["Signal"]["Preselection"]["Events"] += 1
                        fill_histos(histos, selection, row, event_weight(row))

                        # mark event as used
                        usedEvents["Signal"]["Preselection"].append(eventkey)

                    continue
                # fill controls
                foundControl = 0
                for control in self.controls:
                    if key == control:
                        if preselection(row,key):
                            # check if we already used this event
                            if eventkey in usedEvents["Control"][control]: continue

                            self.cutmap["Control"][key]["Events"] += 1
                            fill_histos(histos, selection, row, event_weight(row))
                            
                            # add to list of used events
                            usedEvents["Control"][control].append(eventkey)

                        foundControl = 1
                if foundControl: continue
                # select appropriate regions
#                 ossf = key[0]
#                 onZ = key[1]
#                 if selections.numberOSSF(row,channel)!=int(ossf): continue
#                 if selections.numberOnZ(row,channel)!=int(onZ):   continue
                fill_histos(histos, selection, row, event_weight(row))

        self.dictToJson(usedEvents)
        self.output_cut_flow()

    def cut_flow_init(self):
        '''Initialize cut flow
        Structure: {(label,sublabel): number}'''
        cutmap = {"Initial": 0, "Control": {}, "Signal": {}}
        self.cutmap = cutmap

    def output_cut_flow(self):
        '''outputs the cut flow to a txt file
        Label          Sublabel      Cut     Events   Cut %   Total %
        Initial                              ######   100.000 100.000
        Signal                               ######    ##.###  ##.###
                       Preselection          ######    ##.###  ##.###
                       ...
        '''
        cutmap = self.cutmap
        labelOrder = ["Initial","Signal","Control"]
        signalOrder = ["Preselection"]
#         for ossf in [2]:
#             for onZ in range(ossf+1):
#                 for b in range(3):
#                     signalOrder.append("OSSF%sonZ%sb%s" % (ossf, onZ, b))
        selectionOrderSignal = ["Events", "Trigger","ID4l", "Overlap", "OSSF2",
                                "Isolation","Combinatorics", "Z1Mass", "Z2Mass", 
                                "LeptonPairMass", "LeptonPt20", "LeptonPt10", 
                                "InvariantMass4l"]
        selectionOrderBackground = ["Events", "Trigger", "Overlap", "GoodZ1",
                                    "OSSF2", "LooseID4", "TightID3", "Isolation3"]
        selectionOrderControl = ["Events", "Trigger", "Overlap", "GoodZ1",
                                 "LooseID3", "MET25"]


        filename = os.path.splitext(os.environ['megatarget'])[0]+".txt"
        cutfile = open(filename,'w')
        labels = "Label".ljust(15)+"Sublabel".ljust(15)+"Cut".ljust(15) \
                 +"Events".ljust(9)+"Cut %".ljust(9)+"Total %".ljust(9)+"\n"
        cutfile.write(labels)

        # print initial stuff
        total = cutmap["Initial"]
        prevcut = total
        prevcutmajor = total
        initstring = "Initial".ljust(15)+"".ljust(15)+"".ljust(15) \
                     +str(total).rjust(6)+"".rjust(9)+"".rjust(9)+"\n"
        cutfile.write(initstring)

        # print signal stuff
        for sublabel in signalOrder:
            if sublabel == "Preselection":
                events = cutmap["Signal"]["Preselection"]["Events"]
                prevevents = total
                numcutstring = "%0.3f" % (events/total*100)
                prestring = "".ljust(15)+sublabel.ljust(15)+"".ljust(15) \
                            +str(events).rjust(6)+numcutstring.rjust(9)+numcutstring.rjust(9)+"\n"
                cutfile.write(prestring)
                for cutlabel in selectionOrderSignal:
                    if cutlabel not in cutmap["Signal"]["Preselection"]: continue
                    curevents = cutmap["Signal"]["Preselection"][cutlabel]
                    if prevevents:
                        cutpercent = "%0.3f" % (curevents/prevevents)
                    else:
                        cutpercent = "-.---"
                    totalpercent = "%0.3f" % (curevents/total)
                    cutstring = "".ljust(15)+"".ljust(15)+cutlabel.ljust(15) \
                                +str(curevents).rjust(6)+cutpercent.rjust(9)+totalpercent.rjust(9)+"\n" 
                    cutfile.write(cutstring)
                    prevevents = curevents

        # print control stuff
        controlstring = "Controls".ljust(15)+"".ljust(15)+"".ljust(15) \
                        +"".ljust(9)+"".ljust(9)+"".ljust(9)+"\n"
        cutfile.write(controlstring)
        for control in cutmap["Control"].keys():
            events = cutmap["Control"][control]["Events"]
            prevevents = total
            numcutstring = "%0.3f" % (events/total*100)
            totstring = "".ljust(15)+control.ljust(15)+"".ljust(15) \
                        +str(events).rjust(6)+numcutstring.rjust(9)+numcutstring.rjust(9)+"\n" 
            cutfile.write(totstring)
            theSelectionOrder = []
            if control == 'ZLep':
                theSelectionOrder = selectionOrderControl
            else:
                theSelectionOrder = selectionOrderBackground
            for cutlabel in theSelectionOrder:
                if cutlabel not in cutmap["Control"][control]: continue
                curevents = cutmap["Control"][control][cutlabel]
                if prevevents:
                    cutpercent = "%0.3f" % (curevents/prevevents)
                else:
                    cutpercent = "-.---"
                totalpercent = "%0.3f" % (curevents/total)
                cutstring = "".ljust(15)+"".ljust(15)+cutlabel.ljust(15) \
                            +str(curevents).rjust(6)+cutpercent.rjust(9)+totalpercent.rjust(9)+"\n" 
                cutfile.write(cutstring)
                prevevents = curevents
            
        cutfile.close()
            
        

    def book_kin_histos(self, folder, Id):
        '''book histograms for basic kinematic quantities'''
        IdMap  = {'m': 'Muon', 'e': 'Electron', 'j': 'Jet', 't': 'Tau', 'g': 'Photon', 'Z': 'Z'}
        number = Id[1] if len(Id) == 2 else ''
        self.book(folder, '%sPt' % Id, '%s %s p_{T}' % (IdMap[Id[0]], number), 100, 0, 1000)
        self.book(folder, '%sEta' % Id, '%s %s #eta' % (IdMap[Id[0]], number), 100, -3, 3)
        self.book(folder, '%sPhi' % Id, '%s %s #phi' % (IdMap[Id[0]], number), 100, -ROOT.TMath.Pi(), ROOT.TMath.Pi())

    def book_Z_histos(self, folder):
        '''book histograms for Z bosons'''
        self.book_kin_histos(folder, 'Z1')
        self.book(folder, 'Z1Mass', 'Z 1 Mass', 100, 0, 200)
        self.book_kin_histos(folder, 'Z2')
        self.book(folder, 'Z2Mass', 'Z 2 Mass', 100, 0, 200)
        self.book(folder, 'Z1_Z2_Mass', 'M(4l)', 310, 70., 1000)
        self.book(folder, 'Z1_Z2_Scatter', 'Z1 v Z2', 100, 0, 200, 100, 0, 200, type=ROOT.TH2F)

#     def book_bprime_histos(self, folder):
#         '''book histograms for reconstructed bprime object'''
#         self.book(folder, 'j1_Z1_Mass', 'M(j1,Z1)', 100, 0, 2000)
#         self.book(folder, 'j2_Z1_Mass', 'M(j2,Z1)', 100, 0, 2000)
#         self.book(folder, 'j2_Z2_Mass', 'M(j2,Z2)', 100, 0, 2000)
#         self.book(folder, 'j1_Z2_Mass', 'M(j1,Z2)', 100, 0, 2000)
# 
#     def book_dPhi_histos(self, folder):
#         '''book delta phi histograms'''
#         self.book(folder, 'j1_Z1_dPhi', '#Delta#phi(j1,Z1)', 100, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
#         self.book(folder, 'j2_Z1_dPhi', '#Delta#phi(j2,Z1)', 100, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
#         self.book(folder, 'j1_Z2_dPhi', '#Delta#phi(j1,Z2)', 100, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
#         self.book(folder, 'j2_Z2_dPhi', '#Delta#phi(j2,Z2)', 100, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
# 
    def book_event_histos(self, folder):
        '''book histos of event variables'''
        self.book(folder, 'Mass', 'Mass', 100, 0, 3000)
        self.book(folder, 'Pt', 'Pt', 100, 0, 3000)
#         self.book(folder, 'LT', 'LT', 100, 0, 3000)
        self.book(folder, 'pfMetEt', 'MET', 100, 0, 3000)
#         self.book(folder, 'numberOSSF', 'Number OSSF', 3, 0, 3)
#         self.book(folder, 'numberOnZ', 'Number on Z', 3, 0, 3)
#         self.book(folder, 'numJets', 'Number of Jets', 15, 0, 15)
#         self.book(folder, 'numBJets', 'Number of B Jets', 15, 0, 15)
#         if len(self.channel)==6:
#             self.book(folder, 'numberBjet', 'Number b-jets', 3, 0, 3)

    def fill_histos(self, histos, folder, row, weight):
        '''fill histograms'''
        folder_str =  "/".join(folder)+'/'
        for key, value in histos.iteritems():
            location = key[ : key.rfind('/')]+'/'
            if folder_str != location:
                #print "NOT EQUAL: " + folder_str + ", " + location
                continue
            attr = key[ key.rfind('/') + 1 :]
            if attr.find('Z1')>-1 and self.numZ<1: continue
            if attr.find('Z2')>-1 and self.numZ<2: continue
            if attr in self.hfunc:
                args = self.hfunc[attr](row,weight)
                if args.__class__==tuple:
                    value.Fill(*args)
                else:
                    value.Fill(args)
            else:
                value.Fill( getattr(row,attr), weight )

    def getObjectMap(self, row):
        '''returna a map of objects in event'''
        objectmap = {}
#         if self.channel == 'eemmjj': self.objects = ['e1', 'e2', 'm1', 'm2', 'j1', 'j2']
#         if self.channel == 'eeeejj': self.objects = ['e1', 'e2', 'e3', 'e4', 'j1', 'j2']
#         if self.channel == 'mmmmjj': self.objects = ['m1', 'm2', 'm3', 'm4', 'j1', 'j2']
        if self.channel == 'eemm':   self.objects = ['e1', 'e2', 'm1', 'm2']
        if self.channel == 'eeee':   self.objects = ['e1', 'e2', 'e3', 'e4']
        if self.channel == 'mmmm':   self.objects = ['m1', 'm2', 'm3', 'm4']
        if self.channel == 'eee':    self.objects = ['e1', 'e2', 'e3']
        if self.channel == 'eem':    self.objects = ['e1', 'e2', 'm3']
        if self.channel == 'mme':    self.objects = ['m1', 'm2', 'e3']
        if self.channel == 'mme':    self.objects = ['m1', 'm2', 'm3']
        objDict = map(lambda x: self.getObjectDict(row, x), self.objects)
        for obj, dict in zip(self.objects, objDict):
            objectmap[obj] = dict
        Zdict = self.getZ(row)
        self.numZ = len(Zdict)
        if self.numZ>0:
            objectmap['Z1'] = Zdict[0]
        if self.numZ>1:
            objectmap['Z2'] = Zdict[1]
        return objectmap

    def getZ(self, row):
        '''returns an array of dictionaries of Z properties ordered in closest to Z mass'''
        result = self.getZdict(row,'','','','')
        [obj1, obj2, obj3, obj4] = self.objects[0:4]
        combos1 = itertools.combinations(self.objects[0:4], 2)
        combos2 = itertools.combinations(self.objects[0:4], 2)
        for objcombo1 in combos1:
            for objcombo2 in combos2:
                 if (objcombo2[0] in objcombo1 or objcombo2[1] in objcombo1): continue
                 if (selections.ZSelection(row, objcombo1[0], objcombo1[1]) 
                     and selections.ZSelection(row, objcombo2[0], objcombo2[1])):
                         tempZdict = self.getZdict(row, objcombo1[0], objcombo1[1],
                                                   objcombo2[0], objcombo2[1])
                         # define Z's with one closest to Z peak
                         #if abs(tempZdict[0]['mass']-90) < abs(result[0]['mass']-90):
                         # define Z's based on both closest to Z peak
                         if (abs(tempZdict[0]['mass']-90)+abs(tempZdict[1]['mass']-90)) \
                            < (abs(result[0]['mass']-90)+abs(result[1]['mass']-90)):
                             result = tempZdict
        if result[0]['pt'] < 0: # case when ossf !=2
            combos = itertools.combinations(self.objects[0:4], 2)
            for objcombo in combos:
                if selections.ZSelection(row, objcombo[0], objcombo[1]):
                    tempZdict = [self.getInvariant(row,objcombo[0],objcombo[1])]
                    if abs(tempZdict[0]['mass']-90) < abs(result[0]['mass']-90): 
                        result = tempZdict
        if result[0]['pt'] < 0: # case when ossf = 0
            result = []
        return result


    def getZdict(self, row, obj1, obj2, obj3, obj4):
        '''return a dictionary of Z kinematics'''
        if obj1=='' or obj2=='' or obj3=='' or obj4=='':
            return [{'mass': -9999, 'pt': -9999, 'eta': -9999, 'phi': -9999},
                    {'mass': -9999, 'pt': -9999, 'eta': -9999, 'phi': -9999}]
        Z0 = self.getInvariant(row,obj1,obj2)
        Z1 = self.getInvariant(row,obj3,obj4)
        return [Z0, Z1]

    def getObjectDict(self, row, obj):
        '''Get a dictonary of object properties'''
        objDict = {}
        objDict[obj+'Pt']   = getattr(row, '%sPt' % obj)
        objDict[obj+'Eta']  = getattr(row, '%sEta' % obj)
        objDict[obj+'Phi']  = getattr(row, '%sPhi' % obj)
        objDict[obj+'Mass'] = getattr(row, '%sMass' % obj)
        return objDict

    def getObjectVector(self, row, obj):
        '''retrieve a TLorentzVector for an object'''
        vec = ROOT.TLorentzVector()
        if obj[0] in ['e', 'm', 't', 'j', 'g']:
            vec.SetPtEtaPhiM(getattr(row, '%sPt' % obj), getattr(row, '%sEta' % obj), 
                             getattr(row, '%sPhi' % obj), getattr(row, '%sMass' % obj))
        if obj[0]=='Z':
            vec.SetPtEtaPhiM(self.objectmap[obj]['pt'], self.objectmap[obj]['eta'],
                             self.objectmap[obj]['phi'], self.objectmap[obj]['mass'])
        return vec

    def getInvariant(self, row, obj1, obj2):
        '''return a dictionary of basic properties of two objects'''
        vec = self.getObjectVector(row,obj1) + self.getObjectVector(row,obj2)
        result = {'mass': vec.M(), 'pt': vec.Pt(), 'eta': vec.Eta(), 'phi': vec.Phi()}
        return result

    def finish(self):
        self.write_histos()

def getVar(name, var):
    return name+var

def getVar2(name1, name2, var):
    return name1 + '_' + name2 + '_' + var

