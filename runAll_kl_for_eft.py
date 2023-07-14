#!/usr/bin/env python
import os
import sys
import glob
import json
import ROOT as r
from tqdm import tqdm
from ROOT import gROOT

r.gSystem.Load('NanoCORE/libTauAnalysis_ClassicSVfit.so')
r.gSystem.Load('loopers/process_kl_for_eft_C.so')

lumi = { "2016" : 16.51, "2016_APV" : 19.39, "2017" : 41.5, "2018" : 59.8 }
years = ['2016', '2016_APV', '2017', '2018']
#years = ['2016_APV']
samples = {}

date="kl_for_eft_30Apr2023"
base_dir='/ceph/cms/store/user/fsetti/c++_looper_ul_output/'
os.system("mkdir -p %s/%s/"%(base_dir,date))

with open('samples_and_scale1fb_ul.json', "r") as f_in:
	samples = json.load(f_in)

processes = [ #'HH_ggTauTau_kl1', 'HH_ggTauTau_kl0', 'HH_ggTauTau_kl2p45', 'HH_ggTauTau_kl5', 
							#'HH_ggWW_dileptonic_kl1', 'HH_ggWW_dileptonic_kl0', 'HH_ggWW_dileptonic_kl2p45', 'HH_ggWW_dileptonic_kl5', 
							'HH_ggWW_semileptonic_kl1', 'HH_ggWW_semileptonic_kl0', 'HH_ggWW_semileptonic_kl2p45', 'HH_ggWW_semileptonic_kl5'
						]


#switch = False
for name, sample in samples.items()[:]:
	if name not in processes :
		continue

	os.system("mkdir -p %s/%s/%s"%(base_dir,date,name))
	for year in years:
		print 'Start processing ', year, ' ' , str(name)
		ch = r.TChain("Events")
		list_of_files = []
		for path in sample[year]['paths']:
			list_of_files += glob.glob(path+'/*/*/*/*.root')
			list_of_files += glob.glob(path+'/*/*/*.root')
			list_of_files += glob.glob(path+'/*.root')
		list_of_files = [ x for x in list_of_files if '.root' in x ]
		for file_ in list_of_files[:]:
			ch.Add(file_);
		scale_factor = sample[year]['metadata']['scale1fb'] * lumi[year]
		r.ScanChain(ch, str(name) , year , date, scale_factor, int(sample['process_id']), bool(sample['resonant']) )
