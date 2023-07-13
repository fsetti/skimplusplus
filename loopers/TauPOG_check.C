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
#include "TTreeCacheUnzip.h"
#include "TTreePerfStats.h"

#include "../NanoCORE/Nano_v9.cc"
#include "../NanoCORE/tqdm.h"
#include "../NanoCORE/utils.cc"

#include <string>
#include <iostream>
#include <iomanip>

#define SUM(vec) std::accumulate((vec).begin(), (vec).end(), 0);
#define SUM_GT(vec,num) std::accumulate((vec).begin(), (vec).end(), 0, [](float x,float y){return ((y > (num)) ? x+y : x); });
#define COUNT_GT(vec,num) std::count_if((vec).begin(), (vec).end(), [](float x) { return x > (num); });
#define COUNT_LT(vec,num) std::count_if((vec).begin(), (vec).end(), [](float x) { return x < (num); });

#define H1(name,nbins,low,high) TH1F *h_##name = new TH1F(#name,#name,nbins,low,high);

// #define DEBUG

struct debugger { template<typename T> debugger& operator , (const T& v) { cerr<<v<<" "; return *this; } } dbg;
#ifdef DEBUG
    #define debug(args...) do {cerr << #args << ": "; dbg,args; cerr << endl;} while(0)
#else
    #define debug(args...)
#endif

using namespace std;
using namespace tas;

int ScanChain( TChain *ch, string proc, string str_year, float scale_factor = 1, int process_ID=-9999, bool resonant = false ) {

  int year;
  if ( str_year == "2016_APV") year = 2016;
  else { year = stoi(str_year); }

  TString file_name = proc + "_TauPOGcheck_" +  str_year;

	TFile* f1 = new TFile("/ceph/cms/store/user/fsetti/c++_output_no_skim++/" + file_name + ".root", "RECREATE");
	H1(dm, 16, 0 , 16 );

  int nEventsTotal = 0;
  int nEventsChain = ch->GetEntries();
	int nMatchedGenTauDM = 0;
	float nTauDM_tot = 0.;
  TFile *currentFile = 0;
  TObjArray *listOfFiles = ch->GetListOfFiles();
  TIter fileIter(listOfFiles);
  tqdm bar;

  while ( (currentFile = (TFile*)fileIter.Next()) ) {
      TFile *file = TFile::Open( currentFile->GetTitle() );
      TTree *tree = (TTree*)file->Get("Events");

      tree->SetCacheSize(128*1024*1024);
      tree->SetCacheLearnEntries(100);

			nt.SetYear(year);
      nt.Init(tree);

      for( unsigned int loop_event = 0; loop_event < tree->GetEntriesFast(); ++loop_event) {

       nt.GetEntry(loop_event);

       nEventsTotal++;
       bar.progress(nEventsTotal, nEventsChain);

			clear_branches();

			if ( fabs(genWeight()) >= 0.5 ){
				continue;
			}

			//////////////////////////////////////////////////////////////////////////////////////////////
			//////////////////////////////////////////////////////////////////////////////////////////////
			///////////////////							photon selection
			vector<int> pho_cands;
			vector<float> pho_pt_cands;
			for (unsigned int i=0; i<nPhoton(); i++){
				if ( Photon_electronVeto().at(i)  >=0.5 &&
					 (	(	Photon_isScEtaEB().at(i) && Photon_r9().at(i) > 0.85 )			//pho_EB_highR9
					||	(	Photon_isScEtaEE().at(i) && Photon_r9().at(i) > 0.90 )			//pho_EE_highR9
					||	(	Photon_isScEtaEB().at(i) && Photon_r9().at(i) < 0.85 && Photon_r9().at(i) > 0.5 && Photon_sieie().at(i) < 0.015 && Photon_trkSumPtHollowConeDR03().at(i) < 6.0  && ( Photon_pfPhoIso03().at(i) - 0.16544*fixedGridRhoFastjetAll() ) < 4.0 )			//pho_EB_lowR9
					||	(	Photon_isScEtaEE().at(i) && Photon_r9().at(i) < 0.90 && Photon_r9().at(i) > 0.8 && Photon_sieie().at(i) < 0.035 && Photon_trkSumPtHollowConeDR03().at(i) < 6.0  && ( Photon_pfPhoIso03().at(i) - 0.13212*fixedGridRhoFastjetAll() ) < 4.0 )			/*pho_EE_lowR9 */ )
				 	&& 	Photon_hoe().at(i) < 0.08
					&&	fabs(Photon_eta().at(i)) < 2.5
					&&	(	fabs(Photon_eta().at(i)) < 1.442 || fabs(Photon_eta().at(i)) > 1.566 )
					&&	( Photon_r9().at(i) > 0.8 || Photon_chargedHadronIso().at(i) < 20 || Photon_chargedHadronIso().at(i) / Photon_pt().at(i) < 0.3 )
					&&  ( Photon_isScEtaEB().at(i) || Photon_isScEtaEE().at(i) )
					&&    Photon_mvaID().at(i) > pho_idmva_cut
					){
						pho_cands.push_back(i);					
						pho_pt_cands.push_back( Photon_pt().at(i) );					
				}
			}
			if ( pho_cands.size() < 2 ) continue;

			sort(pho_pt_cands.begin(), pho_pt_cands.end(), greater<float>());
			int gHidx[2] = {-1,-1};
			for (unsigned int i=0; i<pho_cands.size();i++){
				if ( Photon_pt().at(pho_cands[i]) == pho_pt_cands[0] && Photon_pt().at(pho_cands[i]) > 35 ) gHidx[0]	= pho_cands[i];
				if ( Photon_pt().at(pho_cands[i]) == pho_pt_cands[1] && Photon_pt().at(pho_cands[i]) > 25 ) gHidx[1]	= pho_cands[i];
			}
			if ( gHidx[0] < 0 || gHidx[1] < 0 ) continue;

		//di-photon selection
		mgg = (float)(Photon_p4().at(gHidx[0]) + Photon_p4().at(gHidx[1]) ).M();
		if ( mgg < mgg_lower || mgg > mgg_upper ) continue;
		if ( (proc == "Data" || !resonant) && mgg > mgg_sideband_lower && mgg < mgg_sideband_upper ) continue;

		//photon selection
		if ( Photon_pt().at(gHidx[0]) < pho_pt_cut 				|| Photon_pt().at(gHidx[1]) < pho_pt_cut ) continue;
		if ( Photon_pt().at(gHidx[0]) / mgg < lead_pt_mgg_cut 	|| Photon_pt().at(gHidx[1]) / mgg < sublead_pt_mgg_cut ) continue;
		if ( Photon_mvaID().at(gHidx[0]) < pho_idmva_cut 			|| Photon_mvaID().at(gHidx[1]) < pho_idmva_cut ) continue;
		if ( Photon_electronVeto().at(gHidx[0]) < pho_eveto_cut 	|| Photon_electronVeto().at(gHidx[1]) < pho_eveto_cut ) continue;
		if ( fabs(Photon_eta().at(gHidx[0])) > pho_eta_cut 		|| fabs(Photon_eta().at(gHidx[1])) > pho_eta_cut ) continue;
		if ( fabs(Photon_eta().at(gHidx[0])) > trans_eta_low 		&& fabs(Photon_eta().at(gHidx[0])) < trans_eta_high ) continue;
		if ( fabs(Photon_eta().at(gHidx[1])) > trans_eta_low 		&& fabs(Photon_eta().at(gHidx[1])) < trans_eta_high ) continue;

		//trigger requirements
		//if ( year == 2016 && !HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90() ) continue;
		//if ( (year == 2017 || year == 2018 ) && !HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90() ) continue;

		vector<int> sel_eles;
		for(unsigned int i=0; i<nElectron(); i++){
			if (Electron_pt().at(i) > ele_pt && fabs(Electron_eta().at(i)) < ele_eta && ( fabs(Electron_eta().at(i)) < trans_eta_low || fabs(Electron_eta().at(i)) > trans_eta_high ) && fabs(Electron_dxy().at(i)) < ele_dxy && fabs(Electron_dz().at(i)) < ele_dz 
			&& Electron_mvaFall17V2Iso_WP90().at(i)   
			&& deltaR( Electron_p4().at(i) , Photon_p4().at(gHidx[0]) ) > ele_dR_pho && deltaR( Electron_p4().at(i) , Photon_p4().at(gHidx[1]) ) > ele_dR_pho 
			){
				sel_eles.push_back(i);
			}
		}
		
		vector<int> sel_muons;
		for(unsigned int i=0; i<nMuon(); i++){
			if (Muon_pt().at(i) > muon_pt && fabs(Muon_eta().at(i)) < muon_eta && fabs(Muon_dxy().at(i)) < muon_dxy && fabs(Muon_dz().at(i)) < muon_dz 
			&& Muon_pfRelIso03_all().at(i) < muon_pfRelIso 
			&& Muon_isGlobal().at(i) 
			&& Muon_mediumId().at(i) 
			&& deltaR( Muon_p4().at(i) , Photon_p4().at(gHidx[0]) ) > muon_dR_pho && deltaR( Muon_p4().at(i) , Photon_p4().at(gHidx[1]) ) > muon_dR_pho 
			){
				sel_muons.push_back(i);
			}
		}
		
		vector<int> sel_taus;
		for(unsigned int i=0; i<nTau(); i++){
			if (Tau_pt().at(i) > tau_pt && fabs(Tau_eta().at(i)) < tau_eta && /*Tau_idDecayModeNewDMs().at(i) &&*/ fabs(Tau_dz().at(i)) < tau_dz 
			&& Tau_idDeepTau2017v2p1VSe().at(i) >= tau_deepID_e && Tau_idDeepTau2017v2p1VSmu().at(i) >= tau_deepID_m && Tau_idDeepTau2017v2p1VSjet().at(i) >= tau_deepID_j 
			&& deltaR( Tau_p4().at(i) , Photon_p4().at(gHidx[0]) ) > tau_dR_pho && deltaR( Tau_p4().at(i) , Photon_p4().at(gHidx[1]) ) > tau_dR_pho 
			){

				bool overlap = false;
				for (unsigned int j=0; j<sel_eles.size(); j++){
					if ( deltaR( Tau_p4().at(i) , Electron_p4().at(sel_eles.at(j)) ) < tau_dR_lep ) overlap = true;
				}
				for (unsigned int j=0; j<sel_muons.size(); j++){
					if ( deltaR( Tau_p4().at(i) , Muon_p4().at(sel_muons.at(j)) ) < tau_dR_lep ) overlap = true;
				}

				if ( !overlap ) sel_taus.push_back(i);
			}
		}

		//Isolated Tracks selection
          vector<int> sel_isoTracks;
          for (unsigned int i=0; i<nIsoTrack(); i++){
              if ( IsoTrack_isPFcand().at(i) && IsoTrack_fromPV().at(i) 
								&&	fabs(IsoTrack_dxy().at(i)) < 0.2
								&&	fabs(IsoTrack_dz().at(i)) < 0.1
								){
                  LorentzVector *iso_track = new LorentzVector;
                  iso_track->SetXYZT( IsoTrack_pt().at(i)* TMath::Cos(IsoTrack_phi().at(i)) , IsoTrack_pt().at(i)*TMath::Sin( IsoTrack_phi().at(i)), IsoTrack_pt().at(i)*TMath::SinH( IsoTrack_eta().at(i)),  IsoTrack_pt().at(i)*TMath::CosH( IsoTrack_eta().at(i) ) );
                  if ( deltaR( iso_track , Photon_p4().at(gHidx[0]) ) > isoTrk_dR  && deltaR( iso_track , Photon_p4().at(gHidx[1]) ) > isoTrk_dR  ){
					bool iso = true;
					for (unsigned int j=0; j<sel_eles.size(); j++){
                  		if ( deltaR( iso_track , Electron_p4().at(sel_eles.at(j)) ) < isoTrk_dR ){
							iso = false;
                  		}
              		}
					for (unsigned int j=0; j<sel_muons.size(); j++){
                  		if ( deltaR( iso_track , Muon_p4().at(sel_muons.at(j)) ) < isoTrk_dR ){
							iso = false;
                  		}
              		}
					for (unsigned int j=0; j<sel_taus.size(); j++){
                  		if ( deltaR( iso_track , Tau_p4().at(sel_taus.at(j)) ) < isoTrk_dR ){
							iso = false;
                  		}
              		}
					if ( iso ) sel_isoTracks.push_back( i );
				}
			}
		}

		//Jet Selection			
		vector<int> sel_jets;
		for(unsigned int i=0; i<nJet(); i++){
			if (Jet_pt().at(i) > jet_pt && fabs(Jet_eta().at(i)) < jet_eta && Jet_neEmEF().at(i) < jet_neEmEF && Jet_neHEF().at(i) < jet_neHEF && Jet_chHEF()[i] > jet_chHEF && Jet_chEmEF()[i] < jet_chEmEF && Jet_nConstituents()[i] > jet_nConstituents && deltaR( Jet_p4().at(i) , Photon_p4().at(gHidx[0]) ) > jet_dR_pho && deltaR( Jet_p4().at(i) , Photon_p4().at(gHidx[1]) ) > jet_dR_pho ){

				bool overlap = false;
				for (unsigned int j=0; j<sel_eles.size(); j++){
					if ( !overlap && deltaR( Jet_p4().at(i) , Electron_p4().at(sel_eles.at(j)) ) < jet_dR_lep ){
						overlap = true;
						break;
					}
				}
				for (unsigned int j=0; j<sel_muons.size(); j++){
					if ( !overlap && deltaR( Jet_p4().at(i) , Muon_p4().at(sel_muons.at(j)) ) < jet_dR_lep ){
						overlap = true;
						break;
					}
				}
				for (unsigned int j=0; j<sel_taus.size(); j++){
					if ( !overlap && deltaR( Jet_p4().at(i) , Tau_p4().at(sel_taus.at(j)) ) < jet_dR_tau ){
						overlap = true;
						break;
					}
				}

				if ( !overlap ){
					sel_jets.push_back(i);
					if ( Jet_btagDeepFlavB().at(i) > max_bTag ) max_bTag = Jet_btagDeepFlavB().at(i);
				}
			}
		}

		//bJet Selection			
		vector<int> sel_bJets;
		for(unsigned int i=0; i<sel_jets.size(); i++){
			if ( Jet_btagDeepFlavB().at(sel_jets[i]) > bTag_medium_WP[year - 2016] ) sel_bJets.push_back(sel_jets[i]);
		}


		//Z veto cut
		bool Z_cand = false;
		if ( sel_eles.size() >= 2 ){
			for (unsigned int i=0; i<sel_eles.size(); i++){
				for (unsigned int j=i+1; j<sel_eles.size(); j++){
					if ( (Electron_p4().at(sel_eles[i]) + Electron_p4().at(sel_eles[j])).M() > mZ_veto_low  && (Electron_p4().at(sel_eles[i]) + Electron_p4().at(sel_eles[j])).M() < mZ_veto_up 
						&& Electron_charge().at(sel_eles[i]) * Electron_charge().at(sel_eles[j]) < 0 ){
						Z_cand = true;
						break;
					}
				}
			}
		}
		if ( sel_muons.size() >= 2 ){
			for (unsigned int i=0; i<sel_muons.size(); i++){
				for (unsigned int j=i+1; j<sel_muons.size(); j++){
					if ( (Muon_p4().at(sel_muons[i]) + Muon_p4().at(sel_muons[j])).M() > mZ_veto_low  && (Muon_p4().at(sel_muons[i]) + Muon_p4().at(sel_muons[j])).M() < mZ_veto_up 
						&& Muon_charge().at(sel_muons[i]) * Muon_charge().at(sel_muons[j]) < 0 ){
						Z_cand = true;
						break;
					}
				}
			}
		}
		if ( Z_cand ) continue;

		n_electrons		= sel_eles.size();
		n_muons			= sel_muons.size();
		n_taus			= sel_taus.size();
		n_isoTrks		= sel_isoTracks.size();
		n_jets			= sel_jets.size();
		n_bjets			= sel_bJets.size();

		vector<int> h_cand1, h_cand2;
		vector<vector<int>> raw_results = categorise( sel_eles, sel_muons, sel_taus, sel_isoTracks );
		sel_eles		= raw_results[0];
		sel_muons		= raw_results[1];
		sel_taus		= raw_results[2];
		sel_isoTracks	= raw_results[3];
		h_cand1			= raw_results[4];
		h_cand2			= raw_results[5];

		if ( h_cand1[1] == -1 && h_cand2[1] == -1  ) continue;

		if ( h_cand1[1] == 2 && h_cand2[1] == 1  ) cat1 = true;
		if ( h_cand1[1] == 2 && h_cand2[1] == 0  ) cat2 = true;
		if ( h_cand1[1] == 2 && h_cand2[1] == 2  ) cat3 = true;
		if ( h_cand1[1] == 1 && h_cand2[1] == 1  ) cat4 = true;
		if ( h_cand1[1] == 0 && h_cand2[1] == 0  ) cat5 = true;
		if ( h_cand1[1] == 1 && h_cand2[1] == 0  ) cat6 = true;
		if ( h_cand1[1] == 2 && h_cand2[1] == 3  ) cat7 = true;
		if ( h_cand1[1] == 2 && h_cand2[1] == -1 ) cat8 = true;

		category = 99;
		if ( cat1 ) category = 1;
		if ( cat2 ) category = 2;
		if ( cat3 ) category = 3;
		if ( cat4 ) category = 4;
		if ( cat5 ) category = 5;
		if ( cat6 ) category = 6;
		if ( cat7 ) category = 7;
		if ( cat8 ) category = 8;

		bool tau_DM = false;
		
		if ( ( cat1 || cat2 || cat3 || cat7 || cat8 ) && ( Tau_decayMode()[h_cand1[0]] == 5 || Tau_decayMode()[h_cand1[0]] == 6 ) ){
			nTauDM_tot++;
			for(unsigned int i=0; i<nGenVisTau(); i++){
				if ( deltaR( Tau_p4()[h_cand1[0]], GenVisTau_p4()[i] ) < 0.2 ){
					nMatchedGenTauDM++;
					h_dm->Fill( GenVisTau_status()[i], genWeight() );
					break;
				}
			}
		}
		if ( cat3 && ( Tau_decayMode()[h_cand2[0]] == 5 || Tau_decayMode()[h_cand2[0]] == 6 ) ){
			nTauDM_tot++;
			for(unsigned int i=0; i<nGenVisTau(); i++){

				if ( deltaR( Tau_p4()[h_cand2[0]], GenVisTau_p4()[i] ) < 0.2 ){
					nMatchedGenTauDM++;
					h_dm->Fill( GenVisTau_status()[i], genWeight() );
					break;
				}
			}
		}

		/*
		bool iso_trk = false;
		if ( h_cand1[1] == 2 && h_cand2[1] == 3  ) iso_trk = true;

		if ( !iso_trk ) continue;

		LorentzVector iso_track(IsoTrack_pt()[h_cand2[0]], IsoTrack_eta()[h_cand2[0]], IsoTrack_phi()[h_cand2[0]], 0);

		//GenMatch GenVisTau to selected IsoTrk
		for(unsigned int i=0; i<nGenVisTau(); i++){

			if ( deltaR( iso_track, GenVisTau_p4()[i] ) < 0.2 ){
				h_dm->Fill( GenVisTau_status()[i], genWeight() );
				break;
			}			
		}
		*/

		} // Event loop
		delete file;
	} // File loop
	bar.finish();	

	cout << "Efficiency of tau with DM=5,6 matched to GenVisTau:" << nMatchedGenTauDM / nTauDM_tot << endl;
	TCanvas *c = new TCanvas();
	h_dm->DrawNormalized("HIST");
	c->SaveAs("/home/users/fsetti/public_html/HH2ggtautau/TauPOG_checks/tau_SFs/gvt_dm_for_recoTauDM56.png");

	f1->Write();
	f1->Close();
	return 0;
}
