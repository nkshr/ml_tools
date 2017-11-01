#include <iostream>
#include <fstream>
#include <mutex>
#include <cstring>
#include <vector>
using namespace std;

#include "subsynset_checker.h"

static int synset_id = 0;
subsynset_checker::synset::synset(subsynset_checker * sc,
			     const char * wnid, const e_pos pos):
  is_duplicate(false), pos(pos),sc(sc){  
  if(pos == START){
    synset_id = 0;
  }else{
    synset_id++;
  }

  for(vector<char*>::iterator it = sc->wnids.begin();
      it != sc->wnids.end(); ++it){
    if(strcmp(*it, wnid) == 0){
      is_duplicate = true;
    }
  }
  if(!is_duplicate){
    char * buf = new char[size_wnid];
    memcpy(buf, wnid, size_wnid);
    sc->wnids.push_back(buf);
  }
  memcpy(this->wnid, wnid, size_wnid);
  //cout << "synset id : " << synset_id << endl;
}

subsynset_checker::synset::synset(subsynset_checker * sc): pos(START), sc(sc){
}

void subsynset_checker::synset::expand(){
  if(is_duplicate)
    return;
  
  ifstream &is_a = *(sc->is_a);
  is_a.seekg(0, ifstream::beg);
  vector<char*> &wnids = sc->wnids;
  while(true){
    char buf[1024];
    is_a.getline(buf, 1024);
    if(is_a.eof())
      break;
    char * ptok = strtok(buf, " ");

    if(strcmp(ptok, wnid) == 0){
      ptok = strtok(NULL, " ");
      if(strcmp(ptok, wnid) != 0){
	subsynsets.push_back(new synset(sc, ptok, MIDDLE));

      }
    }
  }

  is_a.clear();
  
  if(subsynsets.size() == 0){
    pos = END;
    return;
  }

  for(vector<synset*>::iterator it = subsynsets.begin(); it != subsynsets.end(); ++it){
    (*it)->expand();
  }
}

const char * subsynset_checker::get_label(){
  return label;
}

const char * subsynset_checker::get_wnid(){
  return wnid;
}

subsynset_checker::subsynset_checker(ifstream &is_a, const char *wnid, const char *label):prev_check(true){
  this->is_a = &is_a;

  memcpy(this->wnid, wnid, size_wnid);
  memcpy(this->label, label, size_label);
  memset(prev_wnid, 0, size_wnid);
}

void subsynset_checker::expand(){
    
    synset s(this, wnid, synset::e_pos::START);
    s.expand();
    
#ifdef DEBUG_ASSIGN_LABEL
    int pos_wnids = 0;
    char fname[1024];
    sprintf(fname, "subsynsets_%s.txt", wnid);
    ofstream fsubsynsets(fname);
    if(!fsubsynsets.good()){
      cerr << "Error::subsynset_checker : Couldn't open " << fname << endl;
    }

    fsubsynsets << wnids[pos_wnids++] << endl;;
    for(int i = pos_wnids; i < wnids.size(); ++i){
      fsubsynsets << "-" << wnids[i] << endl;
    }
    fsubsynsets.close();
#endif
}
  

bool subsynset_checker::is_subsynset(const char * wnid){
  if(strcmp(wnid, prev_wnid) == 0){
    return prev_check;
  }

  bool check = false;
  for(vector<char*>::iterator it = wnids.begin();
      it != wnids.end(); ++it){
    if(strcmp(wnid, *it) == 0){
      check = true;
      break;
    }
  }

  prev_check = check;
  memcpy(prev_wnid, wnid, size_wnid);
  return check;
}
