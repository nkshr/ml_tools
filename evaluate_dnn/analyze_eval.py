from eval_info import eval_info

import argparse
import sys
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--left',
        type = str,
        default = './left'
    )
    parser.add_argument(
        '--right',
        type = str,
        default = './right'
    )
    parser.add_argument(
        '--result',
        type = str,
        default = './result.csv'
    )
    parser.add_argument(
        '--left_debug_dir',
        type = str,
        default = './debug/left'
    )
    parser.add_argument(
        '--right_debug_dir',
        type = str,
        default = './debug/right'
    )

    flags, unparsed = parser.parse_known_args() 

    left_einfo = eval_info.eval_info()
    left_einfo.read(flags.left)

    left_einfo.sort_by_class_id()
    left_einfo.write(flags.left_debug_dir)
    
    right_einfo = eval_info.eval_info()
    right_einfo.read(flags.right)
    right_einfo.write(flags.right_debug_dir)

    if  left_einfo.get_class_count() != right_einfo.get_class_count():
        print('Error : {}({}) and {}({}) must have same classes.'.format(flags.left, left_einfo.get_class_count(), flags.right, right_einfo.get_class_count()))
        exit()

    roc_list = []
    for class_id in range(left_einfo.get_class_count()):
        left_class_info = left_einfo.get_class_info(class_id) 
        right_class_info = right_einfo.get_class_info(class_id)
        if abs(left_class_info.top1_rate) < sys.float_info.epsilon or left_class_info.top1_rate < 0 or right_class_info.top1_rate < 0:
            roc_list.append(sys.float_info.max)
        else:
            roc_list.append(right_class_info.top1_rate / left_class_info.top1_rate)
        
    sorted_indexes = np.argsort(roc_list)

    num_bads = 0
    with open(flags.result, 'w') as f:
        for class_id in sorted_indexes:
            left_cinfo = left_einfo.get_class_info(class_id)
            right_cinfo = right_einfo.get_class_info(class_id)
            roc = roc_list[class_id]
            if roc < 1:
                num_bads += 1

            text = '{},\"{}\",{},{},{}\n'.format(class_id, left_cinfo.label, left_cinfo.top1_rate, right_cinfo.top1_rate, roc)
            f.write(text)

        text = 'bad_rate,{}\n'.format(num_bads/left_einfo.get_class_count())
        f.write(text)
        f.flush()
