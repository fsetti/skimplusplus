import os
import glob
import numpy as np
import pandas as pd

tag="20Mar2023_nonRes"
file_names = glob.glob("/ceph/cms/store/user/fsetti/HiggsDNA/"+tag+"/*/merged_nominal.parquet")

iter = 0
df = pd.DataFrame()

for file_ in file_names:
	print("Now processing: " , file_ )
	df_tmp = pd.read_parquet(file_, engine='pyarrow')
	if "Data" not in file_.split("/")[-2]:
		df_tmp = df_tmp.drop(columns=["SubleadPhoton_genPartFlav"])
		df_tmp = df_tmp.drop(columns=["LeadPhoton_genPartFlav"])
		df_tmp = df_tmp.drop(columns=["weight_central_no_lumi"])
	
	#blind data + non-res. bkg
	if "HHgg" not in file_.split("/")[-2] and "M125" not in file_.split("/")[-2]:
		print("Blinding 120<mgg<130 region for this process")
		df_tmp = df_tmp.loc[ ((df_tmp.Diphoton_mass < 120) | (df_tmp.Diphoton_mass > 130)) ]
	
	df_tmp['weight'] = df_tmp['weight_central']
	
	df_tmp['CMS_hgg_mass'] = df_tmp['Diphoton_mass']
	df_tmp['mgg'] = df_tmp['Diphoton_mass']
	df_tmp['dZ'] = np.ones(len(df_tmp['Diphoton_mass']))

	if iter == 0:
		df = df_tmp
	else:
		df = pd.concat([df,df_tmp], ignore_index=True)
	iter +=1

os.system("mkdir -p /ceph/cms/store/user/fsetti/HiggsDNA_pickle/%s"%(tag))
out_file = '/ceph/cms/store/user/fsetti/HiggsDNA_pickle/'+tag+'/all_nominal.pkl'
#df = df.reset_index()
#df = df.drop(columns=["index"])
df.to_pickle(out_file)
