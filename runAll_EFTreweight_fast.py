#!/usr/bin/env python
import os
import sys
import glob
import json
import ROOT as r
from tqdm import tqdm
from ROOT import gROOT

r.gSystem.Load('loopers/reweight_EFT_fast_C.so')

years = ['2016', '2017', '2018']
#years = ['2016']
samples = {}

in_dir = "/ceph/cms/store/user/fsetti/EFT_samples/01May2023_kl_for_eft/"

date="01May2023_HiggsDNA"
base_dir='/ceph/cms/store/user/fsetti/EFT_samples/'
#os.system("rm -rf %s/%s/"%(base_dir,date))
os.system("mkdir -p %s/%s/"%(base_dir,date))

processes = [ 
		'HH_ggTauTau', 
		#'HH_ggWW_dileptonic', 
		#'HH_ggWW_semileptonic' 
]

kls				= [ 'kl0', 'kl1', 'kl2p45', 'kl5' ]

with open('samples_and_scale1fb_ul_kls_for_eft.json', "r") as f_in:
	samples = json.load(f_in)

#loop over systematics
sys	= glob.glob( in_dir + "/2016/HHggTauTau_kl0_*.root")
sys = [ s.split("HHggTauTau_kl0_")[-1] for s in sys ]
#print(sys)

for year in years:
	for proc in processes[:]:
		scales1fb			= []
		for kl in kls:
			scales1fb += [ samples[proc+'_'+kl][year]['metadata']['scale1fb'] ]
		print ( 'Start processing ', year, " and process: " , proc )
		for sy in sys:
			ch = r.TChain("Events")
			list_of_files 	= glob.glob( in_dir + year + "/"+proc.replace("HH_","HH")+"_kl1_"+sy)
			list_of_files0	= glob.glob( in_dir + year + "/"+proc.replace("HH_","HH")+"_kl0_"+sy)	
			list_of_files2	= glob.glob( in_dir + year + "/"+proc.replace("HH_","HH")+"_kl2p45_"+sy)
			list_of_files5	= glob.glob( in_dir + year + "/"+proc.replace("HH_","HH")+"_kl5_"+sy)
			list_of_files = list_of_files + list_of_files0 + list_of_files2 + list_of_files5

			print("Processing systematic: " , sy.split("125_13TeV")[0] )
			for file_ in list_of_files[:]:
				ch.Add(file_);

			sys_tag = sy.split(".root")[0]
			eft_bm8a = "8a"
			os.system("mkdir -p %s/%s/%s_%s/%s"%(base_dir,date,proc,eft_bm8a,year))
			r.ScanChain( ch, proc, year, eft_bm8a, date, sys_tag, scales1fb[0], scales1fb[1], scales1fb[2], scales1fb[3] )
			for eft_bm in range(1,13):
				eft_bm = str(eft_bm)
				os.system("mkdir -p %s/%s/%s_%s/%s"%(base_dir,date,proc,eft_bm,year))
				r.ScanChain( ch, proc, year, eft_bm, date, sys_tag, scales1fb[0], scales1fb[1], scales1fb[2], scales1fb[3] )
