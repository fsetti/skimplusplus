import os
import glob
import json
import pandas
import argparse
import root_pandas
import numpy as np

years = [ '2016', '2017', '2018' ]
procs_dict = { "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_90": "NMSSMYggHbbMX600MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_95": "NMSSMYggHbbMX600MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_600_MY_100": "NMSSMYggHbbMX600MY100",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_90": "NMSSMYggHbbMX650MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_95": "NMSSMYggHbbMX650MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_650_MY_100": "NMSSMYggHbbMX650MY100",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_90": "NMSSMYggHbbMX700MY90",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_95": "NMSSMYggHbbMX700MY95",  "NMSSM_XYH_Y_gg_H_bb_MX_700_MY_100": "NMSSMYggHbbMX700MY100"}
#procs_dict = { "DY": "DY"}


parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/ceph/cms/store/user/fsetti/XYH_NMSSM_BDT/out_zipped/"
)

parser.add_argument(
    "--tag",
    help = "unique tag to identify batch of processed samples",
    type = str,
    default = "21Sep2022"
)
parser.add_argument(
    "--mvas",
	nargs='*',
    help = "mva limits to SRs",
    type = dict,
    default = {'MY90': [ 0.994120, 0.9986, 99], 'MY95': [0.984621, 0.9969, 99 ], 'MY100': [0.967094, 0.9969, 99] }	
)
parser.add_argument(
    "--nSRs",
    help = "number of Signal Regions",
    type = int,
    default = 2
)

args = parser.parse_args()

#mxs = [ 600]
mys = [ 'MY90', 'MY95', 'MY100' ] 

files = glob.glob(args.input+"xyh_nmssm_*"+args.tag+"*.pkl")
systs = [ f.split("/")[-1].split("xyh_nmssm_")[-1].split("_"+args.tag)[0] for f in files ]

#Load sample_id_map
process_id_map = {}
with open("/home/users/smay/HiggsDNA/xyh_ggbb_2Aug2022/summary.json", "r") as map_file:
	configurations = json.load(map_file)
	process_id_map = configurations["sample_id_map"]

#for mx in mxs:
for my in mys:

		procs = [ proc for proc in procs_dict.keys() if my in procs_dict[proc] or "DY" in proc ]

		srs_boundaries	= args.mvas[my]
		srs_boundaries.sort(reverse=True)
		
		out_dir = '/home/users/fsetti/flashggFinalFit_resonant/CMSSW_10_2_13/src/flashggFinalFit/files/'+ args.tag + "_" + my + "/" 
		
		os.system("rm -rf %s"%(out_dir))
		os.system("mkdir -p %s"%(out_dir))
		
		os.system("mkdir -p %s/Data"%(out_dir))
		os.system("mkdir -p %s/2016"%(out_dir))
		os.system("mkdir -p %s/2017"%(out_dir))
		os.system("mkdir -p %s/2018"%(out_dir))

		#############################################		
		#############    Process Data

		#Read nominal pkl for Data
		df = pandas.read_pickle(str(args.input)+"xyh_nmssm_nominal_"+args.tag+".pkl")

		for sr in range(args.nSRs):
			dfs = df.loc[ ( df.mva_score < srs_boundaries[sr] ) & ( df.mva_score >= srs_boundaries[sr+1] ) & ( df.process_id == 0 ) ]
			dfs.to_root(out_dir+'/Data/'+'/allData.root',key='Data_13TeV_SR'+str(sr+1), mode='a')
		
		#############################################		
		#############    Process Signal & resonant bkg
		for syst in systs:		
			print("Now processing systematic: " , syst )	
			df = pandas.read_pickle(str(args.input)+"xyh_nmssm_"+syst+"_"+args.tag+".pkl")

			"""
			#remove processes not needed
			needed_ids = [ process_id_map[proc] for proc in process_id_map.keys() if my in proc ]
			procs_conditions = ( (df.process_id ==  process_id_map['DY']) | any( df.process_id == id for id in needed_ids ) ) 
			df = df.loc[ procs_conditions ]
			"""

			tag	=	''
			if 'nominal' not in syst:
				if 'up' in syst:
					tag	= '_' + syst.split("_up")[0]
					tag	+= 'Up01sigma'
				elif 'down' in syst:
					tag	= '_' + syst.split("_down")[0]
					tag	+= 'Down01sigma'
			if 'scale' in syst:
				tag = '_MCScale' + tag
			if 'smear' in syst:
				tag = '_MCSmear' + tag

			#Rescale due to splitting of training / testing / validation 
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
			print(rename_sys)
			df = df.rename(columns=rename_sys)

			for sr in range(args.nSRs):
				df_syst = df.loc[ ( df.mva_score < srs_boundaries[sr] ) & ( df.mva_score >= srs_boundaries[sr+1] ) & (df.event % 2 == 1) ]

				for proc in procs:

					df_proc = df_syst.loc[ ( df_syst.process_id == process_id_map[proc] ) ]

					for year in years:
						dfs = pandas.DataFrame()
						if year == '2016':
							dfs = df_proc.loc[ ( df_proc.year == b'2016UL_pre' ) |  ( df_proc.year == b'2016UL_post' ) ]
						elif year == '2017':
							dfs = df_proc.loc[ ( df_proc.year == b'2017' ) ]
						elif year == '2018':
							dfs = df_proc.loc[ ( df_proc.year == b'2018' ) ]
						dfs.to_root(out_dir+year+'/'+procs_dict[proc]+'_'+my.split("MY")[-1]+'_13TeV.root',procs_dict[proc]+'_'+my.split("MY")[-1]+'_13TeV_SR'+str(sr+1)+tag, mode='a')
