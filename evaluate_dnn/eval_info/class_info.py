from . import image_info

import csv
import numpy as np

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
            self.top1_rate = -1
            return

        if iinfo_list[0].rank < -1:
            self.top1_rate = -1
            return 

        num_top1 = 0
        for iinfo in self.iinfo_list:
            if iinfo.rank == 0:
                num_top1 += 1
        self.top1_rate = num_top1 / len(self.iinfo_list)

    def calc_top5_rate(self):
        if (len(self.iinfo_list)) == 0:
            self.top5_rate = -1
            return

        if iinfo_list[0].rank < -1:
            self.top1_rate = -1
            return
        
        num_top5 = 0
        for iinfo in self.iinfo_list:
            if iinfo.rank < 5 and iinfo.rank > 0:
                num_top5 += 1
        self.top5_rate = num_top5 / len(self.iinfo_list)

    def calc_topk_rate(self, k):
        if (len(self.iinfo_list)) == 0:
            return -1

        if self.iinfo_list[0].rank < 0:
            return -1
        
        num_topk = 0
        for iinfo in self.iinfo_list:
            if iinfo.rank < k and iinfo.rank >= 0:
                num_topk += 1

        return num_topk / len(self.iinfo_list)

    def write(self, fname):
        text = 'class_id,{}\n'.format(self.class_id)
        text += 'label,\"{}\"\n'.format(self.label)
        text += 'top1_rate,{}\n'.format(self.top1_rate)
        text += 'top5_rate,{}\n'.format(self.top5_rate)
        text += 'top1_rate_rank,{}\n'.format(self.top1_rate_rank)
        text += 'top5_rate_rank,{}\n'.format(self.top5_rate_rank)
        text += 'image,rank,rank_in_class,prob,1,,2,,3,,4,,5\n'
        
        with open(fname, 'w') as f:
            f.write(text)
            f.flush()

            for iinfo in self.iinfo_list:
                text = '{},{},{},{},'.format(
                    iinfo.name,
                    iinfo.rank,
                    iinfo.rank_in_class,
                    iinfo.prob
                )

                for i in range(5):
                    class_id = iinfo.top5[i]['class_id']
                    prob = iinfo.top5[i]['prob']
                    text += '{},{},'.format(class_id, prob)

                text += '\n'

                f.write(text)
                f.flush()

    def sort_by_prob(self):
        probs = [iinfo.prob for iinfo in self.iinfo_list]
        sorted_indexes = np.argsort(probs)[::-1]
        sorted_iinfo_list = [iinfo_list[index] for index in sorted_indexes]
        self.iinfo_list = sorted_info_list

    def calc_rank_in_class(self):
        probs = []
        for iinfo in self.iinfo_list:
            probs.append(iinfo.prob)

        sorted_indexes = np.argsort(probs)[::-1]
        for rank in range(len(sorted_indexes)):
            self.iinfo_list[sorted_indexes[rank]].rank_in_class = rank

    def read(self, fname):
        iinfo_list = []
        
        with open(fname, 'r') as f:
            reader = csv.reader(f)
            toks = next(reader)
            self.class_id = int(toks[1])

            toks = next(reader)
            self.label = toks[1]

            toks = next(reader)
            self.top1_rate = float(toks[1])

            toks = next(reader)
            self.top5_rate = float(toks[1])

            toks = next(reader)
            self.top1_rate_rank = int(toks[1])

            toks = next(reader)
            self.top5_rate_rank = int(toks[1])
            
            next(reader) #skip header
            for row in reader:
                iinfo = image_info.image_info()
                iinfo.name = row[0]
                iinfo.rank = int(row[1])
                iinfo.rank_in_class = int(row[2])
                iinfo.prob = float(row[3])
                for i in range(5):
                    class_id = row[4+i*2]
                    prob = row[5+i*2]
                    iinfo.top5[i]['class_id'] = class_id
                    iinfo.top5[i]['prob'] = prob

                self.iinfo_list.append(iinfo)
                
    def take_statistics(self):
        self.top1_rate = self.calc_topk_rate(1)
        self.top5_rate = self.calc_topk_rate(5)
        self.calc_rank_in_class()

    def calc_top5_mispreds(self):
        mispred_votes = [0 for i in self.get_class_count()]
        mispred_votes[self.class_id] = -1
        
        for iinfo in iinfo_list:
            for rank in range(5):
                class_id = iinfo.top5[rank]['class_id']
                if class_id == self.class_id:
                    break

                point = 5 - class_id
                mispred_votes[class_id] += point

        sorted_indexes = np.argsort(mispred_votes)[::-1]
        self.top5_mispreds = [sorted_indexes[rank] for rank in range(5)]
        
