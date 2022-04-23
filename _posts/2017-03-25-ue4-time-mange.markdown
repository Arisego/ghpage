---
layout: post
status: publish
published: true
title: UE4时间相关函数
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1571
wordpress_url: http://blog.ch-wind.com/?p=1571
date: '2017-03-25 11:26:22 +0000'
date_gmt: '2017-03-25 03:26:22 +0000'
tags:
- UE4
- Time
---
在进行游戏构建时，我们通常会用到和时间相关的逻辑，在此稍微做下小结。


当前UE4版本为4.15。


基本上游戏引擎都是以Tick为中心运转的，表现在玩家面前就是帧率了，UE4也是如此。


## Tick


tick是引擎的心跳，引擎中很多逻辑就是借助的tick机制自动注册的，例如UMG的动画播放功能就是tick驱动的。


### C++中使用


在蓝图中要使用tick的话只要从灰色的tick上拖出调用就可以了，但是在C++中使用的时候需要注意的是，在默认的情况下，tick是关闭的，必须自己开启才行。



```
PrimaryActorTick.bCanEverTick = true; 
```

另外由于tick本身是在每帧上调用的，出于效率考虑，要尽量避免往上添加复杂的逻辑，例如寻找1000以内的素数之类的。


还有一个比较少动到的地方是ShouldTickIfViewportsOnly，这个和编辑器的Tick策略关系比较大，但是在实际游戏中也可以使用。


主要的差分来自于LevelTick的类型



```
/** Type of tick we wish to perform on the level */
enum ELevelTick
{
/** Update the level time only. */
LEVELTICK_TimeOnly = 0,
/** Update time and viewports. */
LEVELTICK_ViewportsOnly = 1,
/** Update all. */
LEVELTICK_All = 2,
/** Delta time is zero, we are paused. Components don't tick. */
LEVELTICK_PauseTick = 3,
};
```

其中，如果编辑器不是在RealTime模式（Ctrl+R打开）的话，就会是LEVELTICK_TimeOnly ，如果是的话就是LEVELTICK_ViewportsOnly 。一般不是实时模式的话，一些依赖于Tick表现的效果就不会更新，例如旧的粒子特效。


当LEVELTICK_ViewportsOnly 时，只有与角色有相关性的东西才会Tick。而对于在游戏中需要设定达到这个效果的话，可以设置UWorld的bPlayersOnly，这样的话就会强制将Tick类型变为LEVELTICK_ViewportsOnly 。


原始的过滤发生在如下的定义：



```
void AActor::TickActor( float DeltaSeconds, ELevelTick TickType, FActorTickFunction& ThisTickFunction )
{
  //root of tick hierarchy

  // Non-player update.
  const bool bShouldTick = ((TickType!=LEVELTICK_ViewportsOnly) || ShouldTickIfViewportsOnly());
  if(bShouldTick)
  {
    // If an Actor has been Destroyed or its level has been unloaded don't execute any queued ticks
    if (!IsPendingKill() && GetWorld())
    {
      Tick(DeltaSeconds);    // perform any tick functions unique to an actor subclass
    }
  }
}
```

在C++中使用时，如果遇到Tick函数在编辑模式下不会运行的情况，这时可以尝试对以下函数进行重载：



```
virtual bool ShouldTickIfViewportsOnly() const override;
```

然后直接返回True。



```
bool AMyActor::ShouldTickIfViewportsOnly() const
{
	return true;
}
```

### TickGroup


UE4内部对Tick进行了分组管理，TickGroup之间按照先后顺序进行调用，其在引擎内部的定义为：



```
UENUM(BlueprintType)
enum ETickingGroup
{
/** 在物理模拟开始之前的TickGroup */
TG_PrePhysics UMETA(DisplayName="Pre Physics"),

/** 用于开始物理模拟的特殊的TickGroup */
TG_StartPhysics UMETA(Hidden, DisplayName="Start Physics"),

/** 与物理模拟并行的TickGroup */
TG_DuringPhysics UMETA(DisplayName="During Physics"),

/** 用于接受物理模拟的特殊TickGroup */
TG_EndPhysics UMETA(Hidden, DisplayName="End Physics"),

/**在物理模拟（包括衣料材质演算）后运行的TickGroup */
TG_PostPhysics UMETA(DisplayName="Post Physics"),

/** 所有的更新操作完成后的TickGroup */
TG_PostUpdateWork UMETA(DisplayName="Post Update Work"),

/** 包含所有被延迟到最后的TickGroup */
TG_LastDemotable UMETA(Hidden, DisplayName = "Last Demotable"),

/** 并非TickGroup的伪TickGroup，用于处理新生成的物体 */
TG_NewlySpawned UMETA(Hidden, DisplayName="Newly Spawned"),

TG_MAX,

};
```

在蓝图中有提供修改的接口，默认情况下的TickGroup是PrePhysics。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/03/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/03/image.png)


在C++中可以额外的添加Tick函数，使得对象可以获得额外的其他TickGroup的Tick，但是在设计上意义并不是很大。


### Prerequisite


在同一个TickGroup中的Tick似乎是根据优先调度进行的，其顺序近似随机。在特殊的需求下，UE4还提供了前置Tick Actor的设置，它可以保证两个Actor之间的tick按照顺序被调用。  

[![H13GGJPBRDQ5V0]DB$0O4XN](https://blog.ch-wind.com/wp-content/uploads/2017/03/H13GGJPBRDQ5V0DB0O4XN_thumb.png "H13GGJPBRDQ5V0]DB$0O4XN")](https://blog.ch-wind.com/wp-content/uploads/2017/03/H13GGJPBRDQ5V0DB0O4XN.png)[![QSKL3GN[A7SKY{M_JG)$E(C](https://blog.ch-wind.com/wp-content/uploads/2017/03/QSKL3GNA7SKYM_JGEC_thumb.png "QSKL3GN[A7SKY{M_JG)$E(C")](https://blog.ch-wind.com/wp-content/uploads/2017/03/QSKL3GNA7SKYM_JGEC.png)


这个函数只影响当前Actor的tick的执行次序，其子组件的tick并不受影响，如有需要需另行指定。


## TimeLine


时间轴是相当有效的在蓝图中对数值进行时间演变的方式，可以在很多地方被应用。例如打开房门或者是渐变材质的颜色等。


[![91$P{CXG9493~)HZMJYQTWY](https://blog.ch-wind.com/wp-content/uploads/2017/03/91PCXG9493HZMJYQTWY_thumb.png "91$P{CXG9493~)HZMJYQTWY")](https://blog.ch-wind.com/wp-content/uploads/2017/03/91PCXG9493HZMJYQTWY.png)


功能一目了然，不明了的地方可以参照[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Blueprints/UserGuide/Timelines/index.html)]。


TimeLine也可以在C++中使用，但是实际应用的场景似乎不大，如有遇到可以参考这篇[[社区文档](https://wiki.unrealengine.com/Timeline_in_c%2B%2B)]。


## Timer


UE4提供了定时运行的Timer供使用，在游戏逻辑上还是有经常被用到的。


[![D8TY(NNII{5VXAS_]F28XHO](https://blog.ch-wind.com/wp-content/uploads/2017/03/D8TYNNII5VXAS_F28XHO_thumb.png "D8TY(NNII{5VXAS_]F28XHO")](https://blog.ch-wind.com/wp-content/uploads/2017/03/D8TYNNII5VXAS_F28XHO.png)


使用起来需要连接事件或者提供函数名，详细的可以参考[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/HowTo/UseTimers/index.html)]。


在C++中使用Timer也相对简单，使用TimerManager提供的接口函数就可以了。



```
FTimerHandle DummyHandle;

GetWorld()->GetTimerManager()->SetTimer( DummyHandle, StartPulseSurveyIconDelegate, SurveyPulseTimeInterval, false );
```

第二个参数是一个[Delegate](https://blog.ch-wind.com/ue4-event-dispatcher-and-delegate/)，定义如下：



```
DECLARE_DELEGATE(FTimerDelegate);

FTimerDelegate StartPulseSurveyIconDelegate;
```

使用到的第一个参数为FTimerHandle，是用来标识并事后交付给TimerManager用于操作指定Timer的，如果没有这个需求，可以直接定义一个Dummy。



```
GetWorld()->GetTimerManager().UnPauseTimer(SampleTimerHandle);
```

### Delay


延迟执行节点，在蓝图中有时会用到的逻辑。Delay相当于一个不重复执行的Timer，因此在C++中要使用这种功能的话，就是用Timer来了。


[![RPNT]_K6CC@5L6HMON%U7$M](https://blog.ch-wind.com/wp-content/uploads/2017/03/RPNT_K6CC@5L6HMONU7M_thumb.png "RPNT]_K6CC@5L6HMON%U7$M")](https://blog.ch-wind.com/wp-content/uploads/2017/03/RPNT_K6CC@5L6HMONU7M.png)


其中上方的那个Delay节点提供的功能是：当还在倒数时被调用到，就会重新开始倒数。


## 速度调节


UE4有提供调节步进的接口函数，这个功能通常名为slow mode，功能上类似于FPS游戏中经常出现的子弹时间效果。


这个系列的函数提供两种类型的控制，一种是全局的，一种是针对某个特定物体的。


[![Z]B08UAW$FX`EIJ5F@~}%GM](https://blog.ch-wind.com/wp-content/uploads/2017/03/ZB08UAWFXEIJ5F@GM_thumb.png "Z]B08UAW$FX`EIJ5F@~}%GM")](https://blog.ch-wind.com/wp-content/uploads/2017/03/ZB08UAWFXEIJ5F@GM.png)[![]DP7]MMNR3]LR14QVF8$]1R](https://blog.ch-wind.com/wp-content/uploads/2017/03/DP7MMNR3LR14QVF81R_thumb.png "]DP7]MMNR3]LR14QVF8$]1R")](https://blog.ch-wind.com/wp-content/uploads/2017/03/DP7MMNR3LR14QVF81R.png)


全局的时间调节也可以使用控制台指令打开：


[![P3]9OU9IC2Y%5%2GH$PAQQ7](https://blog.ch-wind.com/wp-content/uploads/2017/03/P39OU9IC2Y52GHPAQQ7_thumb.png "P3]9OU9IC2Y%5%2GH$PAQQ7")](https://blog.ch-wind.com/wp-content/uploads/2017/03/P39OU9IC2Y52GHPAQQ7.png)


这个功能相对简单，时间设定的细节需要到具体使用的时候调节为上。


