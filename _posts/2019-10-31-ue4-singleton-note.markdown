---
layout: post
status: publish
published: true
title: UE4单例相关
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2712
wordpress_url: https://blog.ch-wind.com/?p=2712
date: '2019-10-31 15:40:14 +0000'
date_gmt: '2019-10-31 07:40:14 +0000'
tags:
- UE4
---
有很多关于设计模式的书都不建议使用单例，但是实际在很多地方还是会用到。


因为单例实在是太方便了，而且很“干净”。


## 编辑器中使用


在UE4的编辑器中使用单例最大的问题是，默认的调试模式下，所有的PIE共用一个。


如果要进行DS的调试的话，很容易出现一些没有预料的问题。这个时候可以选择使用`GEditorID`来分离。


由于`GEditorID`的特殊性质，可以实现一个奇怪的Trick，能够在不使用RPC的情况下直接在编辑器对服务器上的位置信息进行调试绘制：



```
#if !UE_BUILD_SHIPPING 
if(IS_CLIENT) 
{ 
  UWorld* tp_World = GetWorld(); 
  if (tp_World) 
  { 
    DrawDebugSphere(tp_World, AActor::GetActorLocation(), 30.0f, 7, FColor::Green, false, 4.0f);
    DrawDebugSphere(tp_World, ReplicatedMovement.Location, 35.0f, 7, FColor::Blue, false, 4.0f); 
  } 
} 
#if WITH_EDITOR 
if (IS_SERVER) 
{ 
    UWorld* tp_World = GEditor->GetWorldContextFromPIEInstance(2)->World(); 
    DrawDebugSphere(tp_World, AActor::GetActorLocation(), 40.0f, 7, FColor::Red, false, 4.0f); 
} 
#endif

#endif
```

如果编译没过的话，注意检查是否引用了UnrealEd这个Module。


## 新版本提供的单例类


之前的引擎版本中要使用与引擎相关的单例实现总会有各种各样的麻烦，从UE4.22开始，引擎提供了一组新的类型，包括[UGameInstanceSubsystem](https://docs.unrealengine.com/en-US/API/Runtime/Engine/Subsystems/UGameInstanceSubsystem/index.html)等。可以方便的在引擎内部实现单例的功能，实际进行测试的话：



```
void UMyGameInstanceSubsystem::RefreshAndPrint() 
{ 
  int32 td_LastId = MyGameId; 
  MyGameId = GPlayInEditorID; 
  UE_LOG(LogTemp, Log, TEXT(" UMyGameInstanceSubsystem::RefreshAndPrint: %d->%d || %p"), td_LastId, MyGameId, this); 
}
```

输出的结果如下：



> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 2->2 || 00000184F8152AC0
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 2->2 || 00000184F8152AC0
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 3->3 || 00000184F8152570
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 3->3 || 00000184F8152570
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 1->1 || 00000184F8153FB0
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 1->1 || 00000184F8153FB0
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 2->2 || 00000184F8152AC0
> 
> 
> LogTemp: UMyGameInstanceSubsystem::RefreshAndPrint: 2->2 || 00000184F8152AC0
> 
> 


这样的话就可以不用顾及一些其他的细节问题了。


