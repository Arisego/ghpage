---
layout: post
status: publish
published: true
title: UE4 Light Academy笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2294
wordpress_url: https://blog.ch-wind.com/?p=2294
date: '2018-03-31 22:22:30 +0000'
date_gmt: '2018-03-31 14:22:30 +0000'
tags:
- UE4
---
UE4在实际布局场景的时候，光照的布局是一个很重要的部分。


当前的UE4版本为4.19。


这是对社区的ighting artists大牛[@Daedalus51](https://twitter.com/tillederdon)发布的系列教程的笔记整理，虽然场景光照布局需要很多经验，但是通过看别人是如何进行光照布局的过程也能获得很多知识。


之所以关注这个系列的教程，是因为想要更加的熟练的使用引擎，而不是过多的关注技术上的细节。


场景的光照布局上，不仅需要对引擎的功能熟悉还要有一定的绘画或者摄影基础。对基本的构图原理，光影效果有了解的话才能更好的让场景显得更加真实。


会对场景产生真实感的东西包括：阴影、Reflection、Specular。


由于整个系列的时间跨度比较大，其间引擎有不少大的变更，所以内容上也有很多不再“正确”的地方。


正如Daedalus在视频中所说，他只是在分享个人的经验，并不代表场景光照必须按照这个流程去做。


在整个教材中Daedalus本人分享了很多有用的经验，如果你觉得这对你很有用，请务必向他Donate哦～


原始的社区分享地址请到[[Unreal4 Lighting Academy](https://forums.unrealengine.com/community/community-content-tools-and-tutorials/106867-unreal-4-lighting-academy-or-something-like-that)]。


## 基础调整


### 场景清理


关闭掉一些特效，以便对基础的光照结果进行调节。


尤其是PostProcess中的一些选项，对整体的渲染结果影响是很大的。


只有基础的光照结果是正确的情况下，后期进行调整才会有更大的自由度。


AutoExposion必须关掉，否则对场景的亮度判断基本很难进行。


光照布局时也要将一些动态的光照关掉，必要的时候需要依照次序对光照进行调整。


Fog之类的效果也要关掉，有时候雾气是有颜色的，光照效果会受到影响。


### Light Map Resolution


如果要使用静态光照的话，首先要调整的就是光照贴图的分辨率。当然在此之前需要布局Lightmass Important Volume。


这里需要注意的是，如果材质打开了Use for static light的话，会占用两个贴图位给光照贴图和阴影贴图。


另外记得在什么地方看过，Sampler Source可以基本上全部设置为shared， From Texture Asset是为了与旧版本兼容而存在的。


由于没有实际上的测试过，所以并不知道其准确性。


对于LightMap的UV设置不合理的情况，可以通过提高Lightmap的分辨率来解决，但是最好是在UV制作时就留意光照贴图的布局比较好。


 


LightMapDensity不是越高越好，而是在需要的地方使用需要的分辨率。


如果物体本身通过贴图应用了很多效果或者离玩家较远的话，在上面叠加细节的烘培阴影其实作用不大。


 


对于场景中很小的物体，光照贴图的分辨率调低成点都是可以的。因为它们不需要那么多的光照信息，对场景总体的贡献不大。


### Base Color


对于PBR的场景调整而言，需要注意的是。


不应当让Diffuse Color本身拥有太高的饱和度，似乎在PBR之前的工作流中需要将饱和度的细节烘培到贴图中去，但在PBR的渲染中，Diffuse Color会做进一步的运算。那么预先烘培进去的饱和度就会对场景的颜色产生必要以上的干扰。


另外一个需要注意的是贴图的整体的亮度，PBR渲染需要的Base Color的亮度会与体感有些不同。如果图片的明度不“正确”的话，会导致光照的效果比预先的更暗或者更亮。


通常情况下，白色的墙包括雪的base color都是灰色的而不是印象中的白色。整体而言，亮度的设定会比实际的体感亮度向内收缩。


在Photoshop的直方图中可以很好的对贴图的平均亮度进行观察


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/03/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/03/image.png)


明度的中间值即便对于很亮的物体，也不应当超过230，而再暗的物体也不应该低于50。


这些贴图的效果虽然可以在引擎中进行调节


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/03/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/03/image-1.png)


但是如果可以的话，对资源本身进行相应的调整是最好的。


## 后期调整


### Reflection Capture


在进行初步的预览烘培后，需要对反射捕捉进行合理的布局，可以在Reflection预览模式下查看效果。


必要的时候可以关掉SSR来进行调节。


在需要反射细节的地方需要额外的添加小的捕捉来获得更精细的反射效果。


对于室内场景这种完全方形的构造，可以选择使用方形的反射捕捉。


### Fake Light


即便是进行了布局修改之后，引擎依然无法对现实中的光照进行完美的模拟。


这时候就需要使用到Fake Light的技巧。


通过Light Chanel来使得光照只影响需要的物品，来给过暗的物体添加更多的光照细节。必要的时候可以关闭灯光的投影，防止制造不必要的阴影。


这里还有一个小技巧，就是将光源放到Mesh内部，只要Mesh不是double side的，就可以模拟从内部发光的效果了。


除了Light Shaft和Volumetic Mesh这些常见的Fake Light之外，作者还介绍了一种模拟光照的Bloom效果的方法。


### Fog


雾气的添加和调整被放到了后期，可以防止在前期调整时由于Fog本身的特效导致出现误判的情况。


可以通过调整Start Distance来改变雾气效果开始的距离。


### LUT


Color Grading指的是在实际Tomemapper前进行的一次颜色的调整和修正。


虽然可以在引擎中进行调整，但是使用LUT会更方便一些。


Color Grading可以使得场景向预先设定的场景风格靠拢，LUT的制作方法可以参考官方的[[LUT文档](https://docs.unrealengine.com/en-us/Engine/Rendering/PostProcessEffects/UsingLUTs)]。


Tonemapper的属性，像是WhiteClip可以将一些不真实的颜色Clip掉，但是Tonemapper的属性最好对于一个项目是不变的。针对场景颜色修正最好维持在Color Grading内。


## 细节汇总


### 光照


除了天空光之外，其他的光照都有提供Min Roughness的设置，方便在使用一些光照却不希望其本身产生过高的反射的情况。


点光源在进行光照计算时，成本上接近于6个Spot Light，在使用时要进行留意。


光照的Intensity不够的情况下，可能会出现无法覆盖设定的Radiu的情况。


UE4的动态光照是有缓存的，但是如果有巨大的动态光照的话，当玩家经过是会导致缓存更新，容易产生效率问题。不过本身动态光照优化时就需要注意光照的覆盖范围，所以不需要特别的留意。


Direct Light推荐的默认Intensity是3.141。


Stationary Light有一个Use Area Shadows for Stationary Light可以使得阴影效果更加柔和，光照的衰减也会更加真实。


当场景太暗时，首先检查Auto Exposion设置，然后检查Base Color是否太暗。


不要轻易使用Emmisive来调亮或者简单的调高灯光的亮度或者使用FakeLight，使用Emmisive的时候需要留意是否破坏了整体场景的光照平衡。


### SkyLight


#### Lower Hemisphere Is Solid Color


可以模仿地面的反光效果，例如地面比较绿的话将天空光的这个选项打开，将颜色改为绿色就能获得仿佛是绿色的地面的反光效果。


在设置时注意要选用比较接近Base Color模式下的地面平均色为好。


#### CubeMap


除了捕捉之外，SkyLight也支持指定外部的CubeMap。


导入外部的贴图的话，要注意关掉MipMap和压缩。


天空贴图的导入最好选择EXR的方式，否则贴图的Wrap就需要天空球额外的作旋转处理。这个建议没有测试过，所以不是很明白。


自制天空球时要让其半径足够大，否则会阻挡大气雾和直射光。


#### DFAO


这个功能是依赖于SkyLight的，必须将天空光置为Moveable才能使用。DFGI的功能开关目前似乎是与DFAO绑定的，所以要使用的话SkyLight必须也变成Moveable的。


### Volumetric Lightmaps


近期的版本更新中，引擎引入了新的静态光照缓存方式。


详细的作用和变更可以参考[[官方文档](https://docs.unrealengine.com/en-us/Engine/Rendering/LightingAndShadows/VolumetricLightmaps)]，由于变更了间接光照缓存的存储和插值方式。


使得预烘培的光照能够更好的对场景进行贡献。


最大的帮助之一就是Foliage的光照效果了。


在之前的版本中，Foliage的光照始终都有很多麻烦。尤其是对开放式的场景，如果使用静态光照的话，会导致贴图空间的大规模消耗。


虽然草的话可以使用Landscape Grass Type中的使用Landscape光照信息来解决，对于树而言就没有办法了。


基本上的解决方案只有将AO这些光照信息事先烘培到贴图上，静态光照的树的阴影确实很好看，但是对于游戏环境就很不适宜了。


 


在有了Volumetric LightMaps并更新到4.19的话，就可以通过调整物体的Lightmap Type来让树获得Volumetric LightMap的信息，形成很好的阴影效果。


 


另外，关于Foliage的wind，如果动态的效果不是很好，可以打开项目设置中的Accurate velocities from vertex deformation，这样的话WPO之类的动态效果就会写入到速度缓存中，能够获得TAA更好的处理。


Wind的特效，可以将其与水的运动材质在world space上相乘获得更好的随机运动效果。可以进一步使用UV来控制使得更高的像素获得更多的运动。


Speed tree color variation的随机方式有一定的问题，可以在world space上使用一张GrassNorise来实现颜色的随机效果。


### 动态GI


由于LPV是由LionHead提交到引擎的，而该工作室已经关闭，所以Epic官方在最近的版本中并没有对其进行太多的改进。所以LPV的“实验性”的标签也一直都没有去掉。


动态GI上，目前Nvidia有提供Vxgi的UE4分支，但由于是非Epic官方的分支，在更新步调上多少会有一些滞后性。


而引擎内部有DFGI可供使用，但是由于使用到了Volumetric Distance Field，对于显卡本身的特性支持是有要求的。


### PostProcess


PP中的Lightmass相关选项，理所当然的，在强制不使用静态光照时是没有作用的。


而其中的AO CubeMap的作用会被SkyLight中的相关选项覆盖掉所以要注意。


AutoExposion在洞穴中可以使用Min Brightness 0.1和Max Brightness 0.13这样的值进行调整。


Lens中Dirt Mask用于模拟镜头上的不光滑点在光照下引起的折射泛光，而Lens Flare则模拟强光本身在镜头上引起的泛光。这两者都可以额外的指定Texture。


Bloom method中可以选择Convolution，使用FFT的方式来生成更真实的Bloom效果，但是由于性能消耗较大，可能不适合用于游戏中。


### Distance Field


如果使用了DFAO之类的依赖距离场的特性的话，注意在Depth Field预览中查看场景中的物体是否正确的生成了距离场。


已知的使用率距离场的材质节点有：DistanceToNearestSurface和Distance Field Gradient，一旦用来的话就要注意场景的距离场设置是否正确。


对于粒子使用了距离场碰撞的也是如此，更多的关于距离场的设定可以参照[[官方文档](https://docs.unrealengine.com/en-us/Engine/Rendering/LightingAndShadows/MeshDistanceFields)]。


### World Setting


世界设置中的LightMass的设定可以调整静态光照的烘培设置。


如果要在材质中使用Precomputed AO Mask的话，一定要记得在这里打开相应的生成开关。


关于Bounce的设定，在SkyLight支持Multi Bounce之后，之前版本中用到的一些Trick就不是那么必要了。


同时，虽然官方描述说Bounce的上升对场景的贡献比较少，但是当作封闭性比较强的场景中，多的Bounce可以让光照的预计算传播的更远。


如果Indirect Lighting Quality如果上升的话，就没有必要提高Indirect Lighting Smooth了。


Static Lighting Level Scale这个选项的影响很大，不再必要的时候最好不要修改。


### 杂项


#### Contact Shadow


这个是Point Light才有的功能。Contact Shadow可以用于增加角色的细节特效，同时可以加强视差贴图的效果。


对于视差贴图的情况，pixel depth offset上必须有对应的输出信息才能生成遮蔽效果。


#### Early Z-Pass/D-Buffer Decal


据说在没有这个功能之前，Decal与静态光照的结合相当的让人痛苦。


由于没有实际遇到过，所以不好描述呢。


#### SSR


ssr对场景的遮蔽效果还是有比较大的贡献的，需要注意的是r.SSR.Quality会锁定PP中的SSR质量上限，导致即便调到更高的值也没有什么质量上的变化。


如果要调整Reflection Captrue的话，可以将SSR暂时的关掉。


#### Subsurface


似乎在材质的制作中，会有经常用到Subsurface的情况。


有看到冰块和树叶使用到这种Shading model，不过由于之前没有接触过这方面的工作流，只是对引擎方面的调整稍微看了一下，这个可能要到用到的时候才会继续研究呢。因为似乎在很多材质上都会用到Subsurface的样子。


subsurface需要注意的是，目前的引擎中Static Light并不会参与Subsurface的计算。


#### Tessellation


在使用的时候，world displacement可以与VertexNormalWs相乘，获得更好的效果。


以及，在Lighting Only的预览中是看不见Tessellation的节点效果的。


Tessellation最好做一下DepthFade以在远处物体上关闭，避免不必要的性能消耗。


#### Gbuffer Hint


这个功能在Show/Developer里面，不过打开之后只有在左上角的功能提示。


在视频中也没有看到这个功能实际的被使用到，所以不是很明白到底应当如何使用呢。


#### 天空球


由于Daedalus本人似乎不是很喜欢使用官方的天空球所以只有一开始的视频中有使用到。


天空球有提供绑定到作为太阳光的Directional Light上的功能，同时可以由太阳光的角度来决定天空球的颜色。


