---
layout: post
status: publish
published: true
title: 辅助骨骼系统KineDriver笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3087
wordpress_url: https://blog.ch-wind.com/?p=3087
date: '2020-10-25 21:24:15 +0000'
date_gmt: '2020-10-25 13:24:15 +0000'
tags:
- Animation
---
这个是Square Enix在2019年分享的角色动画相关的笔记。


原文：[www.jp.square-enix.com/tech/library/pdf/CEDEC2019_KineDriver.pdf](http://www.jp.square-enix.com/tech/library/pdf/CEDEC2019_KineDriver.pdf)


## 系统概要


### 辅助骨骼系统简介


辅助骨骼系统主要用于提升蒙皮动画的效果，其目的是为了提高骨骼动画的表现，所以并不与实际存在的骨骼完全对应。


在设计上，由骨骼进行驱动。通过骨骼的运动驱动数值，其结果不仅可以用于蒙皮动画的表现，也可以用于Shader和材质等特效。


因此，辅助骨骼系统并不仅是一个工作于资源制作环境下的工具，而是一个在资源制作和实际运行环境中同时存在，并且能够保证在两个环境下的运行效果一致性的系统。


这么做的好处主要有两个，首先，可以降低动画资源的大小，同时，还可以方便在运行时进行动态的调整。


版本历史上看，一开始是使用softimage的，后面换到了maya上，到3.0版本已经支持使用图形化界面来拖节点的编辑形式了。


由于提供了中间文件，可以方便的在各种引擎环境下运行，也能导入到MotionBuilder中，但是辅助骨骼的制作还是使用的Maya。


### 功能和概念


系统内共有三种控制器(operator)，source、target和constraint。


#### 源和目标控制器


源控制器可以从多个骨骼获取需要的状态并对其进行插值混合。


坐标空间上，默认使用父节点作为local space的坐标参考，同时也支持指定其他骨骼作为坐标参照。


##### 旋转表现


旋转表现有两种方式


1. Bend&Roll，将旋转分解到水平方向和竖直方向，方便美术理解
2. Expmap，使用四元数的对数，主要用于程序自动生成逻辑


对于Bend&Roll，在欧拉角的处理上有一些问题。首先，欧拉角在计算上具有一些复杂度，而且同一个状态所对应的欧拉角并不唯一，例如(0,90,60)和(-30,90,30)是同一个姿势。同时，在运行时通常引擎内部都是采用四元数的，将其转换回欧拉角时便无法保证能够回到预期的那个欧拉角。


因此最终采用了[球极平面投影](https://zh.wikipedia.org/zh/%E7%90%83%E6%A5%B5%E5%B9%B3%E9%9D%A2%E6%8A%95%E5%BD%B1)的方法，来对旋转角度中的水平角度进行处理。处理方式上，将起始位置的朝向分解为vx，vy和vz。将到达目标旋转vx'所需要的角度分解为θh和θv。详细的公式可以看图：


[![旋转转换](https://blog.ch-wind.com/wp-content/uploads/2020/10/圖片.png)](https://blog.ch-wind.com/wp-content/uploads/2020/10/圖片.png)


Bend&Roll在实际使用时，水平旋转和竖直旋转的应用顺序可以根据不同的骨骼进行配置，方便在使用时进行直观的理解。


Expmap则没有顺序上的问题，程序内部直接计算结果并进行控制。


##### 缩放表现


缩放同样采用对数空间进行内部控制，采用对数是为了获得更大的精度空间，如下图所示：


[![对数空间的优势](https://blog.ch-wind.com/wp-content/uploads/2020/10/圖片-1.png)](https://blog.ch-wind.com/?attachment_id=3102)


不过ppt里面说没有实装。


##### 节点图支持


可以使用图形化的方式对控制器进行操作，主要提供了以下的节点：


* EZParamLinkLinear(线性插值)
* EZParamLink(简单贝塞尔插值)
* LinkWith(DrivenKey位置链接)
* RBFInterp(支持多个输入输出的链接)
* Expr(自定义表达式)


节点名和功能微妙的没有对上，但是原文就是这样的。


DrivenKey，查了下是maya的功能，就不详细的去看了。RBF后面有说明。


#### 约束控制器


与节点图不同的，基于约束的控制器。


* Position：位置约束，可以基于多个源进行计算
* Orientation：朝向约束，可以基于多个源进行计算
* Dirction：让旋转指向目标，3点模式可以额外控制水平旋转


##### 紧贴表面


约束控制器也提供紧贴表面的功能，根据Position和Orientation约束以及目标表面的骨骼权重进行计算。


在制作Bonamik的引导骨骼的时候经常用到。


## 工作流


### Maya中的资源制作


似乎是使用了maya的插件功能，节点图部分使用了C++的实现，导出和界面之类的功能使用了Python。


节点在显示时使用的是惯用的单位，在连接节点时会自动插入UnitConversion统一进行单位换算。


### 中间文件


中间文件采用xml的形式进行输出。


文件中保存了各种控制器的的节点的输出，以及节点之间的连接。


在进行文件输出时，可以指定缩放倍数，方便在使用不同单位的引擎中进行使用。


### UE4插件


为了方便在项目中复用，进行了插件化。


模块构成，直接上图：


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image.png)


使用上提供了两种方式


1. 动画节点：使用标准的动画控制流程，无法预览KineDriver的功能
2. Component版：作为SkeletonMesh的子组件，在tick中对骨骼进行更新，可以预览效果


提供了动画通知用于在动画的分段中关闭KineDriver。


对于与Bonamik的兼容关系，分开使用的时候会使用AddTickPrequist来决定调用顺序。另外似乎还有将KineDriver和Bonamik统合在一起的插件。


数据流程直接上图：


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-1.png)


#### AssetUserData


使用了AssetUserData进行数据的存储，方便在骨骼数据上直接添加和修改数据，通过引用指向具体的导入资源。


将数据放在骨骼上的好处是可以不必调整componnet的属性就直接对辅助骨骼的资源进行修改。


#### 缩放传递


在Maya中，对骨骼的缩放不会传递到子骨骼。


而在UE4中则会进行缩放的传递，为了保持效果的一致性，在UE4中作了处理，对于TargetScaleOp的骨骼的子骨骼进行缩放的重新设置。


## 功能实装


### 表达式


提供基本的表达式支持，语法尽量的精简化了，不会使用for这些循环的语句。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-2.png)


主要使用一些内置的函数，同时添加对三维向量和四元数的支持。运算上支持了基本的四则运算和括号。


对于输入的参数，则转换到x1,x2,...,xn的形式进行记录。


在maya内部使用时，会将转换后的表达式使用[[调度场算法](https://zh.wikipedia.org/wiki/%E8%B0%83%E5%BA%A6%E5%9C%BA%E7%AE%97%E6%B3%95)]进行转换和计算。如果要存储到中间文件的话，会将二进制代码转换为汇编语句的格式。各个游戏引擎加载时则重新将汇编语句转换为二进制代码。


之所以会用到表达式是因为有很多的分支需求，同时有的用几行表达式就能做好的事情用节点就要拖半天，所以需求也比较大。即便初期有预先设置很多功能节点，但是最后还是使用表达式具有更高的灵活性。


### RBF插值


RBF总之就是一种拟合的方式，RBF本身可以参考[[径向基函数](https://zh.wikipedia.org/wiki/%E5%BE%84%E5%90%91%E5%9F%BA%E5%87%BD%E6%95%B0)]，RBF插值可以参考[[Radial basis function interpolation](https://en.wikipedia.org/wiki/Radial_basis_function_interpolation)]。


这边有很大的篇幅中介绍这个算法的实现和原理，其实主要的目的是让插值变得更加平滑。


### 辅助骨骼自动生成


通过在特定姿态时美术已经调好的mesh状态，与完全没有调节的默认骨骼在这个状态的表现之间对比，自动的生成辅助骨骼。


使用了[[Smooth Skinning Decompostion with Rigid Bones](http://graphics.cs.uh.edu/wp-content/papers/2012/2012_SA_SSDR_preprint.pdf)] ，简称SSDR。


主要的功能就是，对具有J个顶点的模型，使用N个形变示例动画，尝试生成D个骨骼来做一个蒙皮的操作。


由于很难同时对骨骼的位置和蒙皮的权重同时进行最优化处理，所以会分别进行十次来试图逼近最优解。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-3.png)


进行简单的列出



> a. 主骨骼没有调整的情况下，使用SSDR对权重进行最优化处理
> 
> 
> b. 添加指定数量的辅助骨骼
> 
> 
> c1. 使用SSDR进行权重最优化处理
> 
> 
> c2. 暂时指定辅助骨骼的父骨骼
> 
> 
> c3. 使用SSDR对辅助骨骼的位置进行最优化处理
> 
> 
> d. 决定辅助骨骼的父骨骼，以及自动控制用的RBF插值设定。
> 
> 


其中c的步骤就是要执行10次的步骤。


#### 添加指定数量的辅助骨骼


这个过程只会执行一次，但是其操作内部需要进行多次迭代才能完成。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-4.png)


#### 蒙皮权重最优化


对一开始的公式中的[[二次规划](https://zh.wikipedia.org/wiki/%E4%BA%8C%E6%AC%A1%E8%A7%84%E5%88%92)]中的w进行单独求解。


在整个过程中会多次使用到，虽然角标写的是SSDR。但是额外参考了Computer Graphics Gems JP 2015的向井老师的分享。在辅助骨骼的生成中，为了使得最优化的求解过程更加安定，进行了以下的优化：


1. 移除参考动画中的重复顶点


在对角色的姿态进行学习时，从单独的顶点来看会有完全没有移动的帧存在


2. 对骨骼进行合并


会出现对于某一个顶点而样，有多个骨骼的给出的变换结果相同的情况。此时对这些骨骼进行合并作为一个骨骼来计算，获得的最优化权重结果则按照原本的权重比例分散回去。


#### 辅助骨骼的位置最优化


步骤c3，参考的还是上面的CGG JP2015的分享，同时参考了[Horn 1987]以及[Mukai 2018]的缩放传递控制。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-5.png)


以点群为单位进行适配，来获得最佳的位置、旋转和缩放。


这里面原文是Transform，所以包含了Translation，Rotation和Scale。只是一时找不到合适的中文替代所以翻成了位置。


#### 暂时指定辅助骨骼的父骨骼


步骤c2，这个步骤只有在使用了scale的计算时才会需要，在进行辅助骨骼计算时，为了计算的稳定性，是在本地旋转为0的情况下进行的。此时应用缩放会产生较大的误差，因此要暂时寻找到父骨骼并转换到骨骼空间之后再进行缩放处理，这个父骨骼可以随便找一个，主要的目的是为了将计算转换到骨骼空间去。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-6.png)


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-7.png)


说实话还没有仔细看过计算过程，所以只是把自己的猜测描述了下。


#### 决定父骨骼以及RBF配置


最终的步骤d，计算出辅助骨骼以及其被主骨骼驱动的形式。


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/10/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/10/image-8.png)


生成辅助骨骼的自动控制总共有四个步骤：


1. 从蒙皮权重来寻找候补驱动者


从本辅助骨骼所驱动的顶点来寻找原本驱动这些顶点的主骨骼


2. 从候补驱动中寻找父骨骼


在所有的候补中寻找误差最小的


3. 从剩余的候补中选择RBF用骨骼


选择能够尽量覆盖RBF插值的1~2个骨骼


4. RBF关键点修正


从没有关键点的情况下误差最大的地方开始插入关键点


## 总结


本来是从FF7的动画分享过来的，整个系统的原理其实还是挺清晰的。只是后面自动生成的部分使用了很复杂的计算逻辑，由于没有太过深入的打算，所以详细的公式以及额外引用的论文就没有去参考了，所以可能会有意思不明确的地方。


