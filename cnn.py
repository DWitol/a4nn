import tensorflow as tf
import numpy as np
import cifar10
#Test this one instead of the stuff i downloaded, might download every time tho which is time consuming 
batch_size = 500
test_size = 10000

def init_weights(shape,name):
    with tf.name_scope(name):
        retVal = tf.Variable(tf.random_normal(shape, stddev=0.01),name="W")
        tf.summary.histogram("weights", retVal)
        return retVal

def model(X, w,w2, w_fc, w_o, p_keep_conv, p_keep_hidden):
    l1a = tf.nn.relu(tf.nn.conv2d(X, w,                       # l1a shape=(?, 28, 28, 32)
                        strides=[1, 1, 1, 1], padding='SAME'))
    tf.summary.histogram("activations",l1a)
    l1 = tf.nn.max_pool(l1a, ksize=[1, 4, 4, 1],              # l1 shape=(?, 14, 14, 32)
                        strides=[1, 2, 2, 1], padding='SAME')
    l1 = tf.nn.dropout(l1, p_keep_conv)

    l2a = tf.nn.relu(tf.nn.conv2d(l1, w2,                       # l1a shape=(?, 28, 28, 32)
                        strides=[1, 1, 1, 1], padding='SAME'))
    l2 = tf.nn.max_pool(l2a, ksize=[1, 4, 4, 1],              # l1 shape=(?, 14, 14, 32)
                        strides=[1, 2, 2, 1], padding='SAME')
    l2 = tf.nn.dropout(l2, p_keep_conv)



    l3 = tf.reshape(l2, [-1, w_fc.get_shape().as_list()[0]])    # reshape to (?, 14x14x32)
    l3 = tf.nn.dropout(l3, p_keep_conv)

    l4 = tf.nn.relu(tf.matmul(l3, w_fc))
    l4 = tf.nn.dropout(l4, p_keep_hidden)

    pyx = tf.matmul(l4, w_o)
    print("got here")
    return pyx

cifar10.maybe_download_and_extract()
classNames = cifar10.load_class_names()
#trainingData = cifar10.load_training_data()
images_train, cls_train, labels_train = cifar10.load_training_data()
#testData = cifar10.load_test_data()
images_test, cls_test, labels_test = cifar10.load_test_data()
#print(trainingData[0][1][0])
print("Size of:")
print("- Training-set:\t\t{}".format(len(images_train)))
print("- Test-set:\t\t{}".format(len(images_test)))
print("- Test-set:\t\t{}".format(len(cls_train)))
#trX, trY, teX, teY = trainingData, classNames, testData, classNames
trX, trY, teX, teY = images_train, labels_train, images_test, labels_test
trX = trX.reshape(-1, 32, 32, 3)  # 32x32x1 input img
teX = teX.reshape(-1, 32, 32, 3)  # 32x32x1 input img

X = tf.placeholder("float", [None, 32, 32, 3],name = "x")
Y = tf.placeholder("float", [None, 10],name ="labels")

w = init_weights([3, 3, 3, 64],"w")       # 3x3x1 conv, 32 outputs
w2 = init_weights([3, 3, 64, 128],"w2") 
w_fc = init_weights([128 * 8 * 8, 625],"w_fc") # FC 32 * 14 * 14 inputs, 625 outputs
w_o = init_weights([625, 10],"w_o")         # FC 625 inputs, 10 outputs (labels)

p_keep_conv = tf.placeholder("float")
p_keep_hidden = tf.placeholder("float")
py_x = model(X, w,w2, w_fc, w_o, p_keep_conv, p_keep_hidden)
#InvalidArgumentError (see above for traceback): logits and labels must be same size: logits_size=[128,10] labels_size=[80,10]
with tf.name_scope("cost"):
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y))

with tf.name_scope("train"):
    train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)

with tf.name_scope("accuracy"):
    predict_op = tf.argmax(py_x, 1)


# tf.summary.scalar('cost',cost)
# #tf.summary.scalar('accuracy',predict_op)
# tf.summary.image('test input',images_test,3)
# tf.summary.image('train input',images_train,3)

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.global_variables_initializer().run()
    merged_summary = tf.summary.merge_all()
    writer = tf.summary.FileWriter("results/cifar10/2")
    writer.add_graph(sess.graph)


    for i in range(15):
        training_batch = zip(range(0, len(trX), batch_size),
                             range(batch_size, len(trX)+1, batch_size))
        for start, end in training_batch:
            if end < 50001:
                sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end],
                                      p_keep_conv: 0.8, p_keep_hidden: 0.5})
                
        test_indices = np.arange(10000) # Get A Test Batch
        np.random.shuffle(test_indices)
        test_indices = test_indices[0:test_size]
                
        print(i, np.mean(np.argmax(teY[test_indices], axis=1) ==
                         sess.run(predict_op, feed_dict={X: teX[test_indices],
                                                         p_keep_conv: 1.0,
                                                         p_keep_hidden: 1.0})))

        s = sess.run(merged_summary, feed_dict={X: trX[test_indices],Y: teY[test_indices],
                                  p_keep_conv: 1.0, p_keep_hidden: 1.0})
        #writer.add_summary(s,i)

        print("completed run ", i )
       
