import argparse
import subprocess
from sys import argv
from os import listdir
from os.path import isfile, join, basename, dirname

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir',
                        type = str,
                        default = '',
                        help = 'Directory containing images to be classified.',
                        
    )
    parser.add_argument('--ksize',
                        type = int,
                        default = '101',
                        help = 'kernel size for Gaussian filter',
    )
    parser.add_argument('--sigma',
                        type = float,
                        default = '100',
                        help = 'standard deviation for Gaussian filter',
    )                        

    FLAGS, unparsed = parser.parse_known_args()

    files = [ f for f in listdir(FLAGS.image_dir) if f.lower().endswith('.jpg')]
    print(files)
    for file in files:
        cmd = join(dirname(argv[0]), 'blur_image')
        subprocess.call([cmd, file, file, str(FLAGS.ksize), str(FLAGS.sigma)])
