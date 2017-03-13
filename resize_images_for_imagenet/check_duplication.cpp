#include <iostream>
#include <fstream>
using namespace std;

int main(int argc, char ** argv){
  if(argc == 2){
    cout << "./check_duplication <file>" << endl;
    return 1;
  }

  ifstream file(argv[1]);
  if(!file.good()){
    cout << "Error : Couldn't open " << argv[1] << endl;
    return 1;
  }
  
  string str;
  while(getline(file, str)){
    
  }
  return 0;
}
