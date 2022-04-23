---
layout: post
status: publish
published: true
title: UE4.16新动画与物理功能
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1738
wordpress_url: http://blog.ch-wind.com/?p=1738
date: '2017-05-21 23:51:45 +0000'
date_gmt: '2017-05-21 15:51:45 +0000'
tags:
- UE4
- nvcloth
- Animation
---
4.16的Preview更新已经发布有一段时间了，与以往一样，这次的版本更新也带来了很多新的功能与改变。


本文主要参照官方的功能[[演示文稿](https://www.slideshare.net/EpicGamesJapan/unreal-engine-75203047)]进行整理完成。


## 基于Rig的动画编辑


Rig是一种很方便的驱动骨骼动画的方式，本次的更新中添加了新的Rig动画编辑功能。


这个功能使得在编辑器中对Rig动画进行编辑变得可能，让我们进行更方便对动画调整和原型设计。


要想开启Rig动画编辑功能，首先要开启Control Rig插件：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-14.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-14.png)


启用插件之后就可以在编辑器中看到这个模块到功能了：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-15.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-15.png)


中这个选项卡中新建一个Rig Sequence，然后拖一个骨骼Mesh进来当作目标，就可以在Sequence到编辑器中进行动画到编辑了：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-16.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-16.png)


编辑过程比较直观，也可以在IK与FK模式中进行切换，完成的动画可以导出成动画序列，在这个编辑器中也可以进行Retarget操作。


要导出动画，在Content Manager中找到Control Rig Sequence并点击右键，就可以看到相关到选项


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-17.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-17.png)


然后就可以进行选择设置了


[![SNAGHTML6685395](https://blog.ch-wind.com/wp-content/uploads/2017/05/SNAGHTML6685395_thumb.png "SNAGHTML6685395")](https://blog.ch-wind.com/wp-content/uploads/2017/05/SNAGHTML6685395.png)


但是似乎没有看到从动画序列转换到Rig Sequence到方法。


Rig相关功能在4.16之后似乎还会增强，使得动画蓝图可以对Rig进行控制以及生成。


## Live Link


很强大的功能，使得UE4与其他的3D编辑器可以实时的联动编辑。这样就能更加直观的看到需要做的内容做UE4中是如何工作的。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-18.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-18.png)


看起来非常的实用


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-19.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-19.png)


不过这个似乎要到4.17才会进入试验阶段……


## Immediate Mode


之前的Physx是使用所谓保留模式（Retained Mode）工作的，Retained Mode有不少优点，方便实用。但是也有很多缺点，例如中对物体对Deactive逻辑处理时有不少效率上的问题、对物体进行遍历并不方便、很难对特定对物体组进行模拟成本计算等。


而Immediate Mode通过暴露出更多等底层操作接口，使得引擎能够更有效的对物理引擎进行控制和契合，同时也能大幅度的提升LOD以及Culing机制下的物理效率。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-20.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-20.png)


这个功能目前的一个主要应用是运动角色模型上的小的物体，这是一个在动画蓝图中的新节点：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-21.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-21.png)


它使得在动画蓝图中进行物理资源的模拟变得可能，这种方式比AnimDynamic的方式更方便进行操作，也具有更高的效率。


## NvCloth


4.16开始UE4中开始使用NVIDIA的新的Cloth框架：NvCloth，它能直接在引擎中进行材质制作，大大的减少了以前必须使用Apex外部制作工具带来的很多麻烦。


同时NvCloth也获得了Immediate Mode的优势，使得Cloth的仿真效能得到增强。NvCloth也应用了新的空气阻力模型


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-22.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-22.png)


要使用NvCloth首先需要中试验性功能中打开这个功能：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-23.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-23.png)


然后就可以在骨骼Mesh的编辑器中选中区域选择：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-24.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-24.png)


这之后选择相应的区域就可以对其进行Cloth绘制了：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-25.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-25.png)


添加后就能看到新的区域了


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-26.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-26.png)


不过这里暂时没什么用，最主要的还是绘制的过程：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-27.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-27.png)


在窗口中能看到ClothPaint，打开之后进行权重绘制即可。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-28.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-28.png)


因为手头没有模型，无法进行绘制测试，看官方的演示的话，NvCloth无论是从效果上还是效率上都比原来的Apex路径强很多。


## 其他


在最近的引擎更新中有很多Robo Recall相关的功能实现被合并到了引擎中。


其中前向渲染的添加、运动物体上的CCD、pose snapshot、Constraint profile以及用于模拟移动有一定重量物体的Spring Lerp等已经在之前的版本中添加到了引擎中。


另外似乎有新的粒子系统在制作中，很期待接下来的版本更新。


