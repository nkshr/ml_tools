import numpy as np
import cv2
import os
import fnmatch
import sys

if __name__ == '__main__':
    root_dir = os.path.abspath('./')
    args = sys.argv

    for root_dir, dirs, files in os.walk(args[1]):
        for file in files:
            img = cv2.imread(file)
            abs_path=root_dir+'/'+file

            if abs_path.lower().endswith(('.png')):
                print('{} is deleted.'.format(abs_path))
                os.remove(abs_path)
                continue

            if abs_path.lower().endswith(('.gif')):
                basename = os.path.splitext(abs_path)[0]
                cmd = 'convert -strip ' + abs_path + ' ' + basename + '.jpg'
                print(cmd)
                os.system(cmd)
                continue
            #if fnmatch.fnmatch(file, '*.png'):
            #    print('{} is deleted.'.format(file))

            #if fnmatch.fnmatch(file, '*.')
                    #os.remove(file)

                #cv2.imshow('disp', img)
                #cv2.waitKey(0)
