#include <iostream>

using namespace std;

const float mHiggs					= 125;
const float mZ							= 91.19;
const float trans_eta_low 			= 1.4442;
const float trans_eta_high 			= 1.566;
const float mZ_veto_low				= 80;
const float mZ_veto_up				= 100;
const float mllg_window				= 10;		//update from 25, since using mllg in BDT

//di-photon selection
const float mgg_lower 				= 100;
const float mgg_upper 				= 180;
const float mgg_sideband_lower 		= 120;
const float mgg_sideband_upper 		= 130;
const float lead_pt_mgg_cut			= 0.33;
const float sublead_pt_mgg_cut		= 0.25;
const float pho_idmva_cut			= -0.7;
const float pho_eveto_cut			= 0.5;
const float pho_eta_cut				= 2.5;
const float pho_pt_cut				= 25;

//electron selection
const float ele_pt					= 10;
const float ele_eta					= 2.5;
const float ele_dxy					= 0.045;
const float ele_dz					= 0.2;
const float ele_pfRelIso			= 0.3;
const float ele_dR_pho				= 0.2;

//muon selection
const float muon_pt					= 15;
const float muon_eta				= 2.4;
const float muon_dxy				= 0.045;
const float muon_dz					= 0.2;
const float muon_pfRelIso			= 0.3;
const float muon_dR_pho				= 0.2;

//tau selection
const float tau_pt					= 20;
const float tau_eta					= 2.3;
const float tau_dz					= 0.2;
const int 	tau_deepID_e			= 1;
const int 	tau_deepID_m			= 0;
const int 	tau_deepID_j			= 7;
const float tau_dR_pho				= 0.5;
const float tau_dR_lep				= 0.5;

//jet selection
const float jet_pt					= 25;
const float jet_eta					= 2.4;
const float jet_neEmEF				= 0.99;
const float jet_neHEF				= 0.99;
const float jet_chHEF				= 0;
const float jet_chEmEF				= 0.99;
const int 	jet_nConstituents		= 1;
const float jet_dR_pho				= 0.4;
const float jet_dR_lep				= 0.4;
const float jet_dR_tau				= 0.4;

//bJet MediumWorkingPoint
const float bTag_medium_WP[3] = { 0.3093 , 0.3033, 0.2770 };

//IsoTracks
const float isoTrk_dR				= 0.2;

//Tree branches
int 			t_run;
int				t_lumiBlock;
int				t_event;
float 			t_MET_pt;
float 			t_MET_phi;
float 			t_weight;
float 			t_eft_weight;
int 			process_id;
int 			category;

float 			mgg;
int				n_electrons;
int				n_muons;
int				n_taus;
int				n_jets;
int				n_bjets;
int 			n_isoTrks;

float			lep12_dphi;
float			lep12_deta;
float			lep12_deta_bdt;
float			lep12_dr;

bool			cat1;
bool			cat2;
bool			cat3;
bool			cat4;
bool			cat5;
bool			cat6;
bool			cat7;
bool			cat8;

float 			g1_ptmgg;
float 			g1_pt;
float 			g1_eta;
float 			g1_eta_bdt;
float 			g1_phi;
float 			g1_idmva;
bool 			g1_pixVeto;

float 			g2_ptmgg;
float 			g2_pt;
float 			g2_eta;
float 			g2_eta_bdt;
float 			g2_phi;
float 			g2_idmva;
bool 			g2_pixVeto;

float 			gg_pt;
float 			gg_ptmgg;
float 			gg_eta;
float 			gg_eta_bdt;
float 			gg_phi;
float 			gg_dR;
float 			gg_dPhi;
float 			gg_hel;
float 			gg_hel_phys;
float 			gg_tt_CS;
float 			gg_tt_hel;
float 			gg_tt_hel_phys;

float 			lep1_pt				;
float 			lep1_eta			;
float 			lep1_eta_bdt		;
float 			lep1_phi			;
float 			lep1_charge			;
float 			lep1_pdgID			;
float 			lep1_tightID		;
Int_t 			lep1_id_vs_e		;
Int_t 			lep1_id_vs_m		;
Int_t 			lep1_id_vs_jet	;
int					lep1_dm					;

float 			lep2_pt;
float 			lep2_eta;
float 			lep2_eta_bdt		;
float 			lep2_phi;
float 			lep2_charge;
float 			lep2_pdgID;
float 			lep2_tightID;
Int_t 			lep2_id_vs_e;
Int_t 			lep2_id_vs_m;
Int_t 			lep2_id_vs_jet;
int					lep2_dm					;

float 			jet1_pt			;
float 			jet1_eta		;
float 			jet1_eta_bdt	;
float 			jet1_phi		;
float 			jet1_bTag		;
int 			jet1_id			;

float 			jet2_pt			;
float 			jet2_eta		;
float 			jet2_eta_bdt	;
float 			jet2_phi		;
float 			jet2_bTag		;
int 			jet2_id			;

float			max_bTag		;
float			tt_hel					;
float			tt_hel_phys				;

float			m_tautau_vis			;
float			pt_tautau_vis			;
float			eta_tautau_vis			;
float			eta_tautau_vis_bdt		;
float			phi_tautau_vis			;

float			MET_gg_dPhi				;
float			MET_ll_dPhi				;
float			dPhi_MET_l				;
float			ll_dPhi					;
float			ll_dEta					;
float			ll_dR					;
float			m_Z						;

float			dZ						;
float			g1_energyErr	;
float			g2_energyErr	;
float			max_g_ptmgg		;
float			min_g_ptmgg		;
float			max_g_idmva		;
float			min_g_idmva		;
float			lep2_pfRelIso03_all	;
float			lep2_pfRelIso03_chg	;
float			max_lep_pt		;
float			min_lep_pt		;

float 		pt_tautauSVFitLoose		;
float 		eta_tautauSVFitLoose	;
float 		eta_tautauSVFitLoose_bdt;
float 		phi_tautauSVFitLoose	;
float 		m_tautauSVFitLoose		;
float 		dR_tautauSVFitLoose		;
float 		dR_ggtautauSVFitLoose	;
float 		dPhi_tautauSVFitLoose	;
float 		dPhi_ggtautauSVFitLoose	;

float			tau1_pt_SVFit		;
float			tau1_eta_SVFit	;
float			tau1_phi_SVFit	;
float			tau1_m_SVFit		;
float			tau2_pt_SVFit		;
float			tau2_eta_SVFit	;
float			tau2_phi_SVFit	;
float			tau2_m_SVFit		;

float 		pt_tautau_sntMtt		;
float 		eta_tautau_sntMtt	;
float 		eta_tautau_sntMtt_bdt;
float 		phi_tautau_sntMtt	;
float 		m_tautau_sntMtt		;
float 		dR_tautau_sntMtt		;
float 		dR_ggtautau_sntMtt	;
float 		dPhi_tautau_sntMtt	;
float 		dPhi_ggtautau_sntMtt	;

float			tau1_pt_sntMtt		;
float			tau1_eta_sntMtt	;
float			tau1_phi_sntMtt	;
float			tau1_m_sntMtt		;
float			tau2_pt_sntMtt		;
float			tau2_eta_sntMtt	;
float			tau2_phi_sntMtt	;
float			tau2_m_sntMtt		;

float			mX		;
float 		m_llg_lead;
float 		m_llg_subl;

//Tau ID systematic variations to include decay Modes 5 and 6
vector<float> Tau_sfDeepTau2017v2p1VSjet_Loose_ext;
vector<float> Tau_sfDeepTau2017v2p1VSjet_LooseUp_ext;
vector<float> Tau_sfDeepTau2017v2p1VSjet_LooseDown_ext;
vector<float> Tau_sfDeepTau2017v2p1VSmu_VLoose_ext;
vector<float> Tau_sfDeepTau2017v2p1VSmu_VLooseUp_ext;
vector<float> Tau_sfDeepTau2017v2p1VSmu_VLooseDown_ext;
vector<float> Tau_sfDeepTau2017v2p1VSe_VVLoose_ext;
vector<float> Tau_sfDeepTau2017v2p1VSe_VVLooseUp_ext;
vector<float> Tau_sfDeepTau2017v2p1VSe_VVLooseDown_ext;

vector<float> IsoTrk_SF_id_5perc;
vector<float> IsoTrk_SF_id_5perc_Up;
vector<float> IsoTrk_SF_id_5perc_Down;
vector<float> IsoTrk_SF_id_20perc;
vector<float> IsoTrk_SF_id_20perc_Up;
vector<float> IsoTrk_SF_id_20perc_Down;
vector<float> IsoTrk_SF_id_50perc;
vector<float> IsoTrk_SF_id_50perc_Up;
vector<float> IsoTrk_SF_id_50perc_Down;

vector<float> IsoTrk_SF_ES_5perc;
vector<float> IsoTrk_SF_ES_5perc_Up;
vector<float> IsoTrk_SF_ES_5perc_Down;
vector<float> IsoTrk_SF_ES_20perc;
vector<float> IsoTrk_SF_ES_20perc_Up;
vector<float> IsoTrk_SF_ES_20perc_Down;
vector<float> IsoTrk_SF_ES_50perc;
vector<float> IsoTrk_SF_ES_50perc_Up;
vector<float> IsoTrk_SF_ES_50perc_Down;

//list of SFs for Muon-WP VLoose
//from 	https://indico.cern.ch/event/866243/contributions/3650016/attachments/1950974/3238736/mutauFRRun2_Yiwen_20191121.pdf
//and 	https://github.com/cms-tau-pog/TauIDSFs

//////////////////////////
//////////////////  2016pre Muon
//////////////////////////
float mu_eta0to0p4_2016pre 					= 1.1705;
float mu_eta0to0p4_up_2016pre 			= mu_eta0to0p4_2016pre + 10*(	+ 0.081 );
float mu_eta0to0p4_down_2016pre 		= mu_eta0to0p4_2016pre + 10*(	- 0.081 );
float mu_eta0p4to0p8_2016pre 				= 1.207;
float mu_eta0p4to0p8_up_2016pre 		= mu_eta0p4to0p8_2016pre + 10* ( + 0.162 );
float mu_eta0p4to0p8_down_2016pre 	= mu_eta0p4to0p8_2016pre + 10* ( - 0.128 );
float mu_eta0p8to1p2_2016pre 				= 1.411;
float mu_eta0p8to1p2_up_2016pre 		= mu_eta0p8to1p2_2016pre + 10* ( + 0.111 );
float mu_eta0p8to1p2_down_2016pre 	= mu_eta0p8to1p2_2016pre + 10* ( - 0.108 );
float mu_eta1p2to1p7_2016pre 				= 0.8886 ;
float mu_eta1p2to1p7_up_2016pre 		= mu_eta1p2to1p7_2016pre + 10* ( + 0.190 );
float mu_eta1p2to1p7_down_2016pre 	= mu_eta1p2to1p7_2016pre + 10* ( - 0.214 );
float mu_eta1p7toInf_2016pre 				= 3.933 ;
float mu_eta1p7toInf_up_2016pre 		= mu_eta1p7toInf_2016pre + 10* ( + 0.390 );
float mu_eta1p7toInf_down_2016pre 	= mu_eta1p7toInf_2016pre + 10* ( - 0.361 );

//////////////////////////
//////////////////  2016post Muon
//////////////////////////
float mu_eta0to0p4_2016post 				= 1.0035;
float mu_eta0to0p4_up_2016post 			= mu_eta0to0p4_2016post + 10*(	+ 0.081 );
float mu_eta0to0p4_down_2016post 		= mu_eta0to0p4_2016post + 10*(	- 0.081 );
float mu_eta0p4to0p8_2016post 			= 1.037;
float mu_eta0p4to0p8_up_2016post 		= mu_eta0p4to0p8_2016post + 10* ( + 0.162 );
float mu_eta0p4to0p8_down_2016post 	= mu_eta0p4to0p8_2016post + 10* ( - 0.128 );
float mu_eta0p8to1p2_2016post 			= 0.879;
float mu_eta0p8to1p2_up_2016post 		= mu_eta0p8to1p2_2016post + 10* ( + 0.111 );
float mu_eta0p8to1p2_down_2016post 	= mu_eta0p8to1p2_2016post + 10* ( - 0.108 );
float mu_eta1p2to1p7_2016post 			= 0.947 ;
float mu_eta1p2to1p7_up_2016post 		= mu_eta1p2to1p7_2016post + 10* ( + 0.190 );
float mu_eta1p2to1p7_down_2016post 	= mu_eta1p2to1p7_2016post + 10* ( - 0.214 );
float mu_eta1p7toInf_2016post 			= 3.551 ;
float mu_eta1p7toInf_up_2016post 		= mu_eta1p7toInf_2016post + 10* ( + 0.390 );
float mu_eta1p7toInf_down_2016post 	= mu_eta1p7toInf_2016post + 10* ( - 0.361 );

//////////////////////////
//////////////////  2017 Muon
//////////////////////////
float mu_eta0to0p4_2017 				= 1.2307;
float mu_eta0to0p4_up_2017 			= mu_eta0to0p4_2017 + 10* (  + 0.088 );
float mu_eta0to0p4_down_2017 		= mu_eta0to0p4_2017 + 10* (  - 0.087 );
float mu_eta0p4to0p8_2017 			= 1.1593;
float mu_eta0p4to0p8_up_2017 		= mu_eta0p4to0p8_2017 + 10* ( + 0.119 );
float mu_eta0p4to0p8_down_2017 	= mu_eta0p4to0p8_2017 + 10* ( - 0.107 );
float mu_eta0p8to1p2_2017 			= 0.9032             ;
float mu_eta0p8to1p2_up_2017 		= mu_eta0p8to1p2_2017 + 10* ( + 0.098 );
float mu_eta0p8to1p2_down_2017 	= mu_eta0p8to1p2_2017 + 10* ( - 0.103 );
float mu_eta1p2to1p7_2017 			= 0.79435     ;
float mu_eta1p2to1p7_up_2017 		= mu_eta1p2to1p7_2017 + 10* ( + 0.139 );
float mu_eta1p2to1p7_down_2017 	= mu_eta1p2to1p7_2017 + 10* ( - 0.134 );
float mu_eta1p7toInf_2017 			= 3.11348            ;
float mu_eta1p7toInf_up_2017 		= mu_eta1p7toInf_2017 + 10* ( + 0.305 );
float mu_eta1p7toInf_down_2017 	= mu_eta1p7toInf_2017 + 10* ( - 0.284 );

//////////////////////////
//////////////////  2018 Muon
//////////////////////////
float mu_eta0to0p4_2018 				= 1.2085;
float mu_eta0to0p4_up_2018 			= mu_eta0to0p4_2018 + 10* ( + 0.08 );
float mu_eta0to0p4_down_2018 		= mu_eta0to0p4_2018 + 10* ( - 0.08 );
float mu_eta0p4to0p8_2018 			= 1.02802;
float mu_eta0p4to0p8_up_2018 		= mu_eta0p4to0p8_2018 + 10* ( + 0.153 );
float mu_eta0p4to0p8_down_2018 	= mu_eta0p4to0p8_2018 + 10* ( - 0.128 );
float mu_eta0p8to1p2_2018 			= 0.9927             ;
float mu_eta0p8to1p2_up_2018 		= mu_eta0p8to1p2_2018 + 10* ( + 0.102 );
float mu_eta0p8to1p2_down_2018 	= mu_eta0p8to1p2_2018 + 10* ( - 0.093 );
float mu_eta1p2to1p7_2018 			= 1.225    ;
float mu_eta1p2to1p7_up_2018 		= mu_eta1p2to1p7_2018 + 10*(+ 0.160 );
float mu_eta1p2to1p7_down_2018 	= mu_eta1p2to1p7_2018 + 10*(- 0.150 );
float mu_eta1p7toInf_2018 			= 4.8828             ;
float mu_eta1p7toInf_up_2018 		= mu_eta1p7toInf_2018 + 10*(+ 0.400 );
float mu_eta1p7toInf_down_2018 	= mu_eta1p7toInf_2018 + 10*(- 0.101 );

//Electron Scale Factors from here
// 			https://indico.cern.ch/event/831606/contributions/3483937/attachments/1871414/3079821/EtoTauFR2018-updated.pdf
//and 	https://github.com/cms-tau-pog/TauIDSFs

//////////////////////////
//////////////////  2016 Electron
//////////////////////////
float ele_eta0to1p4_2016pre 				= 1.12;
float ele_eta0to1p4_up_2016pre 			= ele_eta0to1p4_2016pre + 10*(+ 0.0017 );
float ele_eta0to1p4_down_2016pre 		= ele_eta0to1p4_2016pre + 10*(- 0.0017 );
float ele_eta1p5toInf_2016pre 			= 1.07;
float ele_eta1p5toInf_up_2016pre 		= ele_eta1p5toInf_2016pre + 10*(+ 0.016 );
float ele_eta1p5toInf_down_2016pre 	= ele_eta1p5toInf_2016pre + 10*(- 0.016 );

//////////////////////////
//////////////////  2016 Electron
//////////////////////////
float ele_eta0to1p4_2016post 				= 1.06;
float ele_eta0to1p4_up_2016post 			= ele_eta0to1p4_2016post + 10*(+ 0.0017 );
float ele_eta0to1p4_down_2016post 		= ele_eta0to1p4_2016post + 10*(- 0.0017 );
float ele_eta1p5toInf_2016post 			= 0.95;
float ele_eta1p5toInf_up_2016post 		= ele_eta1p5toInf_2016post + 10*(+ 0.016 );
float ele_eta1p5toInf_down_2016post 	= ele_eta1p5toInf_2016post + 10*(- 0.016 );

//////////////////////////
//////////////////  2017 Electron
//////////////////////////
float ele_eta0to1p4_2017 				= 0.89;
float ele_eta0to1p4_up_2017 			= ele_eta0to1p4_2017 + 10*(+ 0.003 );
float ele_eta0to1p4_down_2017 		= ele_eta0to1p4_2017 + 10*(- 0.004 );
float ele_eta1p5toInf_2017 			= 0.93;
float ele_eta1p5toInf_up_2017 		= ele_eta1p5toInf_2017 + 10*(+ 0.004 );
float ele_eta1p5toInf_down_2017 	= ele_eta1p5toInf_2017 + 10*(- 0.004 );

//////////////////////////
//////////////////  2018 Electron
//////////////////////////
float ele_eta0to1p4_2018 				= 0.90;
float ele_eta0to1p4_up_2018 			= ele_eta0to1p4_2018 + 10*(+ 0.003 );
float ele_eta0to1p4_down_2018 		= ele_eta0to1p4_2018 + 10*(- 0.003 );
float ele_eta1p5toInf_2018 			= 1.07;
float ele_eta1p5toInf_up_2018 		= ele_eta1p5toInf_2018 + 10*(+ 0.003 );
float ele_eta1p5toInf_down_2018 	= ele_eta1p5toInf_2018 + 10*(- 0.003 );

//Jet SFs from https://github.com/cms-tau-pog/TauIDSFs
//////////////////////////
//////////////////  2016preVFP Jet
//////////////////////////
float jet_pT20to25_2016pre 				= 0.9370219;
float jet_pT20to25_up_2016pre 		= jet_pT20to25_2016pre + 10*(+ 0.0689 );
float jet_pT20to25_down_2016pre 	= jet_pT20to25_2016pre + 10*(- 0.0689 );
float jet_pT25to30_2016pre 				= 0.9252694;
float jet_pT25to30_up_2016pre 		= jet_pT25to30_2016pre + 10*(+ 0.0432 );
float jet_pT25to30_down_2016pre 	= jet_pT25to30_2016pre + 10*(- 0.0432 );
float jet_pT30to35_2016pre 				= 0.9518583;
float jet_pT30to35_up_2016pre 		= jet_pT30to35_2016pre + 10*(+ 0.0306 );
float jet_pT30to35_down_2016pre 	= jet_pT30to35_2016pre + 10*(- 0.0306 );
float jet_pT35to40_2016pre 				= 0.9382482;
float jet_pT35to40_up_2016pre 		= jet_pT35to40_2016pre + 10*(+ 0.0321 );
float jet_pT35to40_down_2016pre 	= jet_pT35to40_2016pre + 10*(- 0.0321 );
float jet_pT40toInf_2016pre 			= 0.867371231569;
float jet_pT40toInf_up_2016pre 		= jet_pT40toInf_2016pre + 10*(+ 0.0489 );
float jet_pT40toInf_down_2016pre 	= jet_pT40toInf_2016pre + 10*(- 0.0337 );

//////////////////////////
//////////////////  2016postVFP Jet
//////////////////////////
float jet_pT20to25_2016post 			= 0.9148144;
float jet_pT20to25_up_2016post 		= jet_pT20to25_2016post + 10*(+ 0.0650 );
float jet_pT20to25_down_2016post 	= jet_pT20to25_2016post + 10*(- 0.065 );
float jet_pT25to30_2016post 			= 0.9341246;
float jet_pT25to30_up_2016post 		= jet_pT25to30_2016post + 10*(+ 0.0401 );
float jet_pT25to30_down_2016post 	= jet_pT25to30_2016post + 10*(- 0.0401 );
float jet_pT30to35_2016post 			= 0.9509707;
float jet_pT30to35_up_2016post 		= jet_pT30to35_2016post + 10*(+ 0.0309 );
float jet_pT30to35_down_2016post 	= jet_pT30to35_2016post + 10*(- 0.0309 );
float jet_pT35to40_2016post 			= 0.9582294;
float jet_pT35to40_up_2016post 		= jet_pT35to40_2016post + 10*(+ 0.0327 );
float jet_pT35to40_down_2016post 	= jet_pT35to40_2016post + 10*(- 0.0327 );
float jet_pT40toInf_2016post 			= 0.842972195625;
float jet_pT40toInf_up_2016post 	= jet_pT40toInf_2016post + 10*(+ 0.0673 );
float jet_pT40toInf_down_2016post = jet_pT40toInf_2016post + 10*(- 0.0349 );

//////////////////////////
//////////////////  2017 Jet
//////////////////////////
float jet_pT20to25_2017 			= 0.901811;
float jet_pT20to25_up_2017 		= jet_pT20to25_2017 + 10*(+ 0.0613 );
float jet_pT20to25_down_2017 	= jet_pT20to25_2017 + 10*(- 0.0613 );
float jet_pT25to30_2017 			= 0.907348;
float jet_pT25to30_up_2017 		= jet_pT25to30_2017 + 10*(+ 0.0323 );
float jet_pT25to30_down_2017 	= jet_pT25to30_2017 + 10*(- 0.0323 );
float jet_pT30to35_2017 			= 0.9426739;
float jet_pT30to35_up_2017 		= jet_pT30to35_2017 + 10*(+ 0.028776 );
float jet_pT30to35_down_2017 	= jet_pT30to35_2017 + 10*(- 0.028776 );
float jet_pT35to40_2017 			= 0.8963103;
float jet_pT35to40_up_2017 		= jet_pT35to40_2017 + 10*(+ 0.026317 );
float jet_pT35to40_down_2017 	= jet_pT35to40_2017 + 10*(- 0.026317 );
float jet_pT40toInf_2017 			= 0.883461746353;
float jet_pT40toInf_up_2017 	= jet_pT40toInf_2017+ 10*( +  0.0284 );
float jet_pT40toInf_down_2017 = jet_pT40toInf_2017+ 10*( -  0.027698);

//////////////////////////
//////////////////  2018 Jet
//////////////////////////
float jet_pT20to25_2018 			= 0.8838565;
float jet_pT20to25_up_2018 		= jet_pT20to25_2018 + 10*(+ 0.05432 );
float jet_pT20to25_down_2018 	= jet_pT20to25_2018 + 10*(- 0.05432 );
float jet_pT25to30_2018 			= 0.8882092;
float jet_pT25to30_up_2018 		= jet_pT25to30_2018 + 10*(+  0.036946 );
float jet_pT25to30_down_2018 	= jet_pT25to30_2018 + 10*(-  0.036946 );
float jet_pT30to35_2018 			= 0.9241967;
float jet_pT30to35_up_2018 		= jet_pT30to35_2018 + 10*(+ 0.0270 );
float jet_pT30to35_down_2018 	= jet_pT30to35_2018 + 10*(- 0.0270 );
float jet_pT35to40_2018 			= 0.9135042;
float jet_pT35to40_up_2018 		= jet_pT35to40_2018 + 10*(+ 0.026734 );
float jet_pT35to40_down_2018 	= jet_pT35to40_2018 + 10*(- 0.026734 );
float jet_pT40toInf_2018 			= 0.932037798905;
float jet_pT40toInf_up_2018 	= jet_pT40toInf_2018 + 10*( + 0.022959 );
float jet_pT40toInf_down_2018 = jet_pT40toInf_2018 + 10*( - 0.024759 );
