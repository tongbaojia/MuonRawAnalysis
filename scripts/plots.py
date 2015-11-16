"""
plots.py: script to make plots from MuonRawHits histograms. 

Run outside athena.

> python plots.py 
"""

import argparse
import copy
import glob
import multiprocessing as mp
import os
import sys
import time
import warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)

import ROOT
import rootlogon
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPadBottomMargin(0.12)

livetime_csc = 140e-9
livetime_mdt = 1300e-9

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",  help="Output directory for plots.")
    return parser.parse_args()

def main():
    
    runs = [
        # "00278880",
        # "00279169",
        # "00279345",
        # "00279685",
        # "00280464",
        # "00280673",
        "00280862",
        # "00281074",
        "00281143",
        "00281411",
        "00282992",
        "00283429",
        "00283780",
        "00284213",
        "00284285",
        ]
    
    for perbc in [False]:
        plots_vs_lumi(runs, perbc, rate=True)

    for adc in [True, False]:
        plots_vs_r(runs, adc)

    plots_vs_bcid(runs)

def plots_vs_lumi(runs, perbc, rate):

    graphical = False

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    colz()

    fits              = True
    suppress_bullshit = True
    design_bunches    = 2808.0

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    graphs = {}
    funcs  = {}
    template = "hits_vs_lumi_vs_evts_%s_%s"
    if perbc:
        template = template

    rangex = (0.2, 4.8) if not perbc else (1.2, 2.7)
    rangex = (2.0, 5.4) if not perbc else (1.2, 2.7)
    ndiv = 505

    for region in ["mdt_full",
                   "mdt_EIL1",
                   "mdt_EIS1",
                   "csc_CSL1",
                   "csc_CSS1",
                   ]:

        # for 2D plots
        ROOT.gStyle.SetPadRightMargin(0.18)
        ROOT.gStyle.SetPadBottomMargin(0.12)

        for run in runs:

            name = template % (region, run)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()

            hists[name] = input.Get(name)
            if not hists[name]:
                fatal("Cannot retrieve %s" % (name))
            yaxis = hists[name].GetYaxis()
            hists[name].GetXaxis().SetTitle(xtitle(name))
            hists[name].GetYaxis().SetTitle(ytitle(name))
            # hists[name].Rebin2D(2, 2)
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)
            hists[name].Draw("same,colz")

            pfx = name+"_pfx"
            hists[pfx] = hists[name].ProfileX(pfx, 1, -1, "")
            if suppress_bullshit:
                kill_weird_bins(hists[pfx])
            if rate:
                livetime = livetime_csc if "csc" in region else livetime_mdt
                areas = chamber_area()
                area = -1
                if region == "mdt_full": area = sum([areas[cham] for cham in filter(lambda key: not "CS" in key, areas)])
                if region == "mdt_EIL1": area = sum([areas[cham] for cham in filter(lambda key:   "EIL1" in key, areas)])
                if region == "mdt_EIL2": area = sum([areas[cham] for cham in filter(lambda key:   "EIL2" in key, areas)])
                if region == "mdt_EIS1": area = sum([areas[cham] for cham in filter(lambda key:   "EIS1" in key, areas)])
                if region == "mdt_EIS2": area = sum([areas[cham] for cham in filter(lambda key:   "EIS2" in key, areas)])
                if region == "csc_CSL1": area = sum([areas[cham] for cham in filter(lambda key:   "CSL1" in key, areas)])
                if region == "csc_CSS1": area = sum([areas[cham] for cham in filter(lambda key:   "CSS1" in key, areas)])
                hists[pfx].Scale(1.0 / (livetime * area))
                
            hists[pfx].SetLineColor(ROOT.kBlack)
            hists[pfx].SetLineWidth(3)
            hists[pfx].GetXaxis().SetRangeUser(*rangex)
            hists[pfx].GetXaxis().SetNdivisions(ndiv)
            graphs[pfx] = ROOT.TGraph(hists[pfx])
            
            if graphical:
                graphs[pfx].SetMarkerColor(color(run))
                graphs[pfx].SetLineColor(color(run))
                graphs[pfx].SetMarkerStyle(20)
                graphs[pfx].SetMarkerSize(0.8)
                graphs[pfx].SetLineWidth(2)
                graphs[pfx].Draw("Asame")
            else:
                hists[pfx].Draw("pe,same")

            draw_logos(0.36, 0.86, run)
            ROOT.gPad.RedrawAxis()
            # canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

        # for 1D plots
        ROOT.gStyle.SetPadRightMargin(0.06)
        ROOT.gStyle.SetPadBottomMargin(0.12)

        name = template % (region, "overlay")
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()

        multi = ROOT.TMultiGraph()

        xleg, yleg = 0.175, 0.86
        legend = ROOT.TLegend(xleg, yleg-(0.035*len(runs)), xleg+0.2, yleg)

        for run in runs:
            name = (template % (region, run)) + "_pfx"
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)

            hists[name].GetXaxis().SetTitle(xtitle(name))
            hists[name].GetYaxis().SetTitle(ytitle(name if not rate else name.replace("hits_", "rate_")))

            hists[name].SetMinimum(ymin(region))
            hists[name].SetMaximum(ymax(region, rate))
            hists[name].SetLineColor(color(run))
            hists[name].SetMarkerColor(color(run))
            hists[name].SetMarkerStyle(20)
            hists[name].SetMarkerSize(0.8)

            hists[name].GetXaxis().SetTitleSize(0.05)
            hists[name].GetYaxis().SetTitleSize(0.05)
            hists[name].GetXaxis().SetLabelSize(0.05)
            hists[name].GetYaxis().SetLabelSize(0.05)

            # hists[name].SetLineColor(0)

            if graphical:
                graphs[name].SetTitle(";%s;%s" % (hists[name].GetXaxis().GetTitle(),
                                                  hists[name].GetYaxis().GetTitle(),
                                                  ))
                multi.Add(graphs[name], "PZ")
            else:
                hists[name].Draw("pe,same")

            if fits:
                x1 = hists[name].GetBinCenter(hists[name].FindFirstBinAbove()-1)
                x2 = hists[name].GetBinCenter(hists[name].FindLastBinAbove()+1)
                y1 = hists[name].GetBinContent(hists[name].FindFirstBinAbove())
                y2 = hists[name].GetBinContent(hists[name].FindLastBinAbove())
                funcs[name] = ROOT.TF1("fit"+name,"[0]*(x) + [1]", x1, x2)

                m = (y2-y1)/(x2-x1)
                funcs[name].SetParameter(0, m)
                funcs[name].SetParameter(1, y1 - m*x1)

                funcs[name].SetLineColor(ROOT.kBlack)
                funcs[name].SetLineWidth(1)
                funcs[name].SetLineStyle(1)
                hists[name].Fit(funcs[name], "RWQN")
                print " [ fit ] %s: %7.2f (%5.2f), %7.2f (%5.2f) %7.2f" % (
                    run,
                    funcs[name].GetParameter(0), funcs[name].GetParError(0),
                    funcs[name].GetParameter(1), funcs[name].GetParError(1),
                    funcs[name].GetChisquare(),
                    )
                slope  = funcs[name].GetParameter(0)
                offset = funcs[name].GetParameter(1)
                chi2   = funcs[name].GetChisquare()
                funcs[name].Draw("same")

            capt = caption(run) if not fits else "%s (%.1f, %.1f)" % (caption(run), slope, offset)
                
            entry = legend.AddEntry(hists[name], capt, "")
            entry.SetTextColor(color(run))

        if graphical:
            multi.SetTitle(";%s;%s" % (multi.GetListOfGraphs()[0].GetXaxis().GetTitle(),
                                       multi.GetListOfGraphs()[0].GetYaxis().GetTitle(),
                                       ))
            multi.SetMinimum(0.00)
            multi.SetMaximum(ymax(region))
            multi.Draw("Asame")
            multi.GetXaxis().SetRangeUser(*rangex)
            multi.Draw("Asame")
            for run in runs:
                name = (template % (region, run)) + "_pfx"
                funcs[name].SetLineStyle(1)
                funcs[name].Draw("same")
            
        draw_logos(0.36, 0.89)

        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetMargin(0.3)
        legend.SetTextSize(0.03)
        legend.Draw()

        ROOT.gPad.RedrawAxis()
        canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))


def plots_vs_r(runs, adc):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)
    
    ROOT.gStyle.SetPadRightMargin(0.06)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 1

    boundary = 2050 # mm

    # area vs r
    input_area = ROOT.TFile.Open("area.root")
    area_L = input_area.Get("endcap_L_area")
    area_S = input_area.Get("endcap_S_area")

    for hist in [area_L, area_S]:
        hist.Rebin(rebin)
        style_vs_r(hist)
        draw_vs_r(hist, ops.output)

    # hits vs r
    for run in runs:

        name = "evts_%s" % (run)
        entries = input.Get(name).GetBinContent(1)

        for sector in ["L", "S"]:

            name = "hits_vs_r_%s_%s" % (sector, run)
            if adc:
                name = name.replace("_r", "_r_adc")
            hists[name] = input.Get(name)
            hists[name].Rebin(rebin)
            style_vs_r(hists[name])
            for bin in xrange(0, hists[name].GetNbinsX()+1):
                hists[name].SetBinError(bin, 0)
            draw_vs_r(hists[name], ops.output)

            numer = copy.copy(hists[name])
            denom = copy.copy(area_L if sector=="L" else area_S)

            for bin in xrange(0, denom.GetNbinsX()+1):
                radius   = denom.GetBinCenter(bin)
                area     = denom.GetBinContent(bin)
                livetime = livetime_csc if radius < boundary else livetime_mdt
                denom.SetBinContent(bin, entries * area * livetime)

            ratio = copy.copy(hists[name])
            ratio.Reset()
            ratio.Divide(numer, denom)

            name = numer.GetName().replace("hits_", "rate_")
            ratio.SetName(name)
            style_vs_r(ratio)
            ratio.GetYaxis().SetTitle(ratio.GetYaxis().GetTitle().replace("hits", "hit rate [ cm^{-2} s^{-1} ]"))
            ratio.SetMaximum(950)
            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()
            ratio.Draw("psame")

            exponential_csc = ROOT.TF1("fit_csc_"+name,"expo(0)",  950, 2000)
            exponential_mdt = ROOT.TF1("fit_mdt_"+name,"expo(0)", 2050, 4400)
            for expo in [exponential_csc,
                         exponential_mdt,
                         ]:
                expo.SetLineColor(ROOT.kBlack)
                expo.SetLineWidth(2)
                expo.SetLineStyle(7)
                ratio.Fit(expo, "RWQN")
                
                expo.Draw("same")

            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

def plots_vs_bcid(runs):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    per_event = True

    ROOT.gStyle.SetPadLeftMargin(0.08)
    ROOT.gStyle.SetPadRightMargin(0.04)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 1

    # hits vs bcid
    for run in runs:

        entries         = input.Get("evts_%s" % (run)).GetBinContent(1)
        entries_vs_bcid = input.Get("evts_vs_bcid_%s" % (run))
        actlumi_vs_bcid = input.Get("lumi_vs_bcid_%s" % (run))
        avglumi_vs_bcid = input.Get("lumi_vs_bcid_%s" % (run))

        actlumi_vs_bcid.GetYaxis().SetTitle("< inst. lumi. > per BCID per event [ e^{30} ]")
        avglumi_vs_bcid.GetYaxis().SetTitle("< inst. lumi. > per event [ e^{33} ]")

        for hist in [actlumi_vs_bcid, 
                     ]:

            hist.Divide(hist, entries_vs_bcid)
            hist.GetXaxis().SetTitle("BCID")
            hist.SetTitle("")

            for bcid in xrange(3600):
                hist.SetBinError(bcid, 0)
            style_vs_bcid(hist, per_event, setmax=4)

            name = hist.GetName()
            canvas = ROOT.TCanvas(name, name, 1600, 500)
            canvas.Draw()
            hist.Draw("histsame")
            draw_logos(xcoord=0.35, ycoord=0.85, run=run, fit=False)
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

        for det in ["mdt_full", "csc_full"]:

            name = "hits_vs_bcid_%s_%s" % (det, run)
            hists[name] = input.Get(name)
            hists[name].GetYaxis().SetTitle("< hits in %s > per event" % (det.split("_")[0].upper()))
            if per_event:
                hists[name].Divide(hists[name], entries_vs_bcid)
            setmax=4300 if "mdt" in det else 60
            style_vs_bcid(hists[name], per_event, setmax=setmax)

            canvas = ROOT.TCanvas(name, name, 1600, 500)
            canvas.Draw()
            hists[name].Draw("histsame")
            draw_logos(xcoord=0.35, ycoord=0.85, run=run, fit=False)
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

def style_vs_r(hist, ndiv=505):
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kAzure+1 if "L" in name else ROOT.kRed)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetRangeUser(700, 4700)
    hist.GetXaxis().SetTitle(xtitle(name))
    hist.GetYaxis().SetTitle(ytitle(name))
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.6)

def draw_vs_r(hist, output, height=800, width=800, drawopt="psame", logos=False):
    name = hist.GetName()
    canvas = ROOT.TCanvas(name, name, width, height)
    canvas.Draw()
    hist.Draw(drawopt)
    if logos:
        draw_logos()
    canvas.SaveAs(os.path.join(output, canvas.GetName()+".pdf"))

def style_vs_bcid(hist, per_event, ndiv=505, setmax=False):
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetLineStyle(1)
    if "lumi" in name: hist.SetFillColor(ROOT.kYellow)
    if "mdt"  in name: hist.SetFillColor(ROOT.kRed)
    if "csc"  in name: hist.SetFillColor(ROOT.kAzure+1)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetTitle(xtitle(name))
    hist.GetYaxis().SetTitle(ytitle(name))
    hist.GetYaxis().SetTitleOffset(0.65)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    if per_event and setmax:
        hist.SetMaximum(setmax)

def draw_logos(xcoord=0.5, ycoord=0.5, run=None, fit=True):

    atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
    if run:
        runz  = ROOT.TLatex(xcoord, ycoord-0.06, "Run %s" % (run))
        bunch = ROOT.TLatex(xcoord, ycoord-0.12, "%s bunches" % (bunches(run)))
    fits = ROOT.TLatex(xcoord+0.25, ycoord, "(slope, offset)")

    logos = [atlas, runz, bunch] if run else [atlas, fits]

    for logo in logos:
        ROOT.SetOwnership(logo, False)
        logo.SetTextSize(0.040)
        if logo == fits:
            logo.SetTextSize(0.03)
        logo.SetTextFont(42)
        logo.SetTextAlign(22)
        logo.SetNDC()
        logo.Draw()

    return logos

def color(run):

    if run == "00280862": return ROOT.kGray+2
    if run == "00281143": return ROOT.kOrange-3
    if run == "00281411": return ROOT.kRed
    if run == "00282992": return ROOT.kMagenta
    if run == "00283429": return ROOT.kViolet-5
    if run == "00283780": return ROOT.kBlue
    if run == "00284213": return ROOT.kAzure+1
    if run == "00284285": return 210

    if run == "00278880": return ROOT.kBlack
    if run == "00279169": return ROOT.kGray
    if run == "00279345": return ROOT.kGreen+3
    if run == "00279685": return ROOT.kOrange+7
    if run == "00280464": return ROOT.kBlack
    if run == "00280614": return ROOT.kBlack
    if run == "00280673": return ROOT.kRed
    if run == "00280862": return 210
    if run == "00281074": return ROOT.kBlue
    if run == "00281143": return ROOT.kOrange+7
    if run == "00281381": return ROOT.kViolet-5
    if run == "00281385": return ROOT.kOrange-7
    if run == "00281411": return ROOT.kOrange-3
    if run == "00282992": return ROOT.kRed+3
    if run == "00283429": return ROOT.kRed
    if run == "00283780": return ROOT.kBlue
    if run == "00284213": return ROOT.kBlack
    if run == "00284285": return ROOT.kBlack

def ymax(region, rate=False):
    if region == "mdt_full": return 6100 if not rate else   30
    if region == "mdt_EIL1": return  550 if not rate else  200
    if region == "mdt_EIS1": return  380 if not rate else  200
    if region == "mdt_EIL2": return  180
    if region == "mdt_EIS2": return   90
    if region == "mdt_EIL3": return  100
    if region == "mdt_EIS3": return  100
    if region == "csc_full": return  100
    if region == "csc_CSL1": return   50 if not rate else 1000
    if region == "csc_CSS1": return   40 if not rate else 1000
    fatal("no ymax for %s" % (region))
    
def ymin(region):
    if region == "mdt_full": return 0
    if region == "mdt_EIL1": return 0
    if region == "mdt_EIL2": return 0
    if region == "mdt_EIL3": return 0
    if region == "mdt_EIS1": return 0
    if region == "mdt_EIS2": return 0
    if region == "mdt_EIS3": return 0
    if region == "csc_full": return 0
    if region == "csc_CSL1": return 0
    if region == "csc_CSS1": return 0
    fatal("no ymin for %s" % (region))

def xtitle(name):
    if "_vs_bcid" in name: return "BCID"
    if "_vs_r"    in name: return "radius [mm]"
    if "_vs_lumi" in name: return "< inst. lumi. > [e^{33}_cm^{-2}_s^{-1}_]".replace("_", "#scale[0.5]{ }")
    
    if "endcap"   in name: return xtitle("_vs_r")

    return "fuck"

def ytitle(name):
    if "hits_vs_lumi" in name or "hits_vs_bcid" in name:
        if "mdt_full" in name: return      "< MDT hits per event >"
        if "mdt_EIL1" in name: return "< MDT EIL1 hits per event >"
        if "mdt_EIL2" in name: return "< MDT EIL2 hits per event >"
        if "mdt_EIS1" in name: return "< MDT EIS1 hits per event >"
        if "mdt_EIS2" in name: return "< MDT EIS2 hits per event >"
        if "csc_full" in name: return      "< CSC hits per event >"
        if "csc_CSL1" in name: return    "< CSC L hits per event >"
        if "csc_CSS1" in name: return    "< CSC S hits per event >"
    if "rate_vs_lumi" in name:
        unit = "[Hz / cm^{2}]"
        if "mdt_full" in name: return      "MDT hit rate %s" % (unit)
        if "mdt_EIL1" in name: return "MDT EIL1 hit rate %s" % (unit)
        if "mdt_EIL2" in name: return "MDT EIL2 hit rate %s" % (unit)
        if "mdt_EIS1" in name: return "MDT EIS1 hit rate %s" % (unit)
        if "mdt_EIS2" in name: return "MDT EIS2 hit rate %s" % (unit)
        if "csc_full" in name: return      "CSC hit rate %s" % (unit)
        if "csc_CSL1" in name: return    "CSC L hit rate %s" % (unit)
        if "csc_CSS1" in name: return    "CSC S hit rate %s" % (unit)

    if "lumi_vs_bcid" in name: return "< inst. lumi. > [e^{30}_cm^{-2}_s^{-1}_]".replace("_", "#scale[0.5]{ }")
    if "hits_vs_r"    in name: return "< hits per event >"
    if "rate_vs_r"    in name: return "hit rate [Hz / cm^{2}]"

    if name == "endcap_L_area": return "L area [cm^{2}]"
    if name == "endcap_S_area": return "S area [cm^{2}]"

    return "fuck"
            
def caption(run):
    return "%s, %s bunches" % (int(run), bunches(run))

def bunches(run):
    if run == "00278880": return  447
    if run == "00279169": return  733
    if run == "00279345": return  877
    if run == "00279598": return 1021
    if run == "00279685": return 1021
    if run == "00280231": return 1165
    if run == "00280464": return 1309
    if run == "00280614": return 1309
    if run == "00280673": return 1453
    if run == "00280862": return 1453
    if run == "00281074": return 1596
    if run == "00281143": return 1596
    if run == "00281381": return 1813
    if run == "00281385": return 1813
    if run == "00281411": return 1813
    if run == "00282992": return 1813
    if run == "00283429": return 2029
    if run == "00283780": return 2232
    if run == "00284213": return 2232
    if run == "00284285": return 2232

def kill_weird_bins(hist):
    for bin in xrange(1, hist.GetNbinsX()):
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
        if hist.GetBinContent(bin-2) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+2) == 0:
            hist.SetBinContent(bin, 0)

def chamber_area():

    pkg   = "/Users/alexandertuna/Downloads/MuonRawHits/"
    areas = {}
    # here  = os.path.abspath(__file__)
    geo   = os.path.join(pkg, "data/geometry")

    mm2_to_cm2 = (1/10.0)*(1/10.0)

    for detector in ["mdt_chambers.txt",
                     "csc_chambers.txt",
                     ]:
        for line in open(os.path.join(geo, detector)).readlines():
            line = line.strip()
            if not line:
                continue
            
            _, chamber, area = line.split()
            areas[chamber] = float(area) * mm2_to_cm2
            
    return areas

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def colz():
    import array
    ncontours = 200
    stops = array.array("d", [0.0, 0.3, 0.6, 1.0])
    red   = array.array("d", [1.0, 1.0, 1.0, 0.0])
    green = array.array("d", [1.0, 1.0, 0.0, 0.0])
    blue  = array.array("d", [1.0, 0.0, 0.0, 0.0])
    
    ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)


if __name__ == "__main__":
    main()


