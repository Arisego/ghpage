---
layout: post
status: publish
published: true
title: UE4中Paper2D初探
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1486
wordpress_url: http://blog.ch-wind.com/?p=1486
date: '2015-09-17 20:42:51 +0000'
date_gmt: '2015-09-17 12:42:51 +0000'
tags:
- UE4
- Paper2d
---
Paper 2D是UE4提供的基于精灵的2D系统，可以用于构建2D和2D/3D混合游戏。


当前UE4版本4.10.2；


部分内容参考的[[官方文档](https://www.google.com.hk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwj7yprKvc7SAhVFlJQKHfgCA1AQFggaMAA&url=%68%74%74%70%73%3a%2f%2f%64%6f%63%73%2e%75%6e%72%65%61%6c%65%6e%67%69%6e%65%2e%63%6f%6d%2f%6c%61%74%65%73%74%2f%43%48%4e%2f%45%6e%67%69%6e%65%2f%50%61%70%65%72%32%44%2f&usg=AFQjCNG1WlLQvG_q8TSg44GLR4WEJ0ATdA)]版本标识为UE4.9。目前Paper 2D的动画系统是基于帧动画的，社区讨论中虽然有加入2D骨骼动画系统的讨论，但是目前的正式引擎版本中并没有这样的功能。


## Sprite


Sprite是帧动画的基本单位，它来源于对Texture的裁剪，形成动画的一个帧并最终用于FlipBook中。  

Sprite可以从Texture创建也可以创建之后指定Texture，同时UE4支持导入从Texture Packer和Adobe Flash CS6生成的帧动画。


### 属性


Sprite的属性相对比较简单：


**Source Texture**


当前精灵所使用的2D图像


**Source UV**


裁剪的起始点在原图形上的偏离，像素单位


**Source Dimension**


裁剪的大小，像素单位


**Default Material**


精灵的默认材质，系统提供的为Unlit Masked的材质，这个材质可以在Flipbook中进行覆盖设置。


**Pixels per unit**


设置像素与引擎内部单位之间的缩放比例，用于调整精灵在UE世界中的大小。在Paper2D的插件设置中有全局设定，也可以对每个精灵进行指定。


**Pivot Mode**


中心点位置。设置为Custom的话可以进行精细的设置。


**Sockets**


和3D动画中的Sockets功能时类似的，提供一个接口。


**Sprite Collision Domain**


精灵碰撞模式，可以选择无碰撞、2D或者3D。


属性中有些详细的可以在使用的时候进行调整测试。


有一个属性为Additional Textures，从引擎的描述上看是用于为精灵提供额外的贴图的，当前文档中没有给出描述。要使用的话似乎需要对默认材质进行修改，有使用需求的可以参考[这里]的讨论。


精灵的材质可以进行很多的调整和自定义，从Flipbook过来的Sprite Color属性在材质中是Vertext Color的输入项。


### 碰撞检测


整个Paper2D中可以选择的碰撞方式为2D和3D两种，3D碰撞使用的引擎内通用的PhysX，而2D碰撞使用的是Box2D。当前Box2D仍然处于实验阶段，有一些功能是不完整的，文档支持也不够完整。Box2D的支持也只能到Win32和Win64两个平台，要使用额外的功能还要在项目设置中打开bEnable2DPhysics开关。总体而言，目前不是很适合使用。


同时，在Sprite的编辑器中可以选择对碰撞形态进行调整，除了引擎提供的几种模式之外，可以自行指定。


各个碰撞模式的不同可以看官方的[图例]，相当的直观。


使用上的建议是使用默认的简单图形进行碰撞，如果需要使用精细的碰撞的话可以使用Sockets来外挂碰撞体来进行碰撞检测，逐帧进行精细的碰撞检测是相当消耗系统运算力的。


### 区域调整


在Sprite编辑器中可以对裁剪的区域进行调整，也有提供一些快捷的功能。不过一般情况下应该在TexturePacker之类的软件中对这些功能进行调整会更方便一些。


区域调整功能更重要的是对渲染区域进行调整，将有的精灵中多余的空白部分排除到渲染之外的话，可以很好的降低渲染压力。



[![](https://blog.ch-wind.com/wp-content/uploads/2017/03/phpykKLq1.1453384829.png)](https://blog.ch-wind.com/ue4-paper-2d-overview/phpykklq1-1453384829/)


## FlipBook


FlipBook是帧动画的管理类，将Sprite组织成动画进行播放。FlipBook中的属性并不多：


Frames Per Seconds为每秒帧率；


Default Material为所有动画帧使用的材质；


Key Frames中存储的是每一个用到的关键帧的精灵的属性，可以调整的目前只有Frame Run，为帧的持续帧数；


Collision Source为碰撞模式选择，可以选择关闭碰撞、逐帧碰撞或者使用第一帧进行碰撞。


实际运用中更加重要的是FlipBook Components，这个蓝图类提供了很多方便的对Flipbook进行操作的接口。


在使用中如果开启物理出现了翻转出平面之类的不合理现象的话，需要对坐标进行锁定:  

[![](https://blog.ch-wind.com/wp-content/uploads/2017/03/php7XeP65.1453384926.png)](https://blog.ch-wind.com/ue4-paper-2d-overview/php7xep65-1453384926/)  

其他的在使用上并没有什么太多的复杂的地方，唯一的麻烦死目前并没有Paper2D的动画状态机，需要在BP中使用事件自行进行动画的更新控制。


## TileSet& TileMap


瓦片地图功能，当前在UE4中为实验功能。如果不使用的话可以不用太详细研究的感觉。


UE4支持从Tiled进行瓦片地图的导入。


瓦片地图的原理本身比较简单，TileSet与TileMap中的属性设置也都非常的直观。


Tile本身的碰撞是在TileSet中进行设置和调整的，在TileMap中也有开关进行碰撞类型的选择，Sprite Collision


Domain的含义与Sprite中是一样的。TileSet编辑器中也可以对每一个Tile进行一些独立的调整。


TileMap本身支持多层地图，功能上还是比较完整的。


有一个属性需要注意，Sepration Per Layer，这个属性是用于调整每一层地图之间的距离的，在多层地图中，相当于通常的Z-Order设置的位置，可以为一些地图特效提供帮助。


最后，在C++中使用Paper2D的功能当前并未完全开发，官方的建议是自己参考相关文档，例如[[UPaperFlipbookComponent的文档](https://www.google.com.hk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwi8rtmcwM7SAhWIm5QKHTJCAacQFggaMAA&url=%68%74%74%70%73%3a%2f%2f%64%6f%63%73%2e%75%6e%72%65%61%6c%65%6e%67%69%6e%65%2e%63%6f%6d%2f%6c%61%74%65%73%74%2f%49%4e%54%2f%41%50%49%2f%50%6c%75%67%69%6e%73%2f%50%61%70%65%72%32%44%2f%55%50%61%70%65%72%46%6c%69%70%62%6f%6f%6b%43%6f%6d%70%6f%6e%65%6e%74%2f%69%6e%64%65%78%2e%68%74%6d%6c&usg=AFQjCNHCRxbIjTBa0auVoc68-WMegXvSIg)]进行相关操作。



