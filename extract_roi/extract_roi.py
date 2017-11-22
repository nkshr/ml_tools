import cv2
import os
import argparse

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--image',
        type = str,
        default = './',
        help = 'Image to be cropped.'
    )
    parser.add_argument(
        '--x',
        type=int,
        default=0,
        help='x start point of roi'
    )
    parser.add_argument(
        '--y',
        type=int,
        default=0,
        help='y start point of roi'
    )
    parser.add_argument(
        '--w',
        type=int,
        default=0,
        help='roi width'
    )
    parser.add_argument(
        '--h',
        type=int,
        default=100,
        help='roi height'
    )
    
    FLAGS, unparsed=parser.parse_known_args()

    img=cv2.imread(FLAGS.image)
    roi = img[FLAGS.y:FLAGS.y+FLAGS.h, FLAGS.x:FLAGS.x+FLAGS.w]
    roi_name = 'cropped_'+os.path.basename(FLAGS.image)
    cv2.imwrite(os.path.join(os.path.dirname(FLAGS.image), roi_name), roi)
