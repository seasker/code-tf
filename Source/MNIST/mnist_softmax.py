# -*- coding: utf-8 -*-

#=============================================================================
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A very simple MNIST classifier.
See extensive documentation at
http://tensorflow.org/tutorials/mnist/beginners/index.md
"""



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

# Import data
from tensorflow.examples.tutorials.mnist import input_data

import tensorflow as tf

FLAGS = None


def main(_):
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

  # Create the model
  # x 是一个占位符，在运行计算时输入这个值，None表示第一个维度可以是任意长度
  x = tf.placeholder(tf.float32, [None, 784])
   # W 是一个变量，维度是[784,10]
  W = tf.Variable(tf.zeros([784, 10]))
  # b 是偏置值
  b = tf.Variable(tf.zeros([10]))
  # y 是softmax函数的输入
  y = tf.matmul(x, W) + b

  # Define loss and optimizer
  # y_是一个占位符，用于输入正确的答案
  y_ = tf.placeholder(tf.float32, [None, 10])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
  # outputs of 'y', and then average across the batch.
  # 就是计算softmax回归下的交叉熵（就是吴恩达教程中所说的代价函数costFuction）
  cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
  # 使用梯度下降最小化交叉熵
  train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
  #创建一个新的会话
  sess = tf.InteractiveSession()

  # 训练模型
  # 初始化所有的变量
  tf.initialize_all_variables().run()
  # 训练1000次，使用批梯度下降，每次随机抓取训练数据中的100个批处理数据点
  # 运行train_step，在其中用这些批数据点作为参数替换之前的的占位符
  for _ in range(1000):
    batch_xs, batch_ys = mnist.train.next_batch(100)
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

  # 测试训练好的模型
  # tf.argmax返回tensor对象在某一维上的数据最大值的索引值
  # correct_prediction是一个匹配布尔向量，y和y_两者相同则为1，不同为0
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  # 计算准确率
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  # 运行测试，输出结果
  print(sess.run(accuracy, feed_dict={x: mnist.test.images,
                                      y_: mnist.test.labels}))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='/tmp/data',
                      help='Directory for storing data')
  FLAGS = parser.parse_args()
  tf.app.run()