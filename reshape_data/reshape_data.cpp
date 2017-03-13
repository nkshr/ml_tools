#include <iostream>
#include <stdlib.h>
#include <fstream>
#include <cstring>
#include <random>
#include <ctime>
#include <algorithm>
using namespace std;

void shuffle(int * array, size_t t){
  default_random_engine generator(time(NULL));
  uniform_int_distribution<int> distribution(0, t);
  for(int i = 0; i < t; ++i){
    int rval = distribution(generator);
    int tmp = array[rval];
    array[rval] = array[i];
    array[i] = tmp;
  }
}

int main(int argc, char ** argv){
  if(argc != 5){
    cerr << "Invalid argumetns." << endl;
    cerr << "Usage: " << endl;
    cerr << "./reshape_data <label0_ratio> <label1_ration> <src_list> < dst_list>"
	 << endl;
    return 1;
  }

  int label_ratio[2];
  label_ratio[0] = atoi(argv[1]);
  label_ratio[1] = atoi(argv[2]);
  char * fname_src_list = argv[3];
  char * fname_dst_list = argv[4];

  ifstream fsrc_list(fname_src_list);
  if(!fsrc_list.good()){
    cerr << "Couldn't open " << fname_src_list << endl;
    return 1;
  }

  ofstream fdst_list(fname_dst_list);
  if(!fdst_list.good()){
    cerr << "Couldn't open " << fname_dst_list << endl;
    return 1;
  }
  
  int num_labels[2];
  memset(num_labels, 0, 2 * sizeof(int));
  while(true){
    string buf;
    getline(fsrc_list, buf);
    if(buf.empty()){
      break;
    }
    int label;
    size_t pos = buf.find(" ");
    label = atoi(buf.substr(pos+1, 1).c_str());
    if(label == 0){
      num_labels[0]++;
    }else{
      num_labels[1]++;
    }  
  }
  fsrc_list.clear();
  fsrc_list.seekg(0, ios_base::beg);
  for(int i = 0; i < 2; ++i){
    cout << i << " : " << num_labels[i] << endl;
  }

  int reshaped_num_labels0 = (label_ratio[0] / (float)label_ratio[1]) * num_labels[1];
  vector<int> tmp_vec;
  tmp_vec.reserve(num_labels[0]);
  for(int i = 0; i < num_labels[0]; ++i){
    tmp_vec.push_back(i);
  }

  shuffle(tmp_vec.data(), num_labels[0]);
  vector<int> selected_lines(tmp_vec.data(), tmp_vec.data() + reshaped_num_labels0);
  
  sort(selected_lines.begin(), selected_lines.end());
  vector<int>::iterator it = selected_lines.begin();
  int count = 0;
  
  while(it != selected_lines.end()){
    string buf;
    getline(fsrc_list, buf);
    int label;
    size_t pos = buf.find(" ");
    label = atoi(buf.substr(pos+1, 1).c_str());
    if(label == 0){
      if(label == 0 && count == *it){
	fdst_list << buf << endl;
	++it;
      }
      ++count;
    }
  }

  fsrc_list.clear();
  fsrc_list.seekg(0, ios_base::beg);
  for(int i = 0; i < num_labels[1];){
    string buf;
    getline(fsrc_list, buf);
    int label;
    size_t pos = buf.find(" ");
    label = atoi(buf.substr(pos+1, 1).c_str());
    if(label == 1){
      fdst_list << buf << endl;
      ++i;
    }
  }
  return 0;
}
