import os
import json 
import subprocess
from collections import OrderedDict


#mass_range = [ "High" , "Low" ]
mass_range = [ "High" ]

for mr in mass_range:
	skim_dir = '/ceph/cms/store/user/fsetti/c++_looper_ul_output/18Jan2023_resonantSignal_%sMass/'%(mr)
	procs = subprocess.check_output('ls -d %s/*'%(skim_dir), shell=True) 
	procs = procs.splitlines()
	procs = [ p.split("/")[-1] for p in procs if "NMSSM_XYH_Y_tautau_H_gg" in p  and "MY_50" == p[-5:]]
	print("For mass range:  " , mr )
	print("Copy and paste this loooooong list: ")
	print(procs)
