import os
import json 
import subprocess
from collections import OrderedDict


#out_json = "/home/users/fsetti/HHggTauTau/skimplusplus/samples_and_scale1fb_ul_bkg_central.json"
out_jsonLow = "../samples_and_scale1fb_ul_resonant_central_LowMass_ext.json"
#os.system("rm %s"%(out_json))
os.system("rm %s"%(out_jsonLow))

skim_dir = '/ceph/cms/store/user/legianni/skimNano-TestUL__TEST-SamplesV9/'
procs = subprocess.check_output('ls -d %s/NMSSM*/'%(skim_dir), shell=True) 
procs = procs.splitlines()
procs = [ p for p in procs if "MY_50_" in p ]

samplesLowMass = {}
samples = OrderedDict() 

for p in procs:
	proc = p.split("/")[-2]
	files2016 		= subprocess.check_output('ls -d %s/*%s*/*/*/'%(skim_dir+proc, '20UL16MiniAODv2')		, shell=True).splitlines()
	files2016_APV = subprocess.check_output('ls -d %s/*%s*/*/*/'%(skim_dir+proc, '20UL16MiniAODAPVv2'), shell=True).splitlines()
	files2017 		= subprocess.check_output('ls -d %s/*%s*/*/*/'%(skim_dir+proc, '20UL17MiniAODv2')		, shell=True).splitlines()
	files2018 		= subprocess.check_output('ls -d %s/*%s*/*/*/'%(skim_dir+proc, '20UL18MiniAODv2')		, shell=True).splitlines()

	years = OrderedDict({
		"2016" : {
    	"metadata": {
      	"scale1fb": 1
			},
     "paths": [files2016[0]]
	 },
		"2016_APV" : {
    	"metadata": {
      	"scale1fb": 1
			},
     "paths": [files2016_APV[0]]
	 },
		"2017" : {
    	"metadata": {
      	"scale1fb": 1
			},
     "paths": [files2017[0]]
	 },
		"2018" : {
    	"metadata": {
      	"scale1fb": 1
			},
     "paths": [files2018[0]]
	 },
   "fpo": 10,
   "process_id": -1*int(procs.index(p))-1234,
   "resonant": False
	})

	proc = proc.split("_narrow")[0]
	proc = proc.split("_TuneCP5")[0]
	samples[proc] = years
	'''
	#Divide based on low mass diphoton or not
	if "NMSSM_XYH_Y_gg_H_tautau" in proc:
		my = float( proc.split( "MY_")[-1].split("_")[0] )
		if my < 100:
			samplesLowMass[proc] = years
		elif my <= 125:
			samplesLowMass[proc] = years
			samples[proc] = years
		else:
			samples[proc] = years
	else:
		samples[proc] = years

with open(out_json, "w") as outfile:
	json.dump(samples, outfile, indent=2)
	'''
with open(out_jsonLow, "w") as outfile:
	json.dump(samples, outfile, indent=2)
