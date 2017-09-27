#include <stdlib.h>
#include <cstring>
#include <iostream>
#include <fstream>
using namespace std;

bool check_if_file1_contains_file2_elements(const char * fname1,
					 const char * fname2){
  ifstream ifs1(fname1);
  ifstream ifs2(fname2);
  if(!ifs1.good() && !ifs2.good()){
    cerr << "Error : Couldn't open some files." << endl;
    return 1;
  }

  bool state = true;
  
  while(true){
    string str1;
    ifs1 >> str1;
    if(ifs1.eof()){
      break;
    }
    
    ifs2.seekg(0, ifstream::beg);
    bool found = false;
    while(true){
      string str2;
      ifs2 >> str2;
      if(ifs2.eof()){
	ifs2.clear();
	if(!found){
	  state = false;
	  cout << str1 << " did not match anything " << endl;
	}
	break;
      }
      
      if(strcmp(str1.c_str(), str2.c_str()) == 0){
	cout << str1 << " matched " << str2 << endl;
	if(!found)
	  found = true;
	else{
	  cout << str1 << " rematched " << str2 << endl;
	  state = false;
	}
      }      
    }
  }
  return state;
}

int main(int argc, char ** argv){
  if(argc != 3){
    cerr << "Invalid arguments." << endl;
    cerr << "Usage : " << endl;
    cerr << "./subsynsets_debuger <file1> <file2> " << endl;
    return 1;
  }

  if(check_if_file1_contains_file2_elements(argv[1], argv[2]) &&
     check_if_file1_contains_file2_elements(argv[2], argv[1])){
    cout << "all elements in " << argv[1] << " matchs " << argv[2] << endl;
  }
  return 0;
}
