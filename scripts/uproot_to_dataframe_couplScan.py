import glob
import uproot
import numpy as np
import pandas as pd

tag="04Nov2022"
file_names = glob.glob("/ceph/cms/store/user/fsetti/c++_output_no_skim++/"+tag+"/HH_ggWW_*.root")
tag="23Jan2022_ggWWcentralValidation"
file_names += glob.glob("/ceph/cms/store/user/fsetti/c++_output_no_skim++/"+tag+"/*.root")

iter = 0
df = pd.DataFrame()
for file_name in file_names:
	print ( file_name.split("c++_output_no_skim++/")[-1].replace(".root",".pkl") )
	tree = uproot.open(file_name)["Events"]
	df_tmp = tree.pandas.df()
	#df_tmp = df_tmp.loc[ ( df_tmp.lep1_dm != -1 ) | ( df_tmp.lep2_dm != -1 ) ]
	#Adjust weights of NMSSM samples
	#if "NMSSM" in file_name:
	#	df_tmp['weight'] = np.ones(len(df_tmp['weight']))
	if iter == 0:
		df = df_tmp
	else:
		df = pd.concat([df,df_tmp], ignore_index=True)
	iter +=1
df.to_pickle("/ceph/cms/store/user/fsetti/c++_output_no_skim++/pickles/validate_ggWW_central.pkl")
