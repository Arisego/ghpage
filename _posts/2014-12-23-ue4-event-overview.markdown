---
layout: post
status: publish
published: true
title: UE4事件相关总结
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1090
wordpress_url: http://blog.ch-wind.com/?p=1090
date: '2014-12-23 11:55:19 +0000'
date_gmt: '2014-12-23 03:55:19 +0000'
tags:
- UE4
- 事件
---
事件机制是实现游戏内逻辑的重要部分，在开始进行游戏逻辑的设计和实现之前，对UE4的事件机制进行理解是非常必要的。于是在这里对UE4的事件相关内容全部整理一下。


当前使用的UE版本是**4.6.0。**


### ① UE4的内置事件


- **Event Level Reset**


这个事件如其名称，只存在于Level Blueprint。只能在服务端运行。


事件发出在关卡被重置时，例如玩家死亡后地图没有重新载入而是重置的情况。


- **碰撞检测系列**


Event Actor Begin Overlap


Event Actor End Overlap


Event Hit


Overlap事件仅在两个物体的碰撞属性为Overlap且勾选了Generate Overlap Events时才会发生。而Hit事件则必须有Simulation Generates Hit Events的设置才会发出。碰撞检测事件是游戏逻辑的一个重要的触发点。


- **伤害事件**


Event Any Damage


由环境等因素造成的附加伤害，例如持续性伤害的沼泽地。


Event Point Damage


点伤害，是由抛物体引起的伤害。通常用于子弹的伤害以及某些近战武器。


Event Radial Damage


辐射状伤害，通常应用于爆炸伤害或其他的间接伤害类型。


伤害事件只在服务器端发起。


- **交互事件**


Event Actor Begin Cursor Over


Event Actor End Cursor Over


如其名字所描述的鼠标和物体的交互事件。


- **逻辑事件**


Event Begin Play


Event End Play


比较经常用到的两个事件，在Actor于世界中初始化和被消去时触发。


Event Destroyed


当Actor被销毁时触发，这个事件已经被官方标记了，功能合并到了End Play中。


Event Tick


时钟事件，每一帧都会触发。


Event Receive Draw HUD


只有在Hud类中才有的事件，可以用于Hud的逻辑和显示设计。


### ② 碰撞检测相关


碰撞的逻辑和射线追踪使用的逻辑是大体相同的。唯一不同的是追踪扫描线本身也可以拥有响应属性，使得物体可以选择是否阻挡或者忽略这条扫描线。


一些比较重要的属性包括：


CCD


连续碰撞检测。提高碰撞检测的精度，用于防止穿墙和防止二次碰撞。通常在高速移动物体例如子弹的模拟中会用到。


Always Create Physics State


在世界载入时而不是碰撞发生时创建物理属性，可以防止游戏运行中突发的大量物理属性初始化引起的卡顿，代价是载入时间的变长。


Check Async Scene on Move


同时检查同步物理空间和异步物理空间，异步物理空间主要被用于可破坏物体被破坏后的模拟。


Trace Complex on Move


如果使用复杂追踪，则将采用多边形级的模拟。通常采用简单模拟，碰撞图形可以在编辑器中定义。


碰撞属性的优先如下：


Ignore>Overlap>Block


只有在两个参与模拟的物体具有相同的属性时才会触发相应的逻辑，否则采用优先级高的碰撞逻辑。例如两个物体相互的碰撞设置为overlap和block，则会被判定为overlap。


对于场景中的高速移动物体，即时设定了Block有时也会触发Overlap事件，所以并不建议同时使用这两种类型的事件。


更多的实例可以参考[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Physics/Collision/index.html)。


### ③ 蓝图通信相关


**自定义事件**


UE4允许在蓝图中自定义事件。事件的定义只在该蓝图内部有效。


![add_custom_event.png](http://docs.unrealengine.com/latest/images/Engine/Blueprints/UserGuide/Events/Custom/add_custom_event.jpg)


自定义事件的使用方法基本和自定义函数相同。


**事件调度器**


事件调度器会在被调用后触发所有绑定在其上的事件。


[![image](https://blog.ch-wind.com/wp-content/uploads/2014/12/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2014/12/image.png)


可以绑定、解绑、解绑所有事件，同时如果定义的事件不绑定的话那么就不会被调度器调用。


**蓝图接口**


蓝图接口可以使得不同的物体类型提供相同的功能但是拥有各自的实现，和C++的接口功能类似。在蓝图中定义时没什么太大的问题，唯一需要留意的是对于没有输出的函数会被自动在转化为事件。如下图：


[![image](https://blog.ch-wind.com/wp-content/uploads/2014/12/image_thumb1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2014/12/image1.png)


如果要在C++中使用，则需要参考文档进行。


MinimalAPI


尽量的不向外暴露内部的函数。在这个情况下，可以通过为函数指定RequiredAPI来将其暴露出去。虽然官方是这么说明的，但是RequiredAPI的使用方式不明，直接使用会提示错误，有可能是包含问题。[Function Specifiers](https://docs.unrealengine.com/latest/INT/Programming/UnrealArchitecture/Reference/Functions/Specifiers/index.html)中亦没有说明，手上也没UE4的源码，由于不太可能用到这个设定所以不再研究。


DependsOn


声明依赖关系。当接口要使用到别的类中的定义时需要用到。


DependsOn=(ClassName, Classname, ...)


CannotImplementInterfaceInBlueprint


蓝图不能实现的接口，该接口只能在C++中实现。使用了这个指定之后，不能在接口中将函数指定为BlueprintImplementableEvent。相对的，在没有指定亦即可以被蓝图实现的接口中不能使用BlueprintCallable。


UINTERFACE(…, meta = (CannotImplementInterfaceInBlueprint))


需要注意的是，定义的接口不能暴露属性同时如果不使用CannotImplementInterfaceInBlueprint的话也无法将函数暴露给蓝图。功能上真的就只是一个单纯的接口。


------------


以上就是对事件相关部分的整理。


