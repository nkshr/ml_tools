#include <iostream>
using namespace std;

class LightModeling{
public:
  LightModeling();
  ~LightModeling(){};
  bool optimize(const uchar * img, const int num_step, const float epsilon);

private:
  float A;
  float x0, y0;
  float sigma_x, sigma_y;
  float err;
  
  void step();
  float calc_err(const uchar * img);
  float calc_dg_dA(const float x, y);
  float calc_dg_dx0(const float x, y);
  float calc_dg_dy0(const float x, y);
  float calc_dg_dsigma_x(const float x, y);
  float calc_dg_dsigma_y(const float x, y);
};

bool LightModeling::optimize(const uchar * img, const int num_step, const float epsilon){
  for(int i = 0; i < num_step; ++i){
    step();

    err = calc_err();
    if(err < epsilon)
      return true;
  }

  return false;
}

void LightModeling::step(const uchar * img){
  float JtJ[25];
  memset(delta, 0, sizeof(float) * 25);

  float J_diff_yg[5];
  
  for(int y = 0; y < rows; ++y){
    for(int x = 0; x < cols; ++x){
      const float J[5];
      J[0] = calc_dg_dA(x, y);
      J[1] = calc_dg_dx0(x, y);
      J[2] = calc_dg_dy0(x, y);
      J[3] = calc_dg_dsigma_x(x, y);
      J[4] = calc_dg_dsigma_y(x, y);

      res = (float*)pimg - calc_gaussian(x, y);
      for(int i = 0; i < 5; ++i){
	const int idx = i * 5;
	for(int j = 0; j < 5; ++j){
	  delta[i + j] += J[i] * J[j]
	}

	J_diff_yg[i] += J[i] * res;
      }

    }
  }
}

void LightModeling::calc_err(const uchar * img, const int rows, const int cols){
  float err = 0;
  const uchar * pimg = img;
  for(int y = 0; y < rows; ++y){
    for(int x = 0; x < cols; ++x, ++pimg){
      g = calc_gaussian(x, y);
      err += pow(g - (float)*pimg, 2.0);      
    }
  }

  const float num_pixs = (float)(rows * cols);
  return sqrt(err / num_pixs);
}

float LightModeling::calc_gaussian(const float x, const float y){
  gaussian_x = pow(x-x0, 2.f) / (2.f * pow(sigma_x, 2.f));
  gaussian_y = pow(y-y0, 2.f) / (2.f * pow(sigma_y, 2.f));
  return A * exp(-(gaussian_x + gaussian));
}

int main(int argc, char ** argv){
  return 0;
}
