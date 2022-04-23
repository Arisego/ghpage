---
layout: post
status: publish
published: true
title: UE4粒子SubUV模块属性及应用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1345
wordpress_url: http://blog.ch-wind.com/?p=1345
date: '2015-07-01 10:15:36 +0000'
date_gmt: '2015-07-01 02:15:36 +0000'
tags:
- UE4
- 粒子
- Sub UV
---
SubUV模块使得粒子可以从一张排布了很多帧图片的贴图中读取出帧来实现特效。


当前UE4版本为4.8.1。


SubUV模块只有在发射器的Required模块中的Interpolation Method属性不为None时才是有效的，这个属性在Sub UV分类中。该分类下的其他属性也用于对SubUV模块的效果的控制和调节。


## SubImage Index


子图像索引基于浮点型分布来选择子图像，默认的坐标顺序是从左上角到右下角，横轴优先。


*SubUV*


**SubImage Index**


一个浮点型分布，用于决定子图像的选取。选取数值时使用相对时间作为参数。在设定数值时，要稍微高于实际数值。如目标数值是4，则设定为4.1。


*Realtime*


**Use Real Time**


是否进行实时播放。当打开时，动画效果将会无视游戏中的慢动作而实时播放。


## SubUV Movie


子UV动画循环的对子图像进行播放，效果与flipbook类似。


*FlipBook*


**Use Emitter Time**


当打开时，将会使用发射器的时间来计算帧率。关闭时则使用粒子的相对时间。


**Frame Rate**


浮点型分布，帧率。


**Starting Frame**


动画的开始帧，1为第一帧，0表示随机初始帧。如果这个值大于最大帧数的话，则会使用最后一帧。


*RealTime*


**Use Real Time**


打开后将会无视游戏中的慢动作设定，依然实时进行动画播放。


## 应用


SubUV的使用需要一张拼贴图，上面所有的“帧”的大小必须是相同的。这里参考的是官方教程：[SubUV Particle (Tutorial)](https://wiki.unrealengine.com/SubUV_Particle_(Tutorial))。


### 构建材质


操作的第一步是将拼贴图制作成为粒子系统使用的材质。


[![SubUV_Texture](https://blog.ch-wind.com/wp-content/uploads/2015/07/SubUV_Texture_thumb.png "SubUV_Texture")](https://blog.ch-wind.com/wp-content/uploads/2015/07/SubUV_Texture.png)


将图片导入UE4，新建一个材质。并将这个贴图放入材质中。


材质的输出属性中，将Shading Model改为Unlit。这一步的主要作用应该是关闭光照以减少不必要的系统运算量消耗，就算不进行这个操作对演示的结果也不会产生可目视识别的影响。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image.png)


将贴图乘上一个数值之后连接到自发光上，以便能够更好的观察到图形。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image1.png)


### SubUV模块


材质完成后首先在粒子系统默认发射器的Required模块中将材质替换为刚刚制作的材质。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image2.png)


接着，设置SubUV相关属性，由于是2x2的图形则分别设置2，插值模型为Linear_Blend。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image3.png)


SubImage Index


在发射器中添加SubImage Index模块，并对属性进行设置：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image4.png)


修改处为点1的In Val为0.75，Out Val为3.01。也可以点击模块名右边的绿色图标按钮，这样就可以在曲线编辑器中对其进行拖动和可视化修改了。


这样就完成了，效果如下：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image5.png)


### SubUV Movie


新建一个发射器，并关闭第一个发射器的显示。与上面一样的先修改Required中的Sub UV属性，然后添加SubUV Movie模块。


添加上之后就能看到效果，粒子会不断的播放1～4的动画。


由于默认帧率是30，很难进行效果的观察，可以将帧率降到2，就能看到帧动画的播放了。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image6.png)


### 属性测试


经过测试，可以发现Interpolation Method对动画效果的影响中，Linear和Random有很大的区别。在启用了Random的插值方法之后，Sub UV动画将不会再随着粒子时间而改变。而是在一开始的时候进行随机。可见，这里的Linear并不是单纯的指线性插值，而是指的由粒子的生命周期的相对时间进行插值。


插值方法为Random类时，Random Image Changes才会发生作用。在SubImage Index中可以指定生命周期中子图形的改变次数，SubUV Movie则是重新开启动画的播放。


 


---------------------------------------


目前来看，SubUV模块适用于需要子图像进行粒子显示效果控制的情况，在有相应的美工资源的情况下，可以减少使用代码生成相应效果的生产时间和运行时间。也可以将一些2D游戏的资源哪来做子图像粒子效果，说不定会有意想不到的效果～


