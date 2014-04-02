'''
Plotting script for ZZ analysis

Nate Woods, UW Madison
With significant portions cribbed from Devin Taylor and others
'''


import sys
import os
import errno
import glob
import ROOT

from dataStyles import data_styles

ROOT.gROOT.SetBatch(ROOT.kTRUE)

os.environ['jobid'] = '2014-03-03-8TeV'

def python_mkdir(dir):
    '''A function to make a unix directory as well as subdirectories'''
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise


class plotZZ(object):
    '''A plotting class to be used in the FinalStateAnalysis Framework'''
    def __init__(self, channel, blind=False):
        '''Initialize the ZZ Plotter'''
        self.canvas = ROOT.TCanvas("c1","c1",700,700)
        self.channel = channel
        ROOT.gStyle.SetOptStat(0)
        # define samples, jobid, and channel
        self.bkgs = [ 'DYJets*', 'Zjets_M50', 'WWJets*', 'WZJets*', 'TTplusJets_madgraph', 'GluGluToHToZZ*' ]
        self.sigs = ['ZZ4M_powheg', 'ZZ4E_powheg', 'ZZ2E2M_powheg', 'ggZZ4L', 'ggZZ2L2L']
        self.data = []
        if channel[0:4] == "comb":
            self.data += ['data_DoubleMu*']
            self.data += ['data_DoubleElectron*']
            self.data += ['data_MuEG*']
        else:
            if channel[2:4] == 'mm': self.data += ['data_DoubleMu*']
            if channel[0:2] == 'ee': self.data += ['data_DoubleElectron*']
            if channel == 'eemm':    self.data += ['data_MuEG*']
        self.samples_all = self.data[:] + self.bkgs[:] + self.sigs[:]
        self.jobid = os.environ['jobid']
        self.channel = channel
        self.period = '7TeV' if '7TeV' in self.jobid else '8TeV'
        self.sqrts = 7 if '7TeV' in self.jobid else 8
        self.blind = blind
        self.outputdir = 'results/%s/plots/%s' % (self.jobid, channel )
        python_mkdir(self.outputdir)
        self.setup_samples()

    def get_files_lumis_names(self, samples):
        '''Find and return unix style paths to root files and lumicalc sums'''
        fileNames = []
        lumiNames = []
        for x in samples:
            fileNames += glob.glob('results/%s/ZZAnalyzer%s/%s.root' % (self.jobid, self.channel.upper(), x))
            lumiNames += glob.glob('inputs/%s/%s.lumicalc.sum' % (self.jobid, x))
        for f, l in zip(fileNames, lumiNames):
            name = f.replace('results/%s/ZZAnalyzer%s/' % (self.jobid, self.channel.upper()), '').replace('.root', '')
            (dataFile, lumi) = get_file_and_lumi(f, l)
            output[name] = {'file': dataFile, 'lumi': lumi}
        return output

    def get_file_and_lumi(self, datafile,lumifile):
        f = open(lumifile)
        output = (ROOT.TFile(datafile), float(f.readline()))
        f.close()
        return output
        
    def setup_samples(self):
        # build sample dictionary
        self.samples = {}
        self.samples['bkg'] = self.get_files_lumis_names(self.bkgs)
        self.samples['sig'] = self.get_files_lumis_names(self.sigs)
        self.samples['dat'] = self.get_files_lumis_names(self.data)

        self.intLumi = self.get_int_lumi(self.datanames)

    def get_int_lumi(self, samples):
        '''Find the total integrated luminosity of the dataset'''
        intLumi = 0
        for sample in samples:
            intLumi += self.samples[sample]['lumi']
        if self.channel[0:7] == "combine":
            intLumi = intLumi/3. # 3 datasets used
        if self.channel[0:4] == "eemm":
            intLumi = intLumi/3. # 3 datasets used
        return intLumi

    def get_hist(self, filename, folder, var):
        '''Return a histogram of var from folder in TFile(filename)'''
        hist = ROOT.TFile(filename).Get(folder + "/" + var).Clone("h")
        return hist
