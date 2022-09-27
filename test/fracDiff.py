import pandas as pd
import argparse

proc_ids = { '-6': "HH_ggZZ_2l2q",  '-5': "HH_ggZZ_4l", '-4': "HH_ggWW_semileptonic", '-3': "HH_ggWW_dileptonic", '-2': "HH_ggZZ", '-1': "HH_ggTauTau", '0': 'Data', '2': "ZGamma", '3': "DiPhoton", '4': "WGamma", '5': "TTbar", '6': "TTGamma", '7': "TTGG", '8': "GJets", '9': "VH", '10': "ttH", '11': "ggH", '12': "VBFH" }
#proc_ids = { '-1': "HH_ggTauTau"}


parser = argparse.ArgumentParser()

parser.add_argument(
		'-l',
    "--list",
    help = "paths to input root file",
    nargs = '+',
    default = [ '../pickles/run2_01Dec2021.pkl', '../pickles/run2_19Nov2021_test.pkl' ]
)

args = parser.parse_args()

df1 = pd.read_pickle(args.list[0])
df2 = pd.read_pickle(args.list[1])

df1 = df1.sort_values(['process_id','event'],ascending=(False,False))
df2 = df2.sort_values(['process_id','event'],ascending=(False,False))

for proc_id, proc in proc_ids.iteritems():
	print 'Now processing: ' , proc 
	df1_tmp = df1.loc[ df1.process_id == int(proc_id) ]
	df2_tmp = df2.loc[ df2.process_id == int(proc_id) ]
	print 'Sum of weights: ' , sum(df1_tmp.weight) , '  ' , len(df1_tmp.weight) , ' events. '
	print 'Sum of weights: ' , sum(df2_tmp.weight) , '  ' , len(df2_tmp.weight) , ' events. '
	branches = df1_tmp.keys()
	for branch in branches:
		if sum(df1_tmp[branch]) != 0:
			frac_diff = sum( df1_tmp[branch] - df2_tmp[branch] ) / sum(df1_tmp[branch])
			if abs(frac_diff) > 1e-5: 
				print "Fractional difference for branch: " , branch , " is " , frac_diff 
