---
layout: post
status: publish
published: true
title: UE4中Loading和GC的优化
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2390
wordpress_url: https://blog.ch-wind.com/?p=2390
date: '2018-07-26 03:57:21 +0000'
date_gmt: '2018-07-25 19:57:21 +0000'
tags:
- UE4
- GC
- Loading
---
本文翻译整理自Epic Japan分享的Slide，是官方的一些优化建议。


原始的PPT请参看[[这里](https://www.slideshare.net/EpicGamesJapan/ue4loadinggcprofiling)]。


## Loading Time


载入时间在逻辑上分为两个部分：从硬盘中将需要的资源载入内存的时间；以及在AddToWorld时对系统造成的瞬间负载时间。


### Stat Level


通常要对载入状态进行追踪，可以使用Stat Level指令。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image.png)


这个指令会将关卡的载入情况显示出来，不过对于没有使用流关卡的情况，似乎作用不大。


这里显示出来的就是各个关卡载入的情况，总共有五种情况对应不同的颜色：


* 灰色-Persistent level
* 红色-UnLoad level
* 紫色-Loading
* 橙色-AddToWorld
* 绿色-Loaded Level


通常使用MemReport指令输出的关卡状态，由于是命令瞬间的状态，通常只会看到UnLoadLevel和Loaded Level两种常驻状态。


### Loadtimes


要对载入情况进行更加精细的分析，可以借助官方提供的Loadtimes指令。


使用LoadTimes.DumpReport可以将关卡的详细载入时间消耗情况输出到log，如果使用LoadTimes.DumpReport FILE的话就可以将报告输出到\Saved\Profiling\LoadReports\目录。


此外LoadTimes.DumpReport还可以使用LOWTIME=0.05等来过滤小于这个时间的载入报告，方便排查大的时间消耗。


而使用Loadtimes.reset可以对累计的数据进行清理，避免整个测试跑得太久累计下来的不需要的信息。


整个LoadTimes的统计核心是在UObjectGlobals.cpp中的，例如在Endload中这样的Scope：



```
// The time tracker keeps track of time spent in EndLoad.
FExclusiveLoadPackageTimeTracker::FScopedEndLoadTracker Tracker;
```

所有的追踪由单例FExclusiveLoadPackageTimeTracker负责，有兴趣的可以详细的阅读其代码。


报告大体上可以分为下面的两个部分


* asset type load times sorted by exclusive time: 按类型排列的载入时间统计(s)
* Dumping all loaded assets by exclusive/inclusive load time: 按具体的资源排列(ms)


Exclusive的统计不包括具体的Object的依赖资源，而Inclusive是包含所有依赖资源的。


### AddToWorld


在加载过程中AddToWorld是最后一个过程，物体在载入之后必须注册到渲染世界和物理世界中才能正常的进行游戏。


要对这个过程进行记录必须打开PERF_TRACK_DETAILED_ASYNC_STATS宏才行，打开之后可以对FAsyncPackage的CreateExport和PostLoad以及World中的AddToWorld和RemoveFromWorld获得更多的信息。


输出的内容会有像是这样的：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-1.png)


不过实际上感觉用处不是很大~


### 优化


优化载入时间首先的建议是使用官方的PAK机制，社区也有看到使用7zip之类的压缩算法来进行内容压缩的。不过压缩率是一个需要权衡的地方，因为虽然能够缩短载入到内存的时间以及减小包尺寸，却会导致额外的解压缩成本。


#### FileOpenOrder


在载入时间优化方面，官方在PAK机制内还提供了一个FileOpenOrder的优化工具。


要使用这个工具，在运行游戏实例时加上-flieopenorder指令。然后在游戏中将常规操作都执行一遍并退出游戏。这时候会生成一个GameOpenOrder.log，将这个文件拷贝到/Build/WindowsNoEditor/FileOpenOrder/ ，这样重新打包的时候就可以得到优化的文件顺序了。之后根据项目的迭代不断的更新这个文件就可以了。


这个优化主要是为了减少在对资源进行载入的时候的寻道成本了，另外这个优化对于SD卡这样的Mobile其实也是有优化作用的。因为SD卡的文件碎片虽然不会导致机械硬盘那样的延迟，也会导致读取效率的下降。



> File fragmentation: where there is not sufficient space for a file to be recorded in a contiguous region, it is split into non-contiguous fragments. This does not cause rotational or head-movement delays as with electromechanical hard drives, but may decrease speed; for instance, by requiring additional reads and computation to determine where on the card the file's next fragment is stored.
> 
> 
> [[Secure Digital Card](https://en.wikipedia.org/wiki/Secure_Digital)]
> 
> 
> 


#### 减少尺寸


除此之外的就都是一些常见的优化建议了，例如Shader Permutation Reduction 、材质的Instance策略等。


以及一些在不使用的情况下可以去掉的Index Buffer:



```
/** Reversed depth only index buffer, used to prevent changing culling state between drawcalls. */
FRawStaticIndexBuffer ReversedDepthOnlyIndexBuffer;

/** Index buffer containing adjacency information required by tessellation. */
FRawStaticIndexBuffer AdjacencyIndexBuffer;

/** Reversed index buffer, used to prevent changing culling state between drawcalls. */
FRawStaticIndexBuffer ReversedIndexBuffer;
```

其中AdjacencyIndexBuffer是为tessellation而提供的，如果不用的话可以关掉，而ReversedIndexBuffer似乎是为了在DrawCall之间减少culling state计算的成本而存在的，实际在渲染中的作用没有仔细的考据。


代码中能看到的注释是provide a minor rendering speedup at the expense of using twice the index buffer memory，这方面的权衡就需要实际测试了。


#### 加载控制


通过异步，将资源加载推迟或者提前。在4.19后Asset Manager应当已经可以使用了，可以通过Asset Manager对资源的加载进行更好的控制。


详情可以参考官方的[[资源管理](http://api.unrealengine.com/CHN/Engine/Basics/AssetsAndPackages/AssetManagement/index.html)]文档。


传统上的做法，还包括使用软指针来防止蓝图自动加载关联资源等手段。


同时，针对地图的Stream In/Out官方还提供了一些异步化的优化选项：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-2.png)


将Object的加载分散到各个帧去，而不会因为AddToWorld操作导致单帧瞬间卡顿。


另外，蓝图中尽量将逻辑从Begin Play移动到Construction Script中去，可以享受CDO带来的速度加成。


## GC


UE4内部的垃圾回收系统理论上除了提供的优化接口之外应当最好不要手动修改，由于GC本身要照顾很多方面，所以其中必然会有权衡存在。


通常GC会引起问题都是在LevelStreaming的时候，不过如果你在代码中申请了大规模的UObject，在不再使用的时候也不删除。或者频繁而无意义的调用ForceGC，自然也可能会造成性能问题。


UE4通过一张链表进行GC维护基础，数据类型为FUObjectArray。


GC的部分逻辑可以到GarbageCollection.cpp中进行查看。


通常情况下GC采用多线程的形式，但是当可用的处理器核心为1或者关闭了并行GC的时候就会变成单线程的形式。另外，Per Class的GC被打开的时候，由于无法保证线程安全，也会导致GC变为单线程。目前在编辑器中，由于HandleObjectReference中的Modify()的存在，是强制单线程进行的。


上面的内容来自官方的注释，由于不打算深入GC逻辑的修改，所以没有考据为何编辑器中Modify无法被移除。


GC的主要成本来来自遍历成本和实际的Object删除，4.16更新的GC优化就是将Object的实际删除分散到了各个帧中，这样在GC执行的时候就只需要执行依赖关系的切断了。


### Profiling


要对GC的实际消耗进行查看的话，可以打开log LogGarbage log


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-3.png)


也可以使用Stat dumphitches来定位GC造成的瞬间延迟


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-4.png)


通常使用FrontEnd的时候会看到的警告


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-5.png)


可以使用-NOVERIFYGC指令运行来去掉。


对于需要进一步的GC的信息的情况，可以选择打开



```
# define PROFILE_GCConditionalBeginDestroy 1
# define PROFILE_GCConditionalBeginDestroy_byClass 1
```

来输出更加详细的信息：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-6.png)


### 优化


为了避免LevelStreaming造成的GC瞬间成本，可以通过缩小细分关卡的规模来进行。


这样的话在进行角色的移动时，就可以形成小规模的载入和移除，而不是一次性的大规模变更。


#### DisregardGCObject


另外，针对其实不需要进行GC的一些常驻Object，可以通过


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-7.png)


选项来进行限制，这样的话就可以有效的减少遍历成本。


针对这个选项，官方有提供辅助设定的工具，不需要自己进行试错



```
[/Script/Engine.GarbageCollectionSettings]
gc.MaxObjectsNotConsideredByGC=1
gc.SizeOfPermanentObjectPool=0
```

在设定中这样设置后，游戏开启后会在log中输出



```
LogUObjectArray: 52083 objects as part of root set at end of initial load.
LogUObjectAllocator: 9937152 out of 0 bytes used by permanent object pool.
```

这样就可以得到一个有效的设定值了。


在GarbageCollectionSettings中还有一些其他的设定值，以及用于gc的console选项，不过一般情况应当不会动到。


#### Cluster


对于复合性的逻辑物体，其内部的Object随着父物体的状态进行管理的，可以使用Cluster来进行GC管理。


防止不必要的对很多子物体进行GC遍历：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-8.png)


其中，Merge GC Clusters可以运行聚合之间相互构成更大的聚合。


Actor的话需要打开Can be in Cluster，StaticMeshActor是默认打开的。因为其中引用的很多资源基本是跟随其自身的生命周期的。


Cluster由于是在AddToWorld中进行的，所以在Sequence中可能会有问题。


下面的是官方给出的优化结果：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/07/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/07/image-9.png)


#### 减少规模


这个算是通用的建议，例如蓝图的Macros在使用上需要谨慎，因为可能会造成在打包展开时变成很大的结构，应当尽可能的函数化。


还有就是尽可能的使用Blueprint Nativization，但是这个似乎一直没有离开实验阶段……


### FinishDestroy的帧分散


帧分散的思路可以用在LevelStreaming的StreamOut中FinishDestroy的工作分散掉：



> 
> 1. void UWorld::UpdateLevelStreaming()中ForceGarbageCollection(true); 改为false。
> 2. UWorld* UWorld::FindWorldInPackage()中GetObjectsWithOuter改为GetObjectsWithOuter(Package, PotentialWorlds, false, EObjectFlags::RF_NoFlags,EInternalObjectFlags::PendingKill);。
> 3. UWorld* UWorld::FollowWorldRedirectorInPackage()中GetObjectsWithOuter改为GetObjectsWithOuter(Package, PotentialRedirectors, false,EObjectFlags::RF_NoFlags,EInternalObjectFlags::PendingKill);
> 
> 
> 


这个是EpicJapan向Epic官方确认会有效果的一种优化方式。


## 总结


由于是官方的PPT，所以内容上都是一些通用的建议，以及官方本身的优化工具的介绍。


实际项目优化中大概都会有不少的引擎魔改，不过参考一下官方的思路，把基础的优化功能打开也是很重要的~


