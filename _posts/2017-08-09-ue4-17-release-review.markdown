---
layout: post
status: publish
published: true
title: UE4.17新功能探索
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1871
wordpress_url: http://blog.ch-wind.com/?p=1871
date: '2017-08-09 21:36:58 +0000'
date_gmt: '2017-08-09 13:36:58 +0000'
tags:
- UE4
---
4.17的版本更新已经正式的Release了，虽然之前一直有下载Preview的版本进行测试，却没有什么时间查看新添加的功能呢。


现在官方已经有了正式的Release Note，要看看引擎又添加了什么新功能就变得更简单了呢。


## 概览


这次的主要更新之一时Sequencer，不过遗憾的是并没有真正是使用过Sequencer，所以不是很清楚官方的功能提升到底提升到了什么程度。


大概就是简化和强化操作之类的，Sequencer不仅仅是用来制作过场动画的工具，同时也能制作达到影视级别的CG动画输出。


官方的新声音系统，Unreal Audio依然在制作中。


平台支持上，包括苹果的ARKit和Google的Tango都开始了早期支持。


UMG有了新的旋转剪切系统，不过大概用到的人并不多。而蓝图中现在有了伪节点，这个功能就比较好了，可以防止因为C++代码出现变更而蓝图链接全部断掉，完全不知如何是好的局面出现。现在因为定义变更之类的原因断掉的节点会保留原来的节点，标记为红色。这样就可以按图索骥，依样恢复蓝图的连接了。


同时蓝图的编译有了新的Compile Manager，据说蓝图编译速度加快了50%。


## VR/AR


这次的更新中对VR/AR的支持力度变得更大了，比如Sereo Layers现在有了一个平台无关的实现，方便于针对不同VR设备的快速的UI制作。还有诸如VR摄像预览功能之类的。


一个比较大的更新是，现在可以为针对VR游戏的设备设置分屏了，可以让VR头戴设备中的显示与显示器上输出的显示不同。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image.png)


可以通过蓝图函数进行设置控制，据说以后会加入各自的玩家操作支持，使得显示器和VR头盔可以实现”联机”。目前也能看到这样的函数：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-1.png)


由于没有VR设备，无法进行尝试。


## Render


4.17的一个比较期待的更新就是自定义Shader的支持。


虽然官方坚持99.9%的特效都可以通过现有的材质系统来实现，但是对自定义Shader的支持还是到来了。毕竟有时候出于效率和效果的考虑，还是有需要介入到Shader中去的。


自定义Shader的用法ReleaseNote中已经要简要的说明，4.17新推出的


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-2.png)


插件中就能看到官方是如何对自定义Shader进行使用的，这个插件也是年初GDC上官方演示的合成特效之一。而其他的合成效果则在


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-3.png)


这个插件中。


还有一个将Sequencer输出到图片上然后贴到Camera前方的Image Plate插件，应当是为了方便过场动画的渲染和播放吧。


## Asset Management Framework


4.16就开始的试验性功能，在这个版本进行了进一步的加强。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-4.png)


开放了很多蓝图接口，现在可以自主的对预先定义的资产进行异步加载了。


不会像以前那样需要复杂的编码，而且据说对加载速度的提升也比较明显。


但是打包和资产ID的指定方面可能要到更新的版本才会有变更。


与此同时添加的还有Asset Registry的相关功能的蓝图开放。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-5.png)


这样使用蓝图做编辑器扩展就更方便了……


## 其他


其他的还有Sobol准随机序列的蓝图和材质节点的添加，以及基于贴图的重要度采样功能：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-6.png)


以及很多新的功能和改进。


其中有一个比较有用的功能是实例化材质的烘焙。


可以将复杂的材质节点烘焙成简单的材质，有效的降低渲染消耗。


