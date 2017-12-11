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

def add_final_training_ops(class_count, final_tensor_name, bottleneck_tensor,
                           bottleneck_tensor_size):
  """Adds a new softmax and fully-connected layer for training.

  We need to retrain the top layer to identify our new classes, so this function
  adds the right operations to the graph, along with some variables to hold the
  weights, and then sets up all the gradients for the backward pass.

  The set up for the softmax and fully-connected layers is based on:
  https://www.tensorflow.org/versions/master/tutorials/mnist/beginners/index.html

  Args:
    class_count: Integer of how many categories of things we're trying to
    recognize.
    final_tensor_name: Name string for the new final node that produces results.
    bottleneck_tensor: The output of the main CNN graph.
    bottleneck_tensor_size: How many entries in the bottleneck vector.

  Returns:
    The tensors for the training and cross entropy results, and tensors for the
    bottleneck input and ground truth input.
  """
  with tf.name_scope('input'):
    bottleneck_input = tf.placeholder_with_default(
        bottleneck_tensor,
        shape=[None, bottleneck_tensor_size],
        name='BottleneckInputPlaceholder')

    ground_truth_input = tf.placeholder(tf.float32,
                                        [None, class_count],
                                        name='GroundTruthInput')

  # Organizing the following ops as `final_training_ops` so they're easier
  # to see in TensorBoard
  layer_name = 'final_training_ops'
  with tf.name_scope(layer_name):
    with tf.name_scope('weights'):
      initial_value = tf.truncated_normal(
          [bottleneck_tensor_size, class_count], stddev=0.001)

      layer_weights = tf.Variable(initial_value, name='final_weights')

      variable_summaries(layer_weights)
    with tf.name_scope('biases'):
      layer_biases = tf.Variable(tf.zeros([class_count]), name='final_biases')
      variable_summaries(layer_biases)
    with tf.name_scope('Wx_plus_b'):
      logits = tf.matmul(bottleneck_input, layer_weights) + layer_biases
      tf.summary.histogram('pre_activations', logits)

  final_tensor = tf.nn.softmax(logits, name=final_tensor_name)
  tf.summary.histogram('activations', final_tensor)

  with tf.name_scope('cross_entropy'):
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
        labels=ground_truth_input, logits=logits)
    with tf.name_scope('total'):
      cross_entropy_mean = tf.reduce_mean(cross_entropy)
  tf.summary.scalar('cross_entropy', cross_entropy_mean)

  with tf.name_scope('train'):
    optimizer = tf.train.GradientDescentOptimizer(FLAGS.learning_rate)
    train_step = optimizer.minimize(cross_entropy_mean)

  return (train_step, cross_entropy_mean, bottleneck_input, ground_truth_input,
          final_tensor)


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
  tf.summary.scalar('accuracy', evaluation_step)
  return evaluation_step, prediction

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

  return jpeg_data, mul_image, decoded_image
    
def add_jpeg_grayscale_decoding(input_width, input_height,  input_depth, input_mean,
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

def load_model_graph(model_path):
    with tf.Graph().as_default() as graph:
        with gfile.FastGFile(model_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def)
            
    return graph

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


def get_image_batch(batch_size, dtype):
  class_count = len(image_lists.keys())
  image_list = []
  ground_truths = []
  for i in batch_size:
     class_index = random.randrange(class_count)
     class_id = list(image_lists.keys())[label_index]
     ground_truths.append(class_id)

     image_index = random.randrange(len(image_lists[class_id][dtype]))
     image_name = image_lists[class_id][dtype][image_index]
     image_list.append(image_name)

  return image_list, ground_truths

def get_image_batch(batch_size, dtype, image_dir, decoded_image_tensor, jpeg_data_tensor, bottleneck_tensor, resized_input_tensor):
  class_count = len(image_lists.keys())
  image_list = []
  ground_truths = []
  bottlenecks = []
  for i in batch_size:
    class_index = random.randrange(class_count)
    class_id = list(image_lilsts.keys())[class_index]
    ground_truths.append(class_id)

    image_index = random.randrange(len(image_lists[class_id][dtype]))
    image_name = image_lists[class_id][dtype][image_index]
    image_path = os.path.join(image_dir, image_name)

    jpeg_data = tf.gfile.FastGFile(image_path, 'rb')
    resized_image_data = sess.run(decoded_image_tensor,
                                  feed_dict = {jpeg_data_tensor : jpeg_data})
    bottleneck = sess.run(bottleneck_tensor,
                          feed_dict = {resized_input_tensor : resized_image_data})
    bottlenecks.append(bottleneck)

  return  bottlenecks, ground_truths
