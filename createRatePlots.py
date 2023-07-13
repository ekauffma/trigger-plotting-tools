import argparse
import numpy as np
import ROOT

def getRatioHist(inputhist, nevents):
    
    # get bin content
    hist_vals = np.zeros(150)
    for i in range(150):
        hist_vals[i] = inputhist.GetBinContent(i)
        
    # sum bins for rates hist
    hist_sums = np.zeros(150)
    for i in range(150):
        hist_sums[i] = sum(hist_vals[i:])
        
    # initialize rates hist
    ratesHist = ROOT.TH1F("Rates", "Rates", 150, 0, 150)
    ratesHist.Sumw2()

    # fill rates hist with sums
    for i in range(150):
        ratesHist.SetBinContent(i, hist_sums[i])
        
    # normalize to number of events
    ratesHist.Scale(1.00 / nevents)
    
    # scale to 40kHz
    ratesHist.Scale(40.0 * 1000000.0 / 1000.0)
    
    return ratesHist
    
    

def main(infile_path, outdir, histname, basehist):
    
    # open input ROOT file
    inFile = ROOT.TFile.Open( infile_path ,"READ")
    
    # get number of events
    nEvents = inFile.Get("l1NtupleProducer/nEvents")
    nEvts = nEvents.GetEntries()
    
    # get histograms of interest from ROOT file and create rates histogram
    hist1 = inFile.Get(f"l1NtupleProducer/{basehist}")
    rateshist1 = getRatioHist(hist1, nEvts)
    hist2 = inFile.Get(f"l1NtupleProducer/{histname}")
    rateshist2 = getRatioHist(hist2, nEvts)
    
    c = ROOT.TCanvas( 'c', 'c', 10, 10, 600, 600 )
    rateshist1.SetLineColor(1)
    rateshist1.SetMarkerColor(1)
    rateshist1.SetMarkerStyle(8)
    rateshist1.SetMarkerSize(0.5)
    rateshist1.SetTitle("")
    rateshist1.GetXaxis().SetTitle("p_T threshold [GeV]")
    rateshist1.GetXaxis().SetRange(0,60)
    rateshist1.GetYaxis().SetTitle("Rate [kHz]")
    rateshist1.SetMaximum(1e5)
    rateshist1.SetStats(False)
    rateshist1.Draw("PE")
    
    rateshist2.SetLineColor(2)
    rateshist2.SetMarkerColor(2)
    rateshist2.SetMarkerStyle(22)
    rateshist2.SetMarkerSize(1)
    rateshist2.SetStats(False)
    rateshist2.Draw("PE same")
    
    legend = ROOT.TLegend(0.25,0.7,0.9,0.85)
    legend.AddEntry(rateshist1,basehist,"PE")
    legend.AddEntry(rateshist2,histname,"PE")
    legend.SetBorderSize(0);
    legend.SetTextSize(0.03);
    legend.Draw()

    ROOT.gPad.SetLogy()
    c.Draw()
    c.SaveAs(f"{outdir}/rates_{histname}.png")
    c.Close()
    
    
    
    
if __name__ == "__main__":
    
    # parse arguments
    parser = argparse.ArgumentParser(description="This program creates and saves rate plots starting from histograms.")
    parser.add_argument("-i", "--infile_path", help="path to input ROOT file containing histograms")
    parser.add_argument("-o", "--outdir", help="path to directory to save plot", default=".")
    parser.add_argument("-n", "--histname", help="name of histogram to turn into rate plot")
    parser.add_argument("-b", "--basehist", help="name of histogram to use for comparison", default="l1eg_pt")
    
    args = parser.parse_args()
    
    # run main
    main(args.infile_path, args.outdir, args.histname, args.basehist)