import pandas as pd
import numpy as np
import random
import math
import tensorflow as tf
import json

import os

num_periods = 2500
f_horizon = 200


class rnnModel():
    def __init__(self):

        tf.reset_default_graph()
        self.inputs = 1
        self.hidden = 100
        output = 1

        self.X = tf.placeholder(tf.float32, [None, num_periods, self.inputs])
        self.y = tf.placeholder(tf.float32, [None, num_periods, output])

        basic_cell = tf.keras.layers.SimpleRNNCell(units=self.hidden, activation=tf.nn.relu)

        rnn_output, states = tf.nn.dynamic_rnn(basic_cell, self.X, dtype=tf.float32)

        learning_rate = 0.001

        stacked_rnn_output = tf.reshape(rnn_output, [-1, self.hidden])
        stacked_outputs = tf.layers.dense(stacked_rnn_output, output)

        self.outputs = tf.reshape(stacked_outputs, [-1, num_periods, output])


        self.loss = tf.reduce_sum(tf.square(self.outputs - self.y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        self.training_op = self.optimizer.minimize(self.loss)

        self.init = tf.global_variables_initializer()

model = rnnModel()



def load_car_data():
    #files = [str(x) for x in os.listdir("csv") if x.endswith("csv")]
    files = ['0_agent.csv']
    data = []
    for file in files:
        data += list(pd.read_csv("csv/" + file, sep=";")["capacity"])

    TS = np.array(data)

    x_data = TS[0:len(TS) - (len(TS) % num_periods)]
    x_batches = x_data.reshape(-1, num_periods, 1)

    y_data = TS[f_horizon:(len(TS) - (len(TS) % num_periods)) + f_horizon]
    y_batches = y_data.reshape(-1, num_periods, 1)

    return TS, x_data, x_batches, y_data, y_batches


def test_data(TS,forecast):
    test_x_setup = TS[-(num_periods+forecast):]
    testX = test_x_setup[:num_periods].reshape(-1,num_periods,1)
    testY = TS[-(num_periods):].reshape(-1,num_periods,1)
    return testX, testY

def create_training_data():
    TS, x_data, x_batches, y_data, y_batches = load_car_data()
    X_test, Y_test = test_data(TS, f_horizon)

    return TS, x_data, x_batches, y_data, y_batches, X_test, Y_test

def apply_model(test_data,model_path="model/predictor.ckpt"):

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, model_path)
        y_pred = sess.run(model.outputs, feed_dict={model.X: test_data})



    return y_pred


def train_model(output_path="model"):

    TS, x_data, x_batches, y_data, y_batches, X_test, Y_test = create_training_data()

    epochs = 1000
    mse_dic = {"MSE": {}}
    saver = tf.train.Saver()

    with tf.Session() as sess:
        model.init.run()
        for ep in range(epochs):
            sess.run(model.training_op, feed_dict={model.X: x_batches, model.y: y_batches})
            if ep % 100 == 0:
                mse = model.loss.eval(feed_dict={model.X: x_batches, model.y: y_batches})
                print(ep, "\tMSE:", mse)
                mse_dic["MSE"][ep] = mse

        y_pred = sess.run(model.outputs, feed_dict={model.X: X_test})

        import os

        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        save_path = saver.save(sess, "{}/predictor.ckpt".format(output_path))

        print("Model saved in path: %s" % save_path)

        return y_pred

