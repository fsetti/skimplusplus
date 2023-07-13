import os
import glob
import json
import pandas
import argparse
import root_pandas
import numpy as np

years = [ '2016UL_preVFP', '2017', '2018' ]
procs_dict = { "ggH_M125": "ggH", 'HHggTauTau':'HHggTauTau', 'HHggWW_dileptonic':'HHggWWdileptonic', 'HHggWW_semileptonic':'HHggWWsemileptonic', 'ttH_M125':'ttH', 'VBFH_M125':'VBFH', 'VH_M125':'VH'}
#procs_dict = { }
procs_dict_lhe = { "ggH_M125": "ggH", 'HHggTauTau':'HH_ggTauTau_kl1', 'HHggWW_dileptonic':'HH_ggWW_dileptonic_kl1', 'HHggWW_semileptonic':'HH_ggWW_semileptonic_kl1', 'ttH_M125':'ttH', 'VBFH_M125':'VBFH', 'VH_M125':'VH'}


parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    #default = "/ceph/cms/store/user/fsetti/HiggsDNA_output/20Dec2022_lheWeights/"
    default = "/ceph/cms/store/user/fsetti/SRs_BDT/out_zipped/forFinalFit/25Apr2023_final/"
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
    default = "09May2023_nonRes_SM_final"
)
parser.add_argument(
    "--mvas",
	nargs='*',
    help = "mva limits to SRs",
    type = float,
    default = [ 0.973610,  0.9891]		#SR optimisation using HiggsDNA outputs (includes Tau SFs, etc.)
    #default = [ 0.973610,  0.9860]		#v2
)
parser.add_argument(
    "--nSRs",
    help = "number of Signal Regions",
    type = int,
    default = 2
)

args = parser.parse_args()

args.mvas+=[99]
args.mvas.sort(reverse=True)

out_dir = '/home/users/fsetti/ic_flashgg/CMSSW_10_2_13/src/flashggFinalFit/files_systs/' + str(args.tag) + '/'

#os.system("rm -rf %s"%(out_dir))
os.system("mkdir -p %s"%(out_dir))

os.system("mkdir -p %s/Data"%(out_dir))
os.system("mkdir -p %s/2016"%(out_dir))
os.system("mkdir -p %s/2017"%(out_dir))
os.system("mkdir -p %s/2018"%(out_dir))

procs = glob.glob(str(args.input)+'/*')

#Process Data - Use MET filtered data
files = glob.glob(str(args.input)+'/Data*/*.'+args.format)
if args.format == 'parquet':
	df1 = pandas.read_parquet(files[0], engine='pyarrow')
	df2 = pandas.read_parquet(files[1], engine='pyarrow')
	df3 = pandas.read_parquet(files[2], engine='pyarrow')
	df4 = pandas.read_parquet(files[3], engine='pyarrow')
else:
	df1 = pandas.read_pickle(files[0])
	df2 = pandas.read_pickle(files[1])
	df3 = pandas.read_pickle(files[2])
	df4 = pandas.read_pickle(files[3])
#Merge all years together
df = pandas.concat([ df1, df2, df3, df4 ], ignore_index=True)
df['CMS_hgg_mass'] = df['Diphoton_mass']
for sr in range(args.nSRs):
	if args.format == 'parquet':
		#dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) & ( ( df.Diphoton_mass < 120 ) | ( df.Diphoton_mass > 130 ) ) & ( df.Diphoton_mass > 100.2 ) ].copy()
		dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) ].copy()
	else:
		#dfs = df.loc[ ( df.mva_score < args.mvas[sr] ) & ( df.mva_score >= args.mvas[sr+1] ) & ( ( df.Diphoton_mass < 120 ) | ( df.Diphoton_mass > 130 ) ) ].copy()
		dfs = df.loc[ ( df.mva_score < args.mvas[sr] ) & ( df.mva_score >= args.mvas[sr+1] ) ].copy()
	dfs.to_root(out_dir+'/Data/'+'/allData.root',key='Data_13TeV_SR'+str(sr+1), mode='a')


'''
for proc in procs[:]:

	if proc.split("/")[-1].split("_201")[0] not in procs_dict.keys():
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
			df['weight'] = df['weight_central'] #* 2			#ONLY for MC!! 	Removed factor x2 since BDT trained on independent samples
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
				proc_tag = 'ggHHbm' + proc.split("/")[-1].split("EFT_")[-1].split("_201")[0] + procs_dict[proc.split("/")[-1].split("_EFT")[0]] 
			else: 
				proc_tag = procs_dict[proc.split("/")[-1].split("_201")[0]]

			for sr in range(args.nSRs):
					if args.format == 'parquet':
						dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) ].copy() #& (df.event % 2 == 1) ] 		#Removed since BDT trained on privte MC
					else:
						dfs = df.loc[ ( df.mva_score < args.mvas[sr] ) & ( df.mva_score >= args.mvas[sr+1] ) ].copy() #& (df.event % 2 == 1) ]
					#dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',key=proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')

					if tag != '':
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',key=proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')

					else:
						proc_lhe	= procs_dict_lhe[proc.split("/")[-1].split("_201")[0]]

						if proc_lhe == 'ggH':
							dfs['weight_lhe_scale0_sf_central'] 		= np.ones(len(dfs['weight_central']))
							dfs['weight_lhe_scale0_sfDown01sigma']	= np.ones(len(dfs['weight_central'])) 
							dfs['weight_lhe_scale0_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) 
							dfs['weight_lhe_scale1_sf_central']			=	np.ones(len(dfs['weight_central']))
							dfs['weight_lhe_scale1_sfDown01sigma']	=	np.ones(len(dfs['weight_central']))
							dfs['weight_lhe_scale1_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) 
							dfs['weight_lhe_scale2_sf_central']			=	np.ones(len(dfs['weight_central']))
							dfs['weight_lhe_scale2_sfDown01sigma']	=	np.ones(len(dfs['weight_central'])) 
							dfs['weight_lhe_scale2_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) 

							dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',key=proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')
							continue

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
						
						if w_0_down < 1 and w_0_up < 1:
							w_0_up = 2 - w_0_down
						else:
							w_0_down = 2 - w_0_up

						if w_1_down < 1 and w_1_up < 1:
							w_1_up = 2 - w_1_down
						else:
							w_1_down = 2 - w_1_up

						if w_2_down < 1 and w_2_up < 1:
							w_2_up = 2 - w_2_down
						else:
							w_2_down = 2 - w_2_up

						dfs['weight_lhe_scale0_sf_central'] 		= np.ones(len(dfs['weight_central']))
						dfs['weight_lhe_scale0_sfDown01sigma']	= np.ones(len(dfs['weight_central'])) * round(w_0_down, 4)
						dfs['weight_lhe_scale0_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * round(w_0_up, 4)
						dfs['weight_lhe_scale1_sf_central']			=	np.ones(len(dfs['weight_central']))
						dfs['weight_lhe_scale1_sfDown01sigma']	=	np.ones(len(dfs['weight_central'])) * round(w_1_down, 4)
						dfs['weight_lhe_scale1_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * round(w_1_up, 4)
						dfs['weight_lhe_scale2_sf_central']			=	np.ones(len(dfs['weight_central']))
						dfs['weight_lhe_scale2_sfDown01sigma']	=	np.ones(len(dfs['weight_central'])) * round(w_2_down, 4)
						dfs['weight_lhe_scale2_sfUp01sigma']		=	np.ones(len(dfs['weight_central'])) * round(w_2_up, 4)

						print("-----------------    SR%s   ------------------"%(str(sr+1)))
						print("SR post normalisation LHE Scale 0 Up variation: " , w_0_up )
						print("SR post normalisation LHE Scale 0 Down variation: " , w_0_down )
						print("SR post normalisation LHE Scale 1 Up variation: " , w_1_up )
						print("SR post normalisation LHE Scale 1 Down variation: " , w_1_down )
						print("SR post normalisation LHE Scale 2 Up variation: " , w_2_up )
						print("SR post normalisation LHE Scale 2 Down variation: " , w_2_down )

						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',key=proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')
'''
