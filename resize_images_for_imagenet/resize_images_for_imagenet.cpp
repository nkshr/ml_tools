#include <iostream>
#include <fstream>
#include <thread>
#include <mutex>
#include <time.h>
#include <signal.h>
#include <condition_variable>

#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

mutex mtx;

bool finished = false;
bool verbose = false;
bool destroy = false;

int thread_id = 0;
int num_jobs = 0;
int tsleep = 0;

long num_lines = 0;
long success = 0;
long total;

long * num_done;

string error_list_fname = "resizing_error.txt";
string out_list_fname;

ifstream imgs_list_ifs;

ofstream out_list;
ofstream error_list;

thread * th;

void sleep(unsigned int us){
  clock_t goal = us + clock();
  while(goal > clock()){
  }
}

void resizeImageForImageNet(const Mat &src, Mat &dst){
  const int shorter_side = 256;
  Mat _dst;
  float scale;
  Rect roi;
  if(src.cols > src.rows){
    scale = src.cols / (float)src.rows;
    resize(src, _dst, Size(shorter_side * scale, shorter_side));
    roi.x = (_dst.cols - shorter_side)/2;
    roi.y = 0;
    roi.width = roi.height =  shorter_side;
    dst = Mat(_dst, roi).clone();
  }
  else{
    scale = src.rows / (float)src.cols;
    resize(src, _dst, Size(shorter_side, shorter_side * scale));
    roi.x = 0;
    roi.y = (_dst.rows - shorter_side)/2;
    roi.width = roi.height = shorter_side;
    dst = Mat(_dst, roi).clone();
  }
}

void process(){
  
  while(true){    
    string img_name;
    mtx.lock();
    int _tsleep = tsleep;

    if(finished){
      mtx.unlock();
      break;
    }

    imgs_list_ifs >> img_name;

    if(img_name.empty()){
      finished = true;
      mtx.unlock();
      break;
    }    
    
    num_lines++;
   
    mtx.unlock();

    Mat src_img = imread(img_name);

    if(src_img.empty()){
      mtx.lock();
      if(verbose){
      cerr << "Error : "  << img_name << " does not exist" << endl;
      cout << "success ratio : " << success << " / " << num_lines
	   << " = " << (float)success/num_lines << endl;
      cout << "process ratio : " << num_lines << " / " << total
	   << " = " << (float)num_lines/total << endl;
      }else{
	if(num_lines%100 == 0){
	  //cerr << "Error : "  << img_name << " does not exist" << endl;
	  cout << "success ratio : " << success << " / " << num_lines
	       << " = " << (float)success/num_lines << endl;
	  cout << "process ratio : " << num_lines << " / " << total
	       << " = " << (float)num_lines/total << endl;
	}
      }
      
      error_list << img_name << endl;      
      mtx.unlock();
      continue;
    }else{    
      Mat dst_img;
      resizeImageForImageNet(src_img, dst_img);
      imwrite(img_name, dst_img);

      mtx.lock();
      success++;

      if(verbose){
      cout << "Success : "  << img_name << endl;
      cout << "success ratio : " << success << " / " << num_lines
	   << " = " << (float)success/num_lines << endl;
      cout << "process ratio : " << num_lines << " / " << total
	   << " = " << (float)num_lines/total << endl;
      }else{
	if(num_lines%100 == 0){
	  //cout << "Success : "  << img_name << endl;
	  cout << "success ratio : " << success << " / " << num_lines
	       << " = " << (float)success/num_lines << endl;
	  cout << "process ratio : " << num_lines << " / " << total
	       << " = " << (float)num_lines/total << endl;
	}
      }
      
      out_list << img_name << endl;
      mtx.unlock();
    }

    sleep(_tsleep);
  }
}


int main(int argc, char ** argv){
  //parse arguments
  const string keys = "{help h    |   | print help}"
                      "{@in_list  |   | input list file}"
                      "{@out_list |   | output list file}"
                      "{jobs      | 1 | number of threads}"
                      "{verbose v |   | enable verbose print}"
                      "{sleep     | 0 | time for sleep}";
  CommandLineParser parser(argc, argv, keys);
  
  string in_list_fname = parser.get<string>("@in_list");
  out_list_fname = parser.get<string>("@out_list");
  num_jobs = parser.get<int>("jobs");
  verbose = parser.has("verbose");
  tsleep = parser.get<int>("sleep");
  
  if(parser.has("help") || in_list_fname.empty() || out_list_fname.empty()){
    parser.printMessage();
    return -1;
  }

  cout << "input list file : " << in_list_fname << endl;
  cout << "output list file : " << out_list_fname << endl;
  cout << "number of jobs : " << num_jobs << endl;
  cout << "sleep time : " << tsleep << endl;
  
  imgs_list_ifs.open(in_list_fname.c_str());
  if(!imgs_list_ifs.is_open()){
    cerr << "Couldn' open " << in_list_fname << endl;
    exit(1);
  }

  total = count(istreambuf_iterator<char>(imgs_list_ifs),
  		istreambuf_iterator<char>(), '\n');
  imgs_list_ifs.seekg(0, imgs_list_ifs.beg);

  cout << "number of images : "
       << total << endl;
  
  out_list.open(out_list_fname.c_str(), fstream::out | fstream::binary);
  if(!out_list.good()){
    cout << "Couldn't open" <<  out_list_fname << endl;
    exit(1);
  }

  error_list.open(error_list_fname.c_str(), fstream::binary);
  if(!error_list.good()){
    cout << "Couldn't open " << error_list_fname << endl;
    exit(1);
  }
  
  th = new thread[num_jobs];
  for(int i = 0; i < num_jobs; ++i){
    th[i] = thread(process);
  }
  for(int i = 0; i < num_jobs; ++i){
    th[i].join();
  }

  delete[]num_done;
  delete[] th;

  cout << "finished" << endl;
  return 0;
}
