---
layout: post
status: publish
published: true
title: 深入UE4材质管理
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2192
wordpress_url: http://blog.ch-wind.com/?p=2192
date: '2018-01-01 00:02:08 +0000'
date_gmt: '2017-12-31 16:02:08 +0000'
tags:
- UE4
- Material
---
UE4的材质系统使用起来虽然很方便，但是如果不进行有效的管理，很快就会导致项目的体积变得不可控制，材质编译时间也会变成痛苦的折磨。


本文是EpicJapan UE4 DeepDive系列中材质管理部分的总结，对应UE4版本为4.12~14。部分截图来自4.18。


## 抽离共通逻辑


为了减少材质的编译尺寸，首先要做的就是将共通的逻辑都抽出来。


在材质系统中一共有以下两种做法


### Material Function


材质函数可以将一些共同的操作逻辑抽取出来，这样在进行材质的编译的时候，就不会产生重复的部分了。


UE4本身就提供了大量的材质函数来方便进行材质的表现。


### Material Instance


材质实例通过将通用的材质统合起来，有效的减少材质的数量。


使用上，如果材质之间就只有贴图或者参数不同的话，就可以构建一个基础的材质，然后将需要变化的材质进行参数化。


并创建材质实例以应对不同的情况。


## 选项优化


材质在使用时有的选项需要进行优化，否则就会生成很多不会使用到的部分。导致编译时间变长且无端的占用发布体积。


### Usage


材质的选项中有一个Usage的选项，通常会自动勾选上Automatically Set Usage in Editor。


这个选项会在材质被特定的Usage使用的时候自动打开，针对每一种Usage会生成新的Shader来进行对应。


但是，Usage被打开后，如果不再在对应的Usage中使用的话，引擎并不会自动的关闭这个Usage，所以需要手动的进行关闭。


这个选项的作用在极端情况下特别大：使用全部Usage时1837K的材质在仅使用Static Light时却只有97K的。


因此在使用的时候还是需要进行额外的注意的，如果默认去掉这个选项的话，就可以有效的避免误操作导致的勾选了。当然使用起来就会有些麻烦。


### Shader Permutation Reduction


在项目设置>渲染中，能够看到


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/12/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/12/image.png)


这个也是类似的选项，在没有使用对应的功能的时候去掉就好了。


这个如果去掉了却在使用对应的功能的话，编辑器内会有屏幕输出提示，可以放心使用。


## 材质实例关系


材质实例的继承关系会很大的影响到材质的编译过程，部分继承的属性重写是会导致材质实例需要生成新的Shader的。


### Override properties


材质属性覆盖会导致需要为实例生成新的Shader


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/12/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/12/image-1.png)


### Static Switch Parameter


开关是需要额外的生成Shader的


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/12/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/12/image-2.png)


当然也包括Static Component Mask Parameter。


 


因此在进行材质实例的继承的时候，应当进行规划，首先分支出Switch等需要重新生成Shader的材质实例后，再继承其他的如贴图、颜色这些不会导致重新生成的材质实例的继承。


同时，由于材质实例不携带Usage属性，所以这个问题上只能一开始就进行分开。


## Tips


这个是SE的演讲者给出的一些操作建议。


### Textrue


尽量减少图形的分辨率，在使用单色的Textrue时，使用1x1的图片即可，在需要过渡特效时，使用一个小条就可以了。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/12/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/12/image-3.png)


而有对称性的图片，可以通过调整Tilling Method来减小尺寸。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/12/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/12/image-4.png)


**Mipmap**


有一个ComputeMipLevel的节点可以用于将Mipmap进行可视化调节。


Mipmap虽然可以在贴图的选项中关掉，但是这样会导致原始贴图常驻内存，运行时消耗很大。


Texture的Uv入口被用于缩放时并不会对应到MipLevel上，使用时需要注意。


**Power**


不要使用Power来进行2.2次方的运算而是直接相乘。也可以直接将同一个数相乘写成一个材质函数，方便使用。


因为两个的计算几乎无法目视区分，却有着明显的性能消耗。


**vector displacement map**


矢量置换贴图采用BC7压缩可以大幅减小尺寸？


**Maximum Texture Size**


比LOD Bias能够更好的对贴图尺寸进行控制。


**Never Stream**


会一次性载入所有的MipLevel贴图，在使用频率很高的粒子的贴图上可以打开。


### Material


**除0対策**


为了防止0被传到除法运算上，可以考虑加上0.0001，虽然严格意义上应当使用Max或者Min来进行控制，但是Add的效率更高


 **Texture参数**


即便两个参数指定的是同一个Texture，也会进行两次采样。


**SamplerType**


SamplerType选择为Alpha时在有的平台实际上用的确实R通道


### Trick


DynamicParameter 对于float2、float3、float4，如果实际上需要的参数是一样的话，是可以用float来代替的，会自动的被变为对应的类型。


ParticleColor 可以在EmissiveColor不需要通过这个参数指定时用于其他用途


ParticleRandom是GPU粒子独有的节点，值在0~1之间，可以用于添加随机特效


Static Component Mask Parameter可以为1张贴图提供四种变数


UV使用Time进行滚动时，可以先滚动再Tilling，这样的话Tilling进行调整时就不会影响UV动画的速度了。


