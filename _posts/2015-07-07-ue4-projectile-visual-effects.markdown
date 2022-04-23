---
layout: post
status: publish
published: true
title: UE4子弹特效
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1397
wordpress_url: http://blog.ch-wind.com/?p=1397
date: '2015-07-07 17:54:58 +0000'
date_gmt: '2015-07-07 09:54:58 +0000'
tags:
- UE4
- 粒子
- Decal Materia
---
子弹使用抛体就可以实现了，但是要让其看起来更加真实，则可能需要加上一些粒子特效。


当前UE4版本4.8.1。


子弹的特效制作主要使用粒子系统进行实现，只有用于着弹效果的地方使用的是Decal Material。官方的这篇教程对于了解如何去制作一个粒子系统很有作用。原始教程地址：[https://wiki.unrealengine.com/Projectile_Visual_Effects](https://wiki.unrealengine.com/Projectile_Visual_Effects "https://wiki.unrealengine.com/Projectile_Visual_Effects")（教程中有提供相关文件的下载）。


特效的制作基础是UE4自带的第一人称模板，不需要初学者内容。也可以直接下载文档末尾处的工程文件进行观赏，工程文件不到10M，相当的方便。


## 着弹特效


制作特效之前，先实际参考一下现实世界中的效果比较好。为了模拟出好的特效，观察整个过程中能量的变化非常的重要。因此，教程中对子弹的着弹效果进行观察后。将特效分为了闪光、烟雾、破片三个子特效。


### 闪光


闪光特效使用T_Hit.tga贴图来制作材质。材质类型修改为**Translucency**，同时，为了保证闪光特效始终显示在表层，将**Disable Depth Test**设置为**True**。闪光特效中示例工程中额外的添加了Near Camera Fade和Depth Fade，这样的话在子弹有射入角度时就不会依然显示一个光晕了，更加自然一些。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb14.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image14.png) [![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb15.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image15.png)


新建一个粒子系统，并在**Required**模块中将默认发射器的材质修改为刚刚建立的材质。为了方便以后辨识，可以将发射器的名称修改为HIT。按照[之前的教程](https://blog.ch-wind.com/ue4-particle-official-tutorial-summary/)中的建议，删除**Color Over Life**模块，替换为**Initial Color**与**Scale Color/Life**模块。在模块的属性上，主要使用粒子生命周期和初始大小进行随机化来增强特效的随机性。


### 烟雾


第一步依然是构建材质，烟雾的材质相对复杂一些。在示例的截图中，有添加Near Camera Fade特性，但是在示例工程中该材质并没有添加。使用到的贴图分别是T_Smoke与T_S_Normal。


烟雾特效中，额外的使用Initial Rotation和Initial Rotation Rate来作随机化。同时添加Sphere模块对初始位置以及速度应用随机。


烟雾特效中，由于材质中使用了MacroUV，需要对MacroUV进行修改。点击编辑器的空白处，在粒子系统的属性中进行设置。如果不同的发射器使用的是不同的设置，也可以在**Required**模块对MacroUV属性进行修改。


### 破片


破片效果主要使用[SubUV模块](https://blog.ch-wind.com/ue4-particles-subuv-module/)进行实现。需要添加Acceleration模块进行重力模拟，Collision模块进行碰撞模拟。


这一部分示例工程中的材质和教程中的截图相差比较大，Near Camera Fade和Depth Fade被取消，同时用一种近似的方法生成了法线。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb16.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image16.png)


由于碎片较小，很难观察出有什么不同……


## 拖曳


拖拽特效同样通过粒子进行实现。使用的是**Ribbon**类型的发射器。拖拽部分使用的材质教程中没有对Panner的速度进行说明，实际情况如下：


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/07/image_thumb17.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/07/image17.png)


这一部分在操作是需要注意的是，必须删除**Initial Velocity**模块。由于教程中没有明言，会导致结果与预期的不同。


还有一个示例工程的不同之处在**Required**模块中：


**Screen AlignMent**设置为**Facing Camera Position**；


**Sort Mode**设置为**Distance to View**。


## 弹痕与子弹


弹痕的特效使用Decal Materia进行实现。


材质中使用快速方法生成了测试用的替代法线贴图。


子弹的材质没有什么特别的地方，并不是教程的重点。如果是使用球体而不是子弹的话，可以跳过子弹的材质。


## 蓝图


实际的对上面生成的特效进行使用测试。


在组件中添加Ribbon的粒子系统，修改抛体的速度和重力设置，同时勾选平面移动限制。在碰撞点生成粒子系统和Decal Materia。


开始调试，就能看到相当不错的子弹特效了。


