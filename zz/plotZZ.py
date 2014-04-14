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
from array import array
from dataStyles import data_styles

#from dataStyles import data_styles

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
    def __init__(self, channel):
        '''Initialize the ZZ Plotter'''
        self.canvas = ROOT.TCanvas("c1","c1",700,700)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gROOT.ForceStyle()
        # define samples, jobid, and channel
        self.bkgs = [ 'DYJets*', 'Zjets_M50', 'WWJets*', 'WZJets*', 'TTplusJets_madgraph', 'GluGluToHToZZ*' ]
        self.sigs = ['ZZJetsTo4L_pythia']
        self.data = []
        self.channel = [channel]
        if channel[0:4] == "comb":
            self.data += ['*data_DoubleMu*']
            self.data += ['*data_DoubleElectron*']
            self.data += ['*data_MuEG*']
            self.channel = ['eeee', 'eemm', 'mmmm']
        else:
            if channel[2:4] == 'mm': self.data += ['data_DoubleMu*']
            if channel[0:2] == 'ee': self.data += ['data_DoubleElectron*']
            if channel == 'eemm':    self.data += ['data_MuEG*']
        self.samples_all = self.data[:] + self.bkgs[:] + self.sigs[:]
        self.jobid = os.environ['jobid']
        self.period = '7TeV' if '7TeV' in self.jobid else '8TeV'
        self.sqrts = 7 if '7TeV' in self.jobid else 8
#         self.blind = blind
        self.outputdir = 'results/%s/plots/%s' % (self.jobid, channel )
        python_mkdir(self.outputdir)
        self.hists = {'sig': [], 'bkg': {}, 'dat': []}
#        self.bkgNames = []
        self.setup_samples()
        self.ZZMassMinMaxStep = [64, 706, 6]
#        self.xAxisRange = [64, 6]
        self.rebin = 5

    def get_files_lumis_names(self, samples, channel):
        '''Find and return unix style paths to root files and lumicalc sums'''
        fileNames = []
        lumiNames = []
        output = {}
        for x in samples:
            fileNames += glob.glob('results/%s/ZZAnalyzer%s/%s.root' % (self.jobid, channel.upper(), x))
            lumiNames += glob.glob('inputs/%s/%s.lumicalc.sum' % (self.jobid, x))
        for f, l in zip(fileNames, lumiNames):
            name = f.replace('results/%s/ZZAnalyzer%s/' % (self.jobid, channel.upper()), '').replace('.root', '')
            lumi = self.get_lumi(l)
            output[name] = {'file': f, 'lumi': lumi, 'tfile': ROOT.TFile(f)}
        return output

    def get_lumi(self, lumifile):
        f = open(lumifile)
        output = float(f.readline())
        f.close()
        return output
        
    def setup_samples(self):
        # build sample dictionary
        self.samples = {}
        for channel in self.channel:
            self.samples[channel] = {}
            self.samples[channel]['bkg'] = self.get_files_lumis_names(self.bkgs, channel)
            self.samples[channel]['sig'] = self.get_files_lumis_names(self.sigs, channel)
            self.samples[channel]['dat'] = self.get_files_lumis_names(self.data, channel)

        self.intLumi = self.get_int_lumi()

    def get_int_lumi(self):
        '''Find the total integrated luminosity of the dataset'''
        intlumi = {}
        for channel in self.channel:
            intlumi[channel] = 0
            for sample, data in self.samples[channel]['dat'].iteritems():
                intlumi[channel] += data['lumi']

        return max(intlumi.itervalues()) / 3.

        # if len(self.channel) == 3:
        #     intLumi = intLumi/3. # 3 datasets used
        # elif self.channel[0] == "eemm":
        #     intLumi = intLumi/3. # 3 datasets used
        # 
        # return intLumi

    def get_hist(self, tfile, folder, var, isMC=False, lumi=1.):    #, color):
        '''Return a histogram of var from folder in TFile(filename), scaled by luminosity'''
#         theFile = ROOT.TFile(filename)
        hist = tfile.Get(folder + "/" + var).Clone("h")
        if isMC:
            hist.Scale(self.intLumi/lumi)        
            
        if self.rebin > 0:
            hist.Rebin(self.rebin)
            
        return hist

    def make_stack(self, bkg, sig):
        ''' 
        Makes a stack plot of background and signal histograms, with signal on top. 
        Expects single signal histogram, dictionary of bkg histograms in same format as make_legend
        '''
        colors = [ROOT.EColor.kWhite, ROOT.EColor.kCyan, ROOT.EColor.kGreen, ROOT.EColor.kViolet, ROOT.EColor.kBlue, ROOT.EColor.kRed, ROOT.EColor.kOrange]
        colorCounter = 0
        stack = ROOT.THStack("stack", "Monte Carlo Signal + Background")
        for bname, bhist in bkg.iteritems():
            bhist.SetFillStyle(1001)
            bhist.SetFillColor(colors[colorCounter])
            bhist.SetLineColor(ROOT.EColor.kBlack)  #colors[colorCounter])
            colorCounter = (colorCounter + 1) % len(colors)
            stack.Add(bhist)
        sig.SetFillStyle(1001)
        sig.SetFillColor(colors[colorCounter])
        sig.SetLineColor(ROOT.EColor.kBlack) #colors[colorCounter])
        stack.Add(sig)
        return stack

    def add_hists(self, histlist, weights=[]):
        ''' Takes a list of histograms and returns their sum. They better have the same binning...'''
        if len(histlist) == 0:
            return ROOT.TH1F("","",self.ZZMassMinMaxStep[2],self.ZZMassMinMaxStep[0],self.ZZMassMinMaxStep[1])
        if len(weights) != len(histlist):
            if weights != []:
                print "Different number of weights and histograms! Using w=1 for all of them (" + str(len(histlist)) + "," + str(len(weights)) + ")"
            weights = [1] * len(histlist)
        output = histlist[0].Clone()
        output.Scale(weights[0])
        for h, w in zip(histlist[1:], weights[1:]):
            output.Add(h, w)
        
        return output

    def make_legend(self, bkgDict, sig, data, bounds=[0.33, 0.6, 0.9, 0.9]):
        ''' 
        Makes a legend for background, signal, and data histograms, with boundaries in list bounds.
        bkgDict should be in the format {sample1Name: sample1Hist, sample2Name: sample2Hist ... }
        bounds must be a list of length 4, in the format [x1, y1, x2, y2], in the top right corner by default.
        '''
        leg = ROOT.TLegend(*bounds)
        leg.SetFillColor(ROOT.EColor.kWhite)
        for bkgName, bkgHist in bkgDict.iteritems():
            leg.AddEntry(bkgHist, bkgName, "F")
        leg.AddEntry(sig, "ZZ MC", "F")
        leg.AddEntry(data, "4l Inv Mass", "LPE")
        leg.SetTextSize(0.02)
        return leg

    def make_all_hists(self, variable):       #, colors):
#         colorCounter = 0
        folder = 'Signal/Preselection'
        for channel, samples in self.samples.iteritems():
            for source, data in samples.iteritems():
                for name, info in data.iteritems():
                    h = self.get_hist(info['tfile'], folder, variable, (source == 'bkg' or source == 'sig'), info['lumi'])
                    if type(h).__name__ != 'PyROOT_NoneType':
                        if source == 'bkg':
                            if not name in self.hists['bkg']:
                                self.hists['bkg'][name] = []
                            self.hists['bkg'][name].append(h)
                        else:
                            self.hists[source].append(h)
                            

    def construct_bkg_hists(self):
        sampleMap = {}
        for name, hList in self.hists['bkg'].iteritems():
            sampleMap[name] = self.add_hists(hList)
        return sampleMap

    def make_final_hists(self):
        bkg = self.construct_bkg_hists()
        sig = self.add_hists(self.hists['sig'])
        dat = self.add_hists(self.hists['dat'])

        mcStack = self.make_stack(bkg, sig)
        dat.SetMarkerColor(ROOT.EColor.kBlack)
        dat.SetLineColor(ROOT.EColor.kBlack)
        return (mcStack, dat, bkg, sig)

    def get_ratio(self, num, denom, label):
        '''Return a ratio histogram'''
        num.Sumw2()
        num.SetMarkerSize(0.8)
        num.Divide(num, denom, 1., 1., "")
        return num

    def draw_ratio_plot(self, data, mcStack, pad):
        mchist = mcStack.GetStack().Last().Clone("mchist")
        ratio = self.get_ratio(data,mchist,"ratio")
        ratio.SetLineWidth(1)

        ratiostaterr = self.get_ratio_stat_err(mchist)
#         ratiostaterr.GetXaxis().SetTitle(xaxis)
        ratiostaterr.GetXaxis().SetRangeUser(data.GetXaxis().GetXmin(),data.GetXaxis().GetXmin())
        ratiounity = ROOT.TLine(data.GetXaxis().GetXmin(),1,data.GetXaxis().GetXmax(),1)
        ratiounity.SetLineStyle(2)

        pad.cd()
        pad.Draw()
        pad.SetGridy(0)
        ratiostaterr.Draw("e2")
        # ratiostaterr.Draw("e2 same")
        ratiounity.Draw("same")
        ratio.Draw("e1 same")
        

    def get_ratio_stat_err(self, hist):
        '''Return a statistical error bars for a ratio plot'''
        ratiostaterr = hist.Clone("ratiostaterr")
        ratiostaterr.Sumw2()
        ratiostaterr.SetStats(0)
        ratiostaterr.SetTitle("")
        ratiostaterr.GetYaxis().SetTitle("Data/MC")
        ratiostaterr.SetMaximum(3.2)
        ratiostaterr.SetMinimum(0)
        ratiostaterr.SetMarkerSize(0)
        ratiostaterr.SetFillColor(ROOT.EColor.kGray+3)
        ratiostaterr.SetFillStyle(3013)
        ratiostaterr.GetXaxis().SetLabelSize(0.12)
        ratiostaterr.GetXaxis().SetTitleSize(0.14)
        ratiostaterr.GetXaxis().SetTitleOffset(1.10)
        ratiostaterr.GetYaxis().SetLabelSize(0.10)
        ratiostaterr.GetYaxis().SetTitleSize(0.12)
        ratiostaterr.GetYaxis().SetTitleOffset(0.3)
        ratiostaterr.GetYaxis().SetNdivisions(505)

        # bin by bin errors
        for i in range(hist.GetNbinsX()+2):
            ratiostaterr.SetBinContent(i, 1.0)
            if hist.GetBinContent(i)>1e-6:  # not empty
                binerror = hist.GetBinError(i) / hist.GetBinContent(i)
                ratiostaterr.SetBinError(i, binerror)
            else:
                ratiostaterr.SetBinError(i, 999.)

        return ratiostaterr


    def plot_save(self, title, xTitle, yTitle, outFile, printLumi=True):
        (mc,dat,bkg,sig) = self.make_final_hists()

        self.canvas.cd()
 
        plotpad = ROOT.TPad("plotpad", "top pad"   , 0.0, 0.3, 1.0, 1.0)
        plotpad.SetBottomMargin(0.0)
        plotpad.Draw()
        ratiopad = ROOT.TPad("ratiopad", "bottom pad", 0.0, 0.0, 1.0, 0.3)
        ratiopad.SetTopMargin(0.0)
        ratiopad.SetBottomMargin(0.35)
        ratiopad.Draw()

        plotpad.cd()

        # Plot data + mc
        dat.SetTitle(title)
        dat.GetXaxis().SetTitle(xTitle)
        dat.GetYaxis().SetTitle(yTitle)
        dat.Draw("e")
        mc.Draw("histsame")
        dat.Draw("esame")

        # Draw Legend
        legend = self.make_legend(bkg, sig, dat)
        legend.Draw("same")

        ratiopad.SetGridy(0)
        ratiopad.cd()

        mchist = mc.GetStack().Last().Clone("mchist")
        ratio = self.get_ratio(dat.Clone("ratio"),mc.GetStack().Last().Clone("mchist"),"ratio")
        ratio.SetLineWidth(1)

        ratiostaterr = self.get_ratio_stat_err(mc.GetStack().Last().Clone("mchist2"))
#         ratiostaterr.GetXaxis().SetTitle(xaxis)
        ratiostaterr.GetXaxis().SetRangeUser(dat.GetXaxis().GetXmin(),dat.GetXaxis().GetXmin())
        ratiounity = ROOT.TLine(dat.GetXaxis().GetXmin(),1,dat.GetXaxis().GetXmax(),1)
        ratiounity.SetLineStyle(2)

        ratiopad.cd()
        ratio.Draw("e1")
        ratiounity.Draw("same")
        ratiostaterr.Draw("e2same")
        ratiostaterr.Draw("e2same")

#        ratiopad.cd()
#        ratiopad.SetGridy(0)
#        ratiostaterr.Draw("e2")
#        ratiostaterr.Draw("e2 same")
#        ratiounity.Draw("same")
#        if plotdata: ratio.Draw("e1 same")
#        if plotsig: ratiosig.Draw("hist same")

        if printLumi:
            self.canvas.cd()
            pave = ROOT.TPaveText(0.35,0.91,0.95,0.94,"NDC")
            pave.SetBorderSize(0)
            pave.SetFillColor(0)
            pave.AddText("CMS Preliminary   #sqrt{s} = 8 TeV   #int L dt = %.1f fb^{-1}" % (self.intLumi/1000))
            pave.Draw()

        self.canvas.Print(outFile)



####################################################################################################################
####                                        Make a ZZ mass spectrum                                             ####
####################################################################################################################

plotter = plotZZ("comb")
plotter.setup_samples()
plotter.make_all_hists('Z1_Z2_Mass')
plotter.plot_save("ZZ Invariant Mass 8TeV", "Inv Mass (GeV)", "Events", "~nwoods/www/ZZMass.png")
