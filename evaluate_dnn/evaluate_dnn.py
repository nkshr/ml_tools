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


MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # ~134M

class sub_eval_info:
    def __init__(self):
        self.images=[]
        self.ranks=[]
        self.probs=[]
        self.label = ""
        self.class_id = 0
        self.top1_rate = 0
        self.top5_rate = 0
        self.evaluated = False
        
    def __str__(self):
        return "class_id : {}\n\tlabel : {}\n\ttop1_rate : {}\n\ttop5_rate : {}\n".format(self.class_id, self.label, self.top1_rate, self.top5_rate)

    def calc_top1_rate(self):
        if (len(self.images)) == 0:
            self.top1_rate = 0
            return
        
        num_top1 = 0
        for rank in self.ranks:
            if rank == 0:
                num_top1 += 1
        self.top1_rate = num_top1 / len(self.images)

    def calc_top5_rate(self):
        if (len(self.images)) == 0:
            self.top5_rate = 0
            return
        
        num_top5 = 0
        for rank in self.ranks:
            if rank < 5:
                num_top5 += 1
        self.top5_rate = num_top5 / len(self.images)

class eval_info:
    def __init__(self, labeled_images_file, labels_file):
        with open(labels_file, 'r') as f:
            labels = [line.replace('\n', '')  for line in f.readlines()];

        self.__sub_eval_info_list = []

        class_id = 0
        for label in labels:
            sei = sub_eval_info()
            sei.label = label
            sei.class_id = class_id
            self.__sub_eval_info_list.append(sei)
            class_id += 1
            
        with open(labeled_images_file, 'r') as f:
            for line in f.readlines():
                toks = line.split(sep=" ", maxsplit=1)
                idx = int(toks[1].replace('\n', ''))
                image = toks[0]
                #print(image, str(idx))
                self.__sub_eval_info_list[idx].images.append(image)

    def get_class_count(self):
        return len(self.__sub_eval_info_list)

    def get_sub_eval_info(self, idx):
        return self.__sub_eval_info_list[idx]
    
def load_model_graph(model_path):
    with tf.Graph().as_default() as graph:
        with gfile.FastGFile(model_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def)
            
    return graph

def add_jpeg_decoding(input_width, input_height, input_depth, input_mean,
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

  return jpeg_data, mul_image

def add_evaluation_step(result_tensor, ground_truth_tensor):
  """Inserts the operations we need to evaluate the accuracy of our results.

  Args:
    result_tensor: The new final node that produces results.
    ground_truth_tensor: The node we feed ground truth data
    into.

  Returns:
    Tuple of (evaluation step, prediction).
  """
  with tf.name_scope('accuracy'):
    with tf.name_scope('correct_prediction'):
      prediction = tf.argmax(result_tensor, 1)
      correct_prediction = tf.equal(
          prediction, tf.argmax(ground_truth_tensor, 1))
    with tf.name_scope('accuracy'):
      evaluation_step = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  #tf.summary.scalar('accuracy', evaluation_step)
  return evaluation_step, prediction

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
    einfo = eval_info(flags.labeled_images, flags.labels)
    
    graph = load_model_graph(flags.model_path)

    with tf.Session(graph = graph) as sess:
        input_tensor = graph.get_tensor_by_name('import/'+flags.input_tensor_name)
        output_tensor = graph.get_tensor_by_name('import/'+flags.output_tensor_name)

        jpeg_data_tensor, decoded_data_tensor = add_jpeg_decoding(
            flags.input_width, flags.input_height,
            flags.input_depth, flags.input_mean,
            flags.input_std
        )

        ground_truth_tensor = tf.placeholder(
            tf.float32,
            [None, einfo.get_class_count()],
            name = 'GroundTruthInput'
        )            
        
        evaluation_step, prediction = add_evaluation_step(output_tensor, ground_truth_tensor)

        if not flags.valid_class_ids:
            class_ids = range(einfo.get_class_count())
        else:
            class_ids = flags.valid_class_ids
            
        for class_id in class_ids:
            seinfo= einfo.get_sub_eval_info(class_id)
            num_samples = int(flags.eval_rate * len(seinfo.images))
            if num_samples < 1:
                print('class', class_id, 'doesn\'t contain a image.')
                continue
            for image_id in range(num_samples):
                image_path = os.path.join(flags.image_dir, seinfo.images[image_id])
                if flags.debug:
                    print('Evaluate', image_path, class_id)

                if not gfile.Exists(image_path):
                    print(image_path, "doesn't exist.")
                    
                jpeg_data = tf.gfile.FastGFile(image_path, 'rb').read()
                resized_data = sess.run(decoded_data_tensor,
                                       feed_dict={jpeg_data_tensor : jpeg_data})
                            
                results = sess.run(output_tensor,
                                   feed_dict={
                                       input_tensor : resized_data})

                results = np.squeeze(results)
                prob = results[class_id]
                seinfo.probs.append(prob)
                
                sorted_indexes = results.argsort()[::-1]
                for i in range(len(sorted_indexes)):
                    if sorted_indexes[i] == class_id:
                        seinfo.ranks.append(i)
                        
                if flags.debug:
                    print('Result :', image_path, prob)

            
            seinfo.calc_top1_rate()
            seinfo.calc_top5_rate()
            seinfo.evaluated = True
            
    if flags.debug:
        with open(flags.operations, 'w') as f:
            for op in graph.get_operations():
                f.write(op.name+'\n')


    if flags.debug:
        for seinfo_idx in range(einfo.get_class_count()):
            seinfo = einfo.get_sub_eval_info(seinfo_idx)
            if seinfo.evaluated:
                print(seinfo)
        
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
        '--operations',
        default = 'operations.txt'
    )
    parser.add_argument(
        '--eval_rate',
        type = float,
        default = 1.0
    )
    parser.add_argument(
        '--valid_class_ids',
        nargs = '*',
        type = int
    )
    flags, unparsed = parser.parse_known_args()

    main()
    #tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
