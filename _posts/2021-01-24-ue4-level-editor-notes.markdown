---
layout: post
status: publish
published: true
title: UE4关卡编辑问题记录
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3226
wordpress_url: https://blog.ch-wind.com/?p=3226
date: '2021-01-24 11:19:43 +0000'
date_gmt: '2021-01-24 03:19:43 +0000'
tags:
- UE4
---

最近自己摆弄关卡遇到的一些问题的记录。



  

  





由于近段时间基本一直在作逻辑开发，所以很少自己碰编辑器，发现一些常见的问题也不知道该如何应对。于是统一的记录了起来，方便下次查找原因。




## Texture streaming over budget




结论写在前面，基本原因是默认配置太小，调大就可以了。




主要是直接输出一个红色的错误日志在顶部，让人担心自己是不是做错了什么。




首先，找到日志输出的地方：





```
SmallTextItem.SetColor(FLinearColor::Red); 
SmallTextItem.Text = FText::Format(LOCTEXT("TEXTURE_STREAMING_POOL_OVER_BUDGET_FMT", "TEXTURE STREAMING POOL OVER {0} BUDGET"), FText::AsMemory(MemOver)); 
Canvas->DrawItem(SmallTextItem, FVector2D(MessageX, MessageY));
```



这个东西的计算在：





```
FRenderAssetStreamingMipCalcTask::UpdateStats_Async
```



中，主要有两个来源：




### 内存池超过限制





```
Stats.OverBudget += FMath::Max<int64>(Stats.RequiredPool - Stats.StreamingPool, 0);
```



用实际消耗的内存大小减去MemoryBudget，RequairedPool就是每一个FStreamingRenderAsset的消耗加起来





```
Stats.RequiredPool += RequiredSize;
```



### 单个物体超过限制





```
// All persistent mip bias bigger than the expected is considered overbudget. 
const int32 OverBudgetBias = FMath::Max<int32>(0, StreamingRenderAsset.BudgetMipBias - Settings.GlobalMipBias); 
Stats.OverBudget += StreamingRenderAsset.GetSize(StreamingRenderAsset.MaxAllowedMips + OverBudgetBias) - MaxSize;
```



这里累计进去的就是OverBudgetBias，因为前面





```
const int64 MaxSize = StreamingRenderAsset.GetSize(StreamingRenderAsset.MaxAllowedMips);
```



### 实际分析




这样的话，直接stat streaming，看结果




[![image-20201227191346947](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20201227191346947_thumb.png "image-20201227191346947")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20201227191346947.png)


这里就是配置太小了，不知为什么默认只有76M，这样随便上几个大点的pbr贴图就超过了。通过指令上调配置就好。




r.Streaming.PoolSize 2000




也就是说，实际上是默认配置太小导致的，不是哪里操作有问题。




## InstanceMesh




目前共有UInstancedStaticMeshComponent和UHierarchicalInstancedStaticMeshComponent两个组件，但是他们有什么区别呢？一旦开始纠结就不知道应该选哪一个了。




稍微查了下资料，主要的区别是。UHierarchicalInstancedStaticMeshComponent是会按instance更新LOD的，而UInstancedStaticMeshComponent则全部统一使用同一个LOD。




### 本身的限制




由于目前的版本会自动合批，不是很确定UInstancedStaticMeshComponent还有没有必要性。不过至少会减少Actor的数量，也方便使用Cluster来减少GC负担。




InstanceMesh的限制：




1. 无法使用负数的Scale
2. 无法分别指定材质(per instance random可用于一些效果)
3. 碰撞不会在运行时更新(这个现在应该没有了)




### Crash




实际使用instancemesh，发现在编辑器里面直接ctrl+w会崩溃，主要原因是instance的生成直接放到构造函数里面了。




正确的做法是，将生成放到OnConstruction里面，还能在改变属性时自动更新。




## Bound




在愉快的拖动关卡的时候，突然出现了这样的报错：





> The actor will be placed outside the bounds of the current level. Continue?
> 
> 
> 




于是找了下输出来源，这个Bound似乎是实时计算的





```
FBox CurrentLevelBounds(ForceInit);
if (InLevel-&gt;LevelBoundsActor.IsValid())
{
    CurrentLevelBounds = InLevel-&gt;LevelBoundsActor.Get()-&gt;GetComponentsBoundingBox();
}
else
{
    CurrentLevelBounds = ALevelBounds::CalculateLevelBounds(InLevel);
}
```



在有LevelBoundsActor的情况下，会使用指定的Bound





```
/**
 *
 * Defines level bounds
 * Updates bounding box automatically based on actors transformation changes or holds fixed user defined bounding box
 * Uses only actors where AActor::IsLevelBoundsRelevant() == true
 */
```



也就是说，没有自己指定边界Actor为自定义的话，其实没什么太大的意义。




可以在编辑器设置中关闭bPromptWhenAddingToLevelOutsideBounds。



