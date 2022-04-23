---
layout: post
status: publish
published: true
title: UE4光照问题排查指南
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2031
wordpress_url: http://blog.ch-wind.com/?p=2031
date: '2017-10-21 13:49:23 +0000'
date_gmt: '2017-10-21 05:49:23 +0000'
tags:
- UE4
- Lighting
---
这个是官方Wiki中光照问题排查指南的总结，对于排查光照问题很有帮助。


由于文章实在太长，所以并不是逐字翻译。但是会尽量保留所有的内容，之前的文章有重复的部分会导向以前的部分。官方Wiki的原始文章地址在[[这里](https://wiki.unrealengine.com/LightingTroubleshootingGuide)]。


## 通用设定


### 为何我的阴影是黑色的？


通常阴影纯黑是由于没有辅助的填充光照造成的，这种情况通常发生在开放场景中只有一个代替日光的直射光时。这时需要在场景中添加一个Sky Light作为全局光照，由于光照的反射模拟是有限的，天光可以有效的对现实中的光照进行模拟。


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image001.png)


### 将BSP转化为Static Mesh时光照贴图设置错误


这个似乎是早期版本的问题，现在（4.18）已经不会有这个问题了。不过光照贴图的自动设置Index是0，出现问题时可以排查这里。


当将BSP物体转化为模型体时，可能会看到这样的错误


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image002_thumb.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image002.png)


这个是由于光照贴图没有完全的自动设定造成的，需要在SM的设定中手动的指定光照贴图分辨率和光照贴图的UV Channel。


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image003_thumb.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image003.png)


### 如何停止使用光照贴图？


如果整个项目都不使用的话，可以在项目设定中关闭静态光照：


[![clip_image004](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image004_thumb.png "clip_image004")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image004.png)


或者只是在单独的地图的世界设置中禁用预计算光照：


[![clip_image005](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image005_thumb.png "clip_image005")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image005.png)


会有提示，需要重新构建一次光照才会清除当前地图内的光照数据。


### 为何我的模型一部分不见了？


和在建模软件中不同，UE4会对模型的面进行可见度裁剪。如果模型的一部分在UE4中不可见，可以按Alt+2进入线框模式，查看导入是否正确。


通常的情况下对模型进行修改比较好。


如果不想修改模型的话有两个解决方案：


选中对应的物体，打开双面光照


[![clip_image006](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image006_thumb.png "clip_image006")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image006.png)


Lightmass中的是静态光照的开关，Shadow Two Sided则决定了是否作为双面物体进行动态光照阴影计算。


### 将物体材质设定为双面的


在对应物体的材质中将其修改为双面材质


[![clip_image007](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image007_thumb.png "clip_image007")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image007.png)


### 为何突然光照效果变得不一样了？


编辑器内部有自动调整渲染级别的设定，在渲染帧率下降时，编辑器会提示是否下调渲染等级，如果没有留意的话会发现渲染结果突然变得不一样了。直接对设置进行修改就好了


[![clip_image008](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image008_thumb.png "clip_image008")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image008.png)


去掉“显示器编辑器偏好设置？”的勾选，就不会自动进行渲染级别调整了


### 为何光照上有个红叉？


Stationary Light在同一个被覆盖区域中只能有4个


[![clip_image009](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image009_thumb.png "clip_image009")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image009.png)


当超过这个数目时，范围最小的那个Stationary Light会被转化为动态光源。


由于动态光源拥有更高的运行时开销，所以需要注意。


这里的修正上只能对光源的布局进行重新规划。


### 光照贴图错误


光照贴图在设定上必须在0~1的UV空间内，超过的话就会在烘焙时提示警告Lightmap Overlapping by xx%。


当然还有一些其他的报错，光照贴图需要注意以下问题：


* 不要有重叠的部分
* 不要超过0~1的UV空间
* Flag-Mapping并不是最好的方式且经常导致光照贴图错误
* 尽量占满UV空间
* 如果模型很大而且复杂，最后分成数个物体，这样也能有助于裁剪等机制
* 尽量减小光照贴图分辨率以减少贴图尺寸
* 相互不接触的线之间要保持至少2像素的距离，以防止光照污染


更多的内容可以参照官方的[[光照贴图指南](https://docs.unrealengine.com/latest/INT/Engine/Content/Types/StaticMeshes/LightmapUnwrapping/)]。


### Post Process中GI的设定


PP中的GI设定可以对光照效果产生很大的影响，官方有一个示例就是通过两个PP的动态切换来实现灯光效果的变更。


[![clip_image010](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image010_thumb.png "clip_image010")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image010.png)


### Capsule Shadows


这个是4.11版本的新特性，似乎和问题排查关系不大，可以参考之前的[介绍](https://blog.ch-wind.com/ue4-lighting-and-optimize/#Capsule_Shadows)。


## 动态光照


动态光照在使用上比静态光照直观些，不需要每次都重新构建就能看到效果。


### 直射光独有属性：CSM


[![clip_image011](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image011_thumb.png "clip_image011")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image011.png)


这些属性都是决定动态光照级联切换的，在显示中打开


[![clip_image012](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image012_thumb.png "clip_image012")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image012.png)


可以更直观的看到效果


Dyamic Shadow Distance为光照的覆盖的范围，设置为0的话等于禁用这个光照。Stational光照的默认设定为0，也就是不开启动态光照。


Num Dynamic Shadow Cascades为动态贴图的过渡级别，越多的话动态光照的效果就越好，但是也更消耗性能，设置为0的话等同于禁用动态光照。


由于原文章中能够很直观的看到各个属性的调节的[效果](https://wiki.unrealengine.com/LightingTroubleshootingGuide#Directional_Light_ONLY:_Cascaded_Shadow_Maps_Settings:)，打开Shadow Frustrums就可以很好的进行观察，这里就不继续介绍了。


### Far Shadow


远景物体的阴影投射，这一部分之前有总结过，可以移步以前[Far Shadow](https://blog.ch-wind.com/ue4-lighting-and-optimize/#Far_Shadow)的文章。


这里官方提到了额外的注意事项，就是Far Shadow Distance应当比CSM的距离要远，在运算上Far Shadow会在设定距离与CSM距离之间进行Cascade Count次级联运算。


[![clip_image013](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image013_thumb.png "clip_image013")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image013.png)


同时尽量只给大的物体投射Far Shadow，因为对于小的物体而言，Far Shadow其实是不是很必要却有额外消耗的。


### CSM调整


动态光照的污染等问题，通常通过调整CSM的属性来进行排查。


[官方的示例](https://wiki.unrealengine.com/LightingTroubleshootingGuide#Adjusting_Cascades_for_better_Quality:)中是通过调整Cascade Distribution Exponent来解决问题的，但是由于室外场景比较多变，并没有


统一的解决方案，通过Shadow Frustrums工具的配合，对上面的几个属性进行调整比较好。


### 动态光照通用属性


Shadow BIas通常用于调整动态阴影导致的自投影问题，一个过小的值将会导致阴影从很近的地方开始计算。


[![clip_image014](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image014_thumb.png "clip_image014")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image014.png)


Shadow Filter Sharpness则用于调整阴影的边缘是否尖锐


[![clip_image015](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image015_thumb.png "clip_image015")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image015.png)


### 为何光照在远处时穿过物体？


这个问题是由于用于遮挡动态光照的物体在距离很远时已经被裁剪造成的。


[![clip_image016](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image016_thumb.png "clip_image016")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image016.png)


比较直观的解决方案是直接拉大那个物体的Bound来避免其被裁剪。可以直接在物体实例中设置


[![clip_image017](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image017_thumb.png "clip_image017")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image017.png)


放大Bounds Scale，在显示中打开Bounds的预览可以很好的对其进行规划。


但是这里通常情况下的建议是避免这种光照使用方式，这里可以使用聚光灯或者光照函数、IIES来更加高效的实现这个效果。


使用物体遮挡来对光源的形状进行控制并不是一个好主意。


## 静态光照


光照贴图分辨率/阴影质量


这里的建议虽然是官方的，但是并不能对所有的情况通用，只是作为光照问题排查的基础。


光照贴图分辨率用于调整阴影的质量，这里需要注意的是，这个分辨率是决定投影在其上的阴影的精度的，并不是决定其自身的阴影精度的。也就是说物体的阴影的质量是更加这个阴影投射到的物体的光照贴图分辨率决定的。


网格物体的分辨率必须是POT的，且数值越大阴影质量越高


BSP物体的分辨率则相反，数值越低阴影质量越高


Landscapes的分辨率调节则是一个乘数，越大质量越高


### Seams


[![clip_image018](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image018_thumb.png "clip_image018")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image018.png)


就是物体接合处的光照效果不真实的问题，这个问题通常是由间接光照引起的，因为间接光照计算时各个物体相互之间是独立的，因此计算的结果就会不合理。


官方的建议之一是调整世界设置中的静态光照参数


Indirect Lighting Quality设置到2或者更高


Indirect Lighting Smoothness设置到0.65~0.75之间


Static Lighting Level Scale这个属性由于是对计算单位进行缩放，虽然调小会有更好的阴影过度，但是会明显的提高光照计算量。通常应用于建筑展示领域，不建议在游戏开发中使用。


通常上面的调整效果是有限的，其实这个问题更多的应该从关卡构建上入手：


* 不要过分的将关卡模块化，当可以有一整面墙的时候就不要将其拆分为好几个部分。这样可以防止问题的同时减少绘制调用次数。
* 使用物体对接缝处进行遮蔽。


### 构建光照时报错Overlapping UV error


这个之前就有提到，大概是专门又详细的说明一次。


Overlapping和Wrapping都是UV错误的形式，可以使用[错误着色](https://blog.ch-wind.com/ue4-lighting-and-optimize/#Error_Coloring)进行可视化排查，但是通常直接查看UV就能看出问题。


### 如何使用编辑器生成光照UV


在Mesh的编辑窗口


[![clip_image019](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image019_thumb.png "clip_image019")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image019.png)


勾选生成光照贴图UV后，设置下面三个属性就可以了。


通常源光照贴图索引使用的应当是用于贴图渲染的那个UV通道。


目标索引则是要生成的UV索引。


点击应用修改后就会生成光照UV。


这时候就可以在上面的通用设定中对光照UV的索引进行设置了。


[![clip_image020](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image020_thumb.png "clip_image020")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image020.png)


### 间接光照回弹次数


可以在世界设定中对间接光照的回弹次数进行设定，回弹计算的次数越多，间接光照的效果越好。


[![clip_image021](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image021_thumb.png "clip_image021")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image021.png)


设定上拖动只能在1~4之间，但是可以手动输入更大的值。


回弹计算在第一次计算时成本最高，之后计算的话成本不高，但是也不会有什么太大的结果变化。通常4次计算就足够了。


为何间接光照产生了很多“斑点”？


通过调节光照贴图分辨率可以缓解这个问题。


虽然调整光照贴图质量以及平滑度也能解决这个问题


[![clip_image022](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image022_thumb.png "clip_image022")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image022.png)


但是通常会导致过高的光照构建消耗，并不推荐。


提高间接光照回弹次数能够起到比提高光照贴图分辨率更好的效果。


一个更好的解决方案是，不要让区域只受间接光照的影响，添加一个不投影的光源就能很好的防止斑点的出现。


### "Lighting needs to be rebuilt"是什么？


光照需要重新构建，点击构建按钮下的仅构建光照即可。


[![clip_image023](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image023_thumb.png "clip_image023")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image023.png)


### Unbuilt Actors List


如果构建后依然出现这个提示，可以在输出日志中敲入命令DumpUnbuiltLightInteractions来列出未构建的物体。


通常会出现这类物体可能还是由于蓝图或代码在物体摆放后对其移动造成的。


通过这个列表对问题进行排查即可。


### Statistics Window


[![clip_image024](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image024_thumb.png "clip_image024")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image024.png)


这个窗口可以排查是哪些物体过度的消耗了光照构建的时间。


### Lanscape上草的阴影问题


可以在GrassType上找到一个选项，


[![clip_image025](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image025_thumb.png "clip_image025")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image025.png)


让草直接使用Landscape的光照贴图即可。


### 通过命令行构建构造


4.10.2后的功能


UE4-Editor.exe [Project Folder Path] -run=resavepackages -buildlighting -MapsOnly -ProjectOnly -AllowCommandletRendering -Map=[Name of map]


其中-Map是可选项，不过去掉的话会转而构建所有的地图。


### Foliage的光照


在Foliage中可以使用Light Map Resolution选项覆盖掉Mesh本身的光照贴图分辨率。


[![clip_image026](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image026_thumb.png "clip_image026")](https://blog.ch-wind.com/wp-content/uploads/2017/10/clip_image026.png)


由于Foliage实际上是被打包在一起的，所以所有的FoliageInstance的光照贴图将会合在一张里面，所以缩小其分辨率是有一定必要的。


尤其是在构建时出现提示Instanced_Foliage_Actor_[X] lightmap is too large and should be reduced的时候，就可以在这里进行修改。


另外还有一些官方的Foliage官方建议：


* 如果要让Foliage使用风相关的特性的话，要避免对Foliage使用静态光照，因为阴影不会随风而动。
* 减少光照贴图分辨率以减小贴图空间消耗
* 在Grass上禁用静态光照，因为通常Grass是数目极大，会造成明显的构建消耗


