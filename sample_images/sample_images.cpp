#include <iostream>
#include <random>
#include <stdlib.h>
#include <fstream>
#include <algorithm>
#include <functional>
#include <iterator>
using namespace std;

int main(int argc, char ** argv){
  if(argc != 4){
    cerr << "Invalid arguments." << endl;
    cerr << "Usage : " << endl;
    cerr << "./sample_images <list of source> <list of sampled images> <number of samples>" << endl;
    return 1;
  }

  int num_lines = 0;
  ifstream fsrc(argv[1]);

  if(!fsrc.good()){
    cout << "Error : Couldn't open " << argv[1] << endl;
    return 1;
  }  

  for(;;){
    string buf;
    getline(fsrc, buf);
    if(buf.empty()){
      break;
    }
    num_lines++;
  }
  fsrc.clear();
  cout << "number of lines of " << argv[1]
       << " is " << num_lines << endl;
  default_random_engine generator;
  uniform_int_distribution<int> distribution(0, num_lines);
  vector<int> lines;
  int num_samples = atoi(argv[3]);
  cout << "number of samples is " << num_samples << endl;
  for(int i = 0; i < num_samples;){
    while(true){
      int rval = distribution(generator);
      bool duplicated = false;
      for(int j = 0; j < lines.size(); ++j){
	if(lines[j] == rval){
	  duplicated = true;
	  break;
	}
      }
      if(!duplicated){
	//cout << i << " : " << rval << " is added" << endl;
	lines.push_back(rval);
	i++;
	break;
      }
    }
  }

  sort(lines.begin(), lines.end());

  ofstream fsampled(argv[2]);
  if(!fsampled.good()){
    cout << "Error : Couldn't open " << argv[2] << endl;
    return 1;
  }

  num_lines = 0;

  fsrc.seekg(0, ios_base::beg);
  vector<int>::iterator it = lines.begin();
  int count = 0;
  while(true){
    string buf;
    getline(fsrc, buf);
    if(buf.empty()){
      break;
    }
    if(num_lines == *it){
      cout << count++ << " : " << buf
	   << "is added to " << argv[2] << endl;
      fsampled << buf << endl;
      ++it;
    }
    
    num_lines++;
  }
  return 0;
}
