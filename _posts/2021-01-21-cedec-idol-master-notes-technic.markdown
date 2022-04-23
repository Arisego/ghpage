---
layout: post
status: publish
published: true
title: CEDEC IdolMaster笔记-制作事例技术篇
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3159
wordpress_url: https://blog.ch-wind.com/?p=3159
date: '2021-01-21 23:10:00 +0000'
date_gmt: '2021-01-21 15:10:00 +0000'
tags:
- Idolmaster
- CEDEC
---
CEDEC看到的IdolMaster相关的分享，严格上来说并不是系列。


主要的构成是，CEDEC2016的三篇：


[アイドルマスターシンデレラガールズ スターライトステージ 制作事例・テクニカル編](https://cedec.cesa.or.jp/2016/session/ENG/3515.html)


[アイドルマスターシンデレラガールズ スターライトステージ 制作事例・アート編](https://cedec.cesa.or.jp/2016/session/VA/4787.html)


[『目指せトップアイドル！』　PS4アイドルマスタープラチナスターズで目指したこと](https://cedec.cesa.or.jp/2016/session/VA/3727.html)


这三篇都没有公开PPT，所以是以其他地方的引用为基础的。


以及CEDEC2020的：


[「アイドルマスター シンデレラガールズ スターライトステージ」制作事例](https://cedil.cesa.or.jp/cedil_sessions/view/2315)



> 由于部分参考的是二手资料，会将几篇文章相互对照，采用个人认为合理的解释。
> 
> 
> 所以可能会出现与原文意思有出入的情况~
> 
> 


由于放在一起实在是太长了，所以按照篇章进行了拆分：


* 技术篇(就是这篇)
* [美术篇](https://blog.ch-wind.com/cedec-idol-master-notes-art/)
* [白金星光篇](https://blog.ch-wind.com/cedec-idol-master-notes-platinum-stars/)
* [長期運用篇](https://blog.ch-wind.com/cedec-idol-master-notes-iteration/)


 


这里是技术篇，参照的这里：<https://www.4gamer.net/games/307/G030796/20160829088/>


## 引擎选择


候补引擎有Unity和Cocos2d-x两个，花费一个月的时间对两个引擎进行了考察验证。分成两组分别使用对应的引擎进行功能实现。


最核心的要求是：一定要保证帧率维持在60帧。


目标上，要能够让偶像的演出更加接近插画的风格。对于高性能的手机，则要能够提供对应的高品质输出。


在验证时，分别对2D旋律游戏和3D演出这两个部分进行。


3D部分的主要考察点是顶点数、贴图分辨率、骨骼数量等基本性能。在进行性能分析时，除了使用引擎本身提供的工具之外，还使用了硬件开发商提供的性能优化工具对Shader的性能进行分析。


除了基本的性能验证，对图像特效这些可以动态调整的要素也进行了验证。图像效果上，考虑到为了表现出插画的风格，必须要能够支持Bloom和DOF特效的实现。


 


经过了一个月的验证后，最终选择了Unity。虽然Cocos2d-x具有开源的优势，但是Unity的开发效率更高，同时公司内部也已经有了相应的开发经验。最重要的是，在1个月的验证期间Unity产出的成果的品质起了关键作用。


## 性能优化


在引擎验证阶段就遇到了Thermal Throttling的问题，手机在高负荷运作导致温度上升后，会对CPU和GPU的运行效率进行下调。这个问题只能通过优化来解决。


为了在所有的设备上都达到60帧，CGSS提供了*3D轻量*和*3D标准*两个级别的画质级别，对于2D部分也相应的有两个选项。这方面，苹果手机由于机种和性能比较明确，对于IPhone 5之前的手机使用的是3D轻量，包括IPhone 6之后的手机，则使用3D标准。


对于Android手机，由于存在很多碎片化的问题，则是通过获取手机的硬件信息，根据其性能参数来动态的决定使用哪一个性能等级。



> IOS使用UnityEngine.iOS.Device.generation
> 
> 
> Android基于SystemInfo.graphicsDeviceName进行判定
> 
> 


对于MV视频播放这种用户无法操作的3D部分，由于性能负担较低，全部都使用的3D标准级别进行。


## 图像效果


两个性能等级在渲染上的差别之一在于部分图像效果的启用与否。


CGSS使用了一个混合的方法来达到Bloom和DOF的效果：


[![image-20210112075819248](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210112075819248_thumb.png "image-20210112075819248")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210112075819248.png)


在进行效果计算时，使用四分之一大小的渲染结果作为基础，上面的路径使用深度贴图进行模糊处理，下面的路径使用基于亮度的像素抽出。


由于深度贴图会额外的消耗一个DrawCall，对于低端设备而言难以承担，所以在3D轻量中没有启用。


四分之一大小的渲染贴图除了在这里使用之外，也会被用于场景中显示器上的图像输出。


## 光照


CGSS没有使用动态光照，角色、背景的光照都是通过Ambient Light来实现的。环境光照通过时间轴来控制，SpotLight的效果则使用面片来实现。


OutLine(轮廓线)使用的是反转Culling这种古典的方法来实现的，轮廓线的宽度和颜色，则通过Vertex Color来控制。


角色下方的阴影，使用的也是假的阴影。主要原因有两个，首先，要生成阴影必须使用深度贴图，无法在没有深度贴图的3D轻量上实现；另一方面，舞台上有非常多的光源，即便使用光照计算也无法很好的再现。


[![image-20210112083029487](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210112083029487_thumb.png "image-20210112083029487")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210112083029487.png)


通过对DrawCall进行限制可以很好的减轻CPU的负担，Unity提供的Draw call Batching功能提供了很大的帮助。


## 角色动画


对于CGSS而言，角色的动画是相当重要的部分，所有的动画都是采用动态捕捉制作的。


从MotionCapture数据到角色动画，全部使用同一个Generic的Rig，不使用IK而是使用旋转传递的方式来映射动画。同时基础骨骼全部都是等倍率，不会进行缩放。


在进行动画播放时，会给每一个角色添加一个随机的时间偏差，让动作产生差别。这样即便玩家在MV中进行暂停，也会看到全员的动作微妙的有一些不同。这样是为了模拟出人在舞蹈的真实感，而不是所有的模型都在作一模一样的动作。


旋转处理方面有一个问题，就是旋转的误差会随着骨骼累计到末端，尤其是当手上拿着什么东西的时候会特别的明显。这里一般会使用Motion Reduction来处理。



> The **Motion Reduction** property settings enable you to reduce the amount of motion transferred between the chest, neck, head, and shoulder body parts of your source Actor or Character to the corresponding object of your target character.
> 
> 


对于一些无法消除的抖动，会让动画表现中的一部分直接使用相对身体的Transform，而不是使用骨骼传递。例如利用手上拿着的麦克风，即便手的末端有一些传递过来的抖动，由于有麦克风遮挡住，可以有效的减少穿帮。


## 衣服模拟


衣服的物理模拟主要就是单纯的sprint计算，以及添加尽可能少的碰撞形态来作简单的碰撞判定。碰撞判定用的形态上，只有Sphere与Sphere以及Sphere与Capsule两种。由于运算在C#上消耗比较大，在完成之后转移到了原生代码上，获得了10%~20%的性能提升。


 


总体而言，在技术上很大程度使用了上一个世代的主机的很多优化技术。现代(指2015年)的手机已经具有能够匹敌上一个世代的主机的运算能力了，所以技术方面也能有很大的沿用。


