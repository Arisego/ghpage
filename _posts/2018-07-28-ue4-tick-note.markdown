---
layout: post
status: publish
published: true
title: UE4中Tick使用小结
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2409
wordpress_url: https://blog.ch-wind.com/?p=2409
date: '2018-07-28 10:03:37 +0000'
date_gmt: '2018-07-28 02:03:37 +0000'
tags:
- UE4
- Tick
---
Tick在UE4的逻辑中是最基本的单元之一，不过也有些地方需要注意的。


当前使用的UE4版本为4.18。


## 并行


Tick是可以打开并行的，对于一些和主要逻辑没有耦合的逻辑，可以打开该Object的并行Tick：bRunOnAnyThread来进行运行优化。


实际并行的执行方式可以到FTickTaskSequencer::ReleaseTickGroup中去查看。


并行只在TickGroup内部执行，但是要小心多线程同步问题，考虑到加锁的成本，还是只对独立的逻辑进行异步比较好。


在优化上，还有一个bAllowTickOnDedicatedServer的选项，不过具体与使用_Server宏来屏蔽代码相比哪个更好些并没有测试过~


## ActualTickGroup


每个TickFunc都可以指定TickGroup，但是这个TickGroup并不代表最终实际执行的TickGroup。


根据每个Tick注册的Prerequisite不同，Tick的执行Group会被延迟。


例如，如果TickFunc要求的Prerequisite是在PostPhiscs中的，那么即便它自己是注册为PrePhyiscs，也会被推迟到Post才能执行。


这个时候可以看到TickFunc的ActualStartTickGroup会变成实际的Tick执行组。


## 自定义Tick


可以通过自定义TickFunc来构建自己的Tick逻辑，相比TimerManager最大的优势就是这样可以在原有的Tick之外获得自己需要的逻辑执行时间。


引擎内部有一些额外定义的TickFunc，以前似乎是有SecondaryTick的，不过后来弃用了。


### UWorld


作为PhsxScene的维护者，拥有额外的三个TickFunc：FStartPhysicsTickFunction、FEndPhysicsTickFunction、FStartAsyncSimulationFunction。


都是用于对物理世界进行操作的Tick，其中StartAsyncSimulation是用于cloth的模拟的，注册在EndPhysicsTickFunction之后。而StartPysics是用于启动物理模拟，EndPhysics则是物理模拟结束的。


所以如果要保证物理处理已经完成，最好是注册到PostPhysics。


### USkeletalMeshComponent


FSkeletalMeshComponentEndPhysicsTickFunction是注册在EndPhysics的，用于骨骼动画的状态同步等操作，没有仔细的看过，详情参考USkeletalMeshComponent::EndPhysicsTickComponent。


这个Tick是要求在关卡完成物理结算之后的：



```
EndPhysicsTickFunction.AddPrerequisite(World, World->EndPhysicsTickFunction);
```

FSkeletalMeshComponentClothTickFunction则是负责对Cloth进行更新的，它被添加到了SkeletalMesh的EndPhysicsTickFunction之后，保证物理更新完成之后再进行衣服的演算更新。


### UCharacterMovmentComponent


FCharacterMovementComponentPostPhysicsTickFunction这个是在角色移动中，执行PostPhysicsTickComponent，当bDeferUpdateBasedMovement打开了的话，会在这里进行一次移动更新。


### UPrimitiveComponent


FPrimitiveComponentPostPhysicsTickFunction，这个是用来执行每个Component的PostPhysicsTick的，按照官方注释已经弃用。


### 自定义


参照上面的TickFunc的用法，自定义比较简单



```
USTRUCT()
struct FMyCustomTick : public FTickFunction
{
  GENERATED_USTRUCT_BODY()

  class UVehicleSyncComponent*    Target;

  FMyCustomTick();

  virtual void ExecuteTick(float DeltaTime, ELevelTick TickType, ENamedThreads::Type CurrentThread, const FGraphEventRef& MyCompletionGraphEvent) override;
  /** Abstract function to describe this tick. Used to print messages about illegal cycles in the dependency graph **/
  virtual FString DiagnosticMessage() override;
};

template<>
struct TStructOpsTypeTraits<FMyCustomTick> : public TStructOpsTypeTraitsBase2<FMyCustomTick>
{
  enum
  {
    WithCopy = false
  };
};
```

其中，下面的宏是必须的，否则会导致编译出错。因为TickFunc是不允许复制的。之后再对函数进行实现：



```
FMyCustomTick::FMyCustomTick()
{
  TickGroup = ETickingGroup::TG_PostPhysics;
  bCanEverTick = true;
}

void FMyCustomTick::ExecuteTick(float DeltaTime, ELevelTick TickType, ENamedThreads::Type CurrentThread, const FGraphEventRef& MyCompletionGraphEvent)
{
  FActorComponentTickFunction::ExecuteTickHelper(Target, /*bTickInEditor=*/ false, DeltaTime, TickType, [this](float DilatedTime) { Target->PostPhysicsTick(*this); });
}

FString FMyCustomTick::DiagnosticMessage()
{
  return Target->GetFullName() + TEXT("[UMyComp::PostPhysxTick]");
}
```

对于Component，定义了FMyCustomTick的变量PostPhysxComponentTick之后，在其Tick注册函数RegisterComponentTickFunctions中继续注册就可以了，可以使用的帮助函数SetupActorComponentTickFunction来进行注册，以及注意解注册：



```
if (bRegister)
{
  if (SetupActorComponentTickFunction(&PostPhysxComponentTick))
  {
    PostPhysxComponentTick.Target = this;

    UWorld* World = GetWorld();
    if (World != nullptr)
    {
      PostPhysxComponentTick.AddPrerequisite(World, World->EndPhysicsTickFunction);
    }
  }
}
else
{
  if (PostPhysxComponentTick.IsTickFunctionRegistered())
  {
    PostPhysxComponentTick.UnRegisterTickFunction();
  }
}
```

TickFunc的自定义还是比较简单的 ，不明白的地方可以参考上面那些引擎内部用法。


