import random
import argparse
import numpy as np

def create_image_lists(fname, test_rate, val_rate):
    image_lists = {}
    random.seed(1)
    with open(fname, 'r') as f:
        for line in f.readlines():
            toks = line.split()
            name = toks[0]
            class_id = int(toks[1])
            if class_id not in image_lists:
                image_lists[class_id]={
                    'train' : list(),
                    'test' : list(),
                    'val' : list()
                }

            rval = random.randrange(100) * 0.01

            if rval < val_rate:
                image_lists[class_id]['val'].append(name)
            elif rval < val_rate + test_rate:
                image_lists[class_id]['test'].append(name)
            else:
                image_lists[class_id]['train'].append(name)

            
    return image_lists

def write_out_image_lists(image_lists, ftrain, ftest, fval):
    flist = {'train' : ftrain, 'test' : ftest, 'val' : fval}
    for dtype, fname in flist.items():
        with open(fname, 'w') as f:
            for class_id, image_list in image_lists.items():
                for image in image_list['train']:
                    f.write(image+' '+ str(class_id)+'\n')

def sort_image_lists_by_class_id(image_lists):
    class_ids = []
    for k, v in image_lists.items():
        class_ids.append(k)

    sorted_indexes = np.argsort(class_ids)
    sorted_image_lists = {}
    for index in sorted_indexes:
        class_id = class_ids[index]
        print(class_id)
        sorted_image_lists[class_id] = image_lists[class_id]
    return sorted_image_lists
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--image_dir',
        type=str,
        default='',
    )
    parser.add_argument(
        '--labeled_images',
        type=str,
        default='./labeled_images.txt'
    )
    parser.add_argument(
        '--test_rate',
        type = int,
        default = 0.1
    )
    parser.add_argument(
        '--val_rate',
        type = int,
        default = 0.1
    )
    parser.add_argument(
        '--labeled_val_images',
        type=str,
        default='./labeled_val_images.txt'
    )
    parser.add_argument(
        '--labeled_test_images',
        type=str,
        default='./labeled_test_images.txt'
    )
    parser.add_argument(
        '--labeled_train_images',
        type=str,
        default='labeled_train_images.txt'
    )
    
    flags, unparsed = parser.parse_known_args()
    image_lists = create_image_lists(flags.labeled_images, flags.test_rate, flags.val_rate)
    image_lists = sort_image_lists_by_class_id(image_lists)
    write_out_image_lists(image_lists, flags.labeled_train_images, flags.labeled_test_images, flags.labeled_val_images)
