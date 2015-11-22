#include "MuonRawAnalysis/MuonRawHistograms.h"

#include <iostream>
#include <vector>
#include <string>
#include <chrono>

#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

MuonRawHistograms::MuonRawHistograms(std::string ipath, std::string opath){
    input_path  = ipath;
    output_path = opath;
}

MuonRawHistograms::~MuonRawHistograms(){}

int MuonRawHistograms::initialize(){

    file = TFile::Open(input_path.c_str());
    if (!file)
        std::cout << "\n FATAL FUCK MuonRawHistograms::initialize: no file \n" << std::endl;

    tree = (TTree*)(file->Get("physics"));
    if (!tree)
        std::cout << "\n FATAL FUCK MuonRawHistograms::initialize: no tree \n" << std::endl;

    announce();
    initialize_branches();
    initialize_histograms();
    
    return 0;
}

int MuonRawHistograms::execute(int ents){

    int ent = 0;
    int ch  = 0;
    int hit = 0;
    int hit_rad = 0;
    int hit_adc = 0;

    int hits_mdt_full = 0;
    int hits_mdt_EIL1 = 0;
    int hits_mdt_EIL2 = 0;
    int hits_mdt_EIS1 = 0;
    int hits_mdt_EIS2 = 0;

    int hits_mdt_EML1 = 0;
    int hits_mdt_EML2 = 0;
    int hits_mdt_EML3 = 0;
    int hits_mdt_EMS1 = 0;
    int hits_mdt_EMS2 = 0;
    int hits_mdt_EMS3 = 0;

    int hits_csc_full = 0;
    int hits_csc_CSL1 = 0;
    int hits_csc_CSS1 = 0;

    std::string chamber_side = "";
    std::string chamber_type = "";
    int         chamber_eta  = 0;
    int         chamber_phi  = 0;
    int         chamber_hits = 0;
    
    int tree_entries = (int)(tree->GetEntries());
    if (ents < 0 || ents > tree_entries)
        entries = tree_entries;
    else
        entries = ents;

    time_start = std::chrono::system_clock::now();

    for (ent = 1; ent < entries; ++ent){

        tree->GetEntry(ent);

        if (ent % 5000 == 0) {
            printf("%8i / %8i \n", ent, entries);
            printf("\033[F\033[J");
        } 

        hits_mdt_full = 0;
        hits_mdt_EIL1 = 0;
        hits_mdt_EIL2 = 0;
        hits_mdt_EIS1 = 0;
        hits_mdt_EIS2 = 0;

        hits_mdt_EML1 = 0;
        hits_mdt_EML2 = 0;
        hits_mdt_EML3 = 0;
        hits_mdt_EMS1 = 0;
        hits_mdt_EMS2 = 0;
        hits_mdt_EMS3 = 0;

        hits_csc_full = 0;
        hits_csc_CSL1 = 0;
        hits_csc_CSS1 = 0;

        for (ch = 0; ch < mdt_chamber_n; ++ch){

            chamber_hits = mdt_chamber_tube_n->at(ch);
            chamber_eta  = mdt_chamber_eta_station->at(ch);
            chamber_phi  = mdt_chamber_phi_sector->at(ch);
            chamber_type = mdt_chamber_type->at(ch);
            chamber_side = mdt_chamber_side->at(ch);

            hits_mdt_full += chamber_hits;
            if (chamber_type=="EIL" && chamber_eta==1) hits_mdt_EIL1 += chamber_hits;
            if (chamber_type=="EIL" && chamber_eta==2) hits_mdt_EIL2 += chamber_hits;
            if (chamber_type=="EIS" && chamber_eta==1) hits_mdt_EIS1 += chamber_hits;
            if (chamber_type=="EIS" && chamber_eta==2) hits_mdt_EIS2 += chamber_hits;
            if (chamber_type=="EML" && chamber_eta==1) hits_mdt_EML1 += chamber_hits;
            if (chamber_type=="EML" && chamber_eta==2) hits_mdt_EML2 += chamber_hits;
            if (chamber_type=="EML" && chamber_eta==3) hits_mdt_EML3 += chamber_hits;
            if (chamber_type=="EMS" && chamber_eta==1) hits_mdt_EMS1 += chamber_hits;
            if (chamber_type=="EMS" && chamber_eta==2) hits_mdt_EMS2 += chamber_hits;
            if (chamber_type=="EMS" && chamber_eta==3) hits_mdt_EMS3 += chamber_hits;

            if (chamber_type=="EIL" && (chamber_eta==1 || chamber_eta==2)){
                for (hit = 0; hit < chamber_hits; ++hit){

                    hit_rad = (mdt_chamber_tube_r->at(ch)).at(hit);
                    hit_adc = (mdt_chamber_tube_adc->at(ch)).at(hit);
                    hits_vs_r_L->Fill(hit_rad, prescale_HLT);
                    if (hit_adc > 50)
                        hits_vs_r_adc_L->Fill(hit_rad, prescale_HLT);

                    if (chamber_phi ==  1) hits_vs_r_L_01->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  3) hits_vs_r_L_03->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  5) hits_vs_r_L_05->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  7) hits_vs_r_L_07->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  9) hits_vs_r_L_09->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 11) hits_vs_r_L_11->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 13) hits_vs_r_L_13->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 15) hits_vs_r_L_15->Fill(hit_rad, prescale_HLT);
                }
            }
            if (chamber_type=="EIS" && (chamber_eta==1 || chamber_eta==2)){
                for (hit = 0; hit < chamber_hits; ++hit){

                    hit_rad = (mdt_chamber_tube_r->at(ch)).at(hit);
                    hit_adc = (mdt_chamber_tube_adc->at(ch)).at(hit);
                    hits_vs_r_S->Fill(hit_rad, prescale_HLT);
                    if (hit_adc > 50)
                        hits_vs_r_adc_S->Fill(hit_rad, prescale_HLT);

                    if (chamber_phi ==  2) hits_vs_r_S_02->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  4) hits_vs_r_S_04->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  6) hits_vs_r_S_06->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  8) hits_vs_r_S_08->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 10) hits_vs_r_S_10->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 12) hits_vs_r_S_12->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 14) hits_vs_r_S_14->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 16) hits_vs_r_S_16->Fill(hit_rad, prescale_HLT);
                }
            }
        }
        
        for (ch = 0; ch < csc_chamber_n; ++ch){

            chamber_hits = csc_chamber_cluster_n->at(ch);
            chamber_type = csc_chamber_type->at(ch);
            chamber_phi  = csc_chamber_phi_sector->at(ch);

            hits_csc_full += chamber_hits;
            if (chamber_type=="CSL") hits_csc_CSL1 += chamber_hits;
            if (chamber_type=="CSS") hits_csc_CSS1 += chamber_hits;

            if (chamber_type=="CSL"){
                for (hit = 0; hit < chamber_hits; ++hit){

                    hit_rad = (csc_chamber_cluster_r->at(ch)).at(hit);
                    hit_adc = (csc_chamber_cluster_qmax->at(ch)).at(hit);
                    hits_vs_r_L->Fill(hit_rad, prescale_HLT);
                    if (hit_adc > 25*1000)
                        hits_vs_r_adc_L->Fill(hit_rad, prescale_HLT);

                    if (chamber_phi ==  1) hits_vs_r_L_01->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  3) hits_vs_r_L_03->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  5) hits_vs_r_L_05->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  7) hits_vs_r_L_07->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  9) hits_vs_r_L_09->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 11) hits_vs_r_L_11->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 13) hits_vs_r_L_13->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 15) hits_vs_r_L_15->Fill(hit_rad, prescale_HLT);
                }
            }
            if (chamber_type=="CSS"){
                for (hit = 0; hit < chamber_hits; ++hit){

                    hit_rad = (csc_chamber_cluster_r->at(ch)).at(hit);
                    hit_adc = (csc_chamber_cluster_qmax->at(ch)).at(hit);
                    hits_vs_r_S->Fill(hit_rad, prescale_HLT);
                    if (hit_adc > 25*1000)
                        hits_vs_r_adc_S->Fill(hit_rad, prescale_HLT);

                    if (chamber_phi ==  2) hits_vs_r_S_02->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  4) hits_vs_r_S_04->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  6) hits_vs_r_S_06->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi ==  8) hits_vs_r_S_08->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 10) hits_vs_r_S_10->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 12) hits_vs_r_S_12->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 14) hits_vs_r_S_14->Fill(hit_rad, prescale_HLT);
                    if (chamber_phi == 16) hits_vs_r_S_16->Fill(hit_rad, prescale_HLT);
                }
            }
        }
        
        evts->Fill(                                          1, prescale_HLT);
        evts_vs_lumi->Fill(         lbAverageLuminosity/1000.0, prescale_HLT);

        hits_vs_lumi_mdt_full->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_full);

        hits_vs_lumi_mdt_EIL1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EIL1);
        hits_vs_lumi_mdt_EIL2->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EIL2);
        hits_vs_lumi_mdt_EIS1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EIS1);
        hits_vs_lumi_mdt_EIS2->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EIS2);

        hits_vs_lumi_mdt_EML1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EML1);
        hits_vs_lumi_mdt_EML2->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EML2);
        hits_vs_lumi_mdt_EML3->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EML3);
        hits_vs_lumi_mdt_EMS1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EMS1);
        hits_vs_lumi_mdt_EMS2->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EMS2);
        hits_vs_lumi_mdt_EMS3->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_mdt_EMS3);

        hits_vs_lumi_csc_full->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_csc_full);
        hits_vs_lumi_csc_CSL1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_csc_CSL1);
        hits_vs_lumi_csc_CSS1->Fill(lbAverageLuminosity/1000.0, prescale_HLT*hits_csc_CSS1);

        hits_vs_lumi_vs_evts_mdt_full->Fill(lbAverageLuminosity/1000.0, hits_mdt_full, prescale_HLT);
        hits_vs_lumi_vs_evts_mdt_EIL1->Fill(lbAverageLuminosity/1000.0, hits_mdt_EIL1, prescale_HLT);
        hits_vs_lumi_vs_evts_mdt_EIL2->Fill(lbAverageLuminosity/1000.0, hits_mdt_EIL2, prescale_HLT);
        hits_vs_lumi_vs_evts_mdt_EIS1->Fill(lbAverageLuminosity/1000.0, hits_mdt_EIS1, prescale_HLT);
        hits_vs_lumi_vs_evts_mdt_EIS2->Fill(lbAverageLuminosity/1000.0, hits_mdt_EIS2, prescale_HLT);
        hits_vs_lumi_vs_evts_csc_full->Fill(lbAverageLuminosity/1000.0, hits_csc_full, prescale_HLT);
        hits_vs_lumi_vs_evts_csc_CSL1->Fill(lbAverageLuminosity/1000.0, hits_csc_CSL1, prescale_HLT);
        hits_vs_lumi_vs_evts_csc_CSS1->Fill(lbAverageLuminosity/1000.0, hits_csc_CSS1, prescale_HLT);

        evts_vs_bcid->Fill(         bcid, prescale_HLT);
        lumi_vs_bcid->Fill(         bcid, prescale_HLT*lbLuminosityPerBCID);
        hits_vs_bcid_mdt_full->Fill(bcid, prescale_HLT*hits_mdt_full);
        hits_vs_bcid_csc_full->Fill(bcid, prescale_HLT*hits_csc_full);

    }

    time_end = std::chrono::system_clock::now();
    elapsed_seconds = time_end - time_start;

    printf("%8i / %8i in %.2f s = %.2f Hz\n", ent, entries, elapsed_seconds.count(), (float)(entries) / elapsed_seconds.count());

    return 0;
}

int MuonRawHistograms::finalize(){

    output = TFile::Open(output_path.c_str(), "recreate");
    output->cd();

    for (auto hist: histograms1D) hist->Write();
    for (auto hist: histograms2D) hist->Write();
    
    output->Close();
    
    return 0;
}

void MuonRawHistograms::announce(){
    
    std::cout << std::endl;
    std::cout << "   input | " <<  input_path        << std::endl;
    std::cout << "  output | " << output_path        << std::endl;
    std::cout << " entries | " << tree->GetEntries() << std::endl;
    std::cout << std::endl;
}

void MuonRawHistograms::initialize_branches(){

    tree->SetBranchAddress("RunNumber",           &RunNumber);
    tree->SetBranchAddress("EventNumber",         &EventNumber);
    tree->SetBranchAddress("lbn",                 &lbn);
    tree->SetBranchAddress("bcid",                &bcid);
    tree->SetBranchAddress("colliding_bunches",   &colliding_bunches);
    tree->SetBranchAddress("avgIntPerXing",       &avgIntPerXing);
    tree->SetBranchAddress("actIntPerXing",       &actIntPerXing);
    tree->SetBranchAddress("lbAverageLuminosity", &lbAverageLuminosity);
    tree->SetBranchAddress("lbLuminosityPerBCID", &lbLuminosityPerBCID);
    tree->SetBranchAddress("prescale_L1",         &prescale_L1);
    tree->SetBranchAddress("prescale_HLT",        &prescale_HLT);

    tree->SetBranchAddress("mdt_chamber_n",           &mdt_chamber_n);
    tree->SetBranchAddress("mdt_chamber_type",        &mdt_chamber_type);
    tree->SetBranchAddress("mdt_chamber_side",        &mdt_chamber_side);
    tree->SetBranchAddress("mdt_chamber_eta_station", &mdt_chamber_eta_station);
    tree->SetBranchAddress("mdt_chamber_phi_sector",  &mdt_chamber_phi_sector);

    tree->SetBranchAddress("mdt_chamber_tube_n",      &mdt_chamber_tube_n);
    tree->SetBranchAddress("mdt_chamber_tube_r",      &mdt_chamber_tube_r);
    tree->SetBranchAddress("mdt_chamber_tube_adc",    &mdt_chamber_tube_adc);

    tree->SetBranchAddress("csc_chamber_n",              &csc_chamber_n);
    tree->SetBranchAddress("csc_chamber_r",              &csc_chamber_r);
    tree->SetBranchAddress("csc_chamber_type",           &csc_chamber_type);
    tree->SetBranchAddress("csc_chamber_side",           &csc_chamber_side);
    tree->SetBranchAddress("csc_chamber_phi_sector",     &csc_chamber_phi_sector);

    tree->SetBranchAddress("csc_chamber_cluster_n",      &csc_chamber_cluster_n);
    tree->SetBranchAddress("csc_chamber_cluster_r",      &csc_chamber_cluster_r);
    tree->SetBranchAddress("csc_chamber_cluster_rmax",   &csc_chamber_cluster_rmax);
    tree->SetBranchAddress("csc_chamber_cluster_qsum",   &csc_chamber_cluster_qsum);
    tree->SetBranchAddress("csc_chamber_cluster_qmax",   &csc_chamber_cluster_qmax);
    tree->SetBranchAddress("csc_chamber_cluster_strips", &csc_chamber_cluster_strips);
}

void MuonRawHistograms::initialize_histograms(){

    tree->GetEntry(1);
    std::string run = std::to_string(RunNumber);
    run = "00"+run;

    int xbins = 0; float xlo = 0; float xhi = 0;
    int ybins = 0; float ylo = 0;

    evts = new TH1F(("evts_"+run).c_str(), "", 1, 0, 2);
    
    xbins = 200; xlo = 0; xhi = 6;
    evts_vs_lumi          = new TH1F(("evts_vs_lumi_"+run).c_str(),          "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_full = new TH1F(("hits_vs_lumi_mdt_full_"+run).c_str(), "", xbins, xlo, xhi);

    hits_vs_lumi_mdt_EIL1 = new TH1F(("hits_vs_lumi_mdt_EIL1_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EIL2 = new TH1F(("hits_vs_lumi_mdt_EIL2_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EIS1 = new TH1F(("hits_vs_lumi_mdt_EIS1_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EIS2 = new TH1F(("hits_vs_lumi_mdt_EIS2_"+run).c_str(), "", xbins, xlo, xhi);

    hits_vs_lumi_mdt_EML1 = new TH1F(("hits_vs_lumi_mdt_EML1_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EML2 = new TH1F(("hits_vs_lumi_mdt_EML2_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EML3 = new TH1F(("hits_vs_lumi_mdt_EML3_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EMS1 = new TH1F(("hits_vs_lumi_mdt_EMS1_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EMS2 = new TH1F(("hits_vs_lumi_mdt_EMS2_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_mdt_EMS3 = new TH1F(("hits_vs_lumi_mdt_EMS3_"+run).c_str(), "", xbins, xlo, xhi);

    hits_vs_lumi_csc_full = new TH1F(("hits_vs_lumi_csc_full_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_csc_CSL1 = new TH1F(("hits_vs_lumi_csc_CSL1_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_lumi_csc_CSS1 = new TH1F(("hits_vs_lumi_csc_CSS1_"+run).c_str(), "", xbins, xlo, xhi);

    xbins = 200; xlo = 0; xhi = 6;
    ybins = 200; ylo = 0;
    hits_vs_lumi_vs_evts_mdt_full = new TH2F(("hits_vs_lumi_vs_evts_mdt_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, 5000);
    hits_vs_lumi_vs_evts_mdt_EIL1 = new TH2F(("hits_vs_lumi_vs_evts_mdt_EIL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  500);
    hits_vs_lumi_vs_evts_mdt_EIL2 = new TH2F(("hits_vs_lumi_vs_evts_mdt_EIL2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_vs_lumi_vs_evts_mdt_EIS1 = new TH2F(("hits_vs_lumi_vs_evts_mdt_EIS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  400);
    hits_vs_lumi_vs_evts_mdt_EIS2 = new TH2F(("hits_vs_lumi_vs_evts_mdt_EIS2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_vs_lumi_vs_evts_csc_full = new TH2F(("hits_vs_lumi_vs_evts_csc_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_vs_lumi_vs_evts_csc_CSL1 = new TH2F(("hits_vs_lumi_vs_evts_csc_CSL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_vs_lumi_vs_evts_csc_CSS1 = new TH2F(("hits_vs_lumi_vs_evts_csc_CSS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);

    xbins = 500; xlo = 0; xhi = 5200;
    hits_vs_r_L     = new TH1F(("hits_vs_r_L_"    +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_adc_L = new TH1F(("hits_vs_r_adc_L_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_01  = new TH1F(("hits_vs_r_L_01_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_03  = new TH1F(("hits_vs_r_L_03_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_05  = new TH1F(("hits_vs_r_L_05_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_07  = new TH1F(("hits_vs_r_L_07_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_09  = new TH1F(("hits_vs_r_L_09_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_11  = new TH1F(("hits_vs_r_L_11_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_13  = new TH1F(("hits_vs_r_L_13_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_L_15  = new TH1F(("hits_vs_r_L_15_" +run).c_str(), "", xbins, xlo, xhi);

    xbins = 500; xlo = 0; xhi = 5440;
    hits_vs_r_S     = new TH1F(("hits_vs_r_S_"    +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_adc_S = new TH1F(("hits_vs_r_adc_S_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_02  = new TH1F(("hits_vs_r_S_02_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_04  = new TH1F(("hits_vs_r_S_04_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_06  = new TH1F(("hits_vs_r_S_06_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_08  = new TH1F(("hits_vs_r_S_08_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_10  = new TH1F(("hits_vs_r_S_10_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_12  = new TH1F(("hits_vs_r_S_12_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_14  = new TH1F(("hits_vs_r_S_14_" +run).c_str(), "", xbins, xlo, xhi);
    hits_vs_r_S_16  = new TH1F(("hits_vs_r_S_16_" +run).c_str(), "", xbins, xlo, xhi);

    xbins = 3600; xlo = 0; xhi = 3600;
    evts_vs_bcid          = new TH1F(("evts_vs_bcid_"+run).c_str(),          "", xbins, xlo, xhi);
    lumi_vs_bcid          = new TH1F(("lumi_vs_bcid_"+run).c_str(),          "", xbins, xlo, xhi);
    hits_vs_bcid_mdt_full = new TH1F(("hits_vs_bcid_mdt_full_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_bcid_csc_full = new TH1F(("hits_vs_bcid_csc_full_"+run).c_str(), "", xbins, xlo, xhi);

    histograms1D.push_back(evts);
    histograms1D.push_back(evts_vs_lumi);
    histograms1D.push_back(evts_vs_bcid);
    histograms1D.push_back(lumi_vs_bcid);

    histograms1D.push_back(hits_vs_lumi_mdt_full);
    histograms1D.push_back(hits_vs_lumi_mdt_EIL1);
    histograms1D.push_back(hits_vs_lumi_mdt_EIL2);
    histograms1D.push_back(hits_vs_lumi_mdt_EIS1);
    histograms1D.push_back(hits_vs_lumi_mdt_EIS2);

    histograms1D.push_back(hits_vs_lumi_mdt_EML1);
    histograms1D.push_back(hits_vs_lumi_mdt_EML2);
    histograms1D.push_back(hits_vs_lumi_mdt_EML3);
    histograms1D.push_back(hits_vs_lumi_mdt_EMS1);
    histograms1D.push_back(hits_vs_lumi_mdt_EMS2);
    histograms1D.push_back(hits_vs_lumi_mdt_EMS3);

    histograms1D.push_back(hits_vs_lumi_csc_full);
    histograms1D.push_back(hits_vs_lumi_csc_CSL1);
    histograms1D.push_back(hits_vs_lumi_csc_CSS1);

    histograms2D.push_back(hits_vs_lumi_vs_evts_mdt_full);
    histograms2D.push_back(hits_vs_lumi_vs_evts_mdt_EIL1);
    histograms2D.push_back(hits_vs_lumi_vs_evts_mdt_EIL2);
    histograms2D.push_back(hits_vs_lumi_vs_evts_mdt_EIS1);
    histograms2D.push_back(hits_vs_lumi_vs_evts_mdt_EIS2);
    histograms2D.push_back(hits_vs_lumi_vs_evts_csc_full);
    histograms2D.push_back(hits_vs_lumi_vs_evts_csc_CSL1);
    histograms2D.push_back(hits_vs_lumi_vs_evts_csc_CSS1);

    histograms1D.push_back(hits_vs_r_L);
    histograms1D.push_back(hits_vs_r_adc_L);
    histograms1D.push_back(hits_vs_r_S);
    histograms1D.push_back(hits_vs_r_adc_S);

    histograms1D.push_back(hits_vs_r_L_01);
    histograms1D.push_back(hits_vs_r_L_03);
    histograms1D.push_back(hits_vs_r_L_05);
    histograms1D.push_back(hits_vs_r_L_07);
    histograms1D.push_back(hits_vs_r_L_09);
    histograms1D.push_back(hits_vs_r_L_11);
    histograms1D.push_back(hits_vs_r_L_13);
    histograms1D.push_back(hits_vs_r_L_15);

    histograms1D.push_back(hits_vs_r_S_02);
    histograms1D.push_back(hits_vs_r_S_04);
    histograms1D.push_back(hits_vs_r_S_06);
    histograms1D.push_back(hits_vs_r_S_08);
    histograms1D.push_back(hits_vs_r_S_10);
    histograms1D.push_back(hits_vs_r_S_12);
    histograms1D.push_back(hits_vs_r_S_14);
    histograms1D.push_back(hits_vs_r_S_16);

    histograms1D.push_back(hits_vs_bcid_mdt_full);
    histograms1D.push_back(hits_vs_bcid_csc_full);

    for (auto hist: histograms1D) hist->Sumw2();
    for (auto hist: histograms2D) hist->Sumw2();

    for (auto hist: histograms1D){
        hist->SetMarkerStyle(20);
        hist->SetMarkerSize(1);
    }

}
