import os
import glob
import pandas
import argparse
#import root_pandas
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    help = "path to input parquet directory",
    type = str,
    default = "/home/users/smay/HiggsDNA/test_xyh_11Aug2022/"
)

args = parser.parse_args()


files = glob.glob(args.input+"*.parquet")
systs	= [ f.split("/")[-1].split("merged_")[-1].split(".parquet")[0] for f in files ]

for file_ in files:
	print("Now processing: " , systs[files.index(file_)] )
	df = pandas.read_parquet(file_, engine='pyarrow')
	
	#remove events outside mgg fit window
	df = df.loc[ ((df.Diphoton_mass > 65) & (df.Diphoton_mass < 120)) ]
	
	df['weight'] = df['weight_central']
	
	df['CMS_hgg_mass'] = df['Diphoton_mass']
	df['mgg'] = df['Diphoton_mass']
	df['dZ'] = np.ones(len(df['Diphoton_mass']))
	df = df.drop(columns=["bdt_score"])
	
	out_file = '/ceph/cms/store/user/fsetti/XYH_NMSSM_BDT/files/xyh_nmssm_'+systs[files.index(file_)]+'.pkl'
	df.to_pickle(out_file)
