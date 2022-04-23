---
layout: post
status: publish
published: true
title: UE4粒子光束类发射器及应用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1367
wordpress_url: http://blog.ch-wind.com/?p=1367
date: '2015-07-04 13:24:03 +0000'
date_gmt: '2015-07-04 05:24:03 +0000'
tags:
- UE4
- 粒子
- Beam
---
光束类粒子广泛应用于激光、闪电等有传输路径的效果的模拟。 光束类发射器将粒子由源点到目标点之间相互连接并形成一个流。


当前UE4版本：4.8.1。


光束粒子的使用首先要将类型模块改为Beam Data Type，然后根据需要添加模块和修改属性。


 


## Beam Data Type


光束粒子类型模块，添加了这个模块之后发射器将会变成光束型。


 


*Beam*


**Beam Method**


光束方法。有三种。Distance为沿着X轴方向的光束，Target为两点之间的光束，Branch暂时没有功能。


**Texture Tile**


调整粒子材质的平铺数，只对第一套UV有效。当Texture Tile Distance被启用时会被其设置覆盖。


**Texutre Tile Distance**


每一个粒子材质平铺的宽度，为0时关闭设置。


**Sheets** 


沿着光束所渲染的面片的数量。


**Max Beam Count**


光束的数量上限。


**Speed** 


光束的速度，为0时则直接跳转。


**Interpolation Points**


当这个设置大于0时，将会在源点和目标点之间进行插值，可以增强噪波的特效。


**Always On**


当打开这个开关时，发射器将会保证始终有粒子是存活的。


**Up Vector Step Size**


决定光束的Up向量的方法




|  |  |
| --- | --- |
| 0 | 在光束的每一个点进行计算 |
| 1 | 在光束的开始点计算并应用到所有点 |
| N | 插值N个点并计算（当前未实现） |


 


*Branching*


**Branch Parent Name**


分支的父发射点名称，必须在同一个粒子系统内。Beam Method为Branch才可用，当前无效。


 


*Distance*


**Distance**


光束的传播距离，Beam Method为Distance时有效。


 


*Taper*


**Taper Method**


光束随着长度变少的方式。




|  |  |
| --- | --- |
| None | 光束不会变少 |
| Full | 从源到目标点之间变少，无视长度，相对计算。 |
| Partial | 从源到位置之间变少，源为0，位置点为1 |


**Taper Factor**


光束变少因子。当使用曲线编辑器时，时间轴0.0代表光束的源头，时间轴1.0代表目标点处。


**Taper Scale**


光束变少缩放。缩放为Taper Factor与Taper Scale的乘积。


 


*Rendering*


**Render Geometry**


是否渲染光束的几何体。


**Render Direct Line**


调试用。在源点和目标点之间绘制一条线。


**Render Lines**


调试用。沿着光束渲染生成线。


**Render Tessellation**


调试用。绘制源和目标之间的细分路径。


 


*Cascade*


通用编辑器属性


 


## Beam Modules


当前光束发射器共有4种模块可添加并用于配置光束发射器表现：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image7.png)


 


### Beam Modifier


光束修改器。用于修改光束的源点或目标点的属性。


*Modifier*


**Modifier Type**


设定修改器的修改目标。Source为源点，Target为目标点。


 


*Position*


**Position**


修改位置值，可锁定坐标。


**Position Options**


与Position属性关联的选项




|  |  |
| --- | --- |
| Modify | 选中才应用修改 |
| Scale | 选中后会将当前的设置缩放到指定的长度，而不是使用修改后的长度进行计算 |
| Lock | 选中是粒子生命周期中该数值将被锁定 |


 


*Tangent*


**Tangent**


修改切线，可锁定坐标。通过切线来决定运算基础线的弧度。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image8.png)


**Tangent Options**


与Tangent属性关联的选项




|  |  |
| --- | --- |
| Modify | 选中才应用修改 |
| Scale | 选中后会将当前的设置缩放到指定的长度，而不是使用修改后的长度进行计算 |
| Lock | 选中是粒子生命周期中该数值将被锁定 |


**Absolute Tangent**


在世界空间中使用绝对切线。


 


*Strength*


**Strength**


修改强度。添加之后会使得光束有一个动态的移动效果，类似于给点加上受力。对开启了Tangent修改的光束影响极大。


**Strength Options**


与Strength属性关联的选项




|  |  |
| --- | --- |
| Modify | 选中才应用修改 |
| Scale | 选中后会将当前的设置缩放到指定的长度，而不是使用修改后的长度进行计算 |
| Lock | 选中是粒子生命周期中该数值将被锁定 |


 


*Cascade*


通用编辑器属性


 


### Noise


在光束上加上噪波影响的模块。


*Low Freq*


**Low Freq Enabled**


是否打开低频噪波


**Frequency**


噪波的频率


**Frequency Low Range**


噪波频率下界，当非0有效。


**Noise Range**


噪波范围。用于计算噪点的分布，使用曲线时，0为第一点，而1为目标点。通常为Uniform形式，以提供一个随机的范围。


**Noise Range Scale**


噪波范围缩放。


**NRScale Emitter Time**


当打开时噪波范围缩放将会使用发射器时间，否则使用粒子时间。


**Noise Speed**


噪波速度，噪点的移动速度。只有Smooth打开时才有效。


**Smooth**


打开时会在噪点发生之后会进行平滑的移动。


**Noise Lock Radius**


噪波锁定半径。防止生成的噪点过于接近。


**Oscillate**


噪波摆动。如果开启，则噪点在发射线两端摆动。


**Noise Lock Time**


噪波锁定时间。亦即噪点生成之后停留多久进行下一次噪点生成。


**Noise Tension**


噪波张力。随着这个设置的增强，噪点之间的细分点将会受到更大的张力影响。轨迹会变得更尖锐。


**Use Noise Tangent**


使用噪波切线。如果开启则会计算每一个噪点的切线。


**Noise Tangent Strenth**


噪波切线强度。这个值越大，将会使得沿着光束的插值点受到切线方向的影响越大。当这个值为0时，Noise Tension几乎不会对轨迹造成影响。


**Noise Tessellagtion**


在噪点之间插值细分的数量。使得噪波之后的线条轨迹变得平滑。


**Target Noise**


打开时将会应用噪波到目标点。光束的终点将在设置的目标点附近进行随机。


**Frequency Distance**


噪点距离。为0时使用Frequency Low Range~Frequency来决定噪点的频率。不为零时则根据Frequency的值与这个值来共同决定分布，作用在于减少较短的光束上的噪点数，同时保证长光束上的噪点。


**Apply Noise Scale**


噪波缩放开关。


**Noise Scale**


噪波缩放因子。决定噪点远离发射线的波幅比例，在Noise Range的基础产生影响，为0则无可见的噪波效果。


 


*Cascade*


通用编辑器属性


 


### Source


源点，当未指定这个模块时发射器位置将会作为源点。


*Source*


**Source Method**


源点方式。




|  |  |
| --- | --- |
| Default | 使用Source的设定值 |
| UserSet | 用户指定，常用于武器 |
| Emitter | 使用发射器位置 |
| Particle | 使用其他发射器的粒子 |
| Actor | 使用Actor对象位置 |


**Source Name**


源名称。在Source Method为Particle和Acotr时有效，如果没有对应，则会使用Source的设定值。


**Source Absolute**


使用源点绝对位置，亦即不进行变换。


**Source**


源点位置。当Source Method为Default时有效。采用其他设定却无效时也会使用这个值。


**Lock Source**


在粒子生命周期中锁定源点。


**Source Tangent Method**


源切线方法。




|  |  |
| --- | --- |
| Direct | 使用源与目标的连线 |
| UserSet | 用户指定 |
| Distribution | 使用SourceTangent的设定值 |
| Emitter | 使用发射器的朝向 |


**Source Tangent**


源切线的设定值。


**Lock Source Tangent**


在粒子生命周期中锁定源切线值。


**Source Strength**


切线力量强度。


**Lock Source Strength**


在粒子生命周期中锁定切线强度。


 


*Cascade*


通用编辑器属性


 


### Target


目标点。


*Target*


**Target Method**


目标点方式。




|  |  |
| --- | --- |
| Default | 使用Target的设定值 |
| UserSet | 用户指定，常用于武器 |
| Emitter | 使用发射器位置 |
| Particle | 使用其他发射器的粒子 |
| Actor | 使用Actor对象位置 |


**Target Name**


目标名称。在Target Method为Particle和Acotr时有效，如果没有对应，则会使用Target的设定值。


**Target Absolute**


使用目标点绝对位置，亦即不进行变换。


**Target**


目标点位置。当Target Method为Default时有效。采用其他设定却无效时也会使用这个值。


**Lock Target**


在粒子生命周期中锁定目标点。


**Target Tangent Method**


目标切线方法。




|  |  |
| --- | --- |
| Direct | 使用目标与目标的连线 |
| UserSet | 用户指定 |
| Distribution | 使用TargetTangent的设定值 |
| Emitter | 使用发射器的朝向 |


**Target Tangent**


目标切线的设定值。


**Lock Target Tangent**


在粒子生命周期中锁定目标切线值。


**Target Strength**


切线强度。


**Lock Target Strength**


在粒子生命周期中锁定切线强度。


**Lock Radius**


光束的结束点被锁定在目标点的范围内，当光束有Speed设定时用到。


 


## 应用


光束粒子发射器的模块和参数都比较多，不在实际中应用很难掌握其具体含义。


参照官方社区的教程[Beam Particle (Tutorial)](https://wiki.unrealengine.com/Beam_Particle_(Tutorial))进行操作，是一个类似于放电现象的光束粒子。


### 材质


第一步与其他粒子系统一样，是制作材质。材质用到了两张贴图：


[![BeamPulse](https://blog.ch-wind.com/wp-content/uploads/2015/07/BeamPulse_thumb.png "BeamPulse")](https://blog.ch-wind.com/wp-content/uploads/2015/07/BeamPulse.png) [![BaseBeam](https://blog.ch-wind.com/wp-content/uploads/2015/07/BaseBeam_thumb.png "BaseBeam")](https://blog.ch-wind.com/wp-content/uploads/2015/07/BaseBeam.png)


将材质导入UE4制作成为如下的贴图：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image9.png)


Panner节点在放置之后注意设置x轴速度，默认的情况下是不会进行平移的。


### 粒子系统


材质创建完成后，新建一个粒子系统并将默认发射器的材质指定为刚刚创建的材质。同时为发射器添加Beam Data Type模块。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image10.png)


然后参照下表修改各个模块的属性：




|  |  |  |
| --- | --- | --- |
| 属性 | 值 | 目的 |
| **Lifetime Module** |  |  |
| Lifetime | 0 | 使得光束粒子一直存在。 |
| **Beam Data Module** |  |  |
| Beam Method | PEB2M_Distance | 光束将沿着X轴方向发射，便于观察效果 |
| Texture Tile Distance | 500 | 光束上贴图的长度为500单位，与下面的长度1000相匹配，使得光束上有两个“点”在流动 |
| Max Beam Count | 3 | 光束个数为3，便于之后添加噪波效果。 |
| Speed | 0 | 粒子立刻到达目标点 |
| Interpolation Points | 50 | 加强下一步噪波的特效 |
| Distance | 1000 | 光束的发射距离为1000，使得光束足够长 |


上面的属性设定完成后粒子系统的效果类似下图。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image11.png)


### 增加噪波


噪波可以使得光束拥有更多的随机效果，而不是单调的笔直的路径。


噪波模块的属性设置如下：




|  |  |  |
| --- | --- | --- |
| 属性 | 值 | 目的 |
| Frequency | 30 | 噪波频率 |
| Low Freq Enabled | 选中 | 打开噪波特效 |
| Noise Range | Vector Uniform distribution
Min:( 0, -50, -50) Max:( 0, 50, 50) | 噪点能够离开光束的范围 |
| Noise Tessellation | 10 | 使得噪波之后的光束之间的连接变得平滑 |
| Frequency Distance | 100 | 获得合理的噪点个数 |


最终效果如下：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb12.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image12.png)


 


### 属性测试


关于Beam Modifier模块中的Scale，当发射距离为1000时，如果应用修改器将发射点移动到10000。那么在没有启用Scale时，按照设定每100会有一个噪点。当Scale启用时，10000的长度上依然是10个噪点。 对于可以使用Curv型分布的变量，如果改用Curv型的话可以实现很多不同的效果，由于现在还没有具体使用到，就没有一一的去测试了。


