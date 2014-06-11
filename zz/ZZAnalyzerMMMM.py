'''
Analyze mmmm events
'''

import glob
from MuMuMuMuTree import MuMuMuMuTree
import os
import baseSelections as selections
import mcCorrectors 
import ZZAnalyzerBase
import ROOT

class ZZAnalyzerMMMM(ZZAnalyzerBase.ZZAnalyzerBase):
    tree = 'mmmm/final/Ntuple'
    def __init__(self, tree, outfile, **kwargs):
        super(ZZAnalyzerMMMM, self).__init__(tree, outfile, MuMuMuMuTree, 'mmmm', **kwargs)
        target = os.environ['megatarget']
        self.pucorrector = mcCorrectors.make_puCorrector('doublemu')
        
    def book_histos(self, folder):
        self.book_kin_histos(folder, 'm1')
        self.book_kin_histos(folder, 'm2')
        self.book_kin_histos(folder, 'm3')
        self.book_kin_histos(folder, 'm4')

        self.book_Z_histos(folder)
        self.book_event_histos(folder)

        self.objects = ['m1', 'm2', 'm3', 'm4']


    def preselection(self, row, key):
        if key == "Signal":
            return selections.preselectionSignal(row, self.channel, self.cutmap, self.comboMap, self.objects, self.passList, self.passDict)
        return selections.preselectionControl(row,key,"mmmm",self.cutmap, self.objects)

    def event_weight(self, row):
        if row.run >2:
            return 1
        return self.pucorrector(row.nTruePU) * \
               mcCorrectors.get_muon_corrections(row, 'm1', 'm2', 'm3', 'm4')
