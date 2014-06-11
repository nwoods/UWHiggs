'''
Analyze eemm events
'''

import glob
from ElecElecMuMuTree import ElecElecMuMuTree
import os
import baseSelections as selections
import mcCorrectors 
import ZZAnalyzerBase
import ROOT

class ZZAnalyzerEEMM(ZZAnalyzerBase.ZZAnalyzerBase):
    tree = 'eemm/final/Ntuple'
    def __init__(self, tree, outfile, **kwargs):
        super(ZZAnalyzerEEMM, self).__init__(tree, outfile, ElecElecMuMuTree, 'eemm', **kwargs)
        target = os.environ['megatarget']
        self.pucorrector = mcCorrectors.make_puCorrector('doublemu')
        
    def book_histos(self, folder):
        self.book_kin_histos(folder, 'e1')
        self.book_kin_histos(folder, 'e2')
        self.book_kin_histos(folder, 'm1')
        self.book_kin_histos(folder, 'm2')

        self.book_Z_histos(folder)
        self.book_event_histos(folder)

        self.objects = ['e1', 'e2', 'm1', 'm2']

    def preselection(self, row, key):
        if key == "Signal":
            return selections.preselectionSignal(row, self.channel, self.cutmap,self.comboMap, self.objects, self.passList, self.passDict)
        return selections.preselectionControl(row, key, "eemm", self.cutmap, self.objects)

    def event_weight(self, row):
        if row.run >2: 
            return 1 
        return self.pucorrector(row.nTruePU) * \
               mcCorrectors.get_electron_corrections(row, 'e1', 'e2') * \
               mcCorrectors.get_muon_corrections(row, 'm1', 'm2') 
