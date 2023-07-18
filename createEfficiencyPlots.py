import argparse
import numpy as np
import ROOT
import uproot

def main(infile_path, outdir, variable, nbins, xmin, xmax):
    
    # open input ROOT file with uproot
    f = uproot.open( infile_path )
    
    # grab efficiency tree
    effTree = f["l1NtupleSingleProducer/efficiencyTree"]
    
    # load branches for cuts into awkward arrays
    genEta = effTree["genEta"].array()
    genPt = effTree["genPt"].array()
    gct_cPt = effTree["gct_cPt"].array()
    
    # load variable of interest
    var = effTree[variable].array()
    
    # apply cuts to variable of interest (change cuts manually here if desired)
    var_genCut = var[(np.abs(genEta) < 1.4841) & (genPt > 10)]
    var_l1Cut = var[(np.abs(genEta) < 1.4841) & (genPt > 10) & (gct_cPt > 3)]
    
    # create numerator and denominator histograms
    numerator = ROOT.TH1F("numerator", "numerator", nbins, xmin, xmax)
    denominator = ROOT.TH1F("denominator", "denominator", nbins, xmin, xmax)
    
    # fill histograms
    for i in range(len(var_genCut)):
        denominator.Fill(var_genCut[i])

    for i in range(len(var_l1Cut)):
        numerator.Fill(var_l1Cut[i])

    # "Create structure to store sum of squares of weights."
    denominator.Sumw2()
    numerator.Sumw2()
    
    # divide to get efficiency
    numerator.Divide(denominator)
    
    # convert to TGraphAsymmErrors
    effAsym = ROOT.TGraphAsymmErrors(numerator)

    # ensure errors don't exceed (0,1) range
    for i in range(nbins):
        val = effAsym.GetPointY(i)
        errlow = effAsym.GetErrorYlow(i)
        errhigh = effAsym.GetErrorYhigh(i)

        if val+errhigh > 1:
            errhigh = 1-val
        if val-errlow < 0:
            errlow = val

        effAsym.SetPointError(i, 0.0, 0.0, errlow, errhigh)

    # draw
    c1 = ROOT.TCanvas( 'c1', 'c1', 10, 10, 600, 600 )
    effAsym.SetTitle("Efficiency")
    effAsym.SetLineColor(4)
    effAsym.SetMarkerColor(4)
    effAsym.SetMarkerSize(0.7)
    effAsym.SetMarkerStyle(8)
    effAsym.GetXaxis().SetTitle(variable)
    effAsym.GetYaxis().SetTitle("Efficiency")
    effAsym.Draw("AP")

    c1.Draw()
    c1.SaveAs(f"{outdir}/efficiency_{variable}.png")
    c1.Close()
    
    
    
    
if __name__ == "__main__":
    
    # parse arguments
    parser = argparse.ArgumentParser(description="This program creates and saves rate plots starting from histograms.")
    parser.add_argument("-i", "--infile_path", help="path to input ROOT file containing histograms")
    parser.add_argument("-o", "--outdir", help="path to directory to save plot", default=".")
    parser.add_argument("-v", "--variable", help="name of variable to create efficiency plot for")
    parser.add_argument("--nbins", help="number of bins in histogram", default=25)
    parser.add_argument("--low", help="minimum value of histogram", default=0.0)
    parser.add_argument("--high", help="maximum value of histogram", default=100.0)
    
    
    # run main
    main(args.infile_path, args.outdir, args.variable, int(args.nbins), float(args.low), float(args.high))
