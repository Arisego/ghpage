---
layout: post
status: publish
published: true
title: UE4的Live2D插件
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2345
wordpress_url: https://blog.ch-wind.com/?p=2345
date: '2018-05-09 21:51:31 +0000'
date_gmt: '2018-05-09 13:51:31 +0000'
tags:
- UE4
- Live2D
---
Live2D这个技术在公布之后在各种游戏中有使用的痕迹，不过在提供动态的同时还是损失了些许立绘的精细感。


当前UE4版本为4.19.1。


Live2D在Unity上是有提供插件的，在近期Cubism的SDK进行结构更新之后，其在其他类型的项目中的接入就变得更加轻松了。


因此便动了接入UE4插件的念头，不想工作量比想象中的稍微大了一些，再加上最近可用的业余时间变少了，打算将所有的时间集中到一个方面，便只能将这个插件以WIP的形式先放出来了。


由于短时间内在项目内可能不会用到Live2D，可能更新频率会很低呢~


## Cubism SDK


目前可以在项目中使用的Live2D的SDK可以从[[这里](https://live2d.github.io/#native)]下载，由于Cubism最近又出了一款产品，所以其产品主页上的说明有些没有理解。


由于本身没有进行过Live2D的制作，也没有购买过官方的License，所以在接入测试中使用的是官方测试用的Mark的Live2D模型。


Live2D的SDK在变更之前，模型动画的渲染和更新是混合在一起的，虽然可以很方便的直接取到渲染结果贴图。


但是由于渲染的路径是SDK自己控制的，导致在集成到UE4这样的引擎中会有很多心理和时间上的额外成本。


## UE4的接入


变更后的SDK的核心部分只负责对模型进行更新，所以在接入时只需要通过接口函数来进行更新和结果获取就可以了。


在实现上其实并没有什么太多可以解释的地方，基本上参照官方文档进行一一对接就可以了。


目前已经实现了Live2D的moc3模型的导入和使用，在使用上模型的渲染Object会有一个RenderTarget，直接将其用于材质或者UI就可以了。


在渲染时由于SDK那边推过来的时候是大量的Vertex和Index的数据，所以使用了UCanvasRenderTarget。这个类本身是会对Texture进行Batch操作的，但是有一个问题，就是Live2D的Mask类型的渲染方式并不被UCanvaRenderTarget的DrawTriangle所支持，所以必须使用额外的材质来进行Blend的操作。


### TODO


目前剩下的工作主要有三个方面：


* 没有将模型操作的接口接入，要使用的话必须调用SDK的原生接口
* 寻找更高效的渲染方式
* 另外就是编辑器的支持，现在打开导入的资源的话，编辑界面是无法使用的，由于需要处理的细节部分比较多而且也没有详细的研究过需要在编辑器中进行控制的项目，所以没有填入内容。不过并不会影响在项目中使用这个资源~


总体上而言只完成了核心的部分，如果需要在项目中使用的话还需要自己进行一点操作。


### Sample


由于是WIP，所以使用起来会有些繁琐，请直接看[[Sample项目](https://pan.baidu.com/s/1P1DXeIXRmw2czRlpIzt60Q)(y8a2)]。下面是详细的说明：



> 使用上只需要使用UCubismBpLib::CreateCubism就可以了，对于取得之后的Live2D渲染器，必须为其指定贴图。
> 
> 
> 由于不是很清楚Live2D实际在进行模型输出时贴图是如何进行规范命名的，所以这里需要进行一次额外的导入。
> 
> 
> 如果Texture的命名必然和模型对应的话，之后可以考虑直接在导入时进行引入。
> 
> 
> 在蓝图或者代码中完成构建和贴图指定之后，就可以通过Get_RenderTarget来获取渲染的结果的RenderTarget了。
> 
> 


### 链接


插件本体的连接在[[GitHub](https://github.com/Arisego/livv.git)]上~


说到ACG相关的插件，有的童鞋可能知道，其实之前有在做MMD的导入插件，但是后面有两个问题：UE4目前不支持在动画序列中原生的IK动画；要在UE4中实现MMD的一些特殊骨骼绑定例如QDEF之类的需要额外的工作量。所以虽然基本的导入和动画功能都实现了，但是这两个问题导致实质上没有办法推进了，目前是停止的状态呢。


## 更新


由于两次更新尝试之间的时间间隔相差太大，所以对插件进行了整个的重写。现在的渲染效率提高了～


[[插件地址](https://github.com/Arisego/UnrealLive2D)][[文章更新](https://blog.ch-wind.com/ue4-live2d-plugin-rewrite/)]


