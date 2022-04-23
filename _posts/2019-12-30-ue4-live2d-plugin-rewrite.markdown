---
layout: post
status: publish
published: true
title: 重构Live2D插件
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2769
wordpress_url: https://blog.ch-wind.com/?p=2769
date: '2019-12-30 23:08:00 +0000'
date_gmt: '2019-12-30 15:08:00 +0000'
tags:
- UE4
- Live2D
---
这个插件一直没有更新过，有些重要的功能也没有完成，最近好容易找到些时间。


由于和上一次的更新已经有了很长的时间，Live2D的SDK已经变化很大。


再加上打算换成新的渲染方式，所以干脆对整个插件进行了重写。


## 放弃的部分


首先，从目标上，放弃了编辑器支持。因为实质上Live2D的大部分编辑功能都是在官方的编辑器里面的，外部几乎没有什么可以控制的。而如果要做一些UE4这边的编辑器内控制的话，由于没有具体的需求，实在是很难把握分寸，反而会无端的投入时间。所以这一块就放弃了。


另外，也放弃了将所有的控制功能都接入到蓝图层面。这部分的工作其实就只是函数转发，但是也会无端的浪费劳动力，因为如何对Live2D的模型进行控制其实每个人在用的时候也会不一样吧。


因此，这边的主要工作就关注在Live2D模型的读取和渲染上了。


## 模型渲染


由于前次定的目标比较大，所以并没有在渲染上花太多的精力，直接使用了RenderTarget的Canvas绘制功能。


这样的缺点是，渲染的效率非常的低下。很难想象能够在移动平台上使用。


因此，这次使用了UE4后面提供的[[Global Shader Plugin](https://docs.unrealengine.com/en-US/Programming/Rendering/ShaderInPlugin/QuickStart/index.html)]系统。


这个系统在官方的说明里面非常的简略，但是其实实际的作用还是非常强大的。


本次就是通过自定义的VertexShader和PixelShader来进行Live2D的模型绘制。由于之前对渲染管线的知识有很多一知半解的部分，这次算是遇到了不少坑，也学到了很多东西。


其中遇到的最大的两个坑先记录在这里，其他的部分感觉就只是在探索API的用法了……


### 参数传递


参数传递上有个不知道能不能算作是坑的地方，UE4这边VertexShader和PixelShader在例子里面是有作分别实现的。


但是实际如果要传递参数的话，参数必须在公共的基类里面声明，否则传递过去的值就会出现错乱。


尤其是在PixelShader这边的表现特别明显，会出现奇怪的结果。


### 绘制混乱


另一个问题就是RenderThread和GameThread的关系。


由于之前没有怎么接触过需要双边控制的逻辑，所以遇到了奇怪的问题。


最主要的问题是，GameThread在将任务发到RenderThread之后，并不会马上就执行。


在偶然的情况下，会出现GameThread进入第二次Update的时候，RenderThread里面的任务还没有执行完成。


这次遇到的就是，由于渲染还在进行中，GameThread却又进去更新了Live2D模型，导致渲染那边取到了错误的VertexBuffer，最后出现了奇怪的渲染结果。


## TODO


其实有些渲染的细节选项还没有接入，但是由于手头上没有用到对应功能的模型，就算做了也不知道效果是不是正确的。


这块也只能等到用到的时候再搞了，不过既然主体已经完成了的话，也不会有什么太大的工作量。


最后，插件的地址更新了，现在在[[这里](https://github.com/Arisego/UnrealLive2D)]。


