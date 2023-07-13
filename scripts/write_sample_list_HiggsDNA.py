import os
import json 
import subprocess
from collections import OrderedDict


#mass_range = [ "High" , "Low" ]
mass_range = [ "High" ]

for mr in mass_range:
	out_json 		= "/home/users/fsetti/HHggTauTau/HiggsDNA_ggtt/metadata/samples/out_%s_tmp.json"%(mr)
	os.system("rm %s"%(out_json))
	
	skim_dir = '/ceph/cms/store/user/fsetti/c++_looper_ul_output/18Jan2023_resonantSignal_%sMass/'%(mr)
	procs = subprocess.check_output('ls -d %s/*'%(skim_dir), shell=True) 
	procs = procs.splitlines()
	
	samples = OrderedDict() 
	
	for p in procs:
		print(p)
		proc = p.split("/")[-1]
	
		files2016APV 	= str(skim_dir + proc + "/*2016_APV.root")
		files2016 		= str(skim_dir + proc + "/*2016.root")
		files2017 		= str(skim_dir + proc + "/*2017.root")
		files2018 		= str(skim_dir + proc + "/*2018.root")
		years = OrderedDict({ "files" : OrderedDict({ "2016UL_preVFP": files2016APV, "2016UL_postVFP": files2016, "2017": files2017, "2018": files2018}) , "xs": 0.001, "fpo": 3, "process_id": - int(procs.index(p)) - 176 })
		samples[proc] = years
	
	with open(out_json, "w") as outfile:
		json.dump(samples, outfile, indent=2)
