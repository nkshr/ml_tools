#include <iostream>
#include <fstream>
#include <mutex>
#include <cstring>
#include <vector>
#include <map>
using namespace std;

#include "subsynset_checker.h"

int main(int argc, char ** argv){
  if(argc != 5){
    cerr << "Invalid arguments" << endl;
    cerr << "Usage : " << endl;
    cerr << "\t./assign_label <is_a file> <map_wnids>"
	 << "<list of source images> <list of labeled images>" << endl;
    return 1;
  }

  const char * fname_is_a = argv[1];
  const char * fname_map_wnids = argv[2];
  const char * fname_src_images = argv[3];
  const char * fname_labeled_images = argv[4];
  const char * fname_log = "log_assign_label.txt";
  
  //open files
  ifstream fis_a(fname_is_a, ifstream::binary);
  if(!fis_a.good()){
    cerr << "Error : Couldn't open "
	 << fname_is_a << endl;
    return 1;
  }
  
  ifstream fmap_wnids(fname_map_wnids);
  if(!fmap_wnids.good()){
    cerr << "Error : Couldn't open "
	 << fname_map_wnids << endl;
    return 1;
  }

  ifstream fsrc_images(fname_src_images);
  if(!fsrc_images.good()){
    cerr << "Error : Couldn't open " << fname_src_images << endl;
    return 1;
  }
  
  ofstream flabeled_images(fname_labeled_images);
  if(!flabeled_images.good()){
    cerr << "Error : Couldn't open " << fname_labeled_images << endl;
    return 1;
  }

  ofstream flog(fname_log);
  if(!flog.good()){
    cerr << "Error : Couldn't open " << fname_log << endl;
    return 1;
  }
  vector<pair<subsynset_checker*, int> > vec_sc;
  char buf[1024];
  while(fmap_wnids.getline(buf, 1024)){
    if(fmap_wnids.eof())
      break;
    char * wnid = strtok(buf, " ");
    int label = atoi(strtok(NULL, " "));
#ifdef DEBUG_AL
    cout << wnid << ", " << label << endl;
#endif
    subsynset_checker * sc = new subsynset_checker(fis_a, wnid);
    sc->expand();
    vec_sc.push_back(pair<subsynset_checker*, int>(sc, label));
  }

  char fname[1024];
  char wnid[10];
  while(fsrc_images.getline(fname, 1024)){
    sscanf(fname, "/mnt/hdd1/ml/%09s/", wnid);

    vector<pair<subsynset_checker*, int> >::iterator it = vec_sc.begin();
    while(true){
      if(it == vec_sc.end()){
	flog << fname << " is omittetd." << endl;
	break;
      }
      if(it->first->is_subsynset(wnid)){
#ifdef DEBUG_AL
	cout << fname << " " << it->second << " is added." << endl;
#endif
	flabeled_images << fname << " " << it->second << endl;
	break;
      }
      else{
	
      }
      ++it;
    }
  }
  return 0;
}
