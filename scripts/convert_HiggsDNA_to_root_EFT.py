import os
import glob
import json
import pandas
import argparse
import root_pandas
import numpy as np

years = [ '2016UL_preVFP', '2017', '2018' ]
procs_dict = [
		#'HHggTauTau_kl1',         'HHggTauTau_kl0',         'HHggTauTau_kl2p45',         'HHggTauTau_kl5', 
		#'HHggWW_dileptonic_kl1',  'HHggWW_dileptonic_kl0',  'HHggWW_dileptonic_kl2p45',  'HHggWW_dileptonic_kl5', 
		'HHggWW_semileptonic_kl1','HHggWW_semileptonic_kl0','HHggWW_semileptonic_kl2p45','HHggWW_semileptonic_kl5',
]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/ceph/cms/store/user/fsetti/HiggsDNA/30Apr2023_nonRes_kl_for_eft/"
)
parser.add_argument(
    "--format",
    help = "format of input files, supported .pkl and .parquet",
    type = str,
    default = "parquet"
    #default = "pkl"
)
parser.add_argument(
    "--tag",
    help = "unique tag to identify batch of processed samples",
    type = str,
    default = "01May2023_kl_for_eft"
)
parser.add_argument(
    "--mvas",
	nargs='*',
    help = "mva limits to SRs",
    type = float,
    default = [ 0.973610 ]		#SR optimisation using HiggsDNA outputs (includes Tau SFs, etc.)
)
parser.add_argument(
    "--nSRs",
    help = "number of Signal Regions",
    type = int,
    default = 2
)

args = parser.parse_args()

out_dir = '/ceph/cms/store/user/fsetti/EFT_samples/' + str(args.tag) + '/'

#os.system("rm -rf %s"%(out_dir))
os.system("mkdir -p %s"%(out_dir))

os.system("mkdir -p %s/2016"%(out_dir))
os.system("mkdir -p %s/2017"%(out_dir))
os.system("mkdir -p %s/2018"%(out_dir))

procs = glob.glob(str(args.input)+'/*')

for proc in procs[:]:

	if proc.split("/")[-1].split("_201")[0] not in procs_dict:
		continue
		
	for year in years:
		if year not in proc.split("/")[-1]:
			continue
	
		#get all files including systematic variations
		files = glob.glob(proc+'/*.'+args.format)
		
		for file_ in files:
			print ("Now processing: ", file_)
			df = pandas.DataFrame()
			if args.format == 'parquet':
				df = pandas.read_parquet(file_, engine='pyarrow')
			else:
				df = pandas.read_pickle(file_)
			if year == '2016UL_preVFP':
				try:
					if args.format == 'parquet':
						df_ext1 						= pandas.read_parquet(file_.replace("2016UL_preVFP","2016UL_postVFP"), engine='pyarrow')
					else:
						df_ext1 						= pandas.read_pickle(file_.replace("2016UL_preVFP","2016UL_postVFP"))
					df = pandas.concat([ df, df_ext1 ], ignore_index=True)
				except:
					print ("Not finding 2016UL_postVFP for this sample: ", proc )
					print ("Most likely it is data")
				
			tag	=	''
			if 'nominal' not in file_.split("/")[-1]:
				#consider different naming conventions
				if args.format == 'parquet':
					tag	= file_.split("merged")[-1]
				else:
					tag	= "_" +file_.split("/")[-1]
				if 'up' in file_.split("/")[-1]:
					tag	= tag.split("_up")[0]
					tag	+= 'Up01sigma'
				if 'down' in file_.split("/")[-1]:
					tag	= tag.split("_down")[0]
					tag	+= 'Down01sigma'
			if 'scale' in file_.split("/")[-1]:
				tag = '_MCScale' + tag
			if 'smear' in file_.split("/")[-1]:
				tag = '_MCSmear' + tag

			#Define hgg_mass & dZ variable
			#df['weight'] = df['weight_central'] #removed since applied in EFT reweighting 
			df['CMS_hgg_mass'] = df['Diphoton_mass']
			df['dZ'] = np.ones(len(df['Diphoton_mass']))
			yield_systematics	= [ key for key in df.keys() if ( "weight_" in key ) and ( "_up" in key or "_down" in key )]
			rename_sys	= {}
			for sys in yield_systematics:
				#a bit of gymnastics to get the inputs right for Mr. flashggFinalFit
				sys_central = sys.replace("_up","_central")
				sys_central = sys_central.replace("_down","_central")
				if 'btag' in sys_central:
					sys_central = 'weight_btag_deepjet_sf_SelectedJet_central'
				df[sys] 		= df[sys] / df[sys_central]
				if "_up" in sys:
					if 'btag' in sys:
						if 'lf' == sys[-2:] or 'hf' == sys[-2:] :
							rename_sys[sys] = sys.replace("_up","")
							rename_sys[sys] = sys.replace("_lf","_LF")
							rename_sys[sys] = rename_sys[sys].replace("_hf","_HF")
							rename_sys[sys] += "Up01sigma"
							#print("Processed" , sys , " into " , rename_sys[sys] )
							continue
						rename_sys[sys] = sys.replace("_up","")
						rename_sys[sys] += "Up01sigma"
						continue
					rename_sys[sys] = sys.replace("_up","Up01sigma")
				if "_down" in sys:
					if 'btag' in sys:
						if 'lf' == sys[-2:] or 'hf' == sys[-2:] :
							rename_sys[sys] = sys.replace("_down","")
							rename_sys[sys] = sys.replace("_lf","_LF")
							rename_sys[sys] = rename_sys[sys].replace("_hf","_HF")
							rename_sys[sys] += "Down01sigma"
							continue
						rename_sys[sys] = sys.replace("_down","")
						rename_sys[sys] += "Down01sigma"
						continue
					rename_sys[sys] = sys.replace("_down","Down01sigma")
			#print(rename_sys)
			df = df.rename(columns=rename_sys)

			#Process Signal
			year_str = year
			if '2016' in year:
				year_str = '2016'

			proc_tag = ''
			if 'EFT' in proc.split("/")[-1]:
				proc_tag = 'ggHHbm' + proc.split("/")[-1].split("EFT_")[-1].split("_201")[0] + proc.split("/")[-1].split("_EFT")[0]
			else: 
				proc_tag = proc.split("/")[-1].split("_201")[0]

				if args.format == 'parquet':
					dfs = df.loc[ ( df.bdt_score >= args.mvas[0] ) ].copy() 		#Removed since BDT trained on privte MC
				else:
					dfs = df.loc[ ( df.mva_score >= args.mvas[0] ) ].copy() 

				if tag != '':
					dfs.to_root(out_dir+year_str+'/'+proc_tag+ tag + '_125_13TeV.root',key="Events", mode='w')

				else:
					proc_lhe	= proc.split("/")[-1].split("_201")[0].replace("HH","HH_")

					#Compute LHE scales
					w_sr 			= sum(dfs.weight_central)
					w_0_down	= sum(dfs.weight_central *	dfs.weight_lhe_scale0_sfDown01sigma)
					w_0_up		= sum(dfs.weight_central *	dfs.weight_lhe_scale0_sfUp01sigma)
					w_1_down	= sum(dfs.weight_central *	dfs.weight_lhe_scale1_sfDown01sigma)
					w_1_up		= sum(dfs.weight_central *	dfs.weight_lhe_scale1_sfUp01sigma)
					w_2_down	= sum(dfs.weight_central *	dfs.weight_lhe_scale2_sfDown01sigma)
					w_2_up		= sum(dfs.weight_central *	dfs.weight_lhe_scale2_sfUp01sigma)

					w_tot = {}
					with open("/home/users/fsetti/HHggTauTau/skimplusplus/lhe_scales/scales.json") as json_file:
						w_tot = json.load(json_file)
					w_0_down 	= ( w_0_down / w_sr ) / ( w_tot[proc_lhe][year_str]['lhe_scale_3'] / w_tot[proc_lhe][year_str]['tot_norm'] )
					w_0_up 		= ( w_0_up / w_sr ) 	/ ( w_tot[proc_lhe][year_str]['lhe_scale_5'] / w_tot[proc_lhe][year_str]['tot_norm'] )
					w_1_down 	= ( w_1_down / w_sr ) / ( w_tot[proc_lhe][year_str]['lhe_scale_1'] / w_tot[proc_lhe][year_str]['tot_norm'] )
					w_1_up 		= ( w_1_up / w_sr ) 	/ ( w_tot[proc_lhe][year_str]['lhe_scale_7'] / w_tot[proc_lhe][year_str]['tot_norm'] )
					w_2_down 	= ( w_2_down / w_sr ) / ( w_tot[proc_lhe][year_str]['lhe_scale_0'] / w_tot[proc_lhe][year_str]['tot_norm'] )
					w_2_up 		= ( w_2_up / w_sr ) 	/ ( w_tot[proc_lhe][year_str]['lhe_scale_8'] / w_tot[proc_lhe][year_str]['tot_norm'] )

					dfs['weight_lhe_scale0_sf_central'] 		= np.ones(len(dfs['weight_central']))
					dfs['weight_lhe_scale0_sfDown01sigma']	= np.ones(len(dfs['weight_central'])) * w_0_down
					dfs['weight_lhe_scale0_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * w_0_up
					dfs['weight_lhe_scale1_sf_central']			=	np.ones(len(dfs['weight_central']))
					dfs['weight_lhe_scale1_sfDown01sigma']	=	np.ones(len(dfs['weight_central'])) * w_1_down
					dfs['weight_lhe_scale1_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * w_1_up
					dfs['weight_lhe_scale2_sf_central']			=	np.ones(len(dfs['weight_central']))
					dfs['weight_lhe_scale2_sfDown01sigma']	=	np.ones(len(dfs['weight_central'])) * w_2_down
					dfs['weight_lhe_scale2_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * w_2_up

					dfs.to_root(out_dir+year_str+'/'+proc_tag+ tag + '_125_13TeV.root',key="Events", mode='w')
