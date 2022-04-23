---
layout: post
status: publish
published: true
title: UE4-Fest-圣剑传说3笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3243
wordpress_url: https://blog.ch-wind.com/?p=3243
date: '2021-01-24 12:08:31 +0000'
date_gmt: '2021-01-24 04:08:31 +0000'
tags:
- unreal fest
- NPR
---
UEFest2020的圣剑传说3的分享


PPT参考的这里：<https://www.slideshare.net/EpicGamesJapan/unreal-festext2020winter-xeen>


后面才发现有原始视频：<https://www.youtube.com/watch?v=NHZRn4OHa1g>


最终使用引擎版本4.22.3


渲染方面没有使用任何引擎改造，全部使用引擎标准机能实现。


## 角色


美术上的参考主要有：原作的像素风格、插画。以及本作的插画。


从中寻找共通的魅力，以手绘的风格为目标进行制作。


### 轮廓线


轮廓线使用PostProcess来制作。


[![image-20210117185504080](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117185504080_thumb.png "image-20210117185504080")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117185504080-1.png)


使用深度数据比较的方法来计算轮廓线，对于深度差别不大的地方，会并用Detail normal map进行角度比较，抽出轮廓线数据。


[![image-20210117185821442](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117185821442_thumb.png "image-20210117185821442")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117185821442.png)


轮廓线的粗细使用World normal进行Mask来控制。


### Shading


使用NPR渲染，作为特征的Specular和阴影是在材质中实现的。


[![image-20210117190629938](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117190629938_thumb.png "image-20210117190629938")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117190629938.png)


阴影的部分使用了两种颜色的阶调来进行实现，在计算的时候使用Rim进行遮罩，就能在原本的颜色上表现出RimLight的感觉。在对边界和背光进行表现时能够起作用。（这部分不是很确定是不是理解正确了……）


法线贴图在制作时会在Photoshop中使用滤镜来实现最终渲染时类似笔触的画风，这个应该和[街霸5的分享](https://blog.ch-wind.com/cedec-2016-sfv-note/)里面提到的操作方法类似。但是使用的滤镜没有明确说明。


### 光照


在地图中使用一个Stationary的直射光作为天光来使用，其他的光照基本上都是static light。


对于每一个关卡，都有一个曲线来控制24小时的光照。


### 菜单画面


游戏中的菜单画面没有使用RenderTarget，而是直接进行3D绘制。


主要原因是开发时出于抗锯齿、处理负荷等因素，以及无法准备高分辨率的贴图等原因。


这样直接绘制的问题是，场景内的光照因素会反映到菜单画面来。


处理的方法是，首先使用light channel来避免被场景中的光达到。


同时从PostProcess中关闭GI的影响。


最后将r.SkyLightingQuality置为0。


消除掉环境的影响后，使用**Ambient Cubemaps**来添加光照。


[![image-20210117195359304](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117195359304_thumb.png "image-20210117195359304")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117195359304.png)


### 动态装饰物体


混合使用了[KawaiiPhysics](https://github.com/pafuhana1213/KawaiiPhysics)与AnimDynamics。


使用KawaiiPhysics是因为其设置简单，动作起来很萌。


开发初期使用的是PhysicsAsset，由于初期性能优化不好，在帧率下降时，出现了穿模等一系列物理模拟不准确的问题，在各个平台上进行运行测试后，判断要使用需要花费的成本过高。


于是中期就切换到了AnimDynamics，虽然比PhysicsAsset要安定许多，但是在性能下降时还是会出现穿模的现象。为了达到理想的效果，进行了很多试错……


在开发终盘，性能已经稳定下来了。再次对PhysicsAsset进行验证，发现在帧率下降时还是会有穿模现象，同时从AnimDnamic切换过去会花费额外的成本，放弃使用了。


最后发现了KawaiiPhysics，KawaiiPhysics本身在帧率下降后的表现依然很稳定，很少发生穿模，形状出现问题的情况也必须少。与现存的AnimDynamic可以并用，替换的成本也较低，在终盘也能安定的进行。


## 程序编制


### 过场动画


圣剑传说3在游戏过程中，需要从6个主要角色中选择3个人来进行游戏。可组合的方式导致过场动画制作起来有不少的难度。在有的场景中，由于所选的角色组合不同，所播放的内容会有很大不同。


对应方法是，在*Sequencer*中使用一个专用的共通Actor来进行表演的设置，在游戏运行时。则将对应的角色替换到这个共通Actor中。这样就能让队伍的角色成员反映出来，也能保持玩家所携带的装备。


为了实现这一点，所有的角色都会采用一样的命名规范。在进行Sequencer播放时，会由代码按照规则取出对应角色的对应动画。各个角色的动画会通过转换器进行自动收集并输入到csv文件中，最终在UE4中加载成为DataTable。


语音台词和LipSync动画也遵循类似的规则进行取出。


动画在设置上，分为身体、眉毛、眼睛和嘴巴四个层次进行控制。


[![image-20210117204320733](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117204320733_thumb.png "image-20210117204320733")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117204320733.png)


### Event


有的时候，对于特定的组合而言，需要额外的播放一些场景。此时会对当前的角色进行判定，来决定是否播放特定的子动画。


[![image-20210117204241149](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117204241149_thumb.png "image-20210117204241149")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117204241149.png)


### 视线和头的朝向


分为角度型和目标指定型的LookAt两种。


但是主角色的眼球大小会有所不同，所以需要设定眼睛的可达角度限制，在实际运行时进行控制。


由于各个角色的身高不同，所以根据角色的不同会使用不同的摄像。在Sequencer中会提供不同的角色的相机位置设置，可以在运行时进行取出。


[![image-20210117205036407](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117205036407_thumb.png "image-20210117205036407")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117205036407.png)


似乎会通过代码进行CameraTrack的实时替换。


### LipSync


语音对应了日语和英语两种，分别有相应的LipSync数据。


规则上，要求台词的文本ID与语音的文件名一致。


使用SE的[Byblos](https://cedil.cesa.or.jp/cedil_sessions/view/1742)进行文本的管理。


LipSync使用了Oculus的OVRLipSync进行录制，参考这个<https://pafuhana1213.hatenablog.com/entry/2018/11/26/011057>。


对于录制的LipSync数据，必要的话会手工进行调整。


流程上，同样是使用转换器收集成csv并导入到UE4成为DataTable。


运行时在场景中生成时，由台词的文本显示同步触发：


* 同名的语音文件播放
* 在对应的角色上播放LipSync动画


## 其他


避免使用资源的硬链接


使用Interface在设计上避免耦合。


蓝图C++化，由于游戏逻辑9成使用的都是蓝图，实际处理时风险过大。最后只将一部分比较重的逻辑移植到了C++中。


### 削减Load时间比较有效的方法


玩家相关、特效相关、SE相关的常驻处理


Widget、图标贴图事先进行Cache缓存


防止不必要的资源进入地图


### 对于CPU性能改善比较有效的方法


尽可能的关掉Tick，在新建项目的时候一起关掉，只有必要的Actor才Tick


复杂的处理果然还是放到C++里面比较快


PGO(Profile Guided Optimization)，利用游戏中的Profile结果进行最优化处理


URO(Enable Update Rate Optimizations)，对远离摄像的动画更新进行降频


