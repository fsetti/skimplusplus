import os
import glob
import pandas 
import argparse
import root_pandas
import numpy as np

years = [ '2016UL_preVFP', '2017', '2018' ]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/home/users/smay/HiggsDNA/hhggtautau_sr_11May2022/"
)

parser.add_argument(
    "--tag",
    help = "unique tag to identify batch of processed samples",
    type = str,
    default = "25May2022"
)
parser.add_argument(
    "--mvas",
	nargs='*',
    help = "mva limits to SRs",
    type = float,
    default = [0.959506, 0.9899]	
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

out_dir = '/home/users/fsetti/HHggTauTau/coupling_scan/CMSSW_10_2_13/src/flashggFinalFit/files_systs/' + str(args.tag) + '/'

#os.system("rm -rf %s"%(out_dir))
os.system("mkdir -p %s"%(out_dir))

os.system("mkdir -p %s/Data"%(out_dir))
os.system("mkdir -p %s/2016"%(out_dir))
os.system("mkdir -p %s/2017"%(out_dir))
os.system("mkdir -p %s/2018"%(out_dir))

procs = glob.glob(str(args.input)+'/*HH*')

for proc in procs[:]:

	for year in years:
		if year not in proc.split("/")[-1]:
			continue
		#get all files including systematic variations
		files = glob.glob(proc+'/*.parquet')
		
		for file_ in files:
			#print ("Now processing: ".join(file_.split("/")[-2:]), " and ".join(file_.replace("HHggTauTau","HHggWW_dileptonic").split("/")[-2:]), " and ".join(file_.replace("HHggTauTau","HHggWW_semileptonic").split("/")[-2:]) )
			df = pandas.read_parquet(file_, engine='pyarrow')
			if year == '2016UL_preVFP':
				df_ext1 						= pandas.read_parquet(file_.replace("2016UL_preVFP","2016UL_postVFP"), engine='pyarrow')
				df = pandas.concat([ df, df_ext1 ], ignore_index=True)
				
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
	
			#Get kl coupling:
			kl_str = [ x for x in file_.split("/")[-2].split("_") if 'kl' in x ]
			if len(kl_str) == 0:
				kl_str = 'kl1'
			else:
				kl_str = kl_str[0]
			proc_tag = 'ggHH'+kl_str+'kt1'
			if 'dileptonic' in file_.split("/")[-2]:
				proc_tag += 'WWdilep'
			if 'semileptonic' in file_.split("/")[-2]:
				proc_tag += 'WWsemilep'
	
			#Process Signal
			year_str = year
			if '2016' in year:
				year_str = '2016'
			for sr in range(args.nSRs):
					dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) & (df.event % 2 == 1) ]
					#dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) & ( df.weight_central > -9999 ) ]
					dfs.to_root(out_dir+year_str+'/'+proc_tag+'_125_13TeV.root',''+proc_tag+'_125_13TeV_SR'+str(sr+1)+tag, mode='a')
