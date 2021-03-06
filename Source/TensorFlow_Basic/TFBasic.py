# -*- coding: utf-8 -*-
import tensorflow as tf
#########################################################################################
#                                                                                       
#                                1.构建图                                                
#                                                                                         
#########################################################################################

#创建一个常量op，产生一个1*2矩阵，这个op被称作一个节点，并加入到默认图中。
matrix1 = tf.constant([[3.,3.]])

#创建一个常量op，产生一个2*1矩阵。
matrix2 = tf.constant([[2.],[2.]])

#创建一个矩阵乘法matmul op，其输入是'matrix1',其返回值product是矩阵乘法的输出结果
product = tf.matmul(matrix1,matrix2)

#########################################################################################
#                                                                                       
#                                2.在一个Session中启动图                                                
#                                                                                         
#########################################################################################

#非with形式
sess = tf.Session()

#调用sess的run()方法来执行矩阵乘法op，传入product作为该方法的参数
#传入product以向run()方法表明我们希望返回矩阵乘法op的输出。
#整个执行过程是自动化的, 会话负责传递 op 所需的全部输入。 op 通常是并发执行的。
#函数调用 run(product) 触发了图中三个 op (两个常量 op 和一个矩阵乘法 op) 的执行。
#返回的result是一个numpy的ndarry对象。
result = sess.run(product)

#输出结果
print result

#任务完成
sess.close()