import pandas as pd
import uproot
import glob

date="28Apr2022_POGsel"
file_names = glob.glob("../outputs_UL/*"+date+"_201*.root")

iter = 0
df = pd.DataFrame()
for file_name in file_names:
	if "HH_gg" not in file_name :
		continue
	print ( file_name.split("outputs")[-1].replace(".root",".pkl") )
	tree = uproot.open(file_name)["Events"]
	df_tmp = tree.pandas.df()
	if iter == 0:
		df = df_tmp
	else:
		df = pd.concat([df,df_tmp], ignore_index=True)
	iter +=1
#df.to_pickle("/home/users/fsetti/HHggTauTau/HggAnalysisDev/MVAs/files/run2_"+date+"_sig.pkl")
df.to_pickle("/home/users/fsetti/HHggTauTau/HggAnalysisDev/MVAs/files/run2_"+date+"_test.pkl")
