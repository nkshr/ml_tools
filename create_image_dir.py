import argparse
import shutil
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--image_dir',
        type = str,
        default = '',
        help = 'Directroy to contain retraining images.'
    )    
    parser.add_argument(
        '--labeled_image_list_file',
        type = str,
        default = 'labeled_image_list.txt',
        help = 'File dicribing lable image sets.'
    )
    
    FLAGS, unparsed = parser.parse_known_args()
    f = open(FLAGS.labeled_image_list_file, 'r')
    lines = f.readlines()
    num_lines = sum(1 for line in lines)
    result = dict()
    label_image_dict=dict()

    print('Creating a label-image dictonary.')
    for line in lines:
      elems=line.split()
      path = elems[0]
      label = str(elems[1])
      images = label_image_dict.get(label)
      if images != None:
        images.append(path)
      else:
        label_image_dict[label] = [path]

    if not os.path.exists(FLAGS.image_dir):
        os.mkdir(FLAGS.image_dir)

    num_images_copyed = 0
    for label, images in label_image_dict.items():
        sub_dir = os.path.join(FLAGS.image_dir, label)
        if not os.path.exists(sub_dir):
            os.mkdir(sub_dir)
            
        for image in images:
            print('\rCopying : {2:03f}%'.format(image, sub_dir + '/' + os.path.basename(image), 100 * float(num_images_copyed / (num_lines-1))), end='\r')
            shutil.copy(image, sub_dir)
            num_images_copyed += 1

    print('\rCopying : {0:03f}%'.format(100))
