import cv2
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--image_dir',
        type = str,
        default = './',
        help = 'Directory containing images.'
    )
    parser.add_argument(
        '--conversion',
        type = str,
        default = 'none',
        help = 'Select none, gray'
    )

    FLAGS, unparsed = parser.parse_known_args()
    root_dir = FLAGS.image_dir
    conversion = FLAGS.conversion
    dirs = os.listdir(root_dir)

    for dir in dirs:
        subdir_path = os.path.join(root_dir, dir)
        files = os.listdir(subdir_path)
        for file in files:
            file_path = os.path.join(subdir_path, file)
            print(file_path)                
            try:
                img = cv2.imread(file_path)
                if conversion == 'gray':
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    img = img
                cv2.imwrite(file_path, img)
            except Exception as e:
                print('Exception is thrown.')
                print(e)
