import urllib.request
from html.parser import HTMLParser

prefix_wnid = "http://imagenet.stanford.edu/synset?wnid="
url = "http://image-net.org/challenges/LSVRC/2014/browse-synsets"
output = "wnids.txt"

class WNIDSynsetParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.f = open(output, 'w')
        self.label_counter = 0
        self.wnid_synset_dict = dict()
        self.wnid = ''
        
    def __del__(self):
        self.f.close()
        
    def handle_starttag(self, tag, attrs):
        if(tag == "a" and attrs[0][0] == "href"):
            index = attrs[0][1].find(prefix_wnid)
            if(index==0):
                self.wnid = attrs[0][1][len(prefix_wnid):len(attrs[0][1])]
                #self.f.write(s+ " " + str(self.label_counter) + "\n")
                self.label_counter += 1

    def handle_data(self, data):
        if self.wnid:
            self.f.write(self.wnid + ' ' + data + '\n')
            self.wnid=''
            
if __name__== "__main__":
    f = urllib.request.urlopen(url)
    #print(html.read())

    html = f.read();
    parser = WNIDSynsetParser()
    parser.feed(html.decode("utf-8"))
    parser.close()
    f.close()
