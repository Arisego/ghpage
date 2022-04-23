---
layout: post
status: publish
published: true
title: UE4 Render Flow纵览
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2126
wordpress_url: http://blog.ch-wind.com/?p=2126
date: '2017-11-18 17:45:59 +0000'
date_gmt: '2017-11-18 09:45:59 +0000'
tags:
- UE4
- Rendering
---
渲染优化时质量和效率的平衡，虽然按照官方的建议进行相应的调整即可，但是不稍微了解其内部的原理的话还是有些许让人困惑的。


本文基于CEDEC2016的一篇讲稿，目标UE4版本为4.13。


由于到目前的版本（4.18）引擎渲染已经有了很大的变动，所以有的内容只有参考作用。


从概览的角度来看，UE4的渲染可以划分成以下的阶段：


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001_thumb-2.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001-2.png)


这个通路是针对延迟渲染的，与目前主要针对VR设备的前向渲染并不对应。


[[针对渲染通道的优化](https://blog.ch-wind.com/ue4-profiling-preview/#i-4)]虽然之前有做过总结，但是并没有详细的研究过各个通道在整体渲染中的地位。


## Base Pass


作为最重要的基础性通道，Base Pass运算的结果作为之后所有通道运算的基础。


基础通道里主要的可见操作是对Opaque/Masked材质的物体进行的遮蔽运算并完成G-Buffer的生成，VS和PS也在这个阶段进行计算。


[![image[3]](https://blog.ch-wind.com/wp-content/uploads/2017/11/image3_thumb.png "image[3]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/image3.png)


针对Base Pass的优化方向主要针对Vertex Shader和Pixel Shader两个阶段，另外在材质的Shader制作本身上也需要注意降低运算量。


### Vertex Shader


顶点计算的优化主要就是一些通常的建议：对物体的Bound进行规划，不要让bound过大，避免使用覆盖视野前后的物体。以使得Culling能够在早期就剪除掉不需要的顶点计算。


在Console中可以使用一下命令辅助优化：



> Stat InitViews可以查看裁剪计算的效果
> 
> 
> FreezeRendering可以冻结裁剪，对裁剪结果进行可视化分析
> 
> 


更进一步的可以根据平台的GPU特性不同进行对应的优化。


### Pixel Shader


由于Base Pass是后面所有通道的基础，所以会有较高的固有消耗。同时也是在场景中添加物品、Shader等产生性能消耗最直观的地方。


在理想的状态下，在没有Masked或者Translucent的情况，在PreZ阶段完成时就可以决定各个像素的深度并形成遮蔽计算了。在这种情况下，就可以极好的减小Piexel Shader阶段的运算量。但是实际上，为了场景中的特效质量，不能光依靠Opaque的材质，事情就没有那么简单了。


会导致PreZ完成时深度计算结果不完全的运算有，Masked材质的Alpha Test以及在Pixel Shader内部对深度数据的重写。因此需要有PostZ阶段对深度数据进行重新处理。


因此在这里容易形成两种造成性能影响的错误操作：在制作通用的材质时，明明有的不使用半透明蒙版通道情况却开启了半透明蒙版并往其上连接一个参数或者将参数连接到Piexel Depth Offset上。


由于PreZ和PostZ的决策是在GPU中完成的，无法在UE4中进行预览，因此在进行优化的时候要注意对上面的两种情况进行观察。


 


总体而言，作为G-Buffer的生成阶段，BassPass会直接的受到物体增加的影响，在添加物体时要注意检查以下两项：


Bounds的设置是否很好的完成了Culling。


Material的设置是否很好的避免了不必要的Pixel Shader计算。


另外，在项目设置中可以对G-Buffer的精度进行设定，对于需要高质量运算结果的情况或者想要降低性能消耗的情况，可以在这里进行调整。


## Z PrePass


这是在BasePass之前尝试进行深度计算。经过Z PrePass计算之后，可以减少到达Vertex Shader的顶点数量，以提高效率。


在项目设置中可以对Early Z-Pass相关的选型进行调整。


对于单个物体，这里的Use as Occluder默认是开启的，将其去掉就不会参与Early Z-Pass的计算。这个大部分时间应该保持默认，让引擎自行决定是否让物体参与深度计算。


[![clip_image001[5]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0015_thumb-1.png "clip_image001[5]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0015-1.png)


早期深度计算是为了减少Base Pass的运算负荷而存在的，但有时场景中物体布局可能会导致这个阶段形成瓶颈，可以在这里针对物体进行开启关闭来调整效果。


## Custom Depth/Stencil


在BasePass之后有一个可以自行进行定义的阶段，就是自定义深度。


自定义深度可以使得用户为物体在渲染时额外的生成一张深度贴图，可以很好的对需要的物体进行裁剪。


在项目设置中开启自定义深度


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002_thumb-2.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002-2.png)


然后在需要自定义深度的物体上打开


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003_thumb-2.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003-2.png)


需要注意的是，由于是额外进行的深度计算，基本上等同于对Base Pass进行了一次重新计算，自定义深度在场景较大的开放世界或者物体较多的场景中尤其会造成大的性能损失。


因此虽然使用Custom Depth可以相对简单的实现一些效果，但是却是以性能为代价的，应当尽量避免使用这个思路，如果非用不可的话，需要进行更加严格的Profiling。


## Pre-Lighting


这是光照计算之前的一个运算阶段，主要的作用是Decal和AO的计算。


在过去的版本中Decal经常与光照计算产生冲突，造成一些奇特的明显不符合预期的最终结果。


因此后来加入了


[![clip_image001[9]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0019_thumb.png "clip_image001[9]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0019.png)


的选项，目前的引擎中是默认开启的，无需太多关心。由于之前的项目中Decal的使用似乎没有遇到过什么问题，想来目前的默认选项已经很好的解决了问题。


如果在Decal的使用过程中遇到了问题，可以针对性的进行搜索。


## Lighting


就是光照计算阶段，光照的优化其实能找到很多资料。光照在UE4的操作上分为三种，StaticLight是全静态光照，全部使用预计算的结果进行光照。而Movable的光照则是全动态的，所有的光照都在运行时进行计算。Stational的光照则介于两者之间，静态物体的阴影会在预计算阶段进行缓存。


另外Stationary Light有同一个区域只受5个光照作用的限制，多出来的范围最小的那个会变成红叉叉，变成动态光照，在使用时需要注意。在视图选项中可以使用


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/11/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/11/image.png)


来对整体场景进行排查。


在动态光照的优化上，动态光照是重叠的越多性能消耗就越高的，相反的个数很多却相互不重叠的话光照复杂度的上升却不是很快。可以在编辑器中使用光照复杂度视图进行确认和优化。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/11/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/11/image-1.png)


还有一点是，静态光照并不是在运行时完全没有性能消耗。静态光照在运行时InitDynamic Setup计算阶段是会造成CPU消耗的，因此并不是由于是预计算的就可以无计划的放置。另外，据说StaticLight在被移动等时会自动的被变更为Movable的，没有进行过测试所以并不是很确定呢。


总之在进行光照布局时，首先使用Stationary是比较合理的策略。


## Reflect


反射计算虽然在概念上算是光照的一部分，但是其实在运算中是一个额外的阶段。


### Reflection Probe


反射捕获，是预计算的反射。在引擎中提供了球体反射捕获和盒体反射捕获两个选择，在使用反射捕获时，可以在拖入后对所在区域进行手动的重新捕获，也可以自己在其中指定CubeMap。


在项目设置中可以进行设置来调整反射捕获的精度。


[![clip_image001[11]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image00111_thumb.png "clip_image001[11]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image00111.png)


这部分的消耗是在Reflection Environment Compute Shader XXXX中反映的，与动态光照相同，个数对其性能消耗的影响不如区域重叠造成的影响。


官方的建议是，在场景全体放置一个总的反射捕捉，然后在一个单位房间内放一个整合性的捕捉，最后在反射性的物体上针对性的放置。


[![clip_image002[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024_thumb-2.png "clip_image002[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024-2.png)


覆盖全体的捕捉


防止在场景内完全丢失反射信息的情况


房间单位的捕捉


在场景单元内形成详细的反射信息


物体单位的捕捉


反射要求较高的物体附近进行更加详细的捕捉


### Screen Space Reflection


动态反射计算，没有深入看过其实现。


这里的主要问题是，由于是在屏幕空间内进行的计算，在屏幕外的反射无法正确的反映，同时有较多的噪点而且对Translucent的材质在计算时容易出现问题。


因此通常是与上面的反射捕获共同使用，作为其补充而存在的。因此如果出现了反射表面投影质量比较奇怪的问题，通常也可以检查一下是否该区域没有放置反射捕获，而不是一味的去加强动态光照和间接光照的次数，毕竟他们的性能消耗还是非常可观的。


### Planar Reflection


效果很好的反射，全动态计算。


但是其负荷相当的高，如果场景中有两个以上的话，会有目视可见的性能消耗。



> 无法控制反射通道中启用的渲染功能。
> 
> 
> 反射通道中的动态阴影不正确。
> 
> 
> 为保证达到目标帧率，需计算资源是否足以使用平面反射。
> 
> 
> 只支持恒定的粗糙系数，其在平面反射组件上（而非在材质上）进行指定。
> 
> 
> 如可能，须尽量将世界场景中的平面反射 Actor 数量限制为 1 个，将其移动、旋转、缩放，和世界场景搭配。也可使用多个平面反射 Actor，但需多加注意，因为平面反射 Actor 不执行任何距离剔除，只进行视锥和遮蔽剔除。因此，如果画面中同时存在两个平面反射 Actor，项目的帧率将受到严重影响。
> 
> 
> 渲染平面反射 Actor 的开销直接来自当前关卡中渲染的内容。启用此功能后，由三角形组成、绘制调用较大的场景将遭受严重的性能影响，因为这些开销不会随屏幕百分比变化。
> 
> 


以上内容引用自官方文档，在使用时需要额外的进行留意。


## Translucent


由于深度计算的效率等问题，Translucent单独在另一条路径上进行处理。因此在半透明的计算在延迟渲染中，总是会有很多的问题。


### 深度计算


将半透明的粒子投放到场景中时，可以看到并不会在深度数据中产生影响。这样在一些使用深度数据进行的效果如DOF中就会出现BUG。


因此UE4使用Separate Translucency来对半透明物体的深度进行处理


在项目设置中可以看到开关


[![clip_image001[13]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image00113_thumb.png "clip_image001[13]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image00113.png)


关于DepthOfField,在材质中有其运算结果的节点。


### 成本问题


半透明物体会极大的加重场景的渲染负担，在着色器复杂度中能够看到，通常半透明的粒子会导致复杂度变为红色。


优化上可以考虑降低Separate Translucency的分辨率，使用r.SeparateTranslucencyScreenPercentage指令可以通过降低分辨率来减小其消耗。


另一个解决方案是使用Particle CutOut有效的减少半透明计算的区域。


似乎只要使用Create SubUV Animation就会自动应用，没有测试所以并不清楚。


### Responsive AA


在半透明材质中可以看到这个选项，主要是针对使用了半透明材质的粒子的。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/11/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/11/image-2.png)


## Post Process


pp是渲染的最后一个阶段，可以在这里对渲染结果进行进一步的加工。


[![clip_image002[6]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0026_thumb-1.png "clip_image002[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0026-1.png)


PostProcess的成本消耗与添加的特效相关，每一个特效都会产生额外的消耗。如果自己使用了pp的材质来进行控制的话，其Shader复杂度也会对性能产生影响。


自带的PP特效可以通过指令来调整其效果，例如r.BloomQuality，其运算负荷是作为PostProcessWeightedSampleSum显示。


UE4的后期处理能在官方找到很多详细的[[文档](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/PostProcessEffects/index.html)]。


