---
layout: post
status: publish
published: true
title: 事件调度器及C++中的使用
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1450
wordpress_url: http://blog.ch-wind.com/?p=1450
date: '2015-08-16 12:00:50 +0000'
date_gmt: '2015-08-16 04:00:50 +0000'
tags:
- UE4
- 事件调度器
- Delegate
---
事件调度器非常的适合在各个蓝图之间实现通信功能。


当前UE4版本4.8.3。


在蓝图中，事件调度器的作用就像是事件的派发器。通过将事件预先的绑定在事件调度器上，可以让系统可以在需要时将事件派发给所有已经绑定的事件。


## 事件调度器的使用


一个比较常见的使用事件调度器的地方，就是关卡蓝图。


关卡蓝图中的很多物体的Actor及其逻辑，如果要脱离关卡蓝图的话会比较难于使用。因此，可以通过将关卡蓝图中实现好的功能绑定到某个类，例如GameMode的事件调度器上来方便调度。


如下图，在关卡蓝图的BeginPlay中将功能绑定到GameMode上：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/08/image_thumb1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/08/image1.png)


然后可以在GameMode的蓝图中，设定定时的调度关卡蓝图上的功能


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/08/image_thumb2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/08/image2.png)


事件调度器同时支持解绑和解绑全部，以方便对事件调度的逻辑进行进一步的控制。


## Delegate


在C++和蓝图混合使用时，使用Blueprint Function Library可以方便的实现蓝图到C++的调用。如果要实现C++对蓝图的逻辑的话，事件调度机制就非常的方便。


在C++中，与事件调度器对应的是Delegate机制。事实上，Delegate机制的涵盖范围比事件调度器要大一些。


Delegate机制是一种常见的设计模式，相信做程序的童鞋都比较熟悉。这里不做多余的说明了。


UE4官方对Delegate的翻译名称唯代理。按照类型，分为单播代理和多播代理。其中，多播代理与事件调度器的功能类似，而单播代理更接近单纯的代理，也就是只能绑定一个执行函数。


要让多播代理像是事件调度器一样使用的话，需要将其定义为Dynamic。对于单播代理也是一样的。


在C++中使用UE4的代理功能，需要使用官方提供的宏进行定义。





| 函数签名 | 声明宏 |
| void Function() | DECLARE_DELEGATE( DelegateName ) |
| void Function( <Param1> ) | DECLARE_DELEGATE_OneParam( DelegateName, Param1Type ) |
| void Function( <Param1>, <Param2> ) | DECLARE_DELEGATE_TwoParams( DelegateName, Param1Type, Param2Type ) |
| void Function( <Param1>, <Param2>, ... ) | DECLARE_DELEGATE_<Num>Params( DelegateName, Param1Type, Param2Type, ... ) |
| <RetVal> Function() | DECLARE_DELEGATE_RetVal( RetValType, DelegateName ) |
| <RetVal> Function( <Param1> ) | DECLARE_DELEGATE_RetVal_OneParam( RetValType, DelegateName, Param1Type ) |
| <RetVal> Function( <Param1>, <Param2> ) | DECLARE_DELEGATE_RetVal_TwoParams( RetValType, DelegateName, Param1Type, Param2Type ) |
| <RetVal> Function( <Param1>, <Param2>, ... ) | DECLARE_DELEGATE_RetVal_<Num>Params( RetValType, DelegateName, Param1Type, Param2Type, ... ) |


针对不同的代理类型，使用不同的宏前缀即可：




|  |  |
| --- | --- |
| 多播代理 | DECLARE_MULTICAST_DELEGATE... |
| 动态单播代理 | DECLARE_DYNAMIC_DELEGATE... |
| 动态多播代理 | DECLARE_DYNAMIC_MULTICAST_DELEGATE... |


实际使用时，首先要对代理类型进行定义



```
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FDspLRValDelegate, float, LVals, float, RVals);
```

然后在具体的类，例如GameState中进行具体的声明



```
UPROPERTY(BlueprintAssignable, Category = "SoundFuncs")
    FDspLRValDelegate  DspLRVals;
```

这样一来，就可以在需要调用这个代理的地方进行调用了，例如在某个数据生成的地方。



```
AMyGameState* tags = Cast<AMyGameState>(SL_Contex.LC_cGameState);
if (tags)
    tags->DspLRVals.Broadcast(tfLval, tfRval);
```

之后，就可以在蓝图中向这个多播代理绑定事件来获得生成的数据了


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/08/image_thumb3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/08/image3.png)


## 总结


事件调度器的机制在逻辑实现中非常的方便，尤其是在关卡设计中，可能会比较经常用到。使用中也没有遇到什么特别需要注意的地方，逻辑很单纯。


