---
layout: post
status: publish
published: true
title: UE4使用Blender的HairGroom笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2876
wordpress_url: https://blog.ch-wind.com/?p=2876
date: '2020-05-10 20:56:56 +0000'
date_gmt: '2020-05-10 12:56:56 +0000'
tags:
- UE4
- Blender
---
UE4最近更新了对HairGroom的支持，于是对其进行了一些测试。


当前使用的UE4版本为4.25.0，Blender版本为2.82a。


本文主要参考Jayanam的教程[[Blender 2.8 Hair Beginner Tutorial](https://www.youtube.com/watch?v=Oq0q8AmTnDU)]和Marvel Master的教程[[Dynamic Hair Tutorial - Blender to Unreal Engine 4 Groom UE4.25](https://www.youtube.com/watch?v=vQIkyk0-TD4)]。


## UE4设置


这部分按照[[官方文档](https://docs.unrealengine.com/zh-CN/Engine/HairRendering/Overview/index.html)]操作就可以了。


当然，跟着Marvel Master的教程做也是可以的。需要注意的是，当前Groom支持在实验阶段，所以有些部分可能会与实际操作不一致。


例如Niagra发射器的部分，按照官方文档操作之后


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image.png)


Override Parameters并没有出现，由于并不影响实际效果，所以就先放置了。


## Blender内制作Groom


教程里面是直接在导出的SkeletonMesh上做Groom的，默认情况下会从全体表面来发射头发，以功能验证而言倒是无所谓。


总之首先就是加个粒子系统，然后改成头发


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image001.png)


对于需要控制生长区域的情况，目前看主要有三种方法：


1. 单独拉出Mesh用于头发发射
2. 使用头发发射器的顶点组功能
3. 使用贴图进行权重控制


似乎第三个方法主要用于微调的样子。


定点组的设置比较直观，使用贴图Mask的时候需要注意，必须调整贴图的影响方式


[![clip_image001[4]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0014_thumb.png "clip_image001[4]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0014.png)


完成粒子编辑后，将粒子转换为Curv


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-2.png)


然后作Curv转换


[![clip_image001[6]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0016_thumb.png "clip_image001[6]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0016.png)


导出Abc，注意调整缩放


[![clip_image001[8]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0018_thumb.png "clip_image001[8]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0018.png)


## 导入UE4


### 头发导入


导入的选项直接参照教程即可，流程上似乎有些奇怪，不过现在似乎就是这样工作的


[![clip_image001[10]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00110_thumb.png "clip_image001[10]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00110.png)


导入之后，在Asset里面打开物理模拟


[![clip_image001[12]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00112_thumb.png "clip_image001[12]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00112.png)


此时可以将资源拖到地图中预览。


这边遇到问题是点开之后拖到地图里面没有反应，此时，将Asset直接添加到角色蓝图内，会发现能动了，但是没有跟随骨骼限制运动。这时再拖到地图里面就会有物理反应了，可能是哪里有bug。


### 基础导入


无论如何，要让效果跟随物理基础，需要再次做一下导入工作。感觉之后的版本应该会改进，不然这样操作很奇怪


在blender中删除转换后的Mesh，选中角色模型


[![clip_image001[14]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00114_thumb.png "clip_image001[14]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00114.png)


再导出一次abc，覆盖掉旧文件


在UE4的旧Asset上点击重新导入


需要重新设置物理模拟


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image002_thumb.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image002.png)


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image003_thumb.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image003.png)


这个时候就可以看到Groom的跟随骨骼动画的效果了


[![clip_image004](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image004_thumb.png "clip_image004")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image004.png)


## 头发试作


为了实际看看Groom的头发大概是什么风格，这边简单的进行了下测试


### 顶点组绘制控制


在模型上添加一个顶点组


[![clip_image001[16]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00116_thumb.png "clip_image001[16]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image00116.png)


然后将模式切换到权重绘制模式


[![clip_image002[4]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0024_thumb.png "clip_image002[4]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0024.png)


这个时候就可以在模型上绘制顶点组的范围了


[![clip_image003[4]](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0034_thumb.png "clip_image003[4]")](https://blog.ch-wind.com/wp-content/uploads/2020/05/clip_image0034.png)


绘制完成后在粒子的顶点组里面将density指定到这个顶点组


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-3.png)


就不会从整个头上发射头发了


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-4.png)


### 粒子调整


切换到粒子编辑模式随便梳理一下头发


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-5.png)


这里可以通过选项让梳理的时候能够看到子粒子的效果


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-6.png)


这个梳理模式(粒子编辑器)还是挺强大的，有看到教程是直接从空白处开始刷出粒子的，不过由于没有什么美术细胞，就只能从简了。


按照教程里面的进行导出操作，就可以看到效果了


### 效果


努力进行了一番效果调整后，结果是这样的：


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/05/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/05/image-1.png)


由于全局只用了一个发射器，尤其是没有做前发的部分，所以效果不是很好。另外，不知是没有处理好头发的效果，还是过于写实的原因，感觉Groom的和动画风格的模型有些不匹配。


本来是想拉个双马尾的，但是由于对Blender的操作还不是很熟悉，最后放弃了……感觉要达到ArtStation上看到的大神们做出来的效果对我而言暂时似乎是不太可能的。


