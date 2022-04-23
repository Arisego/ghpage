---
layout: post
status: publish
published: true
title: CEDEC IdolMaster笔记-白金星光篇
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3217
wordpress_url: https://blog.ch-wind.com/?p=3217
date: '2021-01-23 14:08:30 +0000'
date_gmt: '2021-01-23 06:08:30 +0000'
tags:
- Idolmaster
- CEDEC
---
原始的演讲标题是：『目指せトップアイドル！』　PS4アイドルマスタープラチナスターズで目指したこと。


同样没有PPT，参考的：<https://game.watch.impress.co.jp/docs/news/1016369.html>


因为是PS4，所以画面要比CGSS好一些，不过这边是765。


开发上，这边也不是Cygames而是万代南宫梦。


[![image-20210115092727212_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210115092727212_thumb.png "image-20210115092727212_thumb_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210115092727212.png)


这边没什么太详细的内容。


## Variable toon


在ToonShader的技术基础上作了很多改进，技术命名是Variable toon。分享中没有透露具体的技术内容，只是一些概要性的说明。


由于默认的ToonShader会丢失掉很多信息，Variable toon的主要做法是，将这些信息重新补充到ToonShader上去。当然并不是单纯的作叠加，而是在Shader中的计算处理，所以有的地方也会作阴影的减弱。


示例给出的都是对比图片，由于没有什么美术素养，很多图片放到图片浏览器里面前后切换才看出差别。对比的图片可以参考原始的文章，为了防止有人访问不了，在DropBox上也上传了一份，可以到[[这里](https://www.dropbox.com/s/cm5bd6b1hcerzg1/Ims-%E7%99%BD%E9%87%91%E6%98%9F%E5%85%89.7z?dl=0)]取。


VariableToon的构成要素有


* 颜色不会有种褪色感
* 阴影计算不会出现预期外的颜色
* 根据角色动作计算出可叠加的详细阴影
* 头发、眼睛、脸颊、舌头、眼瞳各个部分添加不同的特殊处理


让角色无论从哪个角度看都很可爱。


关于详细的计算方式，虽然有作简单的说明，不过不是很确定是否是转述的问题，有点搞不明白。似乎是说，在通常的光照计算中，当3D模型受到光照时，在远离光照的那一侧将会产生阴影。而VaribleToon并不是对所有的物体都作一样的处理，而是针对离光源的远近采用不同的公式。


由于没有PPT，报道的文章也没有详细的记述，只能按照拍照来猜测：


皮肤表现上看，应当是添加了一些颜色的细节，应该是某种阴影实现。


根据角色动作的详细阴影，有可能是作了某种动态的接触阴影计算。


防止白色溢出，*白飛び*应该是过度曝光的意思，例子中是手臂的白色计算溢出过度了。


各个部件的特殊处理：


[![image-20210117154151523](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117154151523_thumb.png "image-20210117154151523_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117154151523.png)


从对比上看，嘴唇鼻子脸颊这些应该是在削减阴影，头发应该是对高光作了处理。同时头发到脸颊有类似接触阴影或者投影的效果，不知道光是哪里来的，无法确定。


VariableToon的效果是受动态光照影响的，至少可以反映周围光照颜色的变化。


动画风格渲染方面，有两个元素非常重要：


1. 轮廓线(outline)
2. 简略化的上色(通过shading进行2~3阶调的上色)


不是很了解上色，这里应该是灰阶上色，不然运算成本会高一些，不确定……


轮廓线处理上会对太过密集的轮廓线进行移除，同时让轮廓线受到周围的颜色的渗透，变得更加自然。


[![image-20210117161655763](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117161655763_thumb.png "image-20210117161655763")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117161655763.png)


这个图就是在密集处移除轮廓线的处理对比


另外，轮廓线带上周围的颜色目前应该算是比较常规的操作了。


表情方面，前作的表情是作用于脸部全体的。本作表情则分为上下两个部分，将两个部分组合以提供更高的灵活性，同时减少资源占用。


## 演出要素


与前作相比，白金星光的舞台特效主要添加的要素有：接近角色的长光束和观众席上的荧光棒的演出。荧光棒对表现力的提升很大，尤其是对于可以在其中行走的伸展式舞台场景更是想要尽可能的多加一些。


在演出制作上，由于具有很多舞台，所以演出就有了舞台和乐曲两个变量。为了减少制作成本，灯光的配置在各个舞台都采用了基本相同的配置。这样各个灯光和大型显示器的变化则可以和动作表演一样按照歌曲来进行设定，对于一个歌曲的演出表就只需要使用一个配置就可以了。


[![image-20210117173907301](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117173907301_thumb.png "image-20210117173907301")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117173907301.png)


特别需要提到的是灯光方面，例如LightHouse、武道馆、Arena三个舞台的灯光组的位置都基本是相同的，不过光的朝向、强度则各有不同，所以即便使用相同的演出表也能产生不同的效果。


[![image-20210117174828697](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117174828697_thumb.png "image-20210117174828697")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117174828697.png)


左边是LightHouse，右边是武道馆。


采用这样的设计之后，添加一个舞台或者添加一首歌曲也不会产生很大的工作量。


