import os
import glob
import pandas
import argparse
import root_pandas
import numpy as np

years = [ '2016UL_preVFP', '2017', '2018' ]
#procs_dict = { "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_90": "NMSSMYggHbbMX600MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_95": "NMSSMYggHbbMX600MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_100": "NMSSMYggHbbMX600MY100",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_90": "NMSSMYggHbbMX650MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_95": "NMSSMYggHbbMX650MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_100": "NMSSMYggHbbMX650MY100",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_90": "NMSSMYggHbbMX700MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_95": "NMSSMYggHbbMX700MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_100": "NMSSMYggHbbMX700MY100"}
procs_dict = { "DY": "DY"}


parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/home/users/smay/HiggsDNA/test_xyh_11Aug2022/"
)

parser.add_argument(
    "--tag",
    help = "unique tag to identify batch of processed samples",
    type = str,
    default = "15Aug2022_bbgg_res"
)
parser.add_argument(
    "--mvas",
	nargs='*',
    help = "mva limits to SRs",
    type = float,
    default = [ 0.882222, 0.9898]	
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

out_dir = '/home/users/fsetti/flashggFinalFit_resonant/CMSSW_10_2_13/src/flashggFinalFit/files/' + str(args.tag) + '/'

#os.system("rm -rf %s"%(out_dir))
os.system("mkdir -p %s"%(out_dir))

os.system("mkdir -p %s/Data"%(out_dir))
os.system("mkdir -p %s/2016"%(out_dir))
os.system("mkdir -p %s/2017"%(out_dir))
os.system("mkdir -p %s/2018"%(out_dir))

#Process Data
'''
files = glob.glob(str(args.input)+'/Data*/*.parquet')
df1 = pandas.read_parquet(files[0], engine='pyarrow')
df2 = pandas.read_parquet(files[1], engine='pyarrow')
df3 = pandas.read_parquet(files[2], engine='pyarrow')
df4 = pandas.read_parquet(files[3], engine='pyarrow')

#Merge all years together
df = pandas.concat([ df1, df2, df3, df4  ], ignore_index=True)
df['CMS_hgg_mass'] = df['Diphoton_mass']
for sr in range(args.nSRs):
	dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) & ( df.Diphoton_mass > 65 ) & ( df.Diphoton_mass < 120 ) ]
	dfs.to_root(out_dir+'/Data/'+'/allData.root',key='Data_13TeV_SR'+str(sr+1), mode='a')
'''

procs = glob.glob(str(args.input)+'/*')
procs = [ proc for proc in procs if proc.split("/")[-1].split("_201")[0] in procs_dict.keys() ]

print(procs)
for proc in procs :
		
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

			proc_tag = procs_dict[proc.split("/")[-1].split("_201")[0]]
			mass_point = ''
			if "MY90" in proc_tag:
				mass_point = '90'
			elif "MY95" in proc_tag:
				mass_point = '95'
			elif "MY96" in proc_tag:
				mass_point = '96'
			elif "MY97" in proc_tag:
				mass_point = '97'
			elif "MY98" in proc_tag:
				mass_point = '98'
			elif "MY99" in proc_tag:
				mass_point = '99'
			elif "MY100" in proc_tag:
				mass_point = '100'

			for sr in range(args.nSRs):
					dfs = df.loc[ ( df.bdt_score < args.mvas[sr] ) & ( df.bdt_score >= args.mvas[sr+1] ) & (df.event % 2 == 1) ]
					if mass_point != '':
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_'+mass_point+'_13TeV.root',''+proc_tag+'_'+mass_point+'_13TeV_SR'+str(sr+1)+tag, mode='a')
					else :
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M90_13TeV.root',''+proc_tag+'_M90_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M95_13TeV.root',''+proc_tag+'_M95_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M96_13TeV.root',''+proc_tag+'_M96_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M97_13TeV.root',''+proc_tag+'_M97_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M98_13TeV.root',''+proc_tag+'_M98_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M99_13TeV.root',''+proc_tag+'_M99_13TeV_SR'+str(sr+1)+tag, mode='a')
						dfs.to_root(out_dir+year_str+'/'+proc_tag+'_M100_13TeV.root',''+proc_tag+'_M100_13TeV_SR'+str(sr+1)+tag, mode='a')
