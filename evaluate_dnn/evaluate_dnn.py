from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
from datetime import datetime
import hashlib
import os.path
import random
import re
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow as tf

from tensorflow.python.framework import graph_util
from tensorflow.python.framework import tensor_shape
from tensorflow.python.platform import gfile
from tensorflow.python.util import compat

import cv2
import csv
from eval_info import eval_info

def load_model_graph(model_path):
    with tf.Graph().as_default() as graph:
        with gfile.FastGFile(model_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def)
            
    return graph

def create_jpeg_decoder(input_width, input_height, input_depth, input_mean,
                         input_std):
  """Adds operations that perform JPEG decoding and resizing to the graph..

  Args:
    input_width: Desired width of the image fed into the recognizer graph.
    input_height: Desired width of the image fed into the recognizer graph.
    input_depth: Desired channels of the image fed into the recognizer graph.
    input_mean: Pixel value that should be zero in the image for the graph.
    input_std: How much to divide the pixel values by before recognition.

  Returns:
    Tensors for the node to feed JPEG data into, and the output of the
      preprocessing steps.
  """

  jpeg_data = tf.placeholder(tf.string, name='DecodeJPGInput')
  decoded_image = tf.image.decode_jpeg(jpeg_data, channels=input_depth)
  decoded_image_as_float = tf.cast(decoded_image, dtype=tf.float32)
  decoded_image_4d = tf.expand_dims(decoded_image_as_float, 0)
  resize_shape = tf.stack([input_height, input_width])
  resize_shape_as_int = tf.cast(resize_shape, dtype=tf.int32)
  resized_image = tf.image.resize_bilinear(decoded_image_4d,
                                           resize_shape_as_int)
  offset_image = tf.subtract(resized_image, input_mean)
  mul_image = tf.multiply(offset_image, 1.0 / input_std)

  return jpeg_data, mul_image, decoded_image
    
def create_jpeg_grayscale_decoder(input_width, input_height,  input_depth, input_mean,
                             input_std):
    jpeg_data = tf.placeholder(tf.string, name='DecodeJPGInput')
    decoded_image = tf.image.decode_jpeg(jpeg_data, channels=1)
    expanded_decoded_image = tf.image.grayscale_to_rgb(decoded_image)
    decoded_image_as_float = tf.cast(expanded_decoded_image, dtype=tf.float32)
    decoded_image_4d = tf.expand_dims(decoded_image_as_float, 0)
    resize_shape = tf.stack([input_height, input_width])
    resize_shape_as_int = tf.cast(resize_shape, dtype=tf.int32)
    resized_image = tf.image.resize_bilinear(decoded_image_4d,
                                             resize_shape_as_int)
    offset_image = tf.subtract(resized_image, input_mean)
    mul_image = tf.multiply(offset_image, 1.0/ input_std)

    return jpeg_data, mul_image, decoded_image

def create_rgb_to_grayscale_converter():
    rgb_data_tensor = tf.placeholder(tf.float32, shape = [None, None, None, 3])
    gray_data_tensor = tf.image.rgb_to_grayscale(rgb_data_tensor)
    expanded_gray_data_tensor = tf.image.grayscale_to_rgb(gray_data_tensor)
    return rgb_data_tensor, expanded_gray_data_tensor

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result


def main():
    einfo = eval_info.eval_info(flags.labeled_images, flags.labels, num_images = flags.num_images)
    
    graph = load_model_graph(flags.model_path)

    with tf.Session(graph = graph) as sess:
        input_tensor = graph.get_tensor_by_name('import/'+flags.input_tensor_name)
        output_tensor = graph.get_tensor_by_name('import/'+flags.output_tensor_name)

        if flags.preprocess == 'grayscale':
            jpeg_data_tensor, decoded_data_tensor, raw_data_tensor = create_jpeg_grayscale_decoder(
                flags.input_width, flags.input_height,
                flags.input_depth, flags.input_mean,
                flags.input_std
            )
            print('grayscale conversion was choosed as preprocess.')
        else:
            jpeg_data_tensor, decoded_data_tensor, raw_data_tensor = create_jpeg_decoder(
                flags.input_width, flags.input_height,
                flags.input_depth, flags.input_mean,
                flags.input_std
            )
            print('No preprocess was choosed.')
        
        ground_truth_tensor = tf.placeholder(
            tf.float32,
            [None, einfo.get_class_count()],
            name = 'GroundTruthInput'
        )            
        
        if not flags.eval_classes:
            class_ids = range(einfo.get_class_count())
        else:
            class_ids = flags.eval_classes
            
        for class_id in class_ids:
            print('class', class_id, 'is processed.')
            cinfo= einfo.get_class_info(class_id)
                                
            for image_id in range(len(cinfo.iinfo_list)):
                iinfo = cinfo.iinfo_list[image_id]
                image_path = os.path.join(flags.image_dir, iinfo.name)
                if flags.debug:
                    print('Evaluate', image_path, class_id)

                if not gfile.Exists(image_path):
                    print(image_path, "doesn't exist.")
                    
                jpeg_data = tf.gfile.FastGFile(image_path, 'rb').read()
                if flags.debug:
                    raw_data = sess.run(raw_data_tensor,
                             feed_dict={jpeg_data_tensor : jpeg_data})
                    if flags.preprocess == 'grayscale':
                        cv2.imwrite('test.png', raw_data)
                    else:
                        cv2.imwrite('test.png', cv2.cvtColor(raw_data, cv2.COLOR_RGB2BGR))
                        
                resized_data = sess.run(decoded_data_tensor,
                                       feed_dict={jpeg_data_tensor : jpeg_data})
                            
                results = sess.run(output_tensor,
                                   feed_dict={
                                       input_tensor : resized_data})

                results = np.squeeze(results)
                prob = results[class_id]
                iinfo.prob = prob
                
                sorted_indexes = results.argsort()[::-1]
                for i in range(len(sorted_indexes)):
                    if sorted_indexes[i] == class_id:
                        iinfo.rank = i
                        
                if flags.debug:
                    print('Result :', image_path, iinfo.rank, iinfo.prob)

                for i in range(5):
                    tmp_cid = sorted_indexes[i]
                    prob = results[tmp_cid]
                    iinfo.top5_labels.append((tmp_cid, prob))
                    
            cinfo.calc_top1_rate()
            cinfo.calc_top5_rate()

    operations_path = os.path.join(flags.result_dir, 'operations.txt')
    with open(operations_path, 'w') as f:
        for op in graph.get_operations():
            f.write(op.name+'\n')

    einfo.calc_top1_rate()
    einfo.calc_top5_rate()
    einfo.calc_top1_rate_rank()
    einfo.calc_top5_rate_rank()
    #einfo.sort_by_top1_rate()

    einfo.write(flags.result_dir)
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path',
        type = str,
        default = '/home/ubuntu/tensorflow/tensorflow/examples/label_image/data/inception_v3_2016_08_28_frozen.pb',
        help=''
    )
    parser.add_argument(
        '--input_tensor_name',
        type = str,
        default = 'input:0',
        help = ''
    )
    parser.add_argument(
        '--output_tensor_name',
        type = str,
        default = 'InceptionV3/Predictions/Reshape_1:0',
        help = ''
    )
    parser.add_argument(
        '--image_dir',
        type = str,
        default = './',
        help = ''
    )
    parser.add_argument(
        '--labeled_images',
        type = str,
        default = './labeled_images.txt',
        help = ''
    )
    parser.add_argument(
        '--labels',
        type = str,
        default = './labels.txt',
        help = ''
    )
    parser.add_argument(
        '--debug',
        action = 'store_true',
    )
    parser.add_argument(
        '--input_width',
        default = 299
    )
    parser.add_argument(
        '--input_height',
        default = 299
    )
    parser.add_argument(
        '--input_depth',
        type = int, 
        default = 3
    )
    parser.add_argument(
        '--input_mean',
        default = 0
    )
    parser.add_argument(
        '--input_std',
        default = 255
    )
    parser.add_argument(
        '--eval_classes',
        nargs = '*',
        type = int,
        help = 'If eval_classes are not  specified, all classes are evaluated.Otherwise only specified classes are evaluated.'
    )
    parser.add_argument(
        '--preprocess',
        type = str,
        default = None,
        help = 'if preprocess is needed, choose \"grayscale\"or \"blur\".'
    )
    parser.add_argument(
        '--num_images',
        type = int,
        default = -1,
        help = 'Maximum number of images to be evaluated per class.\nIf not specified, all images are evaluated.'
    )
    parser.add_argument(
        '--result_dir',
        type = str,
        default = './result'
    )
    
    flags, unparsed = parser.parse_known_args()

    main()
    #tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
