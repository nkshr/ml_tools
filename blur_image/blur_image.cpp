#include <iostream>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

int main(int argc, char ** argv){
  if(argc != 5){
    cerr << "Error : Invalid arguments." << endl;
    cerr << "./blur_image <src> <dst> <ksize> <sigma>" << endl;
    return 0;
  }

  const char * src_img_name = argv[1];
  const char * dst_img_name = argv[2];
  const Size ksize(atof(argv[3]), atof(argv[3]));
  const double sigma = atof(argv[4]);
  
  Mat src_img = imread(src_img_name);
  Mat dst_img;
  
  GaussianBlur(src_img, dst_img, ksize, sigma);

  imwrite(dst_img_name, dst_img);
  
  return 0;
}
