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
        
    def __str__(self):
        return '{},\"{}\",{},{},{},{},{}\n'.format(self.class_id, self.label, len(self.iinfo_list), self.top1_rate, self.top5_rate, self.top1_rate_rank, self.top5_rate_rank)

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
                f.write(str(iinfo))
                f.flush()

    def sort_by_prob(self):
        probs = [iinfo.prob for iinfo in self.iinfo_list]
        sorted_indexes = np.argsort(probs)[::-1]
        sorted_iinfo_list = [iinfo_list[index] for index in sorted_indexes]
        self.iinfo_list = sorted_info_list

    def calc_prob_rank(self):
        ranks = []
        for iinfo in self.iinfo_list:
            ranks.append(iinfo.rank)

        sorted_indexes = np.argsort(ranks)[::-1]
        for rank in range(len(sorted_indexes)):
            self.iinfo_list[sorted_indexes[rank]].rank_in_class = rank

    def read(self, fname):
        with open(fname, 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                print(row)
            #header = next(reader)
            
