---
layout: post
status: publish
published: true
title: CEDEC2021-《Blueprotocol》的渲染实现笔记
wordpress_id: 3557
wordpress_url: https://blog.ch-wind.com/?p=3557
date: '2021-11-16 01:18:59 +0000'
date_gmt: '2021-11-15 17:18:59 +0000'
tags:
- UE4
- CEDEC
---
CEDEC2021上《BLUE PROTOCOL》的分享的渲染部分。



PPT：[[BLUE PROTOCOLにおけるアニメ表現技法について　～実装編～](https://cedil.cesa.or.jp/cedil_sessions/view/2389) ]。




《BLUE PROTOCOL》虽然是用UE4进行实现的，但是由于他们的方法有对引擎进行改造，所以对于不希望进行引擎修改的情况可能不是很有参考作用。




## 简介




渲染实现上，是基于UE4的PBR渲染的。为了实现动画风格的渲染，在UE4的材质系统上，添加了一个新的ShaderModel，对BasePass和PostProcess进行了改造。


这样做的主要目的，一个是可以结合PBR的渲染效果，另一个是降低渲染的成本。




原始的PTT中有一定的篇幅在介绍UE4原本的渲染过程，由于没有现场的视频，不是很好推断想要表达的内容。总体而言，应当是对UE4原有的渲染过程进行一个总结，为之后介绍修改的部分进行铺垫。



[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/ue4-default-pass-300x156.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/ue4-default-pass.png)


实际的修改主要集中在对现有的Pass进行改造以及添加一些新的Pass，改造后的Pass流程：


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/image-300x131.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/image.png)


详细的修改部分在后面会有，总体而言感觉改动不大。主要修改如介绍说的，主要集中在BasePass上，所以其实单看BasePass的话，修改还是挺大的。


GBuffer的使用情况：





| # | Red | Green | Blue | Alpha |
| --- | --- | --- | --- | --- |
| GBufferA | ComputeNomal.x | ComputeNomal.y | ComputeNomal.z | PerObjectGBufferData |
| GBufferB | ToonHairMaskOffsetShadowMask | SpecularMask | SpecularValue | ShadingModelIDSelectiveOutputMask |
| GBufferC | BaseColor.r | BaseColor.g | BaseColor.b | AmbientOcclusion |
| GBufferD | ShadowColor.r | ShadowColor.g | ShadowColor.b | NdotL |
| GBufferE | - | RimLightMask | DiffuseOffset | RimLightWidth |
| GBufferF | OutlineWidth | OutlineID | OutlinePaint | OutlineZShift |


## 光照


光照使用的Mesh资源总共有两组法线以及顶点颜色数据，两组法线分别是在模型制作工具中预先处理的用于动画风格阴影的法线，以及在导入时自动计算的法线。


动画风格阴影的法线(Import Normal)没有介绍具体采用的方案，从效果图上看应该采用的是比较通用的处理方式。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/import-normal-300x240.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/import-normal.png)


导入计算的法线(Compute Normal)，有描述计算方式：


1. 计算三角面的法线
2. 每个顶点的法线是相邻三个面的平均


应该用的就是UE4默认的那种方式，没有考究过。导入计算方面，对于脸部这种分成了好几个部件的情况，会统一导入，防止在边缘出现计算问题。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/compute-normal-merge-300x245.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/compute-normal-merge.png)


顶点颜色方面，使用情况如下：



> 
> Red: Diffuse Offset
> 
> 
> Blue: Ambient Occlusion
> 
> 
> Green: DepthShift(轮廓线用)
> 
> 
> 


### BasePass


主要计算用于后面光照计算的必要数据：


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/base-pass-300x124.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/base-pass.png)


#### BaseColor与ShadowColor


BaseColor为明亮处的颜色，ShadowColor为暗处的颜色。


ShadowColor基于BaseColor进行计算：


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/shadow-color-300x156.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/shadow-color.png)


针对头发的颜色，BaseColor和ShadowColor都是直接在材质中指定颜色。如果头发是两种颜色的情况，会采用梯度图来进行过渡。头发的BaseColor和ShadowColor可以不依赖上面的规则进行设定。


#### NdotL


基于光源方向和ImportNormal进行计算：



```
HalfNoL = dot(Normal, Light) * 0.5 + 0.5;
ToonNoL = step(Threshold, HalfNoL);
```

PPT中解释了为什么要在BasePass中进行NdotL，除了精度上的考虑之外，主要是对要将什么搭载到GBuffer上的设计考量。ImportNormal只会在这个步骤中用，在这里计算完之后就不需要在GBuffer中传递ImportNormal了。


#### Specular


主要是材质中直接传过来的SpecularValue，以及计算SpecularMask。


SpecularMask用于表达主光源的高光，基于Blinn Phong反射模型进行：



```
H = normalize(Light + View);
NoH = dot(Normal,
ToonNoH = step(Threshold, NoH);
```

头发的高光有另外的处理逻辑：


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/hair-specular-mask-300x134.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/hair-specular-mask.png)


似乎会根据头发本身与重心的距离以及其ID，与光源进行配合动态的缩放。


### 方向光


方向光的计算主要分为两个过程：


1. 使用NdotL(GBufferD.Alpha)来处理BaseColor和ShadowColor(ShadowColor作为Subsurface处理)
2. 通过BaseColor的亮度结合SpecularValue以及SpecularMask计算高光


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/directional-light-300x164.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/directional-light.png)


使用的就是上面BasePass过程中生成的5张结果。


### 点光源


无视法线，直接按照与光源的距离来进行计算。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/point-light-300x183.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/point-light.png)


同时为Toon添加专用的参数来进行效果调节。


### 天光和间接光


将法线视为向上(0,0,1)来处理。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/skylight-300x182.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/skylight.png)


同时为Toon添加专用的参数来进行效果调节。


### RimLight


在光照后添加了一个新的PostRimLight的Pass来处理RimLight计算。


计算使用RimLightWidth(GBufferE.Alpha)和RimLightMask(GBufferE.Green)来进行。


通过深度信息作Sobel filter计算


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/rim-light-depth-300x134.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/rim-light-depth.png)


再通过RimLightMask屏蔽掉不希望的部分之后，叠加到Specular上。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/rim-light-mask-300x127.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/rim-light-mask.png)


## 轮廓线


轮廓线的绘制在PostOutlinePass中，这个Pass放在了光照和半透明计算之间，确保轮廓线能在水中等情况下受到折射的影响，同时保证半透明物体上不绘制轮廓线。


轮廓线主要有以下的计算来源：


1. 基于深度： sobel filter，比较深度并只在深度更大的地方绘制，通过depthshift限制一些地方(脸上)的绘制
2. 基于ID：sobel filter，在值较大的上绘制
3. 基于法线： 内积，主要针对深度差不多，ID也分不开的地方
4. 预先绘制的：从G-Buffer中取出


使用到的资源包括之前的顶点颜色G通道中的DepthShift，以及额外的通过TexCoord1来获取的第二组顶点颜色。另外，有一张预先绘制的轮廓线贴图。


绘制过程主要使用GBufferF：


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/line-300x129.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/line.png)


Red: 从TexCoord1.x中获取轮廓线粗细，并根据摄像距离和分辨率进行调整


Green: 从TexCoord1.y中获取轮廓线ID


Blue: 从预先绘制的贴图来绘制，同时使用轮廓模型防止绘制溢出


Alpha: 从VertexColor.g获取DepthShift，在基于深度计算时使用，绘制时基于参数进行反相


### 眉轮廓线


动画风格中常见的将眉毛绘制到前发之上的手法。


绘制上，将除头发以外的部分在BasePass中绘制，而头发单独在上面图中的ToonHairPass绘制。


眉毛的罗廓线由基于ID的方法生成，首先，在BasePass中生成一个眉毛本身的Mask，之后头发绘制时在更新轮廓用的ID的时候，在这个Mask上的部分不再更新。由此，在进行轮廓线生成的时候，就能够通过ID来产生眉毛的轮廓了。


### 抗锯齿


用上面的方法绘制的轮廓线会由于TAA导致模糊。


这里通过利用ResponsiveAA来解决，将轮廓线绘制到stencil来减轻轮廓线被TAA模糊的情况。


## 阴影


### ShadowMap


对于本身的ShadowMap的逻辑改造，主要目的是移除Toon材质上的自阴影。


处理方式上，根据是否是Toon材质将ShadowMap分开处理，这样就可以在移除自阴影的同时接受背景物体的阴影。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/ShadowMaps-284x300.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/ShadowMaps.png)


### OffsetShadow


为了补偿由于没有自阴影导致的图像信息不足，添加了一个在屏幕空间进行偏移的阴影。


处理这个的是最上面图中的OffsetShadowDepth和OffsetShadowMerge。


过程的原理描述起来其实很简单，首先，在OffsetShadowDepth中，根据深度信息产生一个向下的偏移。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/Offset-Shadow-Depth--300x169.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/Offset-Shadow-Depth-.png)


然后在OffsetShadowMerge中，根据深度对比将信息描绘到G-Buffer中的NdotL中去(GBufferD.Alpha)。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/Offset-Shadow-Merge-300x149.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/Offset-Shadow-Merge.png)


## PostProcess


后处理的方面比较简单，使用了柔光滤镜。在动画风格中经常使用到，虽然Bloom也能达到类似的效果，但还是另外的进行了实现。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/11/post-process-300x154.png)](https://blog.ch-wind.com/wp-content/uploads/2021/11/post-process.png)



> 
> 柔光滤镜，应该和[[这个](https://blog.ch-wind.com/ue4-fest-npr-note/#i-10)]是一样的。
> 
> 
> 


## 总结


虽然改造引擎的方法可能不是很通用，但是其中的一些思路还是比较有参考作用的。对于动画风格渲染，需要注意的部分有很多共通的地方，不过由于UE4的渲染流程是写死的，所以不会像U3D之类的那样灵活。


PPT后面还有一些关于Actor的动态Instance相关的优化，由于不是很关注这块，所以没有详细的看过，这里就不记录了。


