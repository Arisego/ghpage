---
layout: post
status: publish
published: true
title: UE4粒子系统官方教程总结
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1379
wordpress_url: http://blog.ch-wind.com/?p=1379
date: '2015-07-06 15:37:27 +0000'
date_gmt: '2015-07-06 07:37:27 +0000'
tags:
- UE4
- 粒子
- GPU Sprites
- Vector Field
---
Epic官方提供的粒子特效教程涵盖的范围比较广，操作上也是由浅入深，对于帮助了解粒子系统很有作用。


当前UE4版本：4.8.1。


粒子系统这一块，虽然之前将文档大概读了一遍，但是有些概念依然比较抽象，故而按照官方教程操作了一遍。


原始教程地址：[https://wiki.unrealengine.com/Visual_Effects:_Lesson_01:_Material_Particle_Color](https://wiki.unrealengine.com/Visual_Effects:_Lesson_01:_Material_Particle_Color "https://wiki.unrealengine.com/Visual_Effects:_Lesson_01:_Material_Particle_Color")。


## 基础材质


粒子系统除了在Mesh Data Type被指定时使用的是Mesh之外，在一般情况下都会使用材质作为发射器的基本粒子。


### 材质构建


教程中使用的材质是Blend Mode为Translucent而Lighting Model为Unlit的，通常情况下粒子上的光照效果并不明显，使用Unlit可以有效的降低系统负担。


教程中使用的十字图片一时找不到原图，因而直接使用默认粒子系统的那张贴图作为制作基础。


基础材质的制作较为简单，基本就是将材质的颜色和alpha通道分别连接到自发光颜色和不透明度上。材质制作完成后，在发射器的Required模块将材质替换为刚刚建立的材质即可。


材质中使用的Particle Color参数可以使用Color Over Life进行控制，操作相对简单，没有什么特别需要注意的地方。


### Depth Fade


使得粒子在与其他物体交集时边界不是那么的尖锐，而是在有交错时减少粒子的透明度。


功能实现很简单，在材质的不透明读输入之前连接上Depth Fade节点即可。


### Near Camera Fade


粒子在摄像机靠近时逐渐变得透明进而消失，在游戏中比较经常用到。这一类的效果基本使用这种方法进行实现。


在材质中使用节点PixelDepth配合Sphere Mask。Shpere Mask用于计算距离并生成遮罩，圆心处为1，Distance处为0，根据Hardness生成过渡效果。因而，要连接到不透明度效果上的话要先进行一减操作。


将生成的不透明度与原有的不透明度相乘即可实现Near Camera Fade的效果。教程中Sphere Mask的参数为Radius:75，Hardness:10。


### Materia Function


材质函数用于将经常用到的材质特效独立出来，便于操作、管理和统一修改，也被用于Layered Materia的制作之中。是材质系统中比较重要的一个功能。


在这里实现的是对Near Camera Fade的材质函数化，因为大部分场景中的粒子都有可能会需要这个功能。可以通过增进Function Input节点来为函数提供参数输入引脚，在函数属性中选中Expose to Library就可以在材质视图的上下文菜单中直接找到这个函数了。如果选择不暴露的话，每次都必须将这个函数拖到材质中去。


### Dynamic Parameter


材质中的Dynamic Parameter节点允许粒子对材质进行动态的参数输入，需要注意的是当使用GPU粒子时，这个传入是无效的。


要给材质传入参数，需要使用Parameter->Dynamic模块进行相关操作。在对动态参数的名称进行修改之后，对Dynamic模块进行刷新就可以看到参数名称的更新。


对于一次性设定的参数，要在Dynamic模块中为参数设置Spawn Time Only，这样就只在粒子生成时进行参数生成和设置。


### 颜色控制


教程中建议删除默认的Color Over Life模块，改为使用Initial Color和Scale Color/Life两个模块进行组合配置。


主要的好处在于，可以解除生成时颜色和生命周期颜色之间的关联。方便进行控制。


总体上操作没有什么太大的不同，其实如果没有对粒子颜色进行控制的话，可以不用进行这个操作。


## GPU Particle


GPU粒子的效率比CPU粒子高，虽然有一些地方的功能有所限制，但按照官方建议，在大多数情况下都应该使用GPU粒子。


GPU粒子在生成粒子时依然使用CPU进行，以便对粒子进行更好的控制。因此，在GPU粒子制作时，应该将CPU生成粒子的消耗考虑在内。否则极有可能成为系统的瓶颈。教程建议单次粒子爆发不要超过15k个，在通过爆发生成大量粒子时，其间隔应该在0.05~0.1以上。同时在有大量粒子生成的情况下，最好使用LOD来尽可能的降低整体的系统消耗。


当粒子系统中的粒子数量超过某个点之后，其对整体视觉效果的贡献并不明显。因此在粒子系统制作中应该对参数进行调整，将粒子个数控制在平衡点附近。可以通过将显示模式调整为**着色器复杂度**来观察粒子个数是否过多。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb13.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image13.png)


在这个模式中，显示为白色的区域代表其成本极高。应该对其进行调整。


### Vector Field


矢量场用于控制粒子的流向，效果上就像是场景中有风带动粒子移动一样。矢量场可以通过模块进行旋转和缩放，能够实现非常独特和真实的效果。


Vector Field模块只有在类型为GPU Sprites时才有效。矢量场分为Local Vector Field和Global Vector Field两种，分别作用在粒子系统的本地空间和实际场景中。


矢量场的制作已经完全进入了美工的领域，不再进行研究。官方的制作教程在这里：[https://wiki.unrealengine.com/Creating_Vector_Fields_(Tutorial)](https://wiki.unrealengine.com/Creating_Vector_Fields_(Tutorial "https://wiki.unrealengine.com/Creating_Vector_Fields_(Tutorial)")。


### 动态参数


GPU粒子不能进行动态参数传值，Dynamic模块将会失效。为了让粒子对参数进行一定程度的控制，教程中介绍了一个变通的方法。


那就是使用依然有效的Particle Color进行数值传递，虽然这样会导致无法对粒子的颜色进行控制，但是在没有办法进行粒子传递时还是需要这样一个替代方案的。


### 粒子碰撞


Collision(Scene Depth)模块用于为粒子添加碰撞功能，这个模块当前只在GPU粒子下有效。同时，这个功能必须使用Translucent的材质作为粒子的时候才会起作用。


可调节参数包括反弹系数、摩擦力、反应模式等。


------------------------


UE4的粒子功能很强大，提供很多用于修改的模块。感觉上作为程序的话，只要了解大概有什么功能，能够实现简单的粒子特效即可。实在有需要制作复杂的粒子时，可以参考别人做好的进行修改。


