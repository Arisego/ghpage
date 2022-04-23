---
layout: post
status: publish
published: true
title: UE4材质初探
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1289
wordpress_url: http://blog.ch-wind.com/?p=1289
date: '2015-06-15 20:42:54 +0000'
date_gmt: '2015-06-15 12:42:54 +0000'
tags:
- UE4
- Materia
- 材质
---
UE4的材质表面上看起来很简单，可是到了用的时候却总是没有办法实现好的效果。所以特意对文档进行阅读，初步了解了一下主要知识点。


当前使用的UE4版本：4.8.0。


UE4中的材质有很多用途，可以用于光照、延迟渲染、粒子系统等等。由于暂时不会用到，目前只做了最基础的材质使用的研究，也就是说是Materia Type为Surface的情况。材质的最终输出节点上的可用项会随着功能选择的不同而有所不同。即便使用Materia Function使所有的引脚都是可用的也会在实际使用时根据选择而被禁用。


## 材质输入引脚


材质中最为关键的是作为最终输出结果的引脚，根据情况的不同有的会使用，有的并不会被使用。


**基础颜色（Base Color）**


定义材质的颜色，接受参数为Vector3(RGB)。颜色采用float形式，任何超出范围的输入数值都将被clamp到0～1的范围内。


相当于在摄影中使用偏光镜滤除由反射引起的杂光之后的物体的颜色。偏光镜的效果可参照以下对比图。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/06/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/06/image.png)


右边为加了偏光镜后的效果。


**金属（Metallic）**


定义材质接近金属的程度。0～1的范围由低到高的接近金属材质。从个人感官上，金属性决定的是类似于高光反射强度的参数。


**高光（Specular）**


在大多数情况下保留默认的0.5即可的参数。调整的是非金属材质的高光反射强度，对金属材质无效。


经实际测试，在金属性为0.5时，这个参数几乎没有可视觉识别的影响。在金属性为0时可以为增加一定程度的高光反射。


**粗糙度（Roughness）**


定义材质的粗糙程度。基本和现实生活中一样，数值越低的材质镜面反射的程度就越高，数值越高就倾向于漫反射。


**自发光颜色（Emissive Color）**


定义材质自主发出光线的参数。超过1的数值将会被视为HDR参数，产生泛光的效果。


高动态范围成像（简称HDRI或HDR）是用来实现比普通图像技术更大曝光动态范围（即更大的明暗差别）的一组技术。高动态范围成像的目的就是要正确地表示真实世界中从太阳光直射到最暗的阴影这样大的范围亮度。


**不透明度（Opacity）**


定义材质的不透明度。


**不透明蒙板（Opacity Mask）**


只在Masked Blend模式可用的参数，与半透明度不同的是。不透明蒙板的输出结果只有可见和完全不可见两种。通常用于实现镂空之类的效果。


**普通（Normal）**


其实是法线参数，通常用于连接法线贴图。UE4中文一直使用『普通』这个翻译，不知是否有什么深意……


**世界位置偏移（World Position Offset）**


世界位置偏移参数使得材质可以控制网格在世界空间中的顶点位置。


使用时如果遇到剔除投影之类的错误，则需要放大网格的Scale Bounds，虽然这样做会导致效率下降。


**世界位移（World Displacement）**


与上面的属性相似，不过世界位移只能在Tessellation属性有设置时才起作用的。


**多边形细分乘数（Tessellation Multiplier）**


同样只有在设置了Tessellation属性时才可以使用，决定的是瓷砖贴片的个数。


![DisplacementNetwork.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/MaterialInputs/DisplacementNetwork.jpg)


**次表面颜色（Subsurface Color）**


只有Shading Model为Subsurface时才有效的引脚，用于模拟类似于人类皮肤这样在光线透过表面之后会有第二种表面颜色反射的情况。


**透明涂层（Clear Coat）**


透明涂层通常用于模拟在材质的表面有一层薄的透明涂层的情况，如钢琴烤漆之类的效果。


**透明涂层粗糙度（Clear Coat Roughness）**


决定透明涂层的粗糙度。


**环境遮挡（Ambient Occlusion）**


用于连接AO贴图的引脚。


**折射（Refraction）**


用于调整透明材质的折射率的。


**像素深度偏移（Pixel Depth Offset）**


当前官方文档没有说明。


## 常用节点


引擎提供了很多非常使用的节点，不过数目有点多，只能在实际使用中熟悉才能渐渐的掌握。下面列出的是可能会经常被用到的节点：


**Panner**


对UV坐标进行平移，用于UV动画的实现。


![PannerExample.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Coordinates/PannerExample.jpg)


**Rotater** 


对UV坐标进行旋转，同样用于UV动画的实现。


![RotatorExample.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Coordinates/RotatorExample.jpg)


**BlackBody**


这个节点可以对贴图应用一个黑体辐射效果，实际效果就像是过了一遍热成像扫描。


![BlackBody.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Utility/BlackBody.jpg)


**BumpOffset** 


这个节点用于实现[视差贴图](https://zh.wikipedia.org/wiki/%E8%A7%86%E5%B7%AE%E8%B4%B4%E5%9B%BE)，使得贴图更具有真实感。


![BumpOffsetExample.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Utility/BumpOffsetExample.jpg)


**ConstantBiasScale** 


这个节点将输入值加上一个值之后再乘上一个值。例如将正弦函数的结果由[-1~1]压制到[0~1]就可以使用1，0.5的参数来操作。


**Fresnel** 


这个节点将摄像机向量与网格法线向量进行点乘并应用到0～1的范围中。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/06/image_thumb1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/06/image1.png)


当摄像机方向与网格的法线垂直时返回1，当方向一致时则返回0。Fresnel的计算在设置了法线贴图时则会使用法线贴图进行运算。这个节点可以用于区分边缘，例如玻璃材质就会使用到。


详细的用法可参照官方教程：[Material - How To Use Fresnel in your Materials](https://docs.unrealengine.com/latest/INT/Engine/Rendering/Materials/HowTo/Fresnel/index.html)。


**DepthFade** 


这个节点的作用是使得两个透明物体在叠加时显得更加自然。


![DepthFade1.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Depth/DepthFade1.jpg)


**DepthOfFieldFunction** 


这个节点的作用如其名称，提供景深的运算结果。0～1的范围代表从聚焦到模糊。


![DepthOfFieldFunction_Texture.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Utility/DepthOfFieldFunction_Texture.jpg)


**Desaturation**


这个节点的作用是去色，会生成一个单调柔和的灰度图。


**Distance**


这个节点的作用是计算两个输入值的距离。输入值可以是两个点、颜色、位置或者向量。


**FeatureLevelSwitch** 


这个节点允许对不同的设备使用不同的材质以保证材质在低运算率的设备上能够有平滑的切换。


**QualitySwitch** 


这个节点可以让材质在不同的视频设置下使用不同的数值。


**GIReplace** 


这个节点为材质提供在全域照明下产生不同间接光效果的方法。


![LPV_gi_replace.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/LightingAndShadows/LightPropagationVolumes/LPV_gi_replace.jpg)![LPV_bounce_color_override.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/LightingAndShadows/LightPropagationVolumes/LPV_bounce_color_override.png)


**LightmassReplace**


这个节点可以使得材质在被到处为光照用时使用一个不同的值。


**LinearInterpolate**


就是Lerp，线性插值，基本上复杂的材质都会用到。


**Noise**


这个节点的作用是生成噪波图。


**RotateAboutAxis**


对给定的向量进行旋转，通常用于获得选择WorldPosition之后传递给WorldPositionOffset。


**SphereMask**


这个节点在指定的位置生成一个球形并进行距离计算，圆心处为1，外围为0。


**AntialiasedTextureMask**


对输入进行抗锯齿运算。


![AAMasked_Demo.png](http://docs.unrealengine.com/latest/images/Engine/Rendering/Materials/ExpressionReference/Utility/AAMasked_Demo.jpg)


-------------------------------------------------------------


到此初步探索就算是完成了，要一下子实现自己想到的材质效果还是有点难度的，不过至少不会茫然了。想要对材质更加的熟悉，需要的大概是更多的经验的积累。


