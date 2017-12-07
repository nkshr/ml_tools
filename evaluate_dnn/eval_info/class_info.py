from . import image_info

import csv

class class_info:
    def __init__(self):
        self.iinfo_list = []
        self.label = ''
        self.class_id = ''
        self.top1_rate = -1
        self.top5_rate = -1
        self.top1_rate_rank = -1
        self.top5_rate_rank = -1
        self.evaluated = False
        
    def calc_top1_rate(self):
        if (len(self.iinfo_list)) == 0:
            self.top1_rate = 0
            return
        
        num_top1 = 0
        for iinfo in self.iinfo_list:
            if iinfo.rank == 0:
                num_top1 += 1
        self.top1_rate = num_top1 / len(self.iinfo_list)

    def calc_top5_rate(self):
        if (len(self.iinfo_list)) == 0:
            self.top5_rate = 0
            return
        
        num_top5 = 0
        for iinfo in self.iinfo_list:
            if iinfo.rank < 5:
                num_top5 += 1
        self.top5_rate = num_top5 / len(self.iinfo_list)

    def write_detail(self, fname):
        text = 'class_id,label,top1_rate,top5_rate\n'
        text += '{},\"{}\",{},{}\n'.format(self.class_id, self.label, self.top1_rate, self.top5_rate)
        text += 'image,rank,rank_in_class,prob,1,,2,,3,,4,,5\n'
        with open(fname, 'w') as f:
            f.write(text)
            f.flush()

            for iinfo in self.iinfo_list:
                text = '{},{},{},{},'.format(
                    self.name,
                    self.rank,
                    self.rank_in_class,
                    self.prob
                )
                
                for elem in self.top5:
                    text += '{},{},'.format(elem[0], elem[1])

                text += '\n'

                f.write(text)
                f.flush()

    def sort_by_prob(self):
        probs = [iinfo.prob for iinfo in self.iinfo_list]
        sorted_indexes = np.argsort(probs)[::-1]
        sorted_iinfo_list = [iinfo_list[index] for index in sorted_indexes]
        self.iinfo_list = sorted_info_list

    def calc_rank_in_class(self):
        ranks = []
        for iinfo in self.iinfo_list:
            ranks.append(iinfo.rank)

        sorted_indexes = np.argsort(ranks)[::-1]
        for rank in range(len(sorted_indexes)):
            self.iinfo_list[sorted_indexes[rank]].rank_in_class = rank

    def read(self, fname):
        with open(fname, 'r') as f:
            reader = csv.reader(f)

            next(reader) #skip header

            text = next(reader)
            toks = text.split(',')
            self.class_id = int(toks[0])
            self.label = toks[1]
            self.top1_rate = toks[2]
            self.top5_rate = toks[3]
            
            for row in reader:
                toks  = row.split(',')
                iinfo = image_info.image_info()
                iinfo.name = toks[0]
                iinfo.rank = toks[1]
                iinfo.rank_in_class = toks[2]
                iinfo.prob = toks[3]
                for i in range(5):
                    class_id = toks[4+i*2]
                    prob = toks[5+i*2]
                    iinfo.top5.append((class_id, prob))
                    
    def take_statistics(self):
        self.calc_top1_rate()
        self.calc_top5_rate()
        self.calc_rank_in_class()
