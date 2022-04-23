---
layout: post
status: publish
published: true
title: UE4流关卡
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1467
wordpress_url: http://blog.ch-wind.com/?p=1467
date: '2015-08-11 19:34:05 +0000'
date_gmt: '2015-08-11 11:34:05 +0000'
tags:
- UE4
- level-streaming
---
流关卡可以使得关卡内容只在玩家“需要”的时候才加载，在很多游戏中都有使用这个技术。


当前UE4版本4.11.0 P6。


官方提供的流关卡功能目前有两种应用方式。


## 世界构成器


有点类似于Tile地图制作的方法，可以将子关卡拼成大地图。方便关卡设计人员的并行开发以及内容的复用。


这部分官方有提供详细的[文档](https://docs.unrealengine.com/latest/CHN/Engine/LevelStreaming/WorldBrowser/index.html)可供参考。这里只作简短的记录。


开启世界构成器的部分，属性的路径稍微有些变更。


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image.png)


关于Simplygon，虽然官方说明上是说引擎自带的，但是要使用的话需要Simplygon官方的许可证。有许可证之后可以参照Simplygon官方的[说明](https://www.simplygon.com/media/1636/simplygonue4integration.pdf)在UE4中开启相关功能。


## 流关卡


如果关闭World Composition开关的话，就是“正常”的使用流关卡功能了。


使用流关卡功能时，相关界面会比世界构成器时有一些功能上的变更。


在此功能下用于计算每个关卡大小的Level Bounds不会再被创建。


在关卡列表中可以对每个子关卡的动态加载方式进行选择


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-1.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-1.png)


关卡左边有蓝色图标的为使用蓝图进行动态加载的子关卡。


“总是加载”的子关卡在游戏开始后默认是可见的。


“蓝图”控制动态加载的子关卡还可以在关卡详细属性中进行单独的配置


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-2.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-2.png)


关卡的载入以及可视性可以通过很多方法进行控制。


## Level Streaming Volume


当玩家进入体积中时，被绑定的子关卡就会进行相应的变更。默认的情况下，子关卡将会显示出来，而玩家离开时就会将关卡移除。


具体的功能对应，可以在属性中进行调整：


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-3.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-3.png)


作用都比较直观。


子关卡和体积的绑定是在关卡详细设定中进行的。


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-4.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-4.png)


Level Streaming Volume必须放到永久关卡中才会起作用。


对于简单的逻辑使用关卡流体积非常的方便。


## 蓝图


对于一些复制的逻辑，可以使用蓝图对关卡的载入进行控制。


例如，使用触发器对关卡的载入进行控制。


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-5.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-5.png)


或者用按钮进行调试。


[![](https://blog.ch-wind.com/wp-content/uploads/2016/02/image_thumb-6.png)](https://blog.ch-wind.com/wp-content/uploads/2016/02/image-6.png)


蓝图和Level Streaming Volume联合使用时可能会出现冲突，使用时需要注意。


关卡的载入和移除都是异步的，可以在操作完成之后再触发其他事件，例如打开通往该关卡的门。


