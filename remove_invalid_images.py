import numpy as np
import cv2
import os
import fnmatch
import sys
from PIL import Image

if __name__ == '__main__':
    args = sys.argv

    # for root_dir, dirs, files in os.walk(args[1]):
    #     for file in files:
    #         path=root_dir+'/'+file

    #         if path.lower().endswith(('.png')):
    #             print('{} is deleted.'.format(path))
    #             os.remove(path)
    #             continue

    #         if abs_path.lower().endswith(('.gif')):
    #             basename = os.path.splitext(path)[0]
    #             cmd = 'convert -strip ' + path + ' ' + basename + '.jpg'
    #             print(cmd)
    #             os.system(cmd)
    #             continue

    for root_dir, dirs, files in os.walk(args[1]):
        for file in files:
            path = root_dir+'/'+file
            if path.lower().endswith(('.jpg')):
                #print(path)
                try:
                    img = cv2.imread(path)
                    if img is not None:
                        pass
                        #cv2.imwrite(path, img)
                    else:
                        os.remove(path)
                        print('Remove', path)
                except Exception as e:
                    print('Exception is thrown.')
                    print(e)
                    print('removing ' + path)
                    os.remove(path)
                    
