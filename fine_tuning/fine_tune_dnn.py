import random
import argparse
import numpy as np

import util

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_path',
        type = str,
        default = '/home/ubuntu/tensorflow/tensorflow/examples/label_image/data/inception_v3_2016_08_28_frozen.pb'
    )
    parser.add_argument(
        '--image_dir',
        type=str,
        default='',
    )
    parser.add_argument(
        '--labeled_images',
        type=str,
        default='./labeled_images.txt'
    )
    parser.add_argument(
        '--test_rate',
        type = int,
        default = 0.1
    )
    parser.add_argument(
        '--val_rate',
        type = int,
        default = 0.1
    )
    parser.add_argument(
        '--labeled_val_images',
        type=str,
        default='./labeled_val_images.txt'
    )
    parser.add_argument(
        '--labeled_test_images',
        type=str,
        default='./labeled_test_images.txt'
    )
    parser.add_argument(
        '--labeled_train_images',
        type=str,
        default='labeled_train_images.txt'
    )
    parser.add_argument(
        '--num_train_steps',
        type=str,
        default=1000,
    )
    parser.add_argument(
        '--train_batch_size',
        type=int,
        default=100
    )
    parser.add_argument(
        '--input_width',
        type=int,
        default=299
    )
    parser.add_argument(
        '--input_height',
        type=int,
        default=299
    )
    parser.add_argument(
        '--input_depth',
        type=int,
        default=3
    )
    parser.add_argument(
        '--input_mean',
        type=int,
        default=0
    )
    parser.add_argument(
        '--input_std',
        type=int,
        default=255
    )
    parser.add_argument(
        '--resized_input_tensor_name',
        type=str,
        default='input:0',
    )
    parser.add_argument(
        '--bottleneck_tensor_name',
        type = str,
        default = 'InceptionV3/Logits/SpatialSqueeze:0'
    )
    parser.add_argument(
        '--operations',
        type = str,
        default = 'operations.txt'
    )
    flags, unparsed = parser.parse_known_args()

    graph = util.load_model_graph(flags.model_path)
    image_lists = util.create_image_lists(flags.labeled_images, flags.test_rate, flags.val_rate)
    image_lists = util.sort_image_lists_by_class_id(image_lists)
    util.write_out_image_lists(image_lists, flags.labeled_train_images, flags.labeled_test_images, flags.labeled_val_images)

    # with tf.Sesion(graph=graph) as sess:
    #     resized_input_tensor = graph.get_tensor_by_name('import/'+flags.resizzed_input_tensor_name)
    #     bottleneck_tensor = graph.get_tensor_by_name('import/'+flags.bottleneck_tensor_name)
    #     if flags.preprocess == "grayscale":
    #         jpeg_data_tensor, decoded_image_tensor = add_jpeg_grayscale_decoding(
    #             flags.input_width, flags.input_height, flags.input_depth,
    #             flags.input_mean, flags.input_std
    #             )
    #     else:
    #         jpeg_data_tensor, decoded_image_tensor = add_jpeg_decoding(
    #             flags.input_width, flags.input_height, flags.input_depth,
    #             flags.input_mean, flags.input_std
    #         )

    #     (train_step, cross_entropy, bottleneck_input, ground_truth_input,
    #     final_tensor) = add_final_training_ops(
    #         len(image_lists.keys()), flags.final_tensor_name, bottleneck_tensor,
    #         flags.bottleneck_tensor_size)

    #     eval_step, pred = add_evaluation_step(
    #         final_tensor, ground_truth_input)

    #     init = tf.global_variables_initializer()
    #     sess.run(init)

    #     for i in range(flags.num_train_steps):
    #         train_image_list, train_ground_truths = get_image_batch(flags.train_batch_size, "train")
    #         train_bottlenecks, train_ground_truths = get_image_batch(flags.batch_size,
    #                                                                  'train',
    #                                                                  flags.image_dir,
    #                                                                  decoded_image_tensor,
    #                                                                  jpeg_data_tensor,
    #                                                                  bottleneck_tensor,
    #                                                                  resized_input_tensor)        
    #         sess.run(train_step, {bottlenck_input :  train_bottlenecks,
    #                              ground_truth_input : train_ground_truths})

    #         is_last_step = (i + 1 == flags.num_train_steps)
    #         if (i % flags.eval_step_interval) == 0 or is_last_step:
    #             train_accuracy, cross_entropy_value = sess.run(
    #                 [eval_step, cross_entropy],
    #                 feed_dict = {bottleneck_input : train_bottlenecks,
    #                              ground_truth_input : train_ground_truths})
    #             val_bottlenecks, val_ground_truths = get_image_batch(flags,batch_size,
    #                                                                  'val',
    #                                                                  flags.image_dir,
    #                                                                  decoded_image_tensor,
    #                                                                  jpeg_data_tensor,
    #                                                                  bottleneck_tensor,
    #                                                                  resized_input_tensor)
    #             val_accuracy = sess.run(
    #                 eval_step,
    #                 feed_dict = {bottleneck_input : val_bottlenecks,
    #                              ground_truth_input : val_ground_truths})

    with open(flags.operations, 'w') as f:
        for op in graph.get_operations():
            f.write(op.name+'\n')
        
