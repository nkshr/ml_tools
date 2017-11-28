import argparse

import tensorflow as tf

from tensorflow.python.framework import graph_util
from tensorflow.python.framework import tensor_shape
from tensorflow.python.platform import gfile
from tensorflow.python.util import compat

MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # ~134M

class sub_eval_info:
    def __init__(self):
        self.images=[]
        self.label = ""
        self.accuracy=0
    
class eval_info:
    def __init__(self, labeled_images_file, labels_file):
        with open(labels_file, 'r') as f:
            labels = [line.replace('\n', '')  for line in f.readlines()];

        self.sub_eval_info_list = []
        
        for label in labels:
            sei = sub_eval_info()
            sei.label = label
            self.sub_eval_info_list.append(sei)
            
        with open(labeled_images_file, 'r') as f:
            for line in f.readlines():
                toks = line.split(sep=" ", maxsplit=1)
                idx = int(toks[1].replace('\n', ''))
                image = toks[0]
                #print(image, str(idx))
                self.sub_eval_info_list[idx].images.append(image)

def load_model_graph(model_path):
    with tf.Graph().as_default() as graph:
        with gfile.FastGFile(model_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def)
    return graph
                
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path',
        type = str,
        default = '/tmp/imagenet/classify_image_graph_def.pb',
        help=''
    )
    parser.add_argument(
        '--output_tensor_name',
        type = str,
        default = 'import/softmax:0',
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
    
    flags, unparsed = parser.parse_known_args()

    einfo = eval_info(flags.labeled_images, flags.labels)
    
    graph = load_model_graph(flags.model_path)

    op = graph.get_tensor_by_name(flags.output_tensor_name)
    #tf.cast(op, tf.float32)
    with graph.as_default():
        add_evaluation_step(op, op)

    ops = graph.get_operations()
    for op in ops:
        print(op.name)

    
        
if __name__ == '__main__':
    main()
    #tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
