'''
Analyze eeee events
'''

import glob
from ElecElecElecElecTree import ElecElecElecElecTree
import os
import baseSelections as selections
import mcCorrectors
import ZZAnalyzerBase
import ROOT

class ZZAnalyzerEEEE(ZZAnalyzerBase.ZZAnalyzerBase):
    tree = 'eeee/final/Ntuple'
    def __init__(self, tree, outfile, **kwargs):
        super(ZZAnalyzerEEEE, self).__init__(tree, outfile, ElecElecElecElecTree, 'eeee', **kwargs)
        target = os.environ['megatarget']
        self.pucorrector = mcCorrectors.make_puCorrector('doublee')
        
    def book_histos(self, folder):
        self.book_kin_histos(folder, 'e1')
        self.book_kin_histos(folder, 'e2')
        self.book_kin_histos(folder, 'e3')
        self.book_kin_histos(folder, 'e4')

        self.book_Z_histos(folder)
        self.book_event_histos(folder)

        self.objects = ['e1', 'e2', 'e3', 'e4']

#    def preselection(self, row):
#        if not selections.doubleElectronTrigger(row): return False
#        self.cutlist[2][2] += 1
#        if not selections.vetoes(row): return False
#        self.cutlist[3][2] += 1
#        if selections.overlap(row, 'e1', 'e2', 'e3', 'e4'): return False
#        self.cutlist[4][2] += 1
#        if not selections.eSelection(row,'e1'):   return False
#        self.cutlist[5][2] += 1
#        if not selections.eSelection(row,'e2'):   return False
#        self.cutlist[6][2] += 1
#        if not selections.eSelection(row,'e3'):   return False
#        self.cutlist[7][2] += 1 
#        if not selections.eSelection(row,'e4'):   return False
#        self.cutlist[8][2] += 1
#        if not selections.leptonIso(row,'e1','e2','e3','e4'):     return False
#        self.cutlist[9][2] += 1 
#        if not selections.preZSelection(row,'e1','e2','e3','e4'): return False
#        self.cutlist[10][2] += 1
#        return True

    def preselection(self, row, key):
        if key == "Signal":
            return selections.preselectionSignal(row, self.channel, self.cutmap, self.comboMap, self.objects)#'e1', 'e2', 'e3', 'e4')
        return selections.preselectionControl(row, key, "eeee", self.cutmap, self.objects)#'e1','e2','e3','e4')

    def event_weight(self, row):
        if row.run >2:
            return 1
        return self.pucorrector(row.nTruePU) * \
               mcCorrectors.get_electron_corrections(row, 'e1', 'e2', 'e3', 'e4')
