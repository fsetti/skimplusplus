#pragma GCC diagnostic ignored "-Wsign-compare"
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TChain.h"

#include "../NanoCORE/Nano_v9.cc"
#include "../NanoCORE/tqdm.h"

#include <string>
#include <iostream>
#include <iomanip>

#define SUM(vec) std::accumulate((vec).begin(), (vec).end(), 0);
#define SUM_GT(vec,num) std::accumulate((vec).begin(), (vec).end(), 0, [](float x,float y){return ((y > (num)) ? x+y : x); });
#define COUNT_GT(vec,num) std::count_if((vec).begin(), (vec).end(), [](float x) { return x > (num); });
#define COUNT_LT(vec,num) std::count_if((vec).begin(), (vec).end(), [](float x) { return x < (num); });

#define H1(name,nbins,low,high) TH1F *h_##name = new TH1F(#name,#name,nbins,low,high);

// #define DEBUG

struct debugger { template<typename T> debugger& operator , (const T& v) { cerr<<v<<" "; return *this; } } dbg;
#ifdef DEBUG
    #define debug(args...) do {cerr << #args << ": "; dbg,args; cerr << endl;} while(0)
#else
    #define debug(args...)
#endif

using namespace std;
using namespace tas;

vector<double> ScanChain( TChain *ch, string str_year, bool ggf ) {

  int year;
  if ( str_year == "2016_APV") year = 2016;
  else { year = stoi(str_year); }

  int nEventsTotal = 0;
  int nEventsChain = ch->GetEntries();
  TFile *currentFile = 0;
  TObjArray *listOfFiles = ch->GetListOfFiles();
  TIter fileIter(listOfFiles);
  tqdm bar;

	vector<double> w_tot(9,0.);
	double w_tot_nom = 0;

  while ( (currentFile = (TFile*)fileIter.Next()) ) {
      TFile *file = TFile::Open( currentFile->GetTitle() );
      TTree *tree = (TTree*)file->Get("Events");

      tree->SetCacheSize(128*1024*1024);
      tree->SetCacheLearnEntries(100);

			nt.SetYear(year);
      nt.Init(tree);

      for( unsigned int loop_event = 0; loop_event < tree->GetEntriesFast(); ++loop_event) {

       nt.GetEntry(loop_event);

       nEventsTotal++;
       bar.progress(nEventsTotal, nEventsChain);

			if ( ( fabs(genWeight()) >= 0.5 ) && ggf ){
				continue;
			}

			w_tot_nom += genWeight();
			for (unsigned int i=0; i<9; i++){
				w_tot[i] += genWeight()*(Float_t)LHEScaleWeight()[i];
			}
  	} // Event loop
  delete file;
 	} // File loop

 	bar.finish();
	vector<double> results = w_tot;
	results.push_back(w_tot_nom);

	cout << " tot norm: " << w_tot_nom << endl;
	cout << " LHEScale0 norm: " << w_tot[0] << endl;
	cout << " LHEScale1 norm: " << w_tot[1] << endl;
	cout << " LHEScale2 norm: " << w_tot[2] << endl;
	cout << " LHEScale3 norm: " << w_tot[3] << endl;
	cout << " LHEScale4 norm: " << w_tot[4] << endl;
	cout << " LHEScale5 norm: " << w_tot[5] << endl;
	cout << " LHEScale6 norm: " << w_tot[6] << endl;
	cout << " LHEScale7 norm: " << w_tot[7] << endl;
	cout << " LHEScale8 norm: " << w_tot[8] << endl;
	return results;
}
