#ifndef _SUBSYNSET_CHECKER_
#define _SUBSYNSET_CHECKER_
const static int size_wnid= 10;

class subsynset_checker{
public:
  subsynset_checker(ifstream &is_a, const char *wnid);
 
  void expand();
  void get_label(const int wnid);
  
  bool is_subsynset(const char * wnid);
  //bool init(char * name_is_a, char * name_list_artifacts);
  
private:
  class synset{
  public:
    enum e_pos{START, MIDDLE, END};
 
    synset(subsynset_checker * sc, const char * wnid, const e_pos pos);
    synset(subsynset_checker * sc);

    void expand();

  private:
    bool is_duplicate;

    e_pos pos;

    subsynset_checker * sc;

    char wnid[size_wnid];

    vector<synset*> subsynsets;

  };

  const static int size_wnid = 10;
  
  bool prev_check;
  
  char wnid[size_wnid];
  char prev_wnid[size_wnid];
  
  ifstream *is_a;
  ifstream list_artifacts;

  vector<char*> wnids; 
};

class show_dmsg{
  const char * str;
 public:

 show_dmsg(const char * str): str(str){
    cout << "Entering " << str << endl;
  }
  
  ~show_dmsg(){
    cout << "Exiting " << str << endl;
  }
};
#endif
