---
layout: post
status: publish
published: true
title: UE4渲染目标使用
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1615
wordpress_url: http://blog.ch-wind.com/?p=1615
date: '2017-04-23 22:26:42 +0000'
date_gmt: '2017-04-23 14:26:42 +0000'
tags:
- UE4
- RenderTarget
---
UE4的Render Target提供了渲染缓存功能，可以制作很多有趣的特效。


当前UE4版本4.15.1。


Render Target作为一种动态生成内容的方法，为材质系统提供了更加精细的控制。引擎本身提供的Scene Capture功能也是可输出到Render Target并连接到材质上作为摄像展示功能的。通过Render Target也能实现类似神秘海域里面的擦拭物体表面灰层的功能。


本文参照[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/RenderTargets/BlueprintRenderTargets/Overview/index.html)]进行完成，由于官方文档的介绍并不详细，所以在这里记录下自己的经验和理解。


## 高度场绘制器


高度场绘制器是通过将玩家操作反映到Render Target，然后传入材质来提升World Position来实现的，是一个非常简单的示例，基本按照官方的指引操作即可。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-5.png)


### MAT_HeighfieldPainter


这个材质是最终应用到物体上的材质,Heightfield参数是Render Target的传入路径。可以看到，传入的高度场被拼接为(0,0,Z)的Vector输出到了World Position上，这就会导致被应用了材质的物体的对应位置向上偏移，同时传入的Render Target也到达了自发光颜色，使得升起的部分有了白色的效果。


### MAT_ForceSplat


这个材质是用来绘制Render Target的，直观的讲，就是在指定的点生成一个由内向外的Gradient一样的效果，作用到高度场上就是上图中那样的锥形效果。材质在实现上，首先根据传入的Force Position，mask之后，让其与UV相减，之后再求取向量长度的话，那么自然就会成为一个由那个点向外扩散的圆了：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-6.png)


这里要注意的是，UV在材质中是以左上角为(0,0)的，在材质蓝图中分别展示为R和G两个通道，但是负数全是黑色的。求出向量长度之后的操作就比较单纯了，通过减法和取整就可以得到目标的“圆点”了。


### 蓝图


蓝图的设置上比较方便，因为官方有提供在网页上复制蓝图脚步的功能，只要拷贝过去就可以了。基本上的功能也非常的直观。


在ConstructionScript中构建并指定材质，由于这里的功能比较简单，RenderTarget时在这里直接构建的；


在BeginPlay时打开Input交互，同时将RenderTarget设置给动态材质；


鼠标按下时标记MouseDown，此时Tick事件就会开始进行Trace操作；


整个蓝图的核心就是通过这个Trace给物体施加Damage事件，并在Damage处理中对进行RenderTarget的绘制。


### 绘制点的获取


需要注意的是，官方在获取绘制点的时候使用了一个简便的方法，这点官方也有给出注释说明。如果想要在所有的Mesh上都实现类似的效果，而不只是在例子中才能使用的话，需要使用Trace时获得的UV来进行计算。


而这个功能是4.13才有的新功能，要使用的话必须在项目设置>引擎>Physics中打开：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-7.png)


使用时要注意勾选Trace Complex才行。


## 流体表面


其实就是一个水波纹的效果，会在用户点击和玩家碰撞的地方产生扩散衰减的水波纹效果。是比高度图稍微复杂一些的效果，也是非常实用的效果。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-10.png)


由于需要的效果比较复杂，所以用到了三个缓存用Render Target以及一个绘制法线贴图的Render Target。


而相对的，绘制用材质ForceSplat可以采用高度场里面用到的材质，是一样的。


### WaterMaterial


这个材质是应用于“水面”的材质，其本身的材质很简单，和通常的水面材质不同的是，将输入的Texture应用到了世界位置便宜与法线上。


其中Heightfield的应用方式与高度场的材质应用是相同的。


### HeightSim


这个是计算水面波纹的核心材质，原理上，首先将PreviousHeight1分别朝四个方向进行TexelSize单位的移动，然后相互叠加后与原有的图形进行相减，就能得到一个向外扩散的外沿了。之后再减去可以算作完全消退的PreviousHeight2作进一步的修正，就是当前的Height了。


### ComputeNormal


根据当前的绘制水面的高度图计算出法线贴图，使用的数学原理与HeightSim类似。


### 蓝图


蓝图实现上的整体逻辑和高度场示例中差不多，复杂之处在于使用tick函数来计算和更新了水波。其中最大的核心在这里：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-8.png)


每次计算的时候通过交换3个Render Target，分别作为Current，Prev1， Prev2来进行水波扩散的更新模拟计算，而法线的运算反而简单，只是在“绘制”执行的时候对“当前”水波进行法线计算而已。


## 小心有坑


官方亲切的提供了在网页中复杂蓝图节点的功能，但是要注意的是，当前版本中有一个BUG，材质蓝图中的所有参数名被多次使用时复制后会被自动重命名，并且这个过程是没有提示的，最后材质中就会变成这样：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-9.png)


此时材质参数无法正常传递，就会出现奇怪的特效。


## 源码


由于官方当前在文档中并没有提供一些必要的Mesh等资源，需要从Content Example中复制，为了方便大家研究，已经将完成的版本上传到了[[GitHub](https://github.com/steinkrausls/Rtg_Test)]上，欢迎取用。


