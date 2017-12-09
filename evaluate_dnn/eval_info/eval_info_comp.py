from . import eval_info
from . import class_info

import csv
import sys
import math
import numpy as np

class eval_info_comp:
    def __init__(self):
        pass

    def read(self, left, right):
        self.left_einfo = eval_info.eval_info()
        self.left_einfo.read(left)
        self.left_einfo.sort_by_class_id()
        
        self.right_einfo = eval_info.eval_info()
        self.right_einfo.read(right)
        self.right_einfo.sort_by_class_id()

        if self.left_einfo.get_class_count() != self.right_einfo.get_class_count():
            raise ValueError('{}({}) and {}({}) have same number of classes.'.format(left, left_einfo.get_class_count(), right,right_einfo.get_class_count()))
                
    def take_synthesis(self):
        self.roc_list = [-1 for i in range(self.right_einfo.get_class_count())]

        for class_id in range(self.left_einfo.get_class_count()):
            left_cinfo = self.left_einfo.get_class_info(class_id)
            right_cinfo = self.right_einfo.get_class_info(class_id)
            if left_cinfo.top1_rate < sys.float_info.epsilon or right_cinfo.top1_rate < 0:
                self.roc_list[class_id] = -1
            else:
                self.roc_list[class_id] = (right_cinfo.top1_rate / left_cinfo.top1_rate)

        self.sum_roc = 0
        self.ave = 0
        num_valid_roc = 0
        
        for roc in self.roc_list:
            if roc >= 0:
                self.sum_roc += roc
                num_valid_roc += 1
        self.ave = self.sum_roc / num_valid_roc

        self.sdev = 0
        for roc in self.roc_list:
            if roc >= 0:
                self.sdev += pow(roc - self.ave, 2.0)
        self.sdev = math.sqrt(self.sdev / num_valid_roc)

        num_roc_under1 = 0
        num_low_roc = 0
        num_normal_roc = 0
        num_high_roc = 0
        
        for roc in self.roc_list:
            if roc < 0:
                continue
            if roc < 1:
                num_roc_under1 += 1
            if roc < (self.ave - self.sdev):
                num_low_roc += 1
            elif roc > (self.ave + self.sdev):
                num_high_roc += 1
            else:
                num_normal_roc += 1

        self.roc_under1_rate = num_roc_under1 / num_valid_roc
        self.low_roc_rate = num_low_roc / num_valid_roc
        self.normal_roc_rate = num_normal_roc / num_valid_roc
        self.high_roc_rate = num_high_roc / num_valid_roc

        pass
    
    def write(self, fname):
        with open(fname, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"')
            
            writer.writerow(['roc_under1_rate', self.roc_under1_rate])
            writer.writerow(['low_roc_rate', self.low_roc_rate])
            writer.writerow(['normal_roc_rate', self.normal_roc_rate])
            writer.writerow(['high_roc_rate', self.high_roc_rate])
            writer.writerow(['ave', self.ave])
            writer.writerow(['sdev', self.sdev])

            writer.writerow(['class_id','label', 'top1_rate', 'top1_rate', 'roc'])
            sorted_indexes = np.argsort(self.roc_list)
            for class_id in sorted_indexes:
                left_cinfo = self.left_einfo.get_class_info(class_id)
                right_cinfo = self.right_einfo.get_class_info(class_id)
                roc = self.roc_list[class_id]
                writer.writerow([class_id, left_cinfo.label, left_cinfo.top1_rate, right_cinfo.top1_rate, roc])

        pass

    def write_left_einfo(self, fname):
        self.left_einfo.write(fname)

    def write_right_einfo(self, fname):
        self.right_einfo.write(fname)
