---
layout: post
status: publish
published: true
title: AnimatioinStarterPack的使用（上）
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2066
wordpress_url: http://blog.ch-wind.com/?p=2066
date: '2017-11-11 10:51:55 +0000'
date_gmt: '2017-11-11 02:51:55 +0000'
tags:
- UE4
- Animation
---
虚幻商城能看到官方提供的AnimationStarterPack，对于制作游戏原型非常的有用，毕竟如果一直用一个立方体来代替角色多少还是有些不足的。


当前使用的UE4版本为4.18.0。


4.18的升级中对角色动画相关的功能进行了改进，不过主要的改动是在PhysicAsset上的。刚好趁着这次开坑，对动画系统重新熟悉一下。


PS：这里只是操作笔记，并不会有很多细节上的说明哦~


## 基础准备


首先当然是通过EpicLaucher添加AnimationStarterPack到项目中。


添加完成后能够看到动画包中有做好的基础角色蓝图，那么第一步就是参照着自己实现一遍。


动画蓝图的操作分别位于角色的蓝图和动画蓝图本身两个部分，这两者会互相交互来对状态进行更新。


### Character


角色蓝图直接新建一个Character即可，由于目标的系统是顶部的上帝视角的，所以会和官方的第一人称(?)的有些不同。


照例，先添加SpringArm和摄像


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001.png)


记得在SpringArm上设置Use Pawn Control Rotation。


之后，在Mesh中将Skeletal Mesh指定为SK_Mannequin，动画蓝图那里随便指定一个Asset，方便预览。


根据官方提供的Character将位置设为(0,0,-100)，同时将旋转设为(0,0,-90)以保持朝向与Arrow一致。


这里如果直接运行的话会发现角色穿到地面以下了，原因是胶囊体的大小不一致。由于不清楚官方设定的理由，这里暂且按照官方的来，修改为


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002_thumb.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002.png)


这样就基本差不多了，然后将官方的角色蓝图中事件图表全部拷贝过来。这些蓝图都是些操作角色的输入处理，从Input拉到Character以及标志位的设置之类的，没有什么特别的地方呢。


没有的变量直接点右键生成，没有的输入直接到项目设置中添加。唯一要注意的是


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003_thumb.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003.png)


Lookup的Scale是-1，要不然操作起来和通常的FPS是相反的。


### 动画蓝图


然后新建一个C++类，继承自AnimInstance，这样做主要是考虑到之后动画蓝图的逻辑可能会变得复杂。


接下来在蓝图中新建一个动画蓝图，父类选择刚刚构建的CharaAnimate，骨架选择UE4_Mannequin_Skeleton。


然后在Character蓝图的Mesh里面将动画指定为刚刚新建的动画蓝图


[![clip_image001[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0014_thumb.png "clip_image001[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0014.png)


指定完成后运行时就是个T字了，因为动画蓝图还是空的。


到达动画图表，添加一个简单的状态机。


状态机是动画蓝图的核心功能之一，可以通过设定的条件，根据变量的值等，跳转到不同的状态值，而不用自己根据众多的值对状态进行控制。


在动画图表中右键，新建一个状态机，名字就模仿官方的动画蓝图叫LocoMotion，并将它连到“最终动画姿势”上。


然后打开LocoMotion，右键新建一个状态，名为Idle。


打开Idle的状态，从右边的动画列表直接拖一个Idle_Rifle_Hip连接到Result上。


这样的话预览有些就能看到角色播放静止动画了。


## 混合空间


混合空间是最基础的动画蓝图操作，大部分时候行走的动画都是靠其实现的。


新建一个混合空间，骨骼选择SK_Mannequin。


混合空间是2D的，通常的行走混合就是通过前进速度和前进方向来混合出八方向行走动画。


### BlendSpace


打开混合空间，在左侧切换到Asset Detail标签，首先将混合用的两个坐标轴设置好。


[![clip_image001[6]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0016_thumb.png "clip_image001[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0016.png)


方向是从-180~180之间，而速度则需要根据Character的设定来决定，由于这里是默认的，就保持和官方示例的一样就好了。


这里的坐标名称是随意的，之后会通过蓝图来设置当前的坐标值。


### 状态机


在进一步操作混合空间前，先将动画蓝图设置好。


动画图表的状态机中新建一个状态，命名为Move。


新建两个变量Speed、Direction，


从Idle的边缘拉一根线到Move，就会自动生成一个Transition。然后在Transition中添加条件为Speed>10.0则执行状态迁移，也就是由Idle变为Move。


然后从Move拉一个Transition到Idle，条件设置为Speed<=10.0。


打开Move的状态，直接拖入刚刚新建的混合空间，把Speed和Direction分别接到混合空间的两个坐标轴上。可以在右边的动画预览页调整两个值来查看效果，不过现在混合空间是空的，会变成摆T字。


这样状态机的部分就设置完了。


### 关键帧


然后回到混合空间中，在坐标系的各个位置添加混合节点。


一般情况下在角度(-180, -90, 0, 90, 180)和(行走速度,跑步速度)上添加关键性的混合用节点就可以了。


但是AnimationStarterPack中似乎没有跑步动画，不过这个版本的引擎中可以在左侧对节点的速度缩放进行调节，某种程度上可以代替跑步，不过反正是用来做原型的，也不用太在意。


在Speed 270上拖放动画，按角度来区分的话-180和180都是向后采用BWD，0则采用FWD，-90是LT而90是RT，然后在Speed 0上放一样的动画，但是将Rate Scale调低一些，变成0.8。


[![clip_image002[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024_thumb.png "clip_image002[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024.png)


然后将Target Weight Interpolation Speed Per Sec设定为2.0，这样混合空间的准备就完成了。


### 状态绑定


此时在动画蓝图中调节预览的两个值，就可以看到效果了。


然后参照官方的动画蓝图中的节点，将速度和方向从Character那边读取过来。


[![clip_image003[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0034_thumb.png "clip_image003[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0034.png)


直接运行游戏，就可以看到行走的动画切换了。


## 额外动作


在基本的行走动画之外，还有一些额外的动作可以加入到动画蓝图的状态机中，通常的FPS中会有跳跃、蹲伏、趴下之类的动作。


AnimationStarterPack中虽然有提供趴下的动作，但是是没有移动动画的，所以是一个静止的状态，这里并没有做，其实动画蓝图这边只是新建一个孤立的状态机就可以。主要还是要在角色蓝图中添加静止移动的逻辑，由于并没有做这种功能的打算，这里就放弃了。


### 静止跳跃


这里官方的动画蓝图有一个问题，由于在Idle->Jump的管道中有加上速度条件，而实际上这个速度是包含跳跃速度的，因此导致状态机沿着Idle->Jog->Run Jump的路径前进，Jump这个状态是永远都不可达的。


由于不知道官方的原始设计时什么样的，这里姑且在Speed计算时忽略掉Z轴的速度。


[![clip_image001[8]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0018_thumb.png "clip_image001[8]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0018.png)


然后在检测到玩家按下跳跃键后，在动画蓝图中记录跳跃标记


[![clip_image002[6]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0026_thumb.png "clip_image002[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0026.png)


基本可以将官方的蓝图中的Jump相关的部分直接抄过来，另外由于修改了Jump的逻辑，要为Jump添加状态进入事件


[![clip_image003[6]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0036_thumb.png "clip_image003[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0036.png)


并在事件蓝图中相应


[![clip_image004](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image004_thumb.png "clip_image004")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image004.png)


在这里的话就能在静止状态下跳起来了，但是如果在行走中按跳跃的话，就会有BUG：在停止运动后额外的播放了一次动画。


这个是因为没有加RunJump状态造成的，不过为了以后添加别的状态不出现这个Bug，需要对CanJump()的实现多加留意。不能跳跃的状态就不要将跳跃标记置为True。


另外一个方面就是，Jump这个动画有一个前摇的过程，但是实际上蓝图的实现是已经跳跃起来了。这里需要对设计进行调整，或者让动画从0.3秒开始播放


[![clip_image005](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image005_thumb.png "clip_image005")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image005.png)


这样调整之后会造成落地有些许的违和感，这个主要是官方没有准备浮空动画而是在跳跃动画播放完后直接切回非跳跃状态造成的。因此大概是为了防止这里的穿帮，官方给的默认跳跃高度还是比较低的。记得以前的某个示例中是有的，但是在AnimationStarterPack中并没有找到这个呢。由于是用来做游戏原型的，这个细节就不管了。


### RunJump


然后就是RunJump的添加。


这里大部分的逻辑可以按照Jump的一样的流程，也可以从官方的示例里面抄过来。不过从Move->Jump的状态其实没有必要对速度进行限制了。直接检测到跳跃标记就切换到RunJump状态就可以了。


RunJump的切换非常的流畅，所以很怀疑官方让Jump状态失效是故意而为的。


### Crouching


下蹲状态和跳跃状态有些类似，不过下蹲状态被当作了一个持续性状态来处理。


所以下蹲分为静止下蹲和下蹲移动两个状态，下蹲移动中也还是一个负责移动处理的BlendSpace，参照Move的BlendeSpace即可


[![clip_image006](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image006_thumb.png "clip_image006")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image006.png)


总体上而言下蹲的静止和移动与Stand->Run是一个对应的关系。


[![clip_image007](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image007_thumb.png "clip_image007")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image007.png)


因此这里基本上没有什么新的东西。


唯一的不同是，由于前面修改过Speed运算方式。在Crouch的状态下按跳跃，只会有位置上升，而不会有动画的变更。


官方原始的类似于蹲下跳跃的效果，是由于Z轴速度大于10导致状态迁移到Crouch Move而产生的。


在CanJump()中添加CrouchingButtonDown时不允许设定Jump标志的逻辑，就可以防止在站起身之后进入跳跃的问题了。



```
bool UCharaAnimate::CanJump(bool ShouldJump)
{
  return !EnableJump && ShouldJump && !Crouching;
}
```

## 总结


至此官方的动画蓝图中实现的功能就基本完成了，虽然在实现上和官方少许有些不同，不过功能上已经没有什么缺陷了。


接下来，就是添加上一些额外的动画来与游戏模式相对应了。


