#!/usr/bin/env python
import os
import sys
import glob
import json
import ROOT as r
from tqdm import tqdm
from ROOT import gROOT

r.gSystem.Load('loopers/reweight_EFT_C.so')

years = ['2016', '2016_APV', '2017', '2018']
#years = ['2016']
samples = {}
file_samples = {}

date="21Mar2023"
base_dir='/ceph/cms/store/user/fsetti/EFT_samples/'
#os.system("rm -rf %s/%s/"%(base_dir,date))
os.system("mkdir -p %s/%s/"%(base_dir,date))
os.system("mkdir -p %s/%s/hists"%(base_dir,date))

with open('samples_and_scale1fb_ul_kls_for_eft.json', "r") as f_in:
	samples = json.load(f_in)

with open('samples_and_scale1fb_ul.json', "r") as f_in:
	file_samples = json.load(f_in)

#processes = [ 'HH_ggTauTau', 'HH_ggWW_dileptonic', 'HH_ggWW_semileptonic' ]
processes = [ 'HH_ggWW_dileptonic' ]
kls				= [ 'kl0', 'kl1', 'kl2p45', 'kl5' ]

for year in years:
	os.system("mkdir -p %s/%s/hists/%s"%(base_dir,date,year))
	for proc in processes[:]:
		print 'Start processing ', year, ' ' , str(proc)
		ch = r.TChain("Events")
		list_of_files = []
		scales1fb			= []
		for kl in kls:
			for path in samples[proc+'_'+kl][year]['paths']:
				list_of_files += glob.glob(path+'/*/*/*/*.root')
				list_of_files += glob.glob(path+'/*.root')
			scales1fb += [ samples[proc+'_'+kl][year]['metadata']['scale1fb'] ]
		list_of_files = [ x for x in list_of_files if '.root' in x ]
		for file_ in list_of_files[:]:
			ch.Add(file_);
		r.make_hist(ch, proc , year, date, scales1fb[0], scales1fb[1], scales1fb[2], scales1fb[3] )

		new_ch = r.TChain("Events")
		new_list_of_files = []
		for kl in kls:
			for path in file_samples[proc+'_'+kl][year]['paths']:
				new_list_of_files += glob.glob(path+'/*/*/*/*.root')
				new_list_of_files += glob.glob(path+'/*/*/*.root')
				new_list_of_files += glob.glob(path+'/*.root')
		new_list_of_files = [ x for x in new_list_of_files if '.root' in x ]
		for file_ in new_list_of_files[:]:
			new_ch.Add(file_);
		eft_bm8a = "8a"
		os.system("mkdir -p %s/%s/%s_%s/%s"%(base_dir,date,proc,eft_bm8a,year))
		r.ScanChain( new_ch, proc, year, eft_bm8a, date, scales1fb[0], scales1fb[1], scales1fb[2], scales1fb[3] )
		for eft_bm in range(1,13):
			eft_bm = str(eft_bm)
			os.system("mkdir -p %s/%s/%s_%s/%s"%(base_dir,date,proc,eft_bm,year))
			r.ScanChain( new_ch, proc, year, eft_bm, date, scales1fb[0], scales1fb[1], scales1fb[2], scales1fb[3] )
