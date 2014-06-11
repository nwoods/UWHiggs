'''
Common selections for SMP ZZ Analysis
'''

import os
import itertools 

# Determine MC-DATA corrections
is7TeV = bool('7TeV' in os.environ['jobid'])

# constants
# CSVL = 0.244
# CSVM = 0.679
# CSVT = 0.898


def getVar(name, var):
    return name+var

def getVar2(name1, name2, var):
    return name1 + '_' + name2 + '_' + var

# Check to make sure this is modified correctly. Was 0.1 instead of 0.5
def overlap(row,*args):
    return any( map( lambda x: x < 0.1, [getattr(row,'%s_%s_DR' % (l1,l2) ) for l1 in args for l2 in args if l1 <> l2 and hasattr(row,'%s_%s_DR' % (l1,l2) )] ) )

def muLooseIso(row, name):
    return getattr(row, getVar(name,'RelPFIsoDB'))<0.4 # Cut used in H4l analysis

def muTightIso(row, name):
    return getattr(row, getVar(name,'RelPFIsoDB'))<0.2

# Are we supposed to use RelPFIsoRho instead of RelPFIsoRhoFSR? I think this is right...
def eLooseIso(row, name):
    return getattr(row, getVar(name,'RelPFIsoRhoFSR'))<0.4 # Cut used in H4l analysis. Again, not sure about FSR 

def eTightIso(row, name):
    return getattr(row, getVar(name,'RelPFIsoRhoFSR'))<0.2

# def bCSVL(row, name):
#     return getattr(row, getVar(name,'CSVBtag'))>CSVL
# 
# def bCSVM(row, name):
#     return getattr(row, getVar(name,'CSVBtag'))>CSVM
# 
# def bCSVT(row, name):
#     return getattr(row, getVar(name,'CSVBtag'))>CSVT
# 
# def vetoes(row):
#     if row.muVetoPt15IsoIdVtx>0: return False
#     if row.eVetoMVAIsoVtx>0:     return False
#     return True

def doubleMuonTrigger(row):
    return (row.doubleMuPass>0 or row.doubleMuTrkPass>0)

def doubleElectronTrigger(row):
    return (row.doubleEPass>0)

def eMuTrigger(row):
    return (row.mu17ele8Pass > 0 or row.mu8ele17Pass > 0)

# Maybe also need a 3e trigger?

def leptonIso(row, *objects):
    for obj in objects:
        if obj[0] == "e":
            if not eLooseIso(row,obj): return False
        if obj[0] == "m":
            if not muLooseIso(row,obj): return False
    return True

def muSelection(row, name):
    if getattr(row, getVar(name,'Pt'))<5:           return False
    if getattr(row, getVar(name,'AbsEta'))>2.4:      return False
    if abs(getattr(row,getVar(name,'PVDXY'))) > 0.5: return False
    if abs(getattr(row,getVar(name,'PVDZ'))) > 1.0: return False
    if abs(getattr(row, getVar(name,'IP3DS')))>4.:     return False
    #if not muLooseIso(row, name):                    return False
    return muIDTight(row,name)

def muIDTight(row, name):
    isGlobal = getattr(row,getVar(name, 'IsGlobal'))
    isTracker = getattr(row, getVar(name, 'IsTracker'))
    return (isGlobal or isTracker)
#    return bool(getattr(row, getVar(name,'PFIDTight')))

def muIDLoose(row, name):
    return bool(getattr(row, getVar(name,'PFIDTight'))) # Placeholder -- fix

def eSelection(row, name):
    if getattr(row, getVar(name,'Pt')) < 7:         return False
    if getattr(row, getVar(name,'AbsEta')) > 2.5:    return False
    if abs(getattr(row, getVar(name,'IP3DS'))) > 4:   return False
    if abs(getattr(row,getVar(name,'PVDXY'))) > 0.5: return False
    if abs(getattr(row,getVar(name,'PVDZ'))) > 1.0: return False
    if abs(getattr(row, getVar(name,'IP3DS')))>4.:     return False
    #if not eLooseIso(row, name):                     return False
    return eIDTight(row,name)

def eIDTight(row, name):
    ''' Tight electron ID from AN2012-141 '''
    eta = getattr(row, getVar(name, 'Eta'))
    pt = getattr(row, getVar(name, 'Pt'))
    bdt = getattr(row, getVar(name, 'MVANonTrig'))
    if pt > 7. and pt < 10.:
        if abs(eta)<0.8 and bdt>0.47: return True
        if abs(eta)>0.8 and abs(eta)<1.479 and bdt>0.004: return True
        if abs(eta)>1.479 and bdt>0.295: return True
    if pt > 10.:
        if abs(eta)<0.8 and bdt>-0.34: return True
        if abs(eta)>0.8 and abs(eta)<1.479 and bdt>-0.65: return True
        if abs(eta)>1.479 and bdt>0.6: return True
    return False
#    return bool(getattr(row, getVar(name,'MVAIDH2TauWP')))

def eIDLoose(row, name):
    return bool(getattr(row, getVar(name,'MVAIDH2TauWP'))) # Placeholder -- fix

def jetSelection(row, name):
    if getattr(row, getVar(name,'Pt')) < 30:         return False
    if getattr(row, getVar(name,'AbsEta')) > 4.7:    return False
    return True

def ZSelection(row, obj1, obj2):
    if obj1[0] != obj2[0]:                           return False
    if getattr(row, getVar2(obj1, obj2, 'SS')):      return False
    return True

def ZIsoSelection(row, obj1, obj2):
    if not ZSelection(row, obj1, obj2): return False
    return True

def objSelection(row,obj):
    if obj[0] == 'e':
        if not eSelection(row,obj): return False
    elif obj[0] == 'm':
        if not muSelection(row,obj): return False
    # In this analysis, 0 jet events are allowed
    #     elif obj[0] == 'j':
    #         if not jetSelection(row,obj): return False
    return True

# Loose selections for control regions
# Needs to be redone once I figure out what the right loose ID cuts are for leptons
def objSelectionLoose(row, obj):
    return objSelection(row,obj)

def preselectionSignal(row, channel, cutmap, comboMap, objects, passList, passDict):
    # setup dictionary
    if not cutmap["Signal"].has_key("Preselection"):
        cutmap["Signal"]["Preselection"] = {}
        cutmap["Signal"]["Preselection"]["Events"]              = 0
        cutmap["Signal"]["Preselection"]["Trigger"]             = 0
        cutmap["Signal"]["Preselection"]["ID4l"]                = 0
        cutmap["Signal"]["Preselection"]["OSSF2"]               = 0
        cutmap["Signal"]["Preselection"]["Combinatorics"]       = 0
        cutmap["Signal"]["Preselection"]["Overlap"]             = 0
        cutmap["Signal"]["Preselection"]["Isolation"]           = 0
        cutmap["Signal"]["Preselection"]["Z1Mass"]              = 0
        cutmap["Signal"]["Preselection"]["Z2Mass"]              = 0
        cutmap["Signal"]["Preselection"]["LeptonPt20"]          = 0
        cutmap["Signal"]["Preselection"]["LeptonPt10"]          = 0
        cutmap["Signal"]["Preselection"]["LeptonPairMass"]      = 0
        cutmap["Signal"]["Preselection"]["InvariantMass4l"]     = 0

    event = getattr(row, 'evt')
    evPass = event in passList

    if evPass:
        passDict[event] = ["\nEVENT " + str(event) + " :", all_object_info(row,channel,objects)]

    cutmap["Signal"]["Preselection"]["Events"] += 1
    # apply lepton cuts
    if not (doubleElectronTrigger(row) or doubleMuonTrigger(row) or eMuTrigger(row)): 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Trigger"))
        return False
    cutmap["Signal"]["Preselection"]["Trigger"] += 1
    leptonCounter = 0
    for obj in objects[0:4]:
        if not objSelection(row, obj): 
            if evPass: passDict[event].append(cut_info(row, channel, objects, "ID4l"))
            return False
        leptonCounter += 1
    if leptonCounter < 4: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "ID4L"))
        return False
    cutmap["Signal"]["Preselection"]["ID4l"] += 1
    if overlap(row, *objects): 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Overlap"))
        return False
    cutmap["Signal"]["Preselection"]["Overlap"] += 1
    # OSSF2 selection
    if numberOSSF(row,channel)<2: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "OSSF2"))
        return False
    cutmap["Signal"]["Preselection"]["OSSF2"] += 1

    # Make sure this is the correct combinatorical version of this event
    ossfs = getOSSF(row, channel, *objects[0:4])
    mz1 = getattr(row, getVar2(ossfs[0], ossfs[1], 'Mass'))
    sumPt = getattr(row, getVar(ossfs[2], 'Pt')) + getattr(row, getVar(ossfs[3], 'Pt'))
    evNum = getattr(row, 'evt')
    if mz1 != comboMap[evNum][0] or sumPt != comboMap[evNum][1]: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Combo"))
        return False
    cutmap["Signal"]["Preselection"]["Combinatorics"] += 1

    # lepton isolation
    if not leptonIso(row, *objects[0:4]): 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Isolation"))
        return False
    cutmap["Signal"]["Preselection"]["Isolation"] += 1

    # apply Z cuts
    if mz1 < 60 or mz1 > 120: # 40 and 120 for H->ZZ->4l analysis
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Z1Mass"))
        return False
    cutmap["Signal"]["Preselection"]["Z1Mass"] += 1
    mz2 = getattr(row, getVar2(ossfs[2], ossfs[3], 'Mass'))
    if mz2 < 60 or mz1 > 120: # 12 and 120 for H->ZZ->4l analysis
        if evPass: passDict[event].append(cut_info(row, channel, objects, "Z2Mass"))
        return False
    cutmap["Signal"]["Preselection"]["Z2Mass"] += 1
    
    # ensure some opposite-sign pair has m > 4 GeV (don't have to have same flavor)
    found4GeVPair = False
    for pair in itertools.combinations(objects[0:4],2):
        if getattr(row, getVar2(pair[0],pair[1],'Mass')) > 4 and not getattr(row, getVar2(pair[0],pair[1], 'SS')):
            found4GeVPair = True
            break
    if not found4GeVPair: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "LeptonPairMass"))
        return False
    cutmap["Signal"]["Preselection"]["LeptonPairMass"] += 1

    # Make sure at least one lepton has pt > 20 and one more has pt > 10
    pts = leptonPts(row, *objects[0:4])
    if pts[0] < 20: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "LeptonPt20"))
        return False
    cutmap["Signal"]["Preselection"]["LeptonPt20"] += 1
    if pts[1] < 10: 
        if evPass: passDict[event].append(cut_info(row, channel, objects, "LeptonPt10"))
        return False
    cutmap["Signal"]["Preselection"]["LeptonPt10"] += 1
    
    # Make sure 4l mass > 100     H->ZZ->4l analysis only
#     if getattr(row, 'Mass') < 100: 
#         if evPass: passDict[event].append(cut_info(row, channel, objects, "InvariantMass4l"))
#         return False
#     cutmap["Signal"]["Preselection"]["InvariantMass4l"] += 1

    if evPass: passDict[event].append(cut_info(row, channel, objects, "BOOM"))
    return True

def preselectionControl(row, key, channel, cutmap, objects): #comboMap, *objects):
    # setup dictionary
    if not cutmap["Control"].has_key(key):
        cutmap["Control"][key] = {}
        cutmap["Control"][key]["Events"]            = 0
        cutmap["Control"][key]["Trigger"]           = 0
        cutmap["Control"][key]["Overlap"]           = 0
        cutmap["Control"][key]["GoodZ1"]            = 0
        if key in ["ttbar","WZ","ZJets"]:           
            cutmap["Control"][key]["OSSF2"]         = 0
            cutmap["Control"][key]["LooseID4"]      = 0
            cutmap["Control"][key]["TightID3"]      = 0 # not actually used for ZJets
            cutmap["Control"][key]["Isolation3"]    = 0 # not actually used for ZJets
        if key in ["ZLep"]:                         
            cutmap["Control"][key]["LooseID3"]      = 0
            cutmap["Control"][key]["MET25"]         = 0
        

    cutmap["Control"][key]["Events"] += 1
    # basic cuts
    if not (doubleElectronTrigger(row) or doubleMuonTrigger(row) or eMuTrigger(row)): return False
    cutmap["Control"][key]["Trigger"] += 1
    if overlap(row, *objects): return False
    cutmap["Signal"]["Preselection"]["Overlap"] += 1
    # all must have 1 good Z
    if numberOSSF(row,channel)<1: return False
    ossfs = getOSSF(row, channel, *objects[0:4])
    for obj in objects[0:2]:
        if not objSelection(row,obj): return False
    if not leptonIso(row, *objects[0:2]): return False
    mz1 = getattr(row, getVar2(ossfs[0], ossfs[1], 'Mass'))
    if mz1 < 40 or mz1 > 120: return False
    cutmap["Control"][key]["GoodZ1"] += 1

#     # Make sure this is the correct combinatorical version of this event
#     evNum = getattr(row, 'evt')
#     if mz1 != comboMap[evNum][0]: return False
#     cutmap["Control"][key]["Combinatorics"] += 1
    
    # select leptons - ZJets
    if key in ["ZJets"]:
        if len(ossfs) < 4: return False
        cutmap["Control"][key]["OSSF2"] += 1
        if not (objSelectionLoose(row,ossfs[2]) and objSelectionLoose(row,ossfs[3])): return False
        cutmap["Control"][key]["LooseID4"] += 1

    # select leptons - WZ, ttbar
    if key in ["WZ", "ttbar"]:
        if len(ossfs) < 4: return False
        cutmap["Control"][key]["OSSF2"] += 1
        if not (objSelectionLoose(row,ossfs[2]) and objSelectionLoose(row,ossfs[3])): return False
        cutmap["Control"][key]["LooseID4"] += 1
        pass2 = objSelection(row, ossfs[2])
        pass3 = objSelection(row,ossfs[3])
        if not (pass2 != pass3): return False   # != serves as xor for bools
        cutmap["Control"][key]["TightID3"] += 1
        if (pass2 and not leptonIso(row, *objects[2])) or (pass3 and not leptonIso(row, *objects[3])): return False
        cutmap["Control"][key]["Isolation3"] += 1

    # select control region events that have exactly one extra lepton passing loose cuts and small MET (used later to find lepton fake rate)
    if key in ["ZLep"]:
        if len(objects) < 3: return False
        if len(objects) > 3:  # can have > 3 objects if they're not lepton candidates
            if objects[3][0] == 'e' or objects[3][0] == 'm': return False
        if not objSelectionLoose(row, objects[2]): return False
        cutmap["Control"][key]["LooseID3"] += 1
        if not getattr(row, 'pfMetEt') < 25: return False
        cutmap["Control"][key]["MET25"] += 1
        
    return True

def selectLeptons(row, key, channel, *objects):
    selectionMap = {"Zjets":  [1,0],
                    "WW":     [0,2],
                    "WZ":     [1,1],
                    "ZZ":     [2,0],
                    "ttbar":  [0,2],
                    "ttbarW": [0,3],
                    "ttbarZ": [1,2]}
    ossfPairs = getOSSF(row, channel, *objects)
    if len(ossfPairs) == 4 and selectionMap[key][0] == 2:
        return ossfPairs
    if len(ossfPairs) == 2 and selectionMap[key][0] == 1:
        if selectionMap[key][1] == 0:
            return ossfPairs
        if selectionMap[key][1] == 1:
            leptons = ossfPairs
            for obj in objects:
                if obj not in leptons:
                   leptons.append(obj)
                   return leptons
        if selectionMap[key][1] == 2:
            leptons = ossfPairs
            for obj1 in objects:
                for obj2 in objects:
                    if obj1 != obj2 and obj1 not in leptons and obj2 not in leptons:
                        leptons.append(obj1)
                        leptons.append(obj2)
                        return leptons
    if ossfPairs == 0 and selectionMap[key][0] == 0:
            return objects[0:selectionMap[key][1]]
    # if no matches, return the highest pt leptons
    return objects[:2*selectionMap[key][0]+selectionMap[key][1]]


def getOSSF(row, channel, *objects):
    '''Will return a list of leptons in OSSF pairs in order of closest to Z mass'''
    OSSFPairs = []
    # will use the knowledge that in eeee and mmmm, the first 2 are the best Z
    # this way we can avoid combinatorics (might generalize later)
    if OSSF(row, objects[0], objects[1]): OSSFPairs.extend([objects[0],objects[1]])
    if OSSF(row, objects[2], objects[3]): OSSFPairs.extend([objects[2],objects[3]])
    if len(OSSFPairs)==4:
        mass0 = getattr(row, getVar2(OSSFPairs[0],OSSFPairs[1],'Mass'))
        mass1 = getattr(row, getVar2(OSSFPairs[2],OSSFPairs[3],'Mass'))
        if abs(mass0-90)>abs(mass1-90): 
            OSSFPairs = [OSSFPairs[2], OSSFPairs[3], OSSFPairs[0], OSSFPairs[1]]
    return OSSFPairs

def OSSF(row, obj1, obj2):
    if getattr(row, getVar2(obj1, obj2, 'SS')):          return False # require opposite sign
    if obj1[0] == obj2[0]: # Require same flavor
        return True
    return False

def onZ(row, obj1, obj2):
    if getattr(row, getVar2(obj1, obj2, 'SS')):           return False # require opposite sign
    if getattr(row, getVar2(obj1, obj2, 'Mass')) < 75.0:  return False 
    if getattr(row, getVar2(obj1, obj2, 'Mass')) > 105.0: return False
    return True

def numberOSSF(row, channel):
    if channel[0:4] == 'eemm':
       return sum([OSSF(row,'e1','e2'), OSSF(row,'m1','m2')])
    if channel[0:4] == 'eeee':
       return max(sum([OSSF(row,'e1','e2'), OSSF(row,'e3','e4')]),
                  sum([OSSF(row,'e1','e3'), OSSF(row,'e2','e4')]),
                  sum([OSSF(row,'e1','e4'), OSSF(row,'e2','e3')]))
    if channel[0:4] == 'mmmm':
       return max(sum([OSSF(row,'m1','m2'), OSSF(row,'m3','m4')]),
                  sum([OSSF(row,'m1','m3'), OSSF(row,'m2','m4')]),
                  sum([OSSF(row,'m1','m4'), OSSF(row,'m2','m3')]))

def numberOnZ(row, channel):
    if channel[0:4] == 'eemm':
       return sum([onZ(row,'e1','e2'), onZ(row,'m1','m2')])
    if channel[0:4] == 'eeee':
       return max(sum([onZ(row,'e1','e2'), onZ(row,'e3','e4')]),
                  sum([onZ(row,'e1','e3'), onZ(row,'e2','e4')]),
                  sum([onZ(row,'e1','e4'), onZ(row,'e2','e3')]))
    if channel[0:4] == 'mmmm':
       return max(sum([onZ(row,'m1','m2'), onZ(row,'m3','m4')]),
                  sum([onZ(row,'m1','m3'), onZ(row,'m2','m4')]),
                  sum([onZ(row,'m1','m4'), onZ(row,'m2','m3')]))

def numberBjet(row):
    return sum([bCSVM(row,'j1'), bCSVM(row,'j2')])

def leptonPts(row, *objects):
    ''' Returns list of lepton pts sorted high to low. Sign and flavor are ignored. Assumes exactly 4 leptons'''
    pts = []
    for lep in objects[0:4]:
        pts.append(getattr(row, getVar(lep, 'Pt')))
    pts.sort()
    pts.reverse()
    return pts

def all_object_info(row,channel,objects):
    ''' Return string with lots of useful event info'''
    objSorted = getOSSF(row,channel,*objects[0:4])
    if len(objSorted) != 4:
        objSorted = objects[0:4]
    outString = ''
    for obj in objSorted:
        outString = outString + '\n      ' + obj + ":   pt: " + str(getattr(row, getVar(obj,'Pt'))) + "  eta: " + str(getattr(row,getVar(obj, 'Eta'))) + \
            '  phi: ' + str(getattr(row,getVar(obj, 'Phi'))) 
    
    return outString

def cut_info(row, channel, objects, cutName):
    if cutName == 'BOOM':
        return '\n      BOOM'
    outString = '\n      CUT: ' + cutName
    objSorted = getOSSF(row, channel, *objects)

    if cutName == 'ID4l':
        for obj in objSorted:
            outString = outString + '\n          ' + obj + ':   SIP3D: ' + str(getattr(row,getVar(obj, 'IP3DS'))) + \
                '   IPXY: ' + str(getattr(row, getVar(obj, 'PVDXY'))) + '   IPZ: ' + str(getattr(row, getVar(obj, 'PVDZ'))) + '   ID: '
            if obj[0] == 'e':
                outString = outString + str(getattr(row, getVar(obj, 'MVAIDH2TauWP')))
            if obj[0] == 'm':
                outString = outString + str(getattr(row, getVar(obj, 'PFIDTight')))
                
    if cutName == 'Isolation':
        for obj in objSorted:
            outString = outString + '\n          ' + obj + ':   Iso: ' + str(getattr(row,getVar(obj, 'RelPFIsoDB')))
                
        
    if cutName == 'OSSF2':
        for obj in objects:
            outString = outString + '\n          ' + obj + ':   Charge: ' + str(getattr(row,getVar(obj,'Charge')))

    if cutName == 'Z1Mass' or cutName == 'Z2Mass':
        outString = outString + '\n          ' + 'Z1Mass: ' + str(getattr(row, getVar2(objSorted[0], objSorted[1], 'Mass'))) +\
            '   Z2Mass: ' + str(getattr(row, getVar2(objSorted[2], objSorted[3], 'Mass')))

    return outString
