import urllib.request
from html.parser import HTMLParser

prefix_wnid = "http://imagenet.stanford.edu/synset?wnid="
url = "http://image-net.org/challenges/LSVRC/2014/browse-synsets"
output = 'wnids.txt'

class WNIDSynsetParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.label_counter = 0
        self.synset_dict = dict()
        self.wnid = -1
        
    def __del__(self):
        pass
    
    def handle_starttag(self, tag, attrs):
        if(tag == "a" and attrs[0][0] == "href"):
            index = attrs[0][1].find(prefix_wnid)
            if(index==0):
                self.wnid = int(attrs[0][1][len(prefix_wnid):len(attrs[0][1])][1:])
                self.label_counter += 1

    def handle_data(self, data):
        if self.wnid > 0:
            self.synset_dict[self.wnid] = data
            self.wnid=-1
            
if __name__== "__main__":
    f = urllib.request.urlopen(url)
    #print(html.read())

    html = f.read();
    parser = WNIDSynsetParser()
    parser.feed(html.decode("utf-8"))
    parser.close()
    f.close()
    
    sorted_dict = sorted(parser.synset_dict.items(), key=lambda x : x[0])
    with open(output, 'w') as f:
        for item in sorted_dict:
            f.write('n{0:08d}\n'.format(item[0]))
        
