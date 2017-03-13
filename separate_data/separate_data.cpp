#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <list>
using namespace std;

bool compare(const int &val0, const int &val1){
  return val0 < val1;
}

int main(int argc, char ** argv){
  if(argc != 5){
    cout << "./separate_date "
	 << "<val_ratio> <full_list> <train_list> <val_list>"
	 << endl;
    return 1;
  }

  ifstream full_list(argv[2]);
  if(!full_list.good()){
    cerr << "Error : Couldn't open " << argv[2] << endl;
    return 1;
  }
  
  ofstream train_list(argv[3]);
  if(!train_list.good()){
    cerr << "Error : Couldn't open " << argv[3] << endl;
    return 1;
  }
  
  ofstream val_list(argv[4]);
  if(!val_list.good()){
    cerr << "Error : Couldn't open " << argv[4] << endl;
    return 1;
  }

  list<int> val_ids;
  string buf;
  int num_lines = 0;
  while(getline(full_list, buf)){
    num_lines++;
  }

  full_list.clear();
  full_list.seekg(0, ifstream::beg);

  srand(time(NULL));
  cout << argv[2] << " contains " << num_lines << " names of images." << endl;
    
  const int num_val = num_lines * atof(argv[1]);
  cout << num_val << " validation images picked up." << endl;
  for(int i = 0; i < num_val;){
    int val_id = rand() % num_lines;
    bool duplicate = false;
    for(list<int>::iterator it = val_ids.begin(); it != val_ids.end(); ++it){
      if(*it == val_id){
	duplicate = true;
	break;
      }
      
      if(*it > val_id){
	break;
      }
    }

    if(!duplicate){
      if(i%1000 ==0){
	cout << "Image at " << val_id
	     << "th line is added to list of validation. " << i
	     << " / " << num_val << endl;
      }
      val_ids.push_back(val_id);
      val_ids.sort(compare);
      ++i;
    }
    else{
     
      //cout << "Image at " << val_id
      //   << "th line has been added to list of train. " << endl;
    }
  }

  list<int>::iterator it = val_ids.begin();
  for(int i = 0; i < num_lines; ++i){
    string buf;
    getline(full_list, buf);
    if(i == (*it)){
      ++it;
      val_list << buf << endl;
    }else
      train_list << buf << endl;
  }
  return 0;
}
