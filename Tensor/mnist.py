import tensorflow as tf
from tensorflow.keras import datasets
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"]='2'
(x,y),_=datasets.mnist.load_data()
x = tf.convert_to_tensor(x,tf.float32)/255
y = tf.convert_to_tensor(y,tf.int32)
train_db = tf.data.Dataset.from_tensor_slices((x,y)).batch(128)
w1 = tf.Variable(tf.random.truncated_normal([28*28,256],stddev=0.1))
b1 = tf.Variable(tf.zeros([256]))
w2 = tf.Variable(tf.random.truncated_normal([256,128],stddev=0.1))
b2 = tf.Variable(tf.zeros([128]))
w3 = tf.Variable(tf.random.truncated_normal([128,10],stddev=0.1))
b3 = tf.Variable(tf.zeros([10]))
for i in range(10):
    for step,(x,y) in enumerate(train_db):
        with tf.GradientTape() as Tape:
            x = tf.reshape(x,[-1,28*28])
            h1 = x@w1 + b1
            h1 = tf.nn.relu(h1)
            h2 = h1@w2 + b2
            h2 = tf.nn.relu(h2)
            out = h2@w3 + b3
            y_one_hot = tf.one_hot(y,depth=10)
            loss = tf.reduce_mean(tf.square(y_one_hot - out))
        L = Tape.gradient(loss,[w1,b1,w2,b2,w3,b3])
        w1.assign_sub(0.001*L[0])
        b1.assign_sub(0.001*L[1])
        w2.assign_sub(0.001*L[2])
        b2.assign_sub(0.001*L[3])
        w3.assign_sub(0.001*L[4])
        b3.assign_sub(0.001*L[5])
        if(step%100==0):
            print(step,"Loss:",float(loss))
print("W1:{0}\nb1:{1}\nW2:{2}\nb2:{3}\nW3:{4}\nb3:{5}".format(w1.numpy(),b1.numpy(),w2.numpy(),b2.numpy(),w3.numpy(),b3.numpy()))






