"""
area.py -- a script to write a root file of the MDT/CSC area.
"""
import os
import ROOT

def main():

    print
    hists = []

    hists += area_vs_region()
    hists += area_vs_r("EI")
    hists += area_vs_r("EM")

    for phi in xrange(1, 17):
        hists += area_vs_r("EI", "%02i" % phi)

    output = ROOT.TFile.Open("area.root", "recreate")
    for hist in hists:
        output.cd()
        hist.Write()
    output.Close()
    print

def area_vs_region():

    xaxis = "eta station"
    yaxis = "chamber type"

    xbins, xlo, xhi = 17, -8.5, 8.5
    ybins, ylo, yhi =  8,  0.5, 8.5

    area_L = ROOT.TH2F("area_vs_region_L", ";%s;%s;%s" % (xaxis, yaxis, "area: L [cm^{2}]"), xbins, xlo, xhi, ybins, ylo, yhi)
    area_S = ROOT.TH2F("area_vs_region_S", ";%s;%s;%s" % (xaxis, yaxis, "area: S [cm^{2}]"), xbins, xlo, xhi, ybins, ylo, yhi)
    hists = [area_L, area_S]

    all_chambers, all_areas = geometry_all_chambers()

    # mdt geometry
    for chamber, area in zip(all_chambers, all_areas):

        chamber_type = chamber[:3]
        chamber_eta  = int(chamber[3])
        chamber_side = chamber[4]

        if chamber_type[2]=="L": area_L.Fill(chamber_eta*sign(chamber_side), ybin(chamber_type), area)
        if chamber_type[2]=="S": area_S.Fill(chamber_eta*sign(chamber_side), ybin(chamber_type), area)

    # turn off uncertainties
    for hist in hists:
        for bin in xrange(0, hist.GetNbinsX()+1):
            hist.SetBinError(bin, 0.0)
        ROOT.SetOwnership(hist, False)

    return hists

def area_vs_r(layer, phi=""):

    xaxis = "radius [mm]"

    mdt_chambers, mdt_radii, mdt_areas, mdt_timings = geometry_mdt_tubes(layer)
    csc_chambers, csc_radii, csc_areas, csc_timings = geometry_csc_strips()

    name_L = "area_vs_r_%sL" % (layer)
    name_S = "area_vs_r_%sS" % (layer)
    if phi:
        name_L += "_%s" % (phi)
        name_S += "_%s" % (phi)

    if layer == "EI":

        area_vs_r_EIL = ROOT.TH1F(name_L, ";%s;%s;" % (xaxis, "area: L [cm^{2}]"), 500, 0, 5200)
        area_vs_r_EIS = ROOT.TH1F(name_S, ";%s;%s;" % (xaxis, "area: S [cm^{2}]"), 500, 0, 5440)
        hists = [area_vs_r_EIL, area_vs_r_EIS]

        for chamber, radius, area, timing in zip(mdt_chambers, mdt_radii, mdt_areas, mdt_timings):
            if   ("EIL1" in chamber or "EIL2" in chamber) and chamber.endswith(phi): area_vs_r_EIL.Fill(radius, area)
            elif ("EIS1" in chamber or "EIS2" in chamber) and chamber.endswith(phi): area_vs_r_EIS.Fill(radius, area)
            else:
                continue
        for chamber, radius, area, timing in zip(csc_chambers, csc_radii, csc_areas, csc_timings):
            if   "CSL" in chamber and chamber.endswith(phi): area_vs_r_EIL.Fill(radius, area)
            elif "CSS" in chamber and chamber.endswith(phi): area_vs_r_EIS.Fill(radius, area)
            else:
                continue

    if layer == "EM":

        area_vs_r_EML = ROOT.TH1F(name_L, ";%s;%s;" % (xaxis, "area: L [cm^{2}]"), 450, 1500, 6000)
        area_vs_r_EMS = ROOT.TH1F(name_S, ";%s;%s;" % (xaxis, "area: S [cm^{2}]"), 450, 1500, 6000)
        hists = [area_vs_r_EML, area_vs_r_EMS]

        for chamber, radius, area, timing in zip(mdt_chambers, mdt_radii, mdt_areas, mdt_timings):
            if   ("EML1" in chamber or "EML2" in chamber) and chamber.endswith(phi): area_vs_r_EML.Fill(radius, area)
            elif ("EMS1" in chamber or "EMS2" in chamber) and chamber.endswith(phi): area_vs_r_EMS.Fill(radius, area)
            else:
                continue

    # turn off uncertainties
    for hist in hists:
        for bin in xrange(0, hist.GetNbinsX()+1):
            hist.SetBinError(bin, 0.0)
        ROOT.SetOwnership(hist, False)

    # dont bother with empty histograms
    hists = filter(lambda hist: hist.Integral() > 0, hists)

    return hists

def geometry_all_chambers():

    mm2_to_cm2  = (1/10.0)*(1/10.0)
    muonrawhits = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geometry    = os.path.join(muonrawhits, "data/geometry/all_chambers.txt")
    geometry    = geometry.replace("MuonRawAnalysis", "MuonRawHits")

    chambers = []
    areas    = []

    print " - retrieving geometry from %s" % (geometry)

    for line in open(geometry).readlines():
        line = line.strip()
        if not line:
            continue
        _, chamber, area = line.split()

        chambers.append(chamber)
        areas.append(float(area)*mm2_to_cm2)

    return chambers, areas

def geometry_mdt_tubes(layer):

    livetime    = 1300e-9
    mm2_to_cm2  = (1/10.0)*(1/10.0)
    muonrawhits = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geometry    = os.path.join(muonrawhits, "data/geometry/mdt_tubes_%s.txt" % (layer))
    geometry    = geometry.replace("MuonRawAnalysis", "MuonRawHits")

    chambers = []
    radii    = []
    areas    = []
    times    = []

    print " - retrieving geometry from %s" % (geometry)

    for line in open(geometry).readlines():
        line = line.strip()
        if not line:
            continue
        _, chamber, ml, layer, tube, r, radius, length, area = line.split()

        chambers.append(chamber)
        radii.append(float(r))
        areas.append(float(area)*mm2_to_cm2)
        times.append(float(livetime))

    return chambers, radii, areas, times

def geometry_csc_strips():

    livetime    = 140e-9
    mm2_to_cm2  = (1/10.0)*(1/10.0)
    muonrawhits = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geometry    = os.path.join(muonrawhits, "data/geometry/csc_strips.txt")
    geometry    = geometry.replace("MuonRawAnalysis", "MuonRawHits")

    chambers = []
    radii    = []
    areas    = []
    times    = []

    print " - retrieving geometry from %s" % (geometry)

    for line in open(geometry).readlines():
        line = line.strip()
        if not line:
            continue
        _, chamber, layer, strip, r, length, width, area = line.split()

        chambers.append(chamber)
        radii.append(float(r))
        areas.append(float(area)*mm2_to_cm2)
        times.append(float(livetime))

    return chambers, radii, areas, times

def ybin(chamber_type):
    if chamber_type == "BIL" or chamber_type == "BIS": return 1
    if chamber_type == "BML" or chamber_type == "BMS": return 2
    if chamber_type == "BOL" or chamber_type == "BOS": return 3
    if chamber_type == "EIL" or chamber_type == "EIS": return 4
    if chamber_type == "EEL" or chamber_type == "EES": return 5
    if chamber_type == "EML" or chamber_type == "EMS": return 6
    if chamber_type == "EOL" or chamber_type == "EOS": return 7
    if chamber_type == "CSL" or chamber_type == "CSS": return 8
    return 0

def sign(chamber_side):
    if chamber_side == "A": return  1
    if chamber_side == "C": return -1
    return 0

if __name__ == "__main__":
    main()
