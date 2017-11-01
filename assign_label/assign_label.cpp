#include <iostream>
#include <fstream>
#include <mutex>
#include <cstring>
#include <vector>
#include <map>
using namespace std;

#include "subsynset_checker.h"
const char * prefix = "/home/ubuntu/ml/image/%09s/"; //"/mnt/hdd1/ml/%09s/";
int main(int argc, char ** argv){
  if(argc != 5){
    cerr << "Invalid arguments" << endl;
    cerr << "Usage : " << endl;
    cerr << "\t./assign_label <is_a file> <map_wnids>"
	 << "<list of source images> <list of labeled images>" << endl;
    return 1;
  }

  const char * fname_is_a = argv[1];
  const char * fname_wnid_map = argv[2];
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
  
  ifstream fwnid_map(fname_wnid_map);
  if(!fwnid_map.good()){
    cerr << "Error : Couldn't open "
	 << fname_wnid_map << endl;
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
  //vector<pair<subsynset_checker*, int> > vec_sc;
  vector<subsynset_checker*> checkers;
  char buf[1024];
  while(fwnid_map.getline(buf, 1024)){
    if(fwnid_map.eof())
      break;
    char * wnid = strtok(buf, " ");
    char * label = strtok(NULL, "\n");
#ifdef DEBUG_ASSIGN_LABEL
    cout << wnid << " " << label << endl;
#endif
    subsynset_checker * sc = new subsynset_checker(fis_a, wnid, label);
    sc->expand();
    //vec_sc.push_back(pair<subsynset_checker*, int>(sc, label));
    checkers.push_back(sc);
  }

  char fname[1024];
  char wnid[10];
  while(fsrc_images.getline(fname, 1024)){
    sscanf(fname, prefix, wnid);

    vector<subsynset_checker*>::iterator it = checkers.begin();
    while(true){
      if(it == checkers.end()){
	flog << fname << " is omittetd." << endl;
	flabeled_images << fname << " " << "other" << endl;
	break;
      }
      if((*it)->is_subsynset(wnid)){
#ifdef DEBUG_ASSIGN_LABEL
	cout << fname << " " << " is added to " << (*it)->get_label() << "." << endl;
#endif
	flabeled_images << fname << " " << (*it)->get_wnid() << endl;
	break;
      }
      else{
	
      }
      ++it;
    }
  }
  return 0;
}
