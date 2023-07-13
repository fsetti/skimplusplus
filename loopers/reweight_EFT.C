#pragma GCC diagnostic ignored "-Wsign-compare"
#include "TFile.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TMath.h"
#include "TTree.h"
#include "TBranch.h"
#include "TChain.h"
#include "THStack.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "TObjString.h"
#include "TTreeCache.h"
#include "TGraphErrors.h"
#include "TTreePerfStats.h"
#include "TTreeCacheUnzip.h"

#include "../NanoCORE/Nano_v9.cc"
#include "../NanoCORE/tqdm.h"
#include "../NanoCORE/utils.cc"
#include "../VSEVA/HHWWgg/reweight/reweight_HH.C"

#include <string>
#include <iostream>
#include <iomanip>

using namespace std;
using namespace tas;

float br_hgg = 0.00227;
float	br_htt = 0.0627;
float br_hww = 0.214;

float br_wlnu = 0.317;
float br_wqq = 0.683;

float	br_hgghtt 				= 2 * br_hgg * br_htt;
float	br_ggWW_dilep 		= 2 * br_hgg * br_hww * ( br_wlnu * br_wlnu );
float	br_ggWW_semilep 	= 2 * br_hgg * br_hww * ( 2 * br_wlnu * br_wqq );


ReweightMandrik rm_pw_NLO = ReweightMandrik("", "VSEVA/HHWWgg/reweight/pm_pw_LO-Ais-13TeV_V2.txt", "VSEVA/HHWWgg/reweight/pm_pw_NLO_Ais_13TeV_V2.txt");

int make_hist( TChain *ch, string proc, string str_year, string tag, float scales1fb_kl0, float scales1fb_kl1, float scales1fb_kl2p45, float scales1fb_kl5 ) {

  int year;
  if ( str_year == "2016_APV") year = 2016;
  else { year = stoi(str_year); }

	TString fname = "/ceph/cms/store/user/fsetti/EFT_samples/" + tag + "/hists/" + str_year + "/" + proc + ".root";
	TFile* f1 = new TFile( fname, "RECREATE");

	const Int_t NCostHHbin = 4;
	Double_t edges_cos[NCostHHbin + 1] = {0.0, 0.4, 0.6, 0.8, 1.0};
	const Int_t NMHHbin = 36;
	Double_t edges_mhh[NMHHbin + 1] = {250., 270.,  290.,  310.,  330., 350.,   370.,  390.,  410.,  430., 450., 470.,  490.,  510.,  530., 550.,   570.,  590., 610.,  630., 650., 670., 700.,  750., 800., 850., 900., 950., 1000., 1100., 1200., 1300., 1400., 1500., 1750., 2000., 5000.};

	TH2F *h = new TH2F("histo_Nev","histo_Nev", NMHHbin, edges_mhh, NCostHHbin, edges_cos );

  int nEventsTotal = 0;
  int nEventsChain = ch->GetEntries();
  TFile *currentFile = 0;
  TObjArray *listOfFiles = ch->GetListOfFiles();
  TIter fileIter(listOfFiles);
  tqdm bar;

  while ( (currentFile = (TFile*)fileIter.Next()) ) {
  	TFile *file = TFile::Open( currentFile->GetTitle() );
  	TTree *tree = (TTree*)file->Get("Events");

		string curr_fname = currentFile->GetTitle();
		float scale1fb;
		if 			(curr_fname.find(std::string("cHHH0")) != std::string::npos)				scale1fb = scales1fb_kl0;
		else if (curr_fname.find(std::string("cHHH1")) != std::string::npos)				scale1fb = scales1fb_kl1;
		else if (curr_fname.find(std::string("cHHH2p45")) != std::string::npos)			scale1fb = scales1fb_kl2p45;
		else if (curr_fname.find(std::string("cHHH5")) != std::string::npos)				scale1fb = scales1fb_kl5;

  	tree->SetCacheSize(128*1024*1024);
  	tree->SetCacheLearnEntries(100);

		nt.SetYear(year);
  	nt.Init(tree);

  	for( unsigned int loop_event = 0; loop_event < tree->GetEntriesFast(); ++loop_event) {

			nt.GetEntry(loop_event);
			
			nEventsTotal++;
			bar.progress(nEventsTotal, nEventsChain);

			//account for instabilities in event weights
			if ( fabs(genWeight()) >= 0.5 ) continue;

			vector<unsigned int> HH_idx;
			for (unsigned int i=0; i<nGenPart(); i++){
				if ( GenPart_pdgId()[i] == 25 && GenPart_statusFlags()[i] & (1 << 13) ) HH_idx.push_back(i);
			}

			auto H1 = GenPart_p4()[HH_idx[0]];
			auto H2 = GenPart_p4()[HH_idx[1]];

			float mHH		= ( H1 + H2 ).M();
 			float HH_CS	= fabs( getCosThetaStar_CS_old( H1, H2 ) );

			h->Fill( mHH, HH_CS, genWeight() * scale1fb );

  	} // Event loop
  	delete file;
  } // File loop
  bar.finish();

	f1->Write();
	f1->Close();

	return 0;
}


int ScanChain( TChain *ch, string proc, string str_year, string eft_bm, string tag, float scales1fb_kl0, float scales1fb_kl1, float scales1fb_kl2p45, float scales1fb_kl5 ) {

	TString file_name = "/ceph/cms/store/user/fsetti/EFT_samples/" + tag + "/hists/" + str_year + "/" + proc + ".root";
	TFile* inputfile =  new TFile(file_name);
	TH2F* histo_Nev = (TH2F*) inputfile->Get("histo_Nev");
	double Nevtot = histo_Nev->Integral();
	
	vector<double> couplings = rm_pw_NLO.GetEFTBenchmark(eft_bm);
	double XStot = get_eft_xsec_13TeV(eft_bm,"nlo");	

  int year;
  if ( str_year == "2016_APV") year = 2016;
  else { year = stoi(str_year); }

	float br_spec;
	if 			(proc.find(std::string("HH_ggTauTau")) != std::string::npos)							br_spec = br_hgghtt;
	else if (proc.find(std::string("HH_ggWW_dileptonic")) != std::string::npos)				br_spec = br_ggWW_dilep;
	else if (proc.find(std::string("HH_ggWW_semileptonic")) != std::string::npos)			br_spec = br_ggWW_semilep;
	else { cout << "Something went wrong. Cannot compute the right branching ratio for the process. " << endl; }

  int nEventsTotal = 0;
  int nEventsChain = ch->GetEntries();
  TFile *currentFile = 0;
  TObjArray *listOfFiles = ch->GetListOfFiles();
  TIter fileIter(listOfFiles);
  tqdm bar;

	int idx = 0;
  while ( (currentFile = (TFile*)fileIter.Next()) ) {

    TFile *file = TFile::Open( currentFile->GetTitle() );
    TTree *tree = (TTree*)file->Get("Events");
    TTree *runs = (TTree*)file->Get("Runs");

		string curr_fname = currentFile->GetTitle();
		float scale1fb;
		if 			(curr_fname.find(std::string("cHHH0")) != std::string::npos)				scale1fb = scales1fb_kl0;
		else if (curr_fname.find(std::string("cHHH1")) != std::string::npos)				scale1fb = scales1fb_kl1;
		else if (curr_fname.find(std::string("cHHH2p45")) != std::string::npos)			scale1fb = scales1fb_kl2p45;
		else if (curr_fname.find(std::string("cHHH5")) != std::string::npos)				scale1fb = scales1fb_kl5;

		tree->SetBranchStatus("*", 1);
		runs->SetBranchStatus("*", 1);

		TString fname = "/ceph/cms/store/user/fsetti/EFT_samples/" + tag + "/"+ proc + "_" + eft_bm + "/" + str_year + "/" + proc + "_" + std::to_string(idx) + ".root";
		TFile* f1 = new TFile( fname, "RECREATE");
	
		TTree *runs_tree	=	new TTree("Runs","Runs");
		runs_tree = runs->CloneTree(-1,"fast");
		TTree *out_tree	=	new TTree("Events","Events");
		out_tree = tree->CloneTree(-1, "fast");

    out_tree->SetCacheSize(128*1024*1024);
    out_tree->SetCacheLearnEntries(100);

		nt.SetYear(year);
    nt.Init(out_tree);

		float eft_weight;
		float eft_reweight;
		TBranch * b_scale1fb			=	out_tree->Branch( "scale1fb"		,	&scale1fb			, "scale1fb/F"			);
		TBranch * b_eft_weight		=	out_tree->Branch( "eft_weight"	,	&eft_weight		, "eft_weight/F"		);
		TBranch * b_eft_reweight	=	out_tree->Branch( "eft_reweight",	&eft_reweight	, "eft_reweight/F"	);

    for( unsigned int loop_event = 0; loop_event < out_tree->GetEntriesFast(); ++loop_event) {

			nt.GetEntry(loop_event);

			nEventsTotal++;
			bar.progress(nEventsTotal, nEventsChain);

			eft_weight = -9;
			eft_reweight = -9;
			//account for instabilities in event weights
			if ( fabs(genWeight()) >= 0.5 ){
				b_scale1fb->Fill();	
				b_eft_weight->Fill();	
				b_eft_reweight->Fill();	
				continue;
			}

			vector<unsigned int> HH_idx;
			for (unsigned int i=0; i<nGenPart(); i++){
				if ( GenPart_pdgId()[i] == 25 && GenPart_statusFlags()[i] & (1 << 13) ) HH_idx.push_back(i);
			}

			auto H1 = GenPart_p4()[HH_idx[0]];
			auto H2 = GenPart_p4()[HH_idx[1]];

			float event_mHH					= ( H1 + H2 ).M();
 			float event_costhetaHH	= fabs( getCosThetaStar_CS_old( H1, H2 ) );

			double Nev = histo_Nev->GetBinContent( histo_Nev->FindBin(event_mHH, event_costhetaHH) );
			double XS = rm_pw_NLO.GetDiffXsection(event_mHH, event_costhetaHH, couplings, "nlo") / 1000.;//diff XS in [fb]
			
			int ibinmhh = histo_Nev->GetXaxis()->FindBin(event_mHH);
			int ibincosthetaHH = histo_Nev->GetYaxis()->FindBin(event_costhetaHH);
			double Noutputev = XS * histo_Nev->GetXaxis()->GetBinWidth(ibinmhh) * histo_Nev->GetYaxis()->GetBinWidth(ibincosthetaHH);
			double reweight = Noutputev/Nev * Nevtot/XStot;

			eft_weight = reweight * genWeight() * scale1fb * br_spec / 4 ;		//divide by 4 since we are combining 4 ggHH NLO samples... really no idea how this works
			eft_reweight = reweight ;

			cout << "for mHH: " << event_mHH << " and cs angle: " << event_costhetaHH << " , we get this re-weight: " << reweight << endl;
			cout << "and genWeight: " << genWeight() << " and scale1fb: " << scale1fb << endl;


			b_scale1fb->Fill();	
			b_eft_weight->Fill();	
			b_eft_reweight->Fill();	

  	} // Event loop
	f1->cd();
	f1->Write();
	f1->Close();
  delete file;
	idx++;
 } // File loop
 bar.finish();
 return 0;
}
