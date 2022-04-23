---
layout: post
status: publish
published: true
title: 从零开始的TensorFlow学习（一）
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2274
wordpress_url: https://blog.ch-wind.com/?p=2274
date: '2018-02-25 23:25:25 +0000'
date_gmt: '2018-02-25 15:25:25 +0000'
tags:
- TensorFlow
---
人工智能现在如火如荼，感觉上再过不久就会变成不可或缺的工具，因此便开始打算重新接触一下。


当前使用的环境为Python 3.6.4；TensorFlow版本1.5.0。


其实一开始对于机器学习这个东西，我是拒绝的。因为感觉上，它放弃了对原理的了解。就像是我们只知道大脑内神经元的连接却不知道它是如何构成思维一样，我们其实并不确切的知道训练完成后的神经网络是如何完成计算处理的。


但是最近出的DeepFake改变了我的看法，既然通过深度学习可以代替我们完成很多以前需要直觉才能完成的事情。那么本着实用主义的原则，应当也能做出很多有趣的东西。


虽然之前读研时看过很多相关的Paper，但是已经忘得差不多了，因此这里从官方教程[[Getting Started for ML Beginners](https://www.tensorflow.org/get_started/get_started_for_beginners)]开始，毕竟世上没有比一知半解更危险的事情了。


## Iris flowers classification


这个是一个比较经典的问题，大概由于是面向初学者的教程，所以使用了比较简单的问题。


要解决的目标问题是鸢尾花分类，通过花萼的长宽以及花瓣的长宽等四个属性来判断。


数据的来源是[[安德森鸢尾花卉数据集](https://zh.wikipedia.org/wiki/%E5%AE%89%E5%BE%B7%E6%A3%AE%E9%B8%A2%E5%B0%BE%E8%8A%B1%E5%8D%89%E6%95%B0%E6%8D%AE%E9%9B%86)]，原数据共150个，在这里被分为120个训练数据和30个测试数据。


### 数据载入


为了对机器学习的效果进行评估，通常已知的数据会被分为训练数据和测试数据两部分。


因为如果一味的使用数据进行训练的话，往往会导致过度拟合的问题。


数据载入部分的代码都在iris_data.py中。


load_data是数据载入的入口，首先会调用maybe_download尝试对远端数据进行下载。


如果数据已存在的情况下就不会下载，由于某些情况一直下不来的话可以尝试架设梯子或者从其他地方下载这些数据。


下载后有两个文件，iris_training.csv和iris_test.csv，默认情况下应当是保存在C:\Users\Administrator\.keras\datasets目录中。


两个文件格式相同，如下


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/02/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/02/image-2.png)


第一行是指示性的数据，分别代表数据的行数、列数，而后面的分别为鸢尾花的类型名称，对应最后一列的[0,2]的数据。


不过这行数据并不会使用到，只是方便阅读。


load_data中会使用panda库对数据进行载入，分割成数据和属性两个部分之后



```
--- test_x ---
SepalLength  SepalWidth  PetalLength  PetalWidth
0           5.9         3.0          4.2         1.5
1           6.9         3.1          5.4         2.1
2           5.1         3.3          1.7         0.5
3           6.0         3.4          4.5         1.6
4           5.5         2.5          4.0         1.3
5           6.2         2.9          4.3         1.3
6           5.5         4.2          1.4         0.2
7           6.3         2.8          5.1         1.5
8           5.6         3.0          4.1         1.3
9           6.7         2.5          5.8         1.8
10          7.1         3.0          5.9         2.1
11          4.3         3.0          1.1         0.1
12          5.6         2.8          4.9         2.0
13          5.5         2.3          4.0         1.3
14          6.0         2.2          4.0         1.0
15          5.1         3.5          1.4         0.2
16          5.7         2.6          3.5         1.0
17          4.8         3.4          1.9         0.2
18          5.1         3.4          1.5         0.2
19          5.7         2.5          5.0         2.0
20          5.4         3.4          1.7         0.2
21          5.6         3.0          4.5         1.5
22          6.3         2.9          5.6         1.8
23          6.3         2.5          4.9         1.5
24          5.8         2.7          3.9         1.2
25          6.1         3.0          4.6         1.4
26          5.2         4.1          1.5         0.1
27          6.7         3.1          4.7         1.5
28          6.7         3.3          5.7         2.5
29          6.4         2.9          4.3         1.3
--- test_y ---
0     1
1     2
2     0
3     1
4     1
5     1
6     0
7     2
8     1
9     2
10    2
11    0
12    2
13    1
14    1
15    0
16    1
17    0
18    0
19    2
20    0
21    1
22    2
23    1
24    1
25    1
26    0
27    1
28    2
29    1
Name: Species, dtype: int64
```

会以这样的形式返回给main函数。


### Feature Column


Feature column是原始数据与TensorFlow之间的中介，通过指定Feature column才能将数据转化为tf可以理解的形式。


示例中通过对train_x的key进行读取，生成了Feature Column，具体的内容如下



```
[
_NumericColumn(key='SepalLength', shape=(1,), default_value=None, dtype=tf.float32, normalizer_fn=None),
_NumericColumn(key='SepalWidth', shape=(1,), default_value=None, dtype=tf.float32, normalizer_fn=None),
_NumericColumn(key='PetalLength', shape=(1,), default_value=None, dtype=tf.float32, normalizer_fn=None),
_NumericColumn(key='PetalWidth', shape=(1,), default_value=None, dtype=tf.float32, normalizer_fn=None)
]
```

根据文档，针对更加复杂的原始数据会有更加复杂的Feature Column生成和类型，这里由于原本就是float的所以无需转换。


### Estimator


Tensorflow将一些预定义的模型封装成了Estimator，方便用户使用，也可以对Estimator进行进一步的定制来符合自己的使用需求。


示例中使用的是tf.estimator.DNNClassifier，应当是Deep Neural Network Classifier的简称，总之就是通常印象中的神经网络。


#### 定义


在有了上面的步骤，定义和使用Estimator相当简洁：



```
classifier = tf.estimator.DNNClassifier(
feature_columns=my_feature_columns,
hidden_units=[10, 10],
n_classes=3)
```

使用的DNN共有两个隐藏层，每层10个节点，目标的类型数目为3。


#### 训练和评估


这两个过程也很简洁，直接使用iris_data中的两个函数来生成Dataset并传回给调用。


最重要的函数是tf.data.Dataset.from_tensor_slices，将test_x和test_y分别作为feature和label组成DataSet。


在train的时候还有一个batch的概念，是针对训练时的iteration的，一次iteration会使用一个batch的数据，一次iteration之后权重会进行一次更新。


#### 预测


预测使用classifier.predict，能够输出概率性的结果，使用的数据是事先给定的。



```
Prediction is "Setosa" (99.6%), expected "Setosa"
Prediction is "Versicolor" (99.4%), expected "Versicolor"
Prediction is "Virginica" (99.0%), expected "Virginica"
```

运行的最后会看到输出结果。


### 杂项


运行时遇到了这样的输出：



```
Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX AVX2
```

虽然没什么影响，但是如果想去掉的话，可以在代码中加上



```
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

另外，Tensorflow的很多log是由



```
tf.logging.set_verbosity(tf.logging.INFO)
```

造成的，如果不想看到的话删掉这句话就好了。


## 总结


总体来看，TensorFlow的封装做的很好，教程也相当的简明，感觉基本上顺着官方的教程学就可以了。


