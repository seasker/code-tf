# -*- coding: utf-8 -*-  

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from six.moves import xrange

import tensorflow as tf

import os

def read_and_decode(filename,feature_name):
    filename_queue = tf.train.string_input_producer([filename])
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(
        serialized_example,
        features = {
            feature_name: tf.FixedLenFeature([],tf.string)
        }
    )
    flow_data = tf.decode_raw(feature[feature_name],tf.float64)
    flow_data = tf.reshape(35,288)
    flow_data = tf.cast(flow_data,tf.float32)
    return flow_data

def inputs(tfrecords_path, batch_size, min_after_dequeue, random=True):
    mat = read_and_decode(tfrecords_path, 'flow')
    if random is not True:
        mat = tf.train.batch(
            [mat],
            batch_size=batch_size,
            capacity=32 * batch_size + 64
            num_threads=12
        )
    else:
        mat = tf.train.shuffle_batch(
            [mat],
            batch_size=batch_size,
            min_after_dequeue = min_after_dequeue
            num_threads=12
        ) 
    return mat

def _activation_summary(x):
    """
    """
    tensor_name = re.sub('%s_[0-9]*/' %TOWER_NAME,'',x.op.name)
    tf.summary.histogram(tensor_name + '/activations',x)
    tf.summary.scalar(tensor_name + '/sparsity',tf.nn.zero_fraction(x))

def _variable_on_cpu(name,shape,initializer):
    with tf.device('/cpu:0'):
        dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
        var = tf.get_variable(name,shape,initializer=initializer,dtype=dtype)
    return var

def _variable_on_gpu(name,shape,initializer):
    with tf.device('/gpu:0'):
        dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
        var = tf.get_variable(name,shape,initializer=initializer,dtype=dtype)
    return var

def _variable_with_weight_decay(name,shape,stddev,wd):
    dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
    var = _variable_on_cpu(
        name,
        shape,
        tf.truncated_normal_initializer(stddev=stddev,dtype=dtype)
    )
    if wd is not None:
        weigth_decay = tf.multiply(tf.nn.l2_loss(var),wd,name='weight_loss')
        tf.add_to_collection('losses',weigth_decay)
    return var

def conv2d(input_matrix, kernel_size, in_channel, out_channel, stride=[1, 1, 1, 1], padding='SAME', name=None):
    kernel = _variable_on_cpu(
        'kernels',
        shape = [kernel_size, kernel_size, in_channel, out_channel],
        tf.truncated_normal_initializer(stddev=5e-2)
    )
    biases = _variable_on_gpu('biases', [out_channel], tf.constant_initializer(0.0))
    conv = tf.nn.conv2d(input_matrix, kernel, padding, stride)
    conv = tf.nn.bias_add(conv, biases)
    conv = tf.nn.relu(conv, name=name)
    _activation_summary(conv)
    return conv

def max_pooling(input_matrix, kernel_size, stride=[1, 2, 2, 1], padding='SAME', name=None):
    pool = tf.nn.max_pool(input_matrix, [1, kernel_size, kernel_size, 1], stride, name=name)
    return pool

def lrn(input_matrix, depth_radius, bias, alpha, beta, name):
    local_response_normalization = tf.nn.lrn(input_matrix, depth_radius, bias, alpha, beta, name)
    return local_response_normalization

def fc(input_fc, in_channel, out_channel, name=None):
    weights = _variable_with_weight_decay('weights', shape=[in_channel, out_channel],stddev=0.04,wd=0.004)
    biases = _variable_on_cpu('biases',[out_channel],tf.constant_initializer(0.1))
    fc = tf.nn.relu(tf.matmul(input_fc, weights) + biases, name=name)
    _activation_summary(fc)
    return fc

def mse_loss(predictions,reality):
    mse = tf.reduce_mean(tf.square(tf.subtract(reality, predictions)))
    return mse