#!/usr/bin/env python
import os
import sys
import glob
import json
import ROOT as r
from tqdm import tqdm
from ROOT import gROOT

r.gSystem.Load('NanoCORE/libTauAnalysis_ClassicSVfit.so')
r.gSystem.Load('loopers/loop_add_BDT_vars_EFT_C.so')

lumi = { "2016" : 16.51, "2016_APV" : 19.39, "2017" : 41.5, "2018" : 59.8 }
#years = ['2016', '2016_APV', '2017', '2018']
years = ['2018']
samples = {}

date="22Mar2023_eft"
base_dir='/ceph/cms/store/user/fsetti/c++_looper_ul_output/'
os.system("mkdir -p %s/%s/"%(base_dir,date))
#os.system("mkdir -p %s/%s/hadded"%(base_dir,date))

with open('samples_and_scale1fb_ul_eft.json', "r") as f_in:
	samples = json.load(f_in)

#processes = [ 'ggTauTau', 'dilep', 'semilept' ] 
process = 'semilept'

for name, sample in samples.items()[:]:

	if process not in name:
		continue

	os.system("mkdir -p %s/%s/%s"%(base_dir,date,name))
	for year in years:
		os.system("rm %s/%s/%s/*2018.root"%(base_dir,date,name))
		print 'Start processing ', year, ' ' , str(name)
		ch = r.TChain("Events")
		list_of_files = []
		try:
			for path in sample[year]['paths']:
				list_of_files += glob.glob(path+'/*/*/*/*.root')
				list_of_files += glob.glob(path+'/*.root')
			list_of_files = [ x for x in list_of_files if '.root' in x ]
			for file_ in list_of_files[:]:
				ch.Add(file_);
			if str(name) != 'Data' and ch.GetEntries() != 0 :
				scale_factor = sample[year]['metadata']['scale1fb'] * lumi[year]
				r.ScanChain(ch, str(name) , year , date, scale_factor, int(sample['process_id']), bool(sample['resonant']) )
		except:
			print name ,' ' , year , ' not available in the samples file or detected corrupted file. '
			print 'Exiting now. '
			sys.exit()
