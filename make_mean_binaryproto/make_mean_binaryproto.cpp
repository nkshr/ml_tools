#include <stdint.h>
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include <fstream>

#include "boost/scoped_ptr.hpp"
#include "gflags/gflags.h"
#include "glog/logging.h"

#include "caffe/proto/caffe.pb.h"
#include "caffe/util/db.hpp"
#include "caffe/util/io.hpp"

#include <opencv2/opencv.hpp>

using namespace caffe;
using namespace cv;
using namespace std;

int main(int argc, char ** argv){
  if(argc != 3){
    cerr << "Invalid arguments." << endl;
    cerr << "Usage : " << endl;
    cerr << "./make_mean_binaryproto <imgs_list> <binaryproto>" << endl;
    return 1;
  }

  char * imgs_list_name = argv[1];
  char * bp_name = argv[2];

  ifstream imgs_list(imgs_list_name);
  if(!imgs_list.good()){
    cerr << "Couldn't open " << imgs_list_name << endl;
    return 1;
  }

  int num_all_imgs = 0;
  while(true){
    string line;
    getline(imgs_list, line);
    if(line.empty()){
      break;
    }
    num_all_imgs++;
  }
  imgs_list.clear();
  imgs_list.seekg(0, ios::beg);
  Mat sum_img = Mat::zeros(256, 256, CV_32FC3);
  int num_imgs = 0;
  while(true){
    string line;
    getline(imgs_list, line);
    if(line.empty())
      break;
    const size_t pos = line.find(" ");
    string img_name;
    if(pos == string::npos)
      img_name = line;
    else
      img_name = line.substr(0, pos);
    //cout << img_name << endl;
    Mat img = imread(img_name);
    if(img.empty()){
      cerr << "Couldn't load " << img_name << endl;
      return 1;
    }

    const uchar * pimg = img.ptr<uchar>(0);
    float * psum_img = sum_img.ptr<float>(0);
    for(int i = 0; i < sum_img.total() * 3; ++i){
      psum_img[i] += (float)pimg[i];
    }
    
    num_imgs++;
    if(num_imgs % 1000 == 0){
      cout << num_imgs << " / " << num_all_imgs << endl;
    }
  }
 
  cout << num_imgs << " / " << num_all_imgs << endl;

  const int num_pixs3 = sum_img.rows * sum_img.cols * sum_img.channels();
  const float inum_imgs = 1.f / (float)num_imgs;
  float * psum_img = sum_img.ptr<float>(0);
  for(int i = 0; i < num_pixs3; ++i){
    psum_img[i] *= inum_imgs;
  }
  
  BlobProto img_blob;
  img_blob.set_num(1);
  img_blob.set_channels(sum_img.channels());
  img_blob.set_height(sum_img.rows);
  img_blob.set_width(sum_img.cols);

  for(int i = 0; i < num_pixs3; ++i){
    img_blob.add_data(0.);
  }
  
  psum_img = sum_img.ptr<float>(0);
  float max = 0;
  float min = FLT_MAX;
  for(int c = 0; c < sum_img.channels(); ++c){
    for(int i = 0; i < sum_img.total(); ++i){
      const float pix = psum_img[3*i + c];
      max = max > pix ? max : pix;
      min = min < pix ? min : pix;
      img_blob.set_data(c*sum_img.total() + i, pix);
    }
  }
  WriteProtoToBinaryFile(img_blob, bp_name);
  cout << "max : " << max << endl;
  cout << "min : " << min << endl;

  max = 0;
  min = FLT_MAX;
  for(int i = 0; i < img_blob.data_size(); ++i){
    const float pix = img_blob.data(i);
    max = max > pix ? max : pix;
    min = min < pix ? min : pix;
  }

  cout << "max : " << max << endl;
  cout << "min : " << min << endl;
  return 0;    
}
