---
layout: post
status: publish
published: true
title: 初探UE4中的Profiling
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1845
wordpress_url: http://blog.ch-wind.com/?p=1845
date: '2017-07-30 16:10:34 +0000'
date_gmt: '2017-07-30 08:10:34 +0000'
tags:
- UE4
- Profiling
---
Profililng是成品制作过程中非常重要的一个步骤，通过Profiling才能提高运行效率使得作品达到用户能够运行从程度。


UE4本身有提供用于Profiling的工具，但是要正确的将其用于优化却需要经过一些学习。在掌握基础之后，要很好的完成优化，需要的是更多的实践所累积的经验了。


本文的主要内容来自对Tech Art Aid的[[Profiling系列视频](https://www.youtube.com/playlist?list=PLF8ktr3i-U4A7vuQ6TXPr3f-bhmy6xM3S)]的总结和官方的[[性能分析文档](https://docs.unrealengine.com/latest/CHN/Engine/Performance/index.html)]。


不过由于Profiling本身的覆盖范围较广，所以这里也只是记录刚刚开始接触的内容。同时，由于并没有很深入的了解过渲染相关的知识，文中有的术语可能存在翻译不正确的现象：D


## Scalability


UE4中有提供所谓的可延展性功能，这个功能可以用于快速的调整引擎的工作性能-效率平衡。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image.png)


但是这个功能并不是为优化而设计的，虽然其中使用到的一些设置可以用于优化，但是Scalability本身更多的是为了让开发者为用户提供一个快速的配置。


通常在游戏配置界面中能够看到的配置就是从Scalability入手的。


可以在蓝图中看到一些类似这样的函数


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-1.png)


社区中也有共享简单的游戏配置的实现，在设置窗口中可以对不同的渲染等级进行预览，以评估游戏在目标渲染等级上的表现。


更多的关于Scalability的内容可以参考[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Performance/Scalability/index.html)]。


## Profiling


通常性的优化目标就是提高帧率，降低每帧消耗时间。由于现代的CPU通常比较强大，只要不是在游戏逻辑中进行复制的物理模拟或者高强度的AI逻辑运算，性能的瓶颈都会出在与渲染相关的地方。


在进行优化的时候需要注意的是，要在项目配置中关闭Smooth Frame Rate，否则没有办法很好的对性能进行分析。对于打包优化，官方的建议是至少在Development以上的级别下进行，因为Debug下有很多东西非常的影响性能。


同时关闭垂直同步在某些情况下也是必要的，使用r.VSync指令就可以了，在打包版本中也可以使用命令行参数-NoVSync。


### 常用指令


官方的stat指令集中提供了大量的用于性能优化的指令，其中比较常用的是通用的问题定位指令，在找到性能瓶颈之后，可以进一步的使用相关的指令进行问题的查看。


#### stat unit


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-2.png)


使用stat unit就可以粗略的对问题的来源进行定位。


为了差分渲染与游戏逻辑的性能消耗，可以通过r.SetRes或者r.ScreenPercentage来有效的降低渲染消耗来辅助定位。


这里面Frame与stat fps输出的帧时间是一样的，其他的三项则对应不同的性能瓶颈：


Game为CPU游戏线程，如果是这里有问题的话通常就是游戏逻辑本身设计太消耗性能了。


Draw为CPU渲染线程，这里是负责向GPU发送DrawCall的，已经是渲染相关的优化。


GPU就是GPU的帧时间了，完全的渲染相关。


#### stat SceneRendering


指令可以用于更加详细的对性能瓶颈进行分析


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-3.png)


通过寻找性能消耗较大的pass，对其进行针对性的优化就好了。


#### stat gpu


则可以用于查看gpu上的性能消耗比例


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-4.png)


#### StartFire/stat stopfile


这组指令可以将性能分析文件生成到Saved/Profiling文件夹中。这些文件可以使用Front End中的分析器进行加载并分析：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-5.png)


#### GPU Visualizer


在优化中最常使用的工具还是GPU Visualizer，按快捷键[Ctrl+Shift+,]就会出来了。


[![SNAGHTMLbe577a](https://blog.ch-wind.com/wp-content/uploads/2017/07/SNAGHTMLbe577a_thumb.png "SNAGHTMLbe577a")](https://blog.ch-wind.com/wp-content/uploads/2017/07/SNAGHTMLbe577a.png)


性能优化从这里入手的话就比较直观一些。


### 渲染优化


渲染上会产生的瓶颈通常分为三大类别，Pixel-bound、Vertex-bound、Memory-bound。


#### Pixel-bound


Translucent的材质物体的大规模使用，半透明粒子都会导致在像素渲染级别上出现瓶颈。


在材质的使用上，Opaque的性能是最高的，因为可以有效的进行Z-buffer裁剪，其次是Masked材质，性能消耗最高的是Translucent。尤其是场景内出现大规模的半透明物体叠加的时候，就会产生大量的绘制负担。


在场景布局上，利用Opaque的物体进行遮蔽，尽量的避免镜头内出现大量半透明物体，有效的利用LOD都是非常重要的。


还有一个方面就是Quad Overdraw，这个似乎是由于GPU的渲染机制引起的，直接引用视频中看到的图片：


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image001.png)


在优化上，要尽量避免屏幕空间内出现小而长的三角形，将其分割为更多的三角形反而更加有效。同时，将屏幕内足够小的物体进行LOD，也可以有效的避免性能消耗。对于Foliage上的叶子，可以使用Particle Trimming来避免过度绘制，据说Speed Tree是自带这个功能的，不过由于没有使用过所以无法确认。particle trimming如其名，在粒子的优化中也有作用。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-6.png)


不过没有实际使用过这个功能，按照介绍的话，性能提升还是比较明显的：



> Original: 100%
> 
> 
> Aligned rect: 69.23%
> 
> 
> Optimized 3 verts: 70.66%
> 
> 
> Optimized 4 verts: 60.16%
> 
> 
> Optimized 5 verts: 55.60%
> 
> 
> Optimized 6 verts: 53.94%
> 
> 
> Optimized 7 verts: 52.31%
> 
> 
> Optimized 8 verts: 51.90%
> 
> 


这个数据来自于[[这里](http://www.humus.name/index.php?page=Comments&ID=266)]。


Quared OverDraw可以通过调整为检查模式来对场景中的物体进行检查


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-7.png)


#### Vertex-bound


通常受到影响的就是场景中三角形的数量，如果印象没有错的话，当前UE4内部所有的面应该都是三角形的。会在这里产生瓶颈的还有阴影投射与曲面细分，关于曲面细分，官方有建议是尽量不要使用，在建模阶段直接进行细分是更加具有效率的。


UV Seam和Hard Edges会额外的增加计算的顶点计算的负担，要尽量避免减少使用的频度。


同时Morph Target与WolrdPostionOffset也会产生更多的顶点计算，Skinned Mesh也是如此，不过这些方面，除了WorldPostionOffset可以尽量避免使用之外，只能从游戏逻辑本身的设计上入手了呢。


如果有使用LandScape的话，尽量减少LandScape的面数可以很好的提高性能。


为了避免过量的顶点计算负担，对于远景物体尽量使用BillBoard或者Imposter meshes、Skyboxe texture来代替3D物体。


#### Memory-bound


如果有大量的材质使用了不同的贴图，导致Texture Sample的数量爆炸的话，就会自然的变成瓶颈。


UE4有使用Texture Streaming，如果存储空间爆炸了的话，就会出现贴图模糊的情况，这时候可以使用Stat Streaming指令进行分析。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-8.png)


对于使用相同的材质的情况，可以通过材质中的设定让他们共享Texture。同时在材质中启用GPU本身支持的压缩可以有效的减少存储空间的占用，尽量的使用Texture Packing也是非常的重要的。载入的时候尽量使用Mip级别较低的图片，可以有效的减少存储占用。在材质的贴图使用中，尽量的进行优化的配置也非常的重要。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-9.png)


对于不需要太精细的贴图可以限制其最大尺寸


[![clip_image001[4]](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0014_thumb.png "clip_image001[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0014.png)


另外，光照贴图等也是被算作贴图占用存储空间的，因此也有在这里产生瓶颈的可能性。因此尽量的调低光照贴图的分辨率可以很好的提高性能。


使用Alt+0/Light Map Density可以对场景中的光照贴图密度进行分析。


在窗口>统计总也能进一步的对当前的存储使用状况进行分析


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-10.png)


#### 前向渲染与延迟渲染


UE4面向VR可以区分前向渲染与延迟渲染，两方各有优劣，在优化上也会有所不同。引擎采用的前向渲染方式是Cluster Forward Shading(Forward+)，详细的技术细节并没有关注过，不过通常前向渲染的光照计算成本会高些，尤其是光照数量较多时会产生明显的性能下降。


使用缓存区可视化功能，可以对延迟渲染使用的缓存进行查看。


## 按通道优化


优化的过程，通常是在玩家通常的地点放置观察摄像，然后通过这个固定点使用GPU Visualizer进行优化。


在使用GPU Visualizer时，会看到各个通道的性能消耗比例，这样就可以针对不同的通道进行优化了。


在打包模式下按下GPU Visualizer后，不会出现界面，但是相关数据会被记录到Log中。


在GPU Visualizer中对帧时间消耗进行排序可以帮助快速找到当前消耗的瓶颈，不过有的pass的消耗可能是不得已的，这里大概就是需要经验的地方了。pass根据工作方式大体上分别工作于屏幕空间和运算空间，像是PostProcess这样的后期处理以及延迟渲染的光照都是工作在屏幕空间的。而像是Z-Buffer的生成这一类的操作则是通过运算空间进行的。一般工作在屏幕空间的通道受到渲染分辨率的影响就会比较大，例如SSAO、AA等。而在运算空间的Pass就会受到Mesh的数量、面数、shader的复杂度的影响。


### 光照


#### LightCompositionTasks_PreLighting


这个通道被SSAO以及非D-Buffer类型的Decals使用。


这里的性能消耗在屏幕空间上，通过在PostProcess中降低AO的半径和消退距离可以减少其产生的运算负担。


同时，非D-Buffer类的Decals也会对其产生影响。


#### Composition After Lighting


只影响Subsurface Profile的Shading Model的SSS效果的通道。


由于工作于屏幕空间，减少其在屏幕中的占比就可以有效的减少消耗。比如使用LOD之类的。


使用Subsurface的Shading Model或者Matcap之类的来进行替代也可以降低这里的消耗。


#### Compute Light Grid


用于计算光照相关性的pass，减少动态光照的数量就可以减低消耗。


#### Lights


[![clip_image001[6]](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0016_thumb.png "clip_image001[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0016.png)


延迟渲染的光照是基于DBuffer在屏幕空间呢进行演算的，因此受屏幕分辨率的影响也比较大。


无论是静态光照还是动态光照，都会受到光照本身的数量以及范围的影响。


而动态光照的效率额外的受到光照影响到的面数的影响。


光照的优化应该尽量的减少光照范围的重叠，避免大范围的动态光照，关闭没有太大必要性物体的动态阴影投射。光照的重叠等的查看可以通过调整视图


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/07/image_thumb-11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/07/image-11.png)


来进行有效的排查。


光照类型的性能消耗是点光源>直线光源>聚光灯，在使用光照时，如果能用IES或者光照函数进行替代的话，不要使用很多个光源组合成类似的效果。


同时光照函数通常的性能消耗大于IES，其消耗受到光照材质本身的复杂度的影响比较大。


在对光照范围进行优化时，可以通过关闭Use Inverse Squared Falloff，并自己设置Light Falloff Exponent来达到减小光照范围达到类似光照效果。


#### Filter Translucent Volume


这是半透明物体的光照计算时会用到的pass


[![clip_image001[8]](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0018_thumb.png "clip_image001[8]")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image0018.png)



> 带光照的半透明物体的光照大多数来源于一系列面向视锥体的cascade处理过的体积贴图。 这样在体积内的任意点，光照均为单次，但缺点就是体积贴图的分辨率比较低，而且从观察者角度来说，只涵盖了有限的深度范围。
> 
> 


详细的说明可以参考官方文档：[[带光照的半透明物体](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/LightingAndShadows/LitTranslucency/index.html)]。


这里产生了瓶颈的话要检查光照的数目、范围和影响到的物体的数量。


#### ShadowDepths


这个生成通过光源进行阴影投射的深度数据的pass。


作用与这里的消耗主要受到开启了投影的光的数目、动态光照影响的面数、以及阴影的质量的影响。


阴影的质量可以通过Sg.shadow quality进行全局的调节。


#### Shadow Projection


实际的阴影投射，工作于屏幕空间，所以受分辨率影响，同时也会受到投影的光照数量和范围的影响。


### 基础通道


#### PrePass DOM_...


EarlyZPass，对非透明物体进行的早期的深度计算。


[![clip_image001[10]](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image00110_thumb.png "clip_image001[10]")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image00110.png)


数据似乎被用于遮蔽计算，如果不使用Dbuffer Decals的话可以关掉。虽然视频中是这样建议的，但是早期的深度计算可以在BasePass之前进行遮蔽计算，能让basepass以及之后所有的通道的计算减少很多。而且即便在这里不进行深度计算，会影响这里的运算量的变量依然会作用与后面的深度计算阶段，因此关闭EarlyZPass还是需要多做考虑的。另外要使用DBuffer Decals的话必须使用Opaque and masked的zpass计算，否则应该会出现奇怪的现象。


[![clip_image001[12]](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image00112_thumb.png "clip_image001[12]")](https://blog.ch-wind.com/wp-content/uploads/2017/07/clip_image00112.png)


性能上受到非透明物体的面数的影响，同时根据上面的选项不同也受到Masked的材质的影响。


#### HZB


Hierarchical Z-Buffer，用于计算HZB遮蔽，同时也会被屏幕空间内的射线演算使用，例如屏幕空间反射计算、AO等。同时被用于Mip的设置。


受屏幕空间的大小影响。据官方描述，HZB拥有较高的固定性能消耗，每个物体所造成的消耗较小。可以通过r.HZBOcclusion来调整运算的类型。


#### Base Pass


对非透明的物体进行演算并填充到GBuffer，使用缓冲区可视化模式可以在视图中看到效果。几乎所有的延迟渲染都受到其影响，因此才叫基础通道。


其计算结果包括base color, metallic, specular, roughness, normal, sss profile，并且Decals、Fog以及Velocity的计算也在此处。


其开销受到屏幕空间尺寸、物体数量、面数、Decals的数量、Shader的复杂度，生成的过程中包含光照贴图的推送，因此也会受到光照贴图的大小的影响。


可以通过Stat rhi指令检查各种贴图和triangle的消耗。


另外，前向渲染的光照也在这里进行，此时光照的数量也会影响到这里的消耗。


#### **Translucency**


半透明的材质以及光照演算，通过Stat gpu中的Translucency and Translucent Lighting可以进一步查看。


消耗受到屏幕空间大小以及屏幕内的半透明物体的数量影响，半透明物体的光照计算要尽量减少过度绘制。以及避免过多的需要进行半透明光照计算的光的数量。


### 其他


#### Particle Simulation/Injection


粒子模拟，这里只展示GPU粒子的消耗，性能主要受粒子数量以及是否开启了基于深度的粒子碰撞影响。


粒子的优化主要通过LOD以及设计上的优化进行。


#### Post process


UE4的后期处理功能比较多，AA、DOF、自动曝光以及很多其他的功能都在其中。每种PP特效都会产生额外的性能消耗，如果使用了PP材质的话，其复杂度也会影响性能。


#### Relection Envirionment


反射捕捉控件的计算缓存


可以将显示模式调整为Reflections来查看各个控件对缓存的影响


通常的建议是，放一个大范围的低精度反射捕捉，然后在需要的地方尽量不重叠的放置高精度的捕捉控件。


影响性能的主要就是捕捉控件的数量及范围，也受屏幕空间的大小影响。


#### Render Velocities


速度主要用于TAA以及Motion Blur，受到移动物体的数量以及其面数的影响。


主要的优化策略是使用LOD。


#### Screen Space Reflections


屏幕空间反射通过以下连个指令来进行调节：


r.ssr.maxroughness 0.0-1.0


r.ssr.quality 0..4


其中Maximum roughness决定着计算的范围的大小。


## 第三方工具


要使用第三方工具进行Profiling，一般需要打包。在进行捕捉之前，打开Toggle draw event的话可以让UE4提供更多的信息给第三方Profiling工具，捕捉完之后则使用同一个命令关闭就好。


第三方工具有Intel的GraphicsPerformance Analyzers、AMD的GPU PerfStudio以及开源的RenderDoc等。


使用第三方工具可以提供一些在硬件层次上获得的细节，在使用UE4本身的Profiling工具无法定位问题时可以进行尝试。


## 总结


总体而言，Profiling是一个复杂的过程。由于是面向最终用户的，需要花费很多精力在上面。


通常的策略包括LOD、裁剪、避免重叠以及低性能的近似替代等，很多的问题还需要在实践中才能发现和解决。


