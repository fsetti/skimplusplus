#!/usr/bin/env python
import os
import sys
import glob
import json
import ROOT as r
from tqdm import tqdm
from ROOT import gROOT

r.gSystem.Load('loopers/compute_LHEscales_C.so')

years = ['2016', '2017', '2018']
#years = ['2016']
samples = {}

base_dir='/home/users/fsetti/HHggTauTau/skimplusplus/lhe_scales/'
os.system("mkdir -p %s"%(base_dir))

with open('samples_and_scale1fb_ul_raw_nanoAOD.json', "r") as f_in:
	samples = json.load(f_in)

processes = [ 'HH_ggTauTau_kl1', 'HH_ggTauTau_kl0', 'HH_ggTauTau_kl2p45', 'HH_ggTauTau_kl5', 
							'HH_ggWW_dileptonic_kl1', 'HH_ggWW_dileptonic_kl0', 'HH_ggWW_dileptonic_kl2p45', 'HH_ggWW_dileptonic_kl5', 
							'HH_ggWW_semileptonic_kl1', 'HH_ggWW_semileptonic_kl0', 'HH_ggWW_semileptonic_kl2p45', 'HH_ggWW_semileptonic_kl5',
							'VBFH', 'VH', 'ttH' 
						]

scales = {}
for name, sample in samples.items()[:]:
	if name not in processes:
		continue
	scales[name] = {}
	ggf = False
	if 'HH' in name:
		ggf = True

	for year in years:
		scales[name][year] = {}
		print ('Start processing ', year, ' ' , str(name))
		ch = r.TChain("Events")
		list_of_files = []
		for path in sample[year]['paths']:
			list_of_files += glob.glob(path+'/*.root')
		list_of_files = [ x for x in list_of_files if '.root' in x  ]
		for file_ in list_of_files[:]:
			ch.Add(file_);
		if ch.GetEntries() != 0 :
			results = r.ScanChain(ch, year, ggf)
		for res in range(len(results)):
			scale = "lhe_scale_"+str(res)
			if res == 9:
				scale = "tot_norm"
			scales[name][year][scale] = results[res]


os.system("rm lhe_scales/scales.json")
with open("lhe_scales/scales.json", "w") as outfile:
  json.dump(scales, outfile, indent=2)
