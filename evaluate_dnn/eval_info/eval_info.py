from . import class_info        
from . import image_info

import numpy as np
import os

class eval_info:
    def __init__(self, labeled_images_file, labels_file, num_images=111):
        with open(labels_file, 'r') as f:
            labels = [line.replace('\n', '')  for line in f.readlines()];

        self.cinfo_list = []
        self.top1_rate = 0
        self.top5_rate = 0
        
        class_id = 0
        for label in labels:
            cinfo = class_info.class_info()
            cinfo.label = label
            cinfo.class_id = class_id
            self.cinfo_list.append(cinfo)
            class_id += 1
            
        with open(labeled_images_file, 'r') as f:
            for line in f.readlines():                                    
                iinfo = image_info.image_info()
                
                toks = line.split(sep=" ", maxsplit=1)
                idx = int(toks[1].replace('\n', ''))
                iinfo.name = toks[0]

                cinfo = self.cinfo_list[idx]
                if len(cinfo.iinfo_list) < num_images or num_images < 0:
                    cinfo.iinfo_list.append(iinfo)
                #self.__cinfo_list[idx].images.append(image)

            for cinfo in self.cinfo_list:
                if len(cinfo.iinfo_list) != num_images:
                    print('class', cinfo.class_id, 'has too less images({}).'.format(len(cinfo.iinfo_list)))

    def __init__(self):
        self.cinfo_list = []
        self.top1_rate = 0
        self.top5_rate = 0
                    
    def get_class_count(self):
        return len(self.cinfo_list)

    def get_class_info(self, class_id):
        for cinfo in self.cinfo_list:
            if cinfo.class_id == class_id:
                return cinfo

    def __str__(self):
        text = ''
        for cinfo in self.cinfo_list:
            text += str(cinfo)

        return text

    def calc_top5_rate(self):
        num_correct_preds = 0
        num_images = 0
        for cinfo in self.cinfo_list:
            for iinfo in cinfo.iinfo_list:
                num_images += 1
                if iinfo.rank < 5:
                    num_correct_preds += 1

        if  num_images:
            self.top5_rate = num_correct_preds / num_images
        else:
            self.top5_rate = 0
            
    def calc_top1_rate(self):        
        num_correct_preds = 0
        num_images = 0
        
        for cinfo in self.cinfo_list:
            num_images += len(cinfo.iinfo_list)
            for iinfo in cinfo.iinfo_list:
                if iinfo.rank == 0:
                    num_correct_preds += 1
        if num_images:
            self.top1_rate = num_correct_preds / num_images
        else:
            self.top1_rate = 0
            
    def __iter__(self):
        self.cinfo_list_idx = 0
        return self        

    def __next__(self):
        if self.cinfo_list_idx == len(self.cinfo_list):
            raise StopIteration
        self.cinfo_list_idx += 1
        return self.cinfo_list[self.cinfo_list_idx-1]

    def sort_by_top1_rate(self):
        top1_rate_arr = np.array([cinfo.top1_rate for cinfo in self.cinfo_list])
        sorted_indexes = np.argsort(top1_rate_arr)[::-1]
        sorted_cinfo_list = [self.cinfo_list[index] for index in sorted_indexes]
        self.cinfo_list  = sorted_cinfo_list

    def calc_top1_rate_rank(self):
        top1_rate_arr = np.array([cinfo.top1_rate for cinfo in self.cinfo_list])
        sorted_indexes = np.argsort(top1_rate_arr)[::-1]
        for rank in range(len(sorted_indexes)):
            self.cinfo_list[sorted_indexes[rank]].top1_rate_rank = rank

    def calc_top5_rate_rank(self):
        top5_rate_arr = np.array([cinfo.top5_rate for cinfo in self.cinfo_list])
        sorted_indexes = np.argsort(top5_rate_arr)[::-1]
        for rank in range(len(sorted_indexes)):
            self.cinfo_list[sorted_indexes[rank]].top5_rate_rank = rank

    def write_summary(self, fname):
        text = 'class_id,label,num_images,top1_rate,top5_rate,top1_rate_rank,top5_rate_rank\n'
        with open(fname, 'w') as f:
            f.write(text)
            f.flush()
            
            f.write(str(self))
            f.flush()

    def write(self, dir):
        summary = os.path.join(dir, 'summary.csv')
        self.write_summary(summary)

        for cinfo in self:
            detail = os.path.join(dir, 'class{0:04d}.csv'.format(cinfo.class_id))
            cinfo.write_detail(detail)
            
    def read(self, dir):
        self.cinfo_list = []
        self.top1_rate = 0
        self.top5_rate = 0

        class_csvs = [class_csv for class_csv in os.listdir(dir) if class_csv.startswith('class')]

        for class_csv in class_csvs:
            cinfo = class_info.class_info()
            cinfo.read(os.path.join(dir, class_csv))
                        
    
