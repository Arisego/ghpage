---
layout: post
status: publish
published: true
title: GDC2018 Fortnite优化演讲笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2328
wordpress_url: https://blog.ch-wind.com/?p=2328
date: '2018-04-08 01:01:09 +0000'
date_gmt: '2018-04-07 17:01:09 +0000'
tags:
- UE4
---
Epic官方在GDC2018的Fortnite的性能优化的演讲介绍了在Fortnite中使用的优化技术，感觉受益匪浅，在这里记录下来。 


当前UE4版本为4.19。


Fortnite是针对所有的平台的，可以让用户在PC、主机、手机上进行游戏并同时联机，这对内容制作和优化都是一个很大的考验。


Fortnite使用[[Device Profiles](https://docs.unrealengine.com/en-us/Platforms/DeviceProfiles)]进行[[Scalability](https://docs.unrealengine.com/en-us/Platforms/DeviceProfiles)]的调整，对TAAU的分辨率、阴影质量、Foliage、材质进行按目标平台的对应和性能调节。


而Mobile的优化经验可以被用到低端平台和60FPS模式上。60FPS模式是针对PS4 Pro和XBox1X提供的一个可选模式，除了常规的选项下降外。在60FPS模式下，关掉了DFAO，动态阴影的CSM变成了最低的一级，使用的也是更简化版本的RTDF阴影。


下面是官方给出的Mobile下的性能表，其中灰色的部分是原本在PC端开启的特性。


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image001.png)


在进行优化时，以60FPS目标，然后在低平台上降到30FPS可以预留更多的运算空间，防止机器过热。


## CPU


### Significance Manager


对所有的玩家进行的优先级管理系统，会影响后面的许多可延展性的系统的运行。


根据其他玩家与当前玩家的位置、可见性、在屏幕上的尺寸来决定他们的优先级，所有的玩家根据高低被分到4个不同的优先等级中。


平台的不同，各个分组的大小也不同。对于移动平台，由于可使用的资源是最少的，所以只有玩家自身使用最高的优先级进行更新。


 


### 骨骼动画


采用模块化的动画策略，每个角色由一个基础骨骼驱动头部、身体、背部装饰、武器四个部分。


五个模块分别使用不同的动画蓝图进行驱动，动画由基础骨骼拷贝到被驱动的骨骼上去。


采用角色的模块化的目的是为了提高复用率，减少动画模型等对内存的占用。


但是这样的方案会带来动画蓝图负担变重的副作用。


 


#### 异步执行Eval


动画系统执行上，大体分为三个部分：



> Update - 动画蓝图从游戏逻辑中收集状态变量并更新骨骼位置
> 
> 
> Evaluate - 根据骨骼位置对动画进行解压和混合
> 
> 
> Complete - 将运算后的顶点数据推送到渲染现场，更新物体位置和动画通知
> 
> 


在实际运行上，使用Profiling工具来查看Evaluate步骤是否是在Worker线程上执行的。


另外Update的过程也是可以异步的，在UAnimInstance::NeedsImmediateUpdate中能看到异步的条件，如果启用了Root Motion的话，就会导致异步的Update无法成立。


在AnimInstance.cpp中能够看到：



```
if(bNeedsValidRootMotion || NeedsImmediateUpdate(DeltaSeconds))
{
  // cant use parallel update, so just do the work here
  Proxy.UpdateAnimation();
  PostUpdateAnimation();
}
```

动画的异步更新可以在项目设置中找到选项


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image.png)


另外，Console中有如下的指令开关：



> a.ForceParallelAnimUpdate  
> 
> 开启时会无视项目设定和动画蓝图设置在WorkerTrhead中进行Update
> 
> 
> a.ParallelAnimEvaluation  
> 
> 打开时会在WorkerThread中执行Evaluatioin
> 
> 
> a.ParallelAnimUpdate  
> 
> 打开时animation blend tree, native update, asset players和montages会在WorkerThread中异步执行
> 
> 
> a.ParallelBlendPhysics  
> 
> 打开后physics blending会在WorkerThread中执行
> 
> 


由于没有实际使用过，不知道会有什么注意事项。


 


#### Nativization


由于动画蓝图的运算量比较大，在蓝图虚拟机中会有额外的运行成本。所以要尽可能的将复杂的逻辑放到C++中进行。


执行逻辑转移之后可以观察到动画的时间成本从0.93ms降低到0.19ms。


同时，在动画蓝图中要尽量的保证Fast Path的使用，但满足条件时就能看到节点上有标志


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-1.png)


需要注意不要再变量连接到节点的过程中在蓝图中执行不被Fast Path支持的变换操作。


 


#### 杂项


应用优先级管理非常重要，首先


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-2.png)


可以将Skeletal Mesh的更新标志置为只在物体被渲染时才执行Tick和骨骼位置更新。


同时根据角色的优先级，关闭非关键性的如武器的动画之类的效果。


Fortnite在移动平台上，除了自身外其他角色的武器动画都是关闭的。


使用URO可以在需要时对动画蓝图本身的更新频率进行降低，通过与前面的优先级管理系统配合可以有效的降低低优先级角色的动画成本。但是要注意不要关闭插值，插值对动画的效果影响比较大。


另外RigidBody在使用上可以用于代替AnimDynamic，其拥有更高的效率和更多的功能。


似乎还有将在地面上的Skeleton Mesh作为Static Mesh渲染的开关，但是在当前版本没有看到呢。


由于Fortnite的动画有的移动比较大，所以没有使用Use Fixed Bounds。而几个Skeleton Mesh的组件则是使用的Use Parent Bounds来继承基础骨骼的Bounds。


动画蓝图中的Trace在Fortinite中也是采用的AsyncTrace以降低GameThread的时间，而动画通知功能也尽量的转移到了C++中，使用[[AimModifier](https://docs.unrealengine.com/en-us/Engine/Animation/AnimModifiers)]以快速的对蓝图中的动画通知进行替换和管理。


关于动画系统的优化的更多内容，可以参考官方的[[动画优化指南](http://api.unrealengine.com/INT/Engine/Animation/Optimization/index.html)]。


 


### 物体管理


对于要跨平台的需求，物品的管理本身也是需要优化的。


 


#### Spawn


在物品的Spawn上，C++的组件会比蓝图的组件更快些。


实际进行生成时，先对Component进行配置再进行注册会更高效一些。


另外，材质实例的参数拷贝过程也被进行过优化。这方面的优化会被提交到引擎的版本中，像是后面会提到的粒子Component的Pooling功能也同样是如此。


对于粒子和声音组件，可以打开Auto Manage AttachMent，让其只在作用时才Atatch到Actor上。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-3.png)


对于Overlap，新添加了计数管理的功能：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-4.png)


防止在没有必要的情况下对物体的遍历查询。


而Generate Overlaps这个选项是默认打开的，也会在不必要的地方产生性能消耗，可以选择将其关掉。


 


#### Character Movement


角色移动在联网游戏上会有Predict系统，但是在实际使用过程中，尤其是对于移动平台而言。会支付很高的运算成本。


因此，对于优先度不高的角色会采用插值同步的方式来进行角色的移动，而不会在本地端进行Predict。


碰撞上，对于开启了per-poly complex collision的物体，为了降低内存消耗，实质上是开启了LOD的。


 


#### 物体


对于场景中的物体，应该考虑到尽量的减少面数以及降低材质本身的复杂度。


要在DrawCall的数量与内存占用之间选择一个好的平衡点。


可以使用ObjList和ListTextures来对当前场景中各个物体和贴图的内存占用进行追踪。


对于角色模型就是如此，在去掉不同的Section以及组合必要的Section之后，就变成了4个部分的设计。


 


#### LOD


将会有新的用于定义LOD的Asset，对于角色模型，采用的策略是。


在LOD1上移除了脸部动画，在LOD2上移除了手指和Twist骨骼。


角色的总体面数，LOD0为30000，LOD1为15000，LOD2为3000，LOD3为300。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-5.png)


对于长度很长的细节动画进行了优化，添加上一些额外的随机性。


对于HLOD的Proxy物体，由于会有额外的内存成本，需要在DC和内存之间进行平衡。


移动平台的LOD是锁定在LOD1的， 所以可以将一些装饰性物品放到LOD上。


环境物体拥有3~4级的LOD，对于屏幕尺寸很小的LOD可以用相当低的设定。


将场景内的物体蓝图化以方便进行调节。


 


#### 粒子


在对粒子进行制作的时候，不能有morph target的mesh，因为他们不支持LOD。


当资源紧张时应当根据优先级管理将较低的粒子特效关掉。


在移动环境下，一些没有游戏作用的环境特效可以关闭掉。


对于使用了Translucent光照的粒子，应当将其光照模型切换到


[![clip_image001[4]](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image0014_thumb.png "clip_image001[4]")](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image0014.png)


或者Volumetric Directional。


对于功能类似的材质应当进行合并，降低内存消耗。


 


#### 组合


对于由多个部分组成的物体，必须对其进行必要的合并和精简。


将可以合并的特效进行合并，并对消耗过大的特效尝试进行更简单的实现。


[![clip_image001[6]](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image0016_thumb.png "clip_image001[6]")](https://blog.ch-wind.com/wp-content/uploads/2018/04/clip_image0016.png)


例如上面的武器特效，原本是有粒子效果的，后面被合并到了半透明的Grid上，而原本通过物体Duplicate来实现的Outline也被放到了PixelShader中。


在Mobile上，材质使用了Fully Rough。


 


#### 草


Fortnite的草经过了不少的优化，由于一开始的草的被踩之类的特效是通过Vertex shader使用Rotation来实现的，而这在数学上的成本非常的高。


后面被改造成了使用Translation的，在移动平台上则完全关闭了这个Vertex Shader。


同时，积极的对草使用Density Scale来降低性能消耗。


 


#### 玩家构造物体


对于玩家在游戏过程中构建的物体，会有采用不同策略的LOD进行控制。


在建造的过程中使用的是基于Vertex的特效，而在Mobile上则采用了Masked的材质类进行实现。


在建造完成之后会切换到性能更低的完成的材质。


 


#### 风暴云


Storm Cloud在PC平台和移动平台上采用的是不一样的设定。


在PC上使用了Tessellated的平面来进行LOD和Cull。


在移动平台上则是一个甜甜圈为基础的材质特效。


 


#### Imposter


Fortnite采用了Imposter作为树的低层LOD。


这种技术还是非常有效的，官方有很详细的文档对[[3d imposter](https://docs.unrealengine.com/en-us/Engine/Content/Tools/RenderToTextureTools/3)]进行描述。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-6.png)


另外，针对玩家在下落阶段会看到的Imposter的阴影，Fortnite采用了blob shadow来进行。


将4个方向的阴影分别烘焙到贴图的RGBA空间中，


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-7.png)


然后根据日照的方向，对阴影进行偏移和取样，最终实现了相当不错的Fake Shadow。


 


## 游戏逻辑


#### UI


关于UMG的使用，官方是有优化指南的。


例如使用Invalidation来减少CPU成本、使用RetainerBox来减少渲染成本，以及将复杂的逻辑移动到C++中去。


而动态绑定功能应当尽量避免使用，因为它不仅有可能破坏缓存机制更有可能在不小心的时候造成相当高的性能消耗。


而对于Image的Batch功能，只有在使用的是同一个Z-Order并打开


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-8.png)


才可以开启Batch。


UMG的相关优化可以参照官方的[[UMG优化指南](https://docs.unrealengine.com/en-US/Engine/UMG/UserGuide/BestPractices)]。


 


#### Tick


逐帧逻辑中的性能消耗可以使用Dumpticks来进行详细的调试和查看。


在性能优化中，有一个关于MaterialParameterCollection的变更会在4.20中到来。主要的优化处是，在每一帧只会对参数集合进行一次更新，而不是在每次被调用时对被影响到的材质进行更新。


 


#### Audio


声音对性能的消耗更多的表现在内存占用上。


根据平台性能的不同，对播放声音的数量进行了限制，PC平台上是32个，Android为12个，IOS为16个。


在一些性能较低的平台上，会关闭声音的Reverb和EQ效果。


同时，在性能越低的平台上，会降低声音的变化效果。在最低等级的移动平台上，是不启用随机变化的特效。


在4.20之后，将会提供按平台在cook时降低压缩的功能，方便针对不同的平台进行不同的压缩策略。


 


#### Texture


贴图最大的问题自然会表现在Streaming上。


至于r.TextureStreaming，不可以随便关掉，因为会导致所有的mip全部被载入到内存中，即便根本就没有使用到。


这个方面可以参考[[官方文档](https://docs.unrealengine.com/en-us/Engine/Content/Types/Textures/Streaming/Config)]。


TextureStreaming上，Fortnite似乎将其载入过程从game thread转移到了async task中。


贴图的大小在制作时也同样是尽可能的合并类似贴图以及尝试减小大的贴图的尺寸，针对不同的平台的特性，对法线贴图和Colormap进行优化。


 


#### Level Streaming


使用关卡流可以很好的降低性能的消耗，为其他的特性预留空间。


不仅能减少内存使用还可以削减DrawCall。


关卡流在使用时，文件的读取由Worker Thread负责，从FArchive进行Deserialize的过程中新版本中也可以放到AsyncLoadingThread。只有最后的PostLoad过程被分散到了GameThread的每一帧中。


这种分散，在空中的时候由于Stream的更新较快为5ms，在地面上移动时，由于实际的Stream需求变低，为每一帧3ms。


这个是针对60fps设计的值，如果在30fps模式的话必须乘以二。


为了保证关卡流的流畅性，会一直尝试保持IO的进行。在本区域载入完成后，会对邻接的区域进行Streaming。


在4.20中还将会有一个用于在编辑器中进行InstancedMesh合并的工具，虽然Fortnite本身最终并没有使用这个方案。


 


#### Culling


一般的基于ViewDistance的裁剪，在设计上为了保证在各个平台的游戏性的一致性。


使用最低的平台的ViewDistance为1，在更高的平台上则放大这个值。


对于在游戏中无法躲藏玩家的物体，会更加积极的进行裁剪操作。


 


#### DHLOD


由于游戏中本身提供了可破坏的建筑物。


所以不能够简单的使用HLOD进行显示控制，所以专门构建了一个DHLOD的系统。


为每一个可破坏的建筑块准备了对应的LOD低模，然后使用一张贴图来标识对应的块有没有破坏掉。


这样就组成了一个DHLOD，让它位于真正的Destructable的建筑和Proxy HLOD之间，保证在使用LOD的情况下也能处理建筑物被破坏的情况。使得玩家可以对远处建筑物内的状况进行把握。


 


#### 线程策略


针对不同的平台的核心数和架构，采用了不同的线程策略。


对于低性能的双核IOS，除了经典的game/render thread之外，额外开出一个主要用于streaming的Async task thread。


对于高性能的IOS会额外开出3个task thread，主要用于前面提到的那些异步任务，包括：动画的Evaluation、粒子模拟、物理任务和查询、Texture Streaming和Scene culling。


Android平台上对性能优化最大的是用于提交OpenGl指令的RHI Thread。


 


#### Draw Call


CPU的性能上的瓶颈之一是Draw Call，在场景中需要进行culling和relevance虽然会对性能造成消耗，但是在采用Level Streaming后这方面的消耗就降低了很多。


Fortnite在PC上有超过4500个DC，在主机端有3500多个DC，但是在移动端，这样的GC数量是无法承受的。


进行的优化包括：


* 积极的进行距离裁剪，一旦物体玩家无法察觉或者不会影响游戏进行就裁剪
* 删除与游戏无关的装饰物品
* 使用遮蔽裁剪删除掉不可见的物体
* 使用HLOD合并DC


遮蔽裁剪使用的都是硬件裁剪，而HLOD对于有很长的可视距离的情况非常有效。


这里官方说的是全部使用硬件裁剪，不知道Target的目标设备是什么样的。UE4本身对于没有硬件剪裁的情况可以采用HZB裁剪，也可以预先进行Precomputed visibility volumes进行预先的计算。


 


#### 联机性能


Fortnite由于同时支持100个玩家，实质上需要同步的物体和关卡流的管理对性能的占用是非常大的。


Dedicated Server


在DS端，使用ForceNetUpdate()进行配合降低了服务器的更新频率到20Hz左右。


同时，应用了前面提到的优先级管理系统，通过自行的列表维护对物品的同步进行维护。并没有使用UE4自带的IsNetRelevantFor()和GetNetPriority()体系。


而属性同步也由原本的分散发布改为了由一个新系统来控制保证尽可能的缓存和重用。


服务器上与服务器无关的逻辑全部都会被关闭掉，例如动画模拟以及一些装饰类的物品。用于角色碰撞逻辑的碰撞形态也是另外为服务端准备的：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-9.png)


Client


客户端这边也会降低RPC的发送频率，对于除了关键性的移动之外的数据，也会将发送频率降到20Hz。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/04/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/04/image-10.png)


上面的这张图可以比较直观的表现发送频率降低的过程。


 


## GPU优化


#### Temporal Upsampling


这个是4.19更新的新的引擎特性，能够动态的根据系统性能对渲染分辨率进行调整。


详细的原理和提升可以参考官方文档[[Dynamic Resolution](https://docs.unrealengine.com/en-us/Engine/Rendering/ScreenPercentage)]和[[Screen Percentage with Temporal Upsample](https://docs.unrealengine.com/en-us/Engine/Rendering/DynamicResolution)]。


为了提高TAAU的效果，可以设置MipBias，r.Streaming.MipBias来获得更好的效果。


 


#### Z PrePass


Fortnite使用完整的Z PrePass，r.EarlyZpass=2|r.EarlyZPassMoable=1。


这样主要的好处是可以开启EarlyZPassOnlyMaterialMasking，有效的降低后期在base pass中包括alpha测试之内的很多成本。


同时完整的Z Prepass可以使得SSAO能够提前进入异步计算的过程，减少时间上的消耗。


 


#### 动态阴影


动态光照由于本身的成本非常的高，所以即便是在最高的scalability上也只使用了两级的CSM，而对于低端性能的设备，则会完全关闭CSM的阴影。


而为了弥补近处的阴影效果，则使用RTDF进行填补。


同时Fortnite还制作了一个轻量版的RTDF，RTDF的主要成本表现在Culling和Raytracing上。而这个轻量版将raymarching的步长从64降到了32，并且不会对subsurface scattering起作用。轻量版的更新将会在4.20到来。


AO方面，DFAO虽然效果比SSAO好，但是有更高的成本。关闭DFAO的时候为了防止出现亮度变高，可以降低Skylight的亮度并调高SSAO。


 


#### Vertex


与Vertex相关的性能是无法使用动态分辨率来解决的，所以这里的优化还是只能按照传统的策略来降低vertex相关的成本。


比如LOD、优化Foliage的Vertex Shader、减少远处的Foliage深度。


一个针对引擎的优化是，将异步计算中的同步锁改成了读写锁而不是排他锁，这个优化应当已经到了引擎中。


而Fortnite还对HLOD系统进行了很大的强化，以更好的保持Draw Call的稳定。


 


#### Foliage


根据不同的设备性能对Foliage的Density和distance进行调整。


对于装饰性的Foliage，在低内存的平台上会完全的隐藏掉。


在所有的平台上，都会关闭草的阴影。


 


#### 材质


材质在调整时使用Quality Switch进行平台特性的粗略对应。


对于Vertex Animation，会尽量的进行简化或移除。


对于Pixel Cost，会尽量使用更少的贴图，采用更高效的blending。


 


## 总结


从总体上来看，Fortnite的优化虽然有很多UE4通用的优化策略，有的确是在实际进行制作中才会遇到的零散的性能瓶颈。


大的系统性的改动在联机同步策略、优先级控制上，另外由于游戏规则本身的需求，对Destructable的物体进行了HLOD系统的嵌入。以及其他的很多对引擎本身的优化都会在4.19和4.20中到达引擎中。


在这里只能做些记录，优化的事情往往在操作过程中才会出现很多意想不到的问题，希望到时能够成为参考的来源。


