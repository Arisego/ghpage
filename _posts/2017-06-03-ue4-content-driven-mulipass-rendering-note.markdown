---
layout: post
status: publish
published: true
title: UE4官方Multipass Rendering笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1765
wordpress_url: http://blog.ch-wind.com/?p=1765
date: '2017-06-03 16:26:07 +0000'
date_gmt: '2017-06-03 08:26:07 +0000'
tags:
- UE4
- RenderTarget
- Rendering
---
这是一篇记录性笔记，可能并没有什么实质性的内容。


看这个视频本质上就是出于一个误会，视频标题是[Content-Driven Mulipass Rendering](https://www.youtube.com/watch?v=QGIKrD7uHu8)，并不是针对某个特效的Step-by-step的教程，而是一些原理上的解释。


故而其中有很多内容都是关于3D渲染的公式和实现的，因此也就不会进行深入的研究。之所以选择UE4这样的引擎来做游戏，就是为了避免过度的接触细节。就像是学习高级语言之后，编译原理什么的粗略了解就可以了。


当然，遇到了非实现不可的特效的时候也没有办法。说实话，不太想和那些Paper呀、公式呀什么的打交道：D


## 材质原理


视频中提到的两个概念很有作用，就是Scatter和Gather


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image001.png)


官方的RT示例中，水波纹扩散就是使用的Gather的方式进行运算的。


这是以前在理解上的一个误区，不能将整个运算目标当作一张贴图来看待，而应该去思考没一个区域（像素）应该处于什么状态。


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image002_thumb.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image002.png)


以及


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image003_thumb.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image003.png)


## 透视光学


视频中有提到水面的折射近似算法，就是所谓的Experience Based Magic Method。


[![clip_image004](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image004_thumb.png "clip_image004")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image004.png)


在光学现象中，还有提到chromatic aberration，也就是色差的实现方式。


色差的基础实现使用RGB Offset，不过演示中使用了spectral photons来进行。但pectral photons究竟是什么却没有搞明白，粗略搜索了一下也不得其门而入。感觉上像是光谱聚合吧，使用光谱这样的线条来进行模拟而不是根据点来进行计算，可以减少运算量。


[![clip_image005](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image005_thumb.png "clip_image005")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image005.png)


另外，色差是什么呢？可以参照维基百科的解释：



> 色差是指光学上透镜无法将各种波长的色光都聚焦在同一点上的现象。它的产生是因为透镜对不同波长的色光有不同的折射率（色散现象）。
> 
> 


对于水面的模拟很有作用，不过实际上，这部分的原理并不是特别的重要，社区有个Ocean的项目对水面、水下的效果模拟都处理的比较好。


## 特效


在视频页面能够找到项目的下载地址，项目中就是在视频里面演示的那些效果。


### FlowMapPainter


基于RenderTarget绘制的FlowMap水面演示


[![clip_image006](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image006_thumb.png "clip_image006")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image006.png)


总体和ContentExample里面的RenderTarget在原理上是差不多的，使用的FlowMap也是材质节点，如果有用到的话可以参考一下。


### FluidSimulation


流体模拟


[![clip_image007](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image007_thumb.png "clip_image007")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image007.png)


基于纳维－斯托克斯方程（Navier-Stokes equations）的流体模拟，这个方程可以参考下维基的解释：



> 纳维－斯托克斯方程（Navier-Stokes equations），以克劳德-路易·纳维（Claude-Louis Navier）和乔治·斯托克斯命名，是一组描述像液体和空气这样的流体物质的方程。这些方程建立了流体的粒子动量的改变率（力）和作用在液体内部的压力的变化和耗散粘滞力（类似于摩擦力）以及重力之间的关系。这些粘滞力产生于分子的相互作用，能告诉我们液体有多粘。这样，纳维-斯托克斯方程描述作用于液体任意给定区域的力的动态平衡。
> 
> 


很复杂……


第一步，Advect，似乎是叫平流计算？不过日式的叫法移流方程式似乎更加的能方便理解，据说原理和上面的FlowMap的差不多。


第二步，计算散度，散度这个东西似乎以前物理中有学过。



> 散度是向量分析中的一个向量算子，将向量空间上的一个向量场（矢量场）对应到一个标量场上。散度描述的是向量场里一个点是汇聚点还是发源点，形象地说，就是这包含这一点的一个微小体元中的向量是“向外”居多还是“向内”居多。举例来说，考虑空间中的静电场，其空间里的电场强度是一个矢量场。正电荷附近，电场线“向外”发射，所以正电荷处的散度为正值，电荷越大，散度越大。负电荷附近，电场线“向内”，所以负电荷处的散度为负值，电荷越大，散度越小。
> 
> 


就是这样的一个感觉。


第三步，计算压力；第四步，计算压力梯度。


这两步都是压力处理，在视频中讲解时似乎被算做了一步：D


每一步都会使用到部分前面计算的结果，全部都是通过RenderTarget进行中继的。


项目中有几个示例，分别是2D空间和3D空间内的流体模拟。


[![clip_image008](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image008_thumb.png "clip_image008")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image008.png)


### HitMaskRender


就是在被命中的地方展示受到伤害的贴图，由于有密集恐惧症，就不贴图了，原理上比上面的都简单，就只是利用RenderTarget来做一个Mask而已。


但是其材质蓝图也是很复杂的，官方这个展示在各个细节方面都很"认真"。不仅仅做了mask，还有做法线上的Mask处理。


不过不知为何有几个地方有莫名的蓝图失连……所以怎么也没法把项目还原到官方视频中的那个效果。还有一个地方就是可能因为视频制作的时间比较靠前，在获取目标点的UV时，没有使用后面有的Trace UV功能，而是制作了一个UnWrap的Material来操作。


### PaintingVoluemTextures


非常酷炫的使用VR进行绘制的云的效果，是VR的……没法测试。


原理上和流体的应该差不多。


### VolumeTextures


就是官方展示的那个3D的UV动画效果，使用了Custom Node，然后里面是有些复杂的Shader……


## 总结


果然做特效是件很复杂是事情，3D图形学实在可怕，还好引擎已经将大部分东西都封装好了，只要不追求酷炫，基本就不太需要关心这些，大概……


