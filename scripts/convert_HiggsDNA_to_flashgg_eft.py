import os
import glob
import pandas
import argparse
import root_pandas
import numpy as np

years = [ '2016UL_preVFP', '2017', '2018' ]
procs_dict = { "ggH_M125": "ggH", 'HH_ggTauTau_EFT_node_1':'ggHHbm1', 'HH_ggTauTau_EFT_node_2':'ggHHbm2', 'HH_ggTauTau_EFT_node_3':'ggHHbm3', 'HH_ggTauTau_EFT_node_4':'ggHHbm4', 'HH_ggTauTau_EFT_node_5':'ggHHbm5', 'HH_ggTauTau_EFT_node_6':'ggHHbm6', 'HH_ggTauTau_EFT_node_7':'ggHHbm7', 'HH_ggTauTau_EFT_node_8':'ggHHbm8', 'HH_ggTauTau_EFT_node_9':'ggHHbm9', 'HH_ggTauTau_EFT_node_10':'ggHHbm10', 'HH_ggTauTau_EFT_node_11':'ggHHbm11', 'HH_ggTauTau_EFT_node_12':'ggHHbm12', 'ttH_M125':'ttH', 'VBFH_M125':'VBFH', 'VH_M125':'VH', "Data":"Data" }

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/home/users/smay/HiggsDNA/"
)

parser.add_argument(
    "--tag",
    help = "unique tag to identify batch of processed samples",
    type = str,
    default = "v0"
)

args = parser.parse_args()

eft_points = [ 'ggtautau_sr_eft_' + str(x) + '_21Apr2022' for x in range(1,13) ]

eft_boundaries = [
[  0.912695,  0.9830 ],
[  0.994044,  0.9995 ],
[  0.894935,  0.9857 ],
[  0.909370,  0.9887] ,
[  0.861141,  0.9816] ,
[  0.828323,  0.9826] ,
[  0.947518,  0.9875] ,
[  0.479675,  0.9865] ,
[  0.920841,  0.9844] ,
[  0.924548,  0.9860] ,
[  0.945699,  0.9772] ,
[  0.957525,  0.9861] 
]

idx=0
for eft_point in eft_points:

	os.system("mkdir -p /home/users/fsetti/HHggTauTau/coupling_scan/CMSSW_10_2_13/src/flashggFinalFit/files_systs/%s"%(eft_point))
	out_dir = '/home/users/fsetti/HHggTauTau/coupling_scan/CMSSW_10_2_13/src/flashggFinalFit/files_systs/'+ str(eft_point) + '/' + str(args.tag) + '/'
	os.system("rm -rf %s"%(out_dir))
	os.system("mkdir -p %s"%(out_dir))
	
	os.system("mkdir -p %s/Data"%(out_dir))
	os.system("mkdir -p %s/2016"%(out_dir))
	os.system("mkdir -p %s/2017"%(out_dir))
	os.system("mkdir -p %s/2018"%(out_dir))

	procs = glob.glob(str(args.input+"/"+eft_point)+'/*')
	mvas = eft_boundaries[idx]	
	mvas += [99]
	mvas.sort(reverse=True)

	print ("Processing: " , eft_point , "with mva cuts: " , mvas )
	#Process Data
	files = glob.glob(str(args.input+"/"+eft_point)+'/Data*/*.parquet')
	for file_ in files:
		df = pandas.read_parquet(file_, engine='pyarrow')
		df['CMS_hgg_mass'] = df['Diphoton_mass']
		for sr in range(2):
			dfs = df.loc[ ( df.bdt_score < mvas[sr] ) & ( df.bdt_score >= mvas[sr+1] ) & ( ( df.Diphoton_mass < 120 ) | ( df.Diphoton_mass > 130 ) ) ]
			dfs.to_root(out_dir+'/Data/'+'/allData.root',key='Data_13TeV_SR'+str(sr+1), mode='a')
	
	for proc in procs[:]:
	
		if "Data" in proc:
			continue
	
		if proc.split("/")[-1].split("_201")[0] not in procs_dict.keys():
			continue
			
		for year in years:
			if year not in proc.split("/")[-1]:
				continue
		
			#get all files including systematic variations
			files = glob.glob(proc+'/*.parquet')
			
			for file_ in files:
				print ("Now processing: ", file_)
				df = pandas.read_parquet(file_, engine='pyarrow')
				if year == '2016UL_preVFP':
					try:
						df_ext1 						= pandas.read_parquet(file_.replace("2016UL_preVFP","2016UL_postVFP"), engine='pyarrow')
						df = pandas.concat([ df, df_ext1 ], ignore_index=True)
					except:
						print ("Not finding 2016UL_postVFP for this sample: ", proc )
						print ("Most likely it is data")
					
				tag	=	''
				if 'nominal' not in file_.split("/")[-1]:
					if 'up' in file_.split("/")[-1]:
						tag	= file_.split("merged")[-1]
						tag	= tag.split("_up")[0]
						tag	+= 'Up01sigma'
					if 'down' in file_.split("/")[-1]:
						tag	= file_.split("merged")[-1]
						tag	= tag.split("_down")[0]
						tag	+= 'Down01sigma'
				if 'scale' in file_.split("/")[-1]:
					tag = '_MCScale' + tag
				if 'smear' in file_.split("/")[-1]:
					tag = '_MCSmear' + tag
	
				#Define hgg_mass & dZ variable
				df['CMS_hgg_mass'] = df['Diphoton_mass']
				df['dZ']	= np.ones(len(df['Diphoton_mass']))
				df['weight'] = df['weight_central'] * 2
				df['weight_central'] = df['weight'] 
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
				proc_tag = procs_dict[proc.split("/")[-1].split("_201")[0]]
				#if 'EFT' in proc.split("/")[-1]:
				#	proc_tag = 'ggHHbm' + proc.split("/")[-1].split("node_")[-1].split("_201")[0]
				#else: 
				#	proc_tag = procs_dict[proc.split("/")[-1].split("_201")[0]]
	
				'''
				Temporary fix to get limits
				'''
				for sr in range(2):
						dfs = df.loc[ ( df.bdt_score < mvas[sr] ) & ( df.bdt_score >= mvas[sr+1] ) & (df.event % 2 == 1) ]
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',''+proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')

	idx += 1
