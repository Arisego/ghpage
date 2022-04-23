---
layout: post
status: publish
published: true
title: UE4-Fest-NPR笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3258
wordpress_url: https://blog.ch-wind.com/?p=3258
date: '2021-01-24 12:01:00 +0000'
date_gmt: '2021-01-24 04:01:00 +0000'
tags:
- unreal fest
- NPR
---

UEFest2020上一篇关于NPR效果实现的演讲。




PPT在这里：<https://www.slideshare.net/EpicGamesJapan/unreal-festext2020winter-npr>




后面发现的视频在这里：<https://www.youtube.com/watch?v=L1tC6wnub2k>




npr是个很宽泛的概念，这边主要是讲ToonShader。




演讲的内容基于U4.25.4。




这边由于没有一个明确的生产目标，所以更多的关注流程的实现。




由于原始的PPT有很多思考和选择过程的记录，在这里会稍微重新组织下内容。




笔记是基于PPT制作的，后面虽然找到Youtube的视频，不过没找到时间从头看一遍……所以可能有的地方和视频说的不一样~




完成之后的效果：




[![image-20210117215700253](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117215700253_thumb.png "image-20210117215700253")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117215700253.png)


角色名 :齋藤胡桃




原本是准备做来放到MarketPlace上去卖的，为了这次演示重新设计，全部重做了一下。




角色设计方案：




[![image-20210117220008747](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117220008747_thumb.png "image-20210117220008747")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117220008747.png)


最初的目标：





> 
> 不是实现单纯的CellShader，而是希望将一些插画绘制的手法融合进来。
> 
> 
> 希望是能够在相对较暗的空间中也能够很好的渲染出结果来。
> 
> 
> 




## 引擎改造




和Unity不同，要在UE4实现渲染的改造是需要修改引擎代码的。




网络上也能找到一些改造UE4的Shading Model的方法介绍。




* [UE4のShading Modelを拡張する](https://qiita.com/dgtanaka/items/41f96ef2090820035609)
* [Toon shading model](https://forums.unrealengine.com/community/work-in-progress/41288-toon-shading-model)
* [Toon Shading Models, Stylized Rendering Experiments](https://forums.unrealengine.com/development-discussion/rendering/1537277-toon-shading-models-stylized-rendering-experiments)
* [[WIP] Anime/Toon Stylized Shading Model](https://forums.unrealengine.com/development-discussion/rendering/1704696-wip-anime-toon-stylized-shading-model)




改造引擎主要的问题是实现方式很难和别人共享，改造后的版本只能内部使用。




重新编译C++和Shader的成本也很高，最大的麻烦是，引擎升级。




所以演讲中使用的制作流程没有对引擎进行改造。




## 基于向量




基于向量计算，使用蓝图和材质节点来达到目标。




参考的文章是这篇：<https://unrealengine.hatenablog.com/entry/2019/12/01/000735>




使用向量的内积来在材质节点中获取更多的信息。




### 光照向量




由于材质中的Light Vector只能在前向渲染中使用，所以在蓝图中写入到Material Parameter Collection中。




之后便可以使用法线与光照向量相乘来达到模拟计算光照的效果




[![image-20210118232253776](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210118232253776_thumb.png "image-20210118232253776")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210118232253776.png)


前面的内积结果会在模型上生成灰阶的渲染值，使用这个值作为下一步的Mask的基础。上图比较简单，当前的渲染结果是这样的：




[![image-20210118233129915](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210118233129915_thumb.png "image-20210118233129915")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210118233129915.png)


为了模仿通常ToonShader的效果，基于上面的内积的结果，总共计算了四个层的内容：




* Shadow: 模拟阴影计算，连接到SubSurface
* HightLight: 模拟高光，连接到Emmisive
* RimLight: 连接到Emmisive
* Patten: 连接到SubSurface




上面三种都是比较常见的效果，所谓的Patten，其实是模仿有的漫画里的那种网点图的感觉




对于用于计算基础的内积结果，根据贴图会采用不同的插值方式。




[![image-20210119230758187_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230758187_thumb.png "image-20210119230758187_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230758187.png)


同时会按照需求使用一些其他的向量节点：CameraVector、ReflectionVector。




贴图提供的信息并不一定会按照0~1来插值，有的会设定为1.0是必然使用，而0~0.5才会插值，总之这个可以按照需求来进行灵活的控制，毕竟贴图是自己制作的。




### 阴影




用于模仿阴影计算：




[![image-20210119230028530_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230028530_thumb.png "image-20210119230028530_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230028530.png)


效果是这样的：




[![image-20210119230049261_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230049261_thumb.png "image-20210119230049261_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230049261.png)


### 高光




用于高光模拟计算，由于是连接到Emmisive，所以可以受到Bloom的影响。




[![image-20210119230329943_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230329943_thumb.png "image-20210119230329943_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230329943.png)


最终结果是这样的：




[![image-20210119230350972_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230350972_thumb.png "image-20210119230350972_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230350972.png)


### RimLight




就是边缘高光，通常用Fresnel进行模拟的那个效果。




[![image-20210119230505405_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230505405_thumb.png "image-20210119230505405_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230505405.png)


最终效果是这样的：




[![image-20210119230527413_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230527413_thumb.png "image-20210119230527413_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230527413.png)


### Patten




这个不是很常见，是用于模仿漫画的那种类似网点的感觉：




[![image-20210119230616663_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230616663_thumb.png "image-20210119230616663_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230616663.png)


[![image-20210119230707458_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230707458_thumb.png "image-20210119230707458_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119230707458.png)


最终结果像是这样：




[![image-20210119225712396_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119225712396_thumb.png "image-20210119225712396_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119225712396.png)


## 光照问题




光照模型选用的是SubSurface，虽然有尝试过Preintegrated Skin和Subsurface Profile，但是效果都有些微妙。




SubSurface存在一个问题，就是从上面来的DirectionalLight会对模型造成一种类似贯通的效果：




[![image-20210119231317537_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119231317537_thumb.png "image-20210119231317537_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119231317537.png)


使用Mesh进行遮挡也无法取消掉这个效果，似乎是SubSurface光照模型的计算特性导致的。只能暂时放弃。




对于主导的DirectionalLight向上的时候，会出现阴影很重的感觉。只能通过限制光的角度，或者额外的打一些光来解决。




另外就是拟似计算的光照不够硬，通过调整自己的参数来解决：




* 『Shadow Bias 』=>『1.0 』
* 『Shadow Slope Bias 』=>『0.0 』
* 『Shadow Filter Sharpe 』=>『1.0 』




### 法线整理




脸部不需要阴影，所以对模型进行处理，让法线全部朝向一个方向。




[![image-20210119231922084_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119231922084_thumb.png "image-20210119231922084_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119231922084.png)


这种处理方式参照的是：





> 
> GUILTY GEAR Xrd開発スタッフが送るアニメ調キャラモデリングTIPS
> 
> 
> <https://www.slideshare.net/ASW_Yokohama/guilty-gear-xrdtips-124324946>
> 
> 
> 




### 眼球高光




很强的那个高光是靠UnLit的材质内部计算出来的。




[![image-20210119232139763_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119232139763_thumb.png "image-20210119232139763_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119232139763.png)


眼球有添加一个假的各向异性光照来提高立体感，根据光照的方向不同这个高光的位置会移动。




### OutLine




没有使用PostProcess，而是在Blender里面制作了一个反转的Mesh，直接包含在骨骼模型里面。




此外还提供了以下的功能：




* 使用VertexColor来控制OutLine的粗细
* 轮廓线是带颜色的
* 根据摄像的距离调整粗细
* 根据FOV调整粗细




粗细控制基于Vertex Color，会使用Opacity Mask额外的处理，当数值小于0.1时，就不会绘制轮廓线。




不过主要的还是依靠将计算结果连接到World Position Offset进行的控制：




[![image-20210119233127332_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233127332_thumb.png "image-20210119233127332_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233127332.png)


颜色则是通过UV查找基础颜色，并与另外准备的OutLine颜色进行叠加计算，实际进行的计算比较简单：




[![image-20210119233437571_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233437571_thumb.png "image-20210119233437571_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233437571.png)


摄像的距离来调整Offset，这是通过内置的相机位置和Actor位置节点来计算的：




[![image-20210119233551957_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233551957_thumb.png "image-20210119233551957_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233551957.png)


FOV也是类似的，直接用Hlsl的custom node去取出来：




[![image-20210119233636756_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233636756_thumb.png "image-20210119233636756_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233636756.png)


### TextureInline




最后还使用了TextureInLine的技巧，实际上并不在OutLine的计算中，只是专门的准备了贴图，用于模拟一些不是很容易计算出来的描画效果。




[![image-20210119233840764_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233840764_thumb.png "image-20210119233840764_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233840764.png)


并不是单纯的打包在角色贴图里面，而是另外有一张贴图，可以动态的在叠加时对RGBA通道进行强弱和颜色调整。计算节点：




[![image-20210119233935788_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233935788_thumb.png "image-20210119233935788_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210119233935788.png)


## PostProcess




主要不是介绍UE4本身的pp，而是指希望达到的一些后处理效果，主要有




### 模造纸效果




[パラフィン紙](https://ja.wikipedia.org/wiki/%E3%83%91%E3%83%A9%E3%83%95%E3%82%A3%E3%83%B3%E7%B4%99)，一时找不到准确的术语翻译，就硬翻成模造纸吧。总之是一种纸，在上个世代的动画制作中用到。这种带颜色的透明的纸叠加到原画上，能够模拟出类似反光或者阴影的效果。




实现上使用了PP的Dirt Mask功能：




[![image-20210120193421631_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210120193421631_thumb.png "image-20210120193421631_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210120193421631.png)


贴图使用黑白的就ok了。




### 柔光滤镜




Diffusion Filter





> 
> 似乎是摄影术语，不是很明确是否采用了正确的翻译。虽然在镜片厂商看到的繁中译法是*擴散濾光片*，但是其他一些地方又似乎分类为柔光滤镜。不纠结了……
> 
> 
> 




总之就是这样一种滤镜，会将光线进行柔和的扩散，对降低图像在高光区域的对比度非常有效。据说可以在摄影时消除脸部的毛刺和皱纹，不是很确定是不是一个东西~




参考的这里：<https://twitter.com/monsho1977/status/670634806124920832>




[![image-20210120195648749_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210120195648749_thumb.png "image-20210120195648749_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210120195648749.png)


印象中虚幻应该也有模糊用的节点，可能有什么限制达不到需求吧。




### Kuwahara滤镜




桑原道義老师所发明的平滑化用的滤镜。




能够让画面产生油画一样的效果，有利于让渲染结果看起来更接近动画的背景的感觉。




这边这篇介绍的很详细的实现方式：[Unreal Engine 4 Paint Filter Tutorial](https://www.raywenderlich.com/100-unreal-engine-4-paint-filter-tutorial#toc-anchor-004)。




### 其他PP特效




还列出了一些其他的后处理特效，应该都是默认的特效




* Cinematic DoF
* Lens Flares
* Bloom
* Exposure
* Chromatic Aberration
* Vignette Intensity
* Color Grading LUT
* Motion Blur
* etc ...




## 总结




总之在不使用自定义引擎特效的情况下达到了一开始设定的ToonShader的效果。



