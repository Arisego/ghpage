---
layout: post
status: publish
published: true
title: UE4粒子系统基础属性整理
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1319
wordpress_url: http://blog.ch-wind.com/?p=1319
date: '2015-06-30 11:30:50 +0000'
date_gmt: '2015-06-30 03:30:50 +0000'
tags:
- UE4
- 粒子
---
要在游戏中实现炫丽的特效，最有效的方法之一就是使用粒子系统。


当前UE4版本为4.8.1。


UE4拥有一个非常强大的模块化粒子系统编辑器，名为Cascade。


与通用的粒子系统设计一样，UE4的粒子系统由发射器产生粒子，并通过设置发射器和粒子的属性来实现不同的效果。在一个单一的粒子系统中，UE4可以同时添加多个发射器，通过组合可以实现非常炫丽的效果。在编辑器中，发射器的计算顺序是从左到右的，而模块的运算顺序是从上到下的。UE4的粒子系统同时支持LOD，以有效的控制粒子在场景中对运算量的消耗。系统中粒子也可以接收光照，只要使用材质时进行设定即可。当前文档中关于LOD上的bLit标签是有问题的，可参照[AnswerHub](https://answers.unrealengine.com/questions/44995/where-is-blit-in-cascade.html)。


和其他UE4的部分一样，大部分的属性都非常的易懂。但是将文档过一遍是很有必要的，这样才能知道系统都提供哪些功能，哪些是系统做不到的。


 


### Particle System Class


粒子系统本身的属性，点击没有发射器的空白处就会出现。


*Particle System*


**System Update Mode**


粒子系统的更新模式，分为实时和固定两种，通常情况下使用实时即可。


**Update Time_FPS**


固定时间模式下的步长设定。


**Warmup Time**


预热时间。粒子系统初始时应该处于的时间，通常用于雾气等环境效果，保证游戏开始时粒子系统就处于完整的状态。会消耗一定的运算量。


**Warmup Tick Rate**


系统预热步长。越低的数值精度越高，相反的，提高这个数值就能降低运算量消耗。0代表默认步长。


**Orient ZAxis Toward Camera**


将粒子的Z轴锁定到摄像机。


**Seconds Before Inactive**


当粒子系统不再被渲染时，经过多长时间才停止运算，0代表不停止。


 


*Thumbnail*


内容浏览器的缩略图用属性，没有什么特别值得关注的地方。


 


*LOD*


粒子系统的LOD相关属性。


**LOD Distance Check Time**


检查粒子系统的距离的时间间隔，只有当LOD Method设定为自动时才起作用，用于自动切换LOD的显示。


**LOD Method**


LOD的切换方式。Automatic为自动由距离决定，DirectSet为由代码进行调整，ActivateAutomatic为系统初始化时进行一次判定之后交由代码自行调整。


**LOD Distances**


LOD级别的距离范围设定，每个数值代表当前等级的最大距离。


**LOD Settings**


如开头所描述，由于当前Lit属性似乎不可用，这个属性当前也没有意义。


 


*Bounds*


通过开关控制的边界盒体，由此决定当粒子不在视野中时不再对粒子系统进行运算，以降低系统消耗。


直接点击上方工具栏的『设置固定边界』，就会自动生成一个，然后在属性中可以手动进行微调。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/06/image_thumb4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/06/image4.png)


 


*Delay*


延迟，设置在调用ActivateSystem之后粒子系统延迟激活的时间。


**Delay**


延迟的时间。


**Delay Low**


延迟的下限时间，需要下面的范围开关启动。


**Use Delay Range**


延迟范围开关。打开之后延迟将会在[Delay Low ~ Delay]之间进行随机。


 


*Macro UV*


中文名称不明。该UV贴图坐标用于将一个贴图平铺在所有的粒子上。


**MacroUVPosition**


决定整个UV平铺的中心。


**MacroUVRadius**


决定UV平铺的半径。


 


*Occlusion*


遮蔽。


**Occlusion Bounds Method**


遮蔽边界方式。None为不启用遮蔽，Particle Bounds为使用粒子系统定义的边界，Custom Bounds为自定义遮蔽边界。


**Custom Occlusion Bounds**


自定义边界，调整时可以在视口中看到预览。


 


*Materials*


**Named Materia Slots**


可暴露给外界蓝图使用的材质参数插槽。


 


### Particle Emitter Class


发射器的属性。


*Particle*


**Emitter Name**


发射器名称


**Initial Allocation Count**


当这个值不为0时，发射器将采用这个数值作为初始化粒子发射数。


**Quality Level Spawn Rate Scale**


显示质量设置缩放比例，决定当系统的视频设置较低时的缩放比例，用于降低系统消耗。


**Detail Mode**


发射器的显示精度，当系统的显示精度低于这个设置时，这个发射器将不会工作。


**Disabled LODs Keep Emitter Alive**


当LOD为禁止状态时仍然保持发射器为激活状态。


 


*Cascade*


在编辑器中的显示设定。


**Emitter Render Mode**


发射器的渲染模式。Normal为正常渲染，Point为近显示点，Cross为显示十字交叉线，Lights Only为仅光照，None为不显示。


**Emitter Editor Color**


发射器在编辑器中的颜色。


**Collapsed**


是否展开显示发射器。


 


### Particle Module Class


粒子模块的基类，提供一些通用的属性。


*Cascade*


**3DDraw Mode**


如果打开的话就会显示相应的辅助渲染信息。


**Module Editor Color**


模块在编辑器中的颜色。


 


### TypeData Modules


发射器的类型。添加时为默认的类型，可以通过添加类型数据进行修改。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/06/image_thumb5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/06/image5.png)


可以添加的类型一共有五种，能够实现不同类型的粒子效果。


除了TypeData之外，还有很多其他的模块。作为对粒子发射器的控制被添加到粒子发射器上，以实现不同的粒子效果。


 


### Required Module


粒子发射器的一些基本属性在这个模块里进行设置。这个模块是必须的，无法手动删除。


 


*Emitter*


发射器相关属性。


**Emitter Materia**


粒子发射器发出的粒子所使用的材质。


**Emitter Origin**


粒子发射器的发射起点。


**Emitter Rotation**


发射粒子的初始旋转。


**Screen Alignment**


粒子相对与摄像机的朝向。




|  |  |
| --- | --- |
| FacingCameraPosition | 粒子旋转朝向摄像机位置（忽略摄像机选择） |
| Square | 面向相机，使用X轴进行统一缩放 |
| Rectangle | 面向相机，非统一缩放 |
| Velocity | 朝向摄像机和粒子自身的运动方向，运行非统一缩放 |
| Away From Center | 背离中心方向 |
| TypeSpecific | 使用TypeData中的定义（仅Mesh类型可用） |


**Use Local Space**


是否使用本地空间或是使用父节点的坐标变换。


**Kill on Deactivate**


是否在非活动时销毁粒子。


**Kill on Completed**


是否在执行完成时销毁自身。


**Sort Mode**


排序模式。




|  |  |
| --- | --- |
| PSORTMODE_None | 不进行排序 |
| PSORTMODE_ViewProjDepth | 根据视图映射深度排序 |
| PSORTMODE_DistanceToView | 根据粒子到摄像机的距离排序 |
| PSORTMODE_Age_OldestFirst | 粒子的生存时间排序，最旧优先 |
| PSORTMODE_Age_NewestFirst | 粒子的生存时间排序，最旧优先 |


**Use Legacy Emitter Time**


是否使用传统发射计时。传统发射计时采用EmitterDuration和SecondsSinceCreation来计算发射器时间，在循环或是变化时间粒子系统中可能会遇到问题。当不使用时，会使用新方法，利用DeltaTime来进行计算。


**Orbit Module Affects Velocity Align**


当开启时，环绕模块所产生的影响将会应用到速度屏幕对齐（Screen Alignment： Velocity）的粒子上。


 


*Duration*


时间间隔，发射器开始循环之前的间隔时间。


**Emitter Duration**


发射器进入循环前的间隔时间，为0则不循环。


**Emitter Duration Low**


发射器间隔低值，需要下面的开关打开才有效。


**Emitter Duration Use Range**


间隔时间范围开关。当打开时间隔时间将在[Emitter Duration~Emitter Duration Low]之间随机。


**Duration Recalc Each Loop**


每一次循环完成后都会重新计算间隔时间


**Emitter Loops**


发射器循环次数，为0则永久循环。


 


*Delay*


**Emitter Delay**


延迟时间。与Duartion不同的是，Delay的期间发射器是不发射粒子的。


**Emitter Delay Low**


延迟时间低值，需要下面的开关打开才有效。


**Emitter Delay Use Range**


延迟范围开关。打开后延迟将会在[Emitter Delay~Emitter Delay Low]之间随机。


**Delay First Loop Only**


仅在第一次循环前延迟


 


*Sub UV*


Sub UV属性是针对Sub UV模块的，详情可以参考这里：[SubUV模块属性及应用](https://blog.ch-wind.com/ue4-particles-subuv-module/)。


**Interpolation Method**


插值方法。




|  |  |
| --- | --- |
| None | 不在应用SubUV功能 |
| Linear(线性) | 按照子图像顺序进行线性的过渡，但是与下一张图像不混合 |
| Linear_Blend (线性_混合) | 按照子图像顺序进行线性的过渡，与下一张图像进行混合 |
| Random(随机) | 下一张子图像随机的抽取，但是与下一张图像不混合 |
| Random_Blend(随机_混合) | 下一张子图像随机的抽取，与下一张图像进行混合 |


**Sub Images Horizontal**


贴图X轴上的子图像数量。


**Sub Images Vertical**


贴图Y轴上的子图像数量。


**Scale UV**


UV缩放的比例。


**Random Image Chagnes**


粒子生命周期中随机图像的变换次数。


 


*Macro UV*


与粒子系统的Macro UV属性类似。


 


*Rendering*


**Use Max Draw Count**


是否使用最大绘制次数限制


**Max Draw Count**


最大绘制次数的限定值


**UVFlipping Mode**


所有粒子的UV翻转模式 。




|  |  |
| --- | --- |
| Flip UV | 翻转UV |
| Flip Uonly | 翻转U |
| Flip Vonly | 翻转V |
| Random Flip UV | 随机翻转UV |
| Random Flip Uonly | 随机翻转U |
| Random Flip Vonly | 随机翻转V |
| Random Flip UV Independent | 随机翻转UV（UV相互独立） |


 


*Normals*


**Emitter Normals Mode**


发射器法线的计算模式




|  |  |
| --- | --- |
| ENM_CameraFacing | 默认模式，法线由朝向几何体的摄像机生成 |
| ENM_Spherical | 以Normals Sphere Center为中心的球体来生成法线 |
| ENM_Cylindrical | 以穿过Normal Sphere Center并以NormalsCylinderDirection为方向的圆柱体来生成法线。 |


**Normals Sphere Center**


法线生成中根据选项不同会用到的参数。


**Normals Cylinder Direction**


法线生成中根据选项不同会用到的参数。


 


**Materias**


Named Materia Overrides


指定材质插槽名称，以替换发射器使用的材质。插槽中的材质则可以通过蓝图进行设置。


 


### Spawn


这也是一个必须的模块，无法删除。用于设定粒子是如何发射出去的。


 


*Spawn*


**Rate**


每秒中产生粒子的个数。


**Rate Scale**


发射速率缩放系数。


**Apply Global Spawn Rate Scale**


如果打开此开关，那么发射器的缩放因子将会受到全局设定中的r.EmitterSpawnRateScale数值影响。


**Process Spawn Rate**


打开之后才会处理Rate的设置，当发射器中有多个Spawn时，其中任何一个关闭这个选项都将导致Rate不被处理。


 


*Burst*


爆发。在给定时间内强制发射一定数量的粒子。


**Particle Burst Method**


粒子爆发方式。




|  |  |
| --- | --- |
| Instant | 立即 |
| Intepolated | 插值 |


**Burst List**


粒子爆发参数列表，用于指定时间和粒子爆发。数组元素的属性有三个。




|  |  |
| --- | --- |
| Count | 爆发的粒子个数 |
| Count Low | 爆发的粒子下限个数，为-1时则无作用 |
| Time | 爆发的时间点 |


**Burst Scale**


爆发的缩放因子。


**Process Burst List**


打开之后才会处理Burst List，发射器中任何一个Spawn模块没有打开这个开关，就会导致Burst List不被处理。


 


*Cascade*


通用的编辑器属性。


 


--------------------------------------


至此，粒子系统部分的主要属性算是整理了一遍。但是还有大量的模块和粒子类型没有进行研究，基本的参数含义在只是知道含义的情况下也没什么用。因此决定接下来从实践的角度对粒子系统进行研究。


