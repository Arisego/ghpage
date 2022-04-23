---
layout: post
status: publish
published: true
title: Subspace neural physics笔记
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 2932
wordpress_url: https://blog.ch-wind.com/?p=2932
date: '2020-09-13 12:07:52 +0000'
date_gmt: '2020-09-13 04:07:52 +0000'
tags:
- physics
---

去年GDC看到育碧的基于神经网络的物理交互模拟，终于找到时间仔细的看了下。



  

  





这边只是记录一些笔记，原始的分享其实就说明的很详细了。




效果演示：<https://www.youtube.com/watch?v=yjEvV86byxg>




论文：[Subspace Neural Physics](http://theorangeduck.com/page/subspace-neural-physics-fast-data-driven-interactive-simulation)




## 物理模拟




首先是对现有的物理模拟方式的总结，并不是介绍引擎，而是更多的在学术方面进行描述。




### Position based dynamic




这个是在商业引擎的布料模拟中已经使用到的模拟方式，基于位置的模拟方式可以更高效的进行碰撞解算也能很有效的避免穿插。详细的内容可以参考这篇论文：[Position based dynamic](https://matthias-research.github.io/pages/publications/posBasedDyn.pdf)。




### Subspace simulation




子空间模拟的思路很简单，就是将物体的碰撞形态简化来提高模拟的效率。虽然听起来和UE4中的simple collision很相似，但是这里其实是更加直白的使用方式。只是对大的物体进行子空间的划分，不会将起简化为基础碰撞形态。




### Data-Driven Simulation




这个方法比较直白，就是将事先模拟的结果存储起来。然后在运行时根据外部变量直接取出模拟结果。




## 神经网络




论文中使用的方法，是将Data-Driven和Subspace结合的一种思路。在数据上，首先对模拟对象进行Subspace划分，然后将数据“存储”在神经网络中。




### 数据生产




使用的训练数据全部是使用Maya的nCloth进行模拟导出的，这里直接引用原文中的训练数据：







| Scene | Material | Verts | Frames | FPS | Time |
| --- | --- | --- | --- | --- | --- |
| Ball&Sheet | T-Shirt | 2601 | 1,000,000 | 7.6 | 36h |
| Four Pins | T-Shirt | 2601 | 1,000,000 | 15.5 | 18h |
| Flag | T-Shirt | 2601 | 1,000,000 | 10.9 | 25h |
| Skirt | Denim | 3000 | 650,000 | 3.1 | 60h |
| Cape | T-Shirt | 2601 | 650,000 | 1.9 | 95h |
| Bunny | Rubber | 2503 | 200,000 | 0.4 | 129h |
| Dragon | Rubber | 3000 | 500,000 | 1.0 | 138h |





后文也有提到，这个方法的缺点之一，就是需要大量的生产训练数据。




### 训练模型




总体思路上，认为当前的物理状态可以由前两帧的状态计算出来。详细的模型可以参考论文，训练使用的是feed-forwad neural network。




训练中预测的是到下一帧需要的每个点需要的步进量。为了防止过度拟合，训练时对一个区间的帧进行预测和评估，而关于模型中的参数A和B，在文章的末尾有提到获取的方式。由于这个是决定在没有外力的情况下从一帧到下一帧的演变的，所以对整体的训练数据做一个帧之间的计算，并对结果进行线性最小二乘拟合就得到两这个参数。




在显示上，其实还使用了Vertex Normal Prediction的过程来对法线进行计算。同时为了防止在显示层面的穿模，对Shader进行了一些特殊处理。




## 额外名词




### PCA




文中只是简短的说使用PCA对模型进行子空间的划分。由于不是很了解这个，稍微查了下，PCA就是主成分分析，详细的可以在维基百科[Principal component analysis](https://en.wikipedia.org/wiki/Principal_component_analysis)看到。




### Ablation Study




由于之前没接触过神经网络，这个是第一次看到。其实是源于生物学的一种处理方式，就是将系统的一部分进行移除来观察系统会如何运作。以验证某个部分在系统中发挥的是什么样的作用。




### Verlet intergration




文中最后通过推导，表明模型的公式就是[Verlet intergration](https://en.wikipedia.org/wiki/Verlet_integration)的一种表示，这个是韦尔莱积分法：





```
韦尔莱算法是一种用于求解牛顿运动方程的数值方法，被广泛应用于分子动力学模拟以及视频游戏中。韦尔莱算法的优点在于：数值稳定性比简单的欧拉方法高很多，并保持了物理系统中的时间可逆性与相空间体积元体积守恒的性质。
```



## 总结




从演示的效果来看，这种布料模拟方式还是有一定的实践作用的。尤其是对于人物的布料模拟，只是目前还没有成熟的流程。尤其是在训练数据生产这方面还是有些让人望而却步。




由于应用场景有些特化，不知以后会不会有进一步的优化和商业产品。



