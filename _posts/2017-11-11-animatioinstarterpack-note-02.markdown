---
layout: post
status: publish
published: true
title: AnimatioinStarterPack的使用（下）
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2091
wordpress_url: http://blog.ch-wind.com/?p=2091
date: '2017-11-11 10:52:21 +0000'
date_gmt: '2017-11-11 02:52:21 +0000'
tags:
- UE4
- Animation
---
前面已经对官方的示例动画蓝图进行了还原，但是要作为原型测试时使用还是有些不足。


当前UE4版本为UE4.18.0。


这里继续对动画蓝图添加一些基本的功能。


## Dead


死亡动画也是可以放到状态机的，但是如果状态机的结构很复杂的话，就会陷入需要从每个状态拉到Dead状态的窘境。


这里就需要在制作之前对状态机进行规划，例如其实静止和移动这两个状态是可以合并到一个BlendSpace中去的，再加上下蹲动画的合并，同时，将Jump和RunJump状态进行统一，状态机的数量就会减少。这里由于是原型用的，之后动画资源可能会不一样，就不会进行详细的设计和修改了。


### 逻辑绑定


由于这里没有游戏逻辑，所以直接按下P键就判定玩家死亡。


在Character蓝图中，调用Disable Input来关闭玩家输入，设置标志位，3秒之后重置这些状态。在此就不做其他逻辑了。


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001_thumb-1.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image001-1.png)


在动画蓝图的更新函数中，取得Character的死亡标记，并设置到动画蓝图中


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002_thumb-1.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image002-1.png)


### 动画蓝图


在状态机中添加Dead状态，随便拉一个Dead动画出来播放，不要循环。


然后从Idle->Dead设定条件为PawnDead，而从Dead->Idle为非PawnDead。


这样就有了基本的死亡动画逻辑。


其实官方总共准备了3种略有不同的站立死亡动画，这里可以选择随机的播放一种，使用名为Blend Poses by int的节点即可。


在Dead状态中，对动画进行操作


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003_thumb-1.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image003-1.png)


DeadAnimatType是新建的Int变量，需要在检测到死亡标志位时随机指定到0~2之间。


[![clip_image004](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image004_thumb-1.png "clip_image004")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image004-1.png)


这样就有了随机死亡动画的功能了，不过这里由于没有添加Respawn的逻辑，3秒的Delay之后是直接原地站起来复活的:D


## AimOffset


这也是UE4提供的动画Asset之一，其主要作用是在移动-静止动画上叠加的额外的瞄准动画。


### 资源准备


新建一个AimOffset打开编辑，能看到它和BlendSpace一样有两个轴向对动画进行Blend，不同之处在于AimOffset最终是叠加到已有的基础动作之上的。


要做AimOffset首先需要的是制作各个瞄准方向的基础动作，在AnimationStarterPack中，瞄准动画可以从Aim_Space_Hip的动画中取出，其中共有9个动作，帧数分别为：




|  |  |
| --- | --- |
| 0 | Aim_Center |
| 10 | Aim_Center_Up |
| 20 | Aim_Center_Down |
| 30 | Aim_Left_Center |
| 40 | Aim_Left_Up |
| 50 | Aim_Left_Down |
| 60 | Aim_Right_Center |
| 70 | Aim_Right_Up |
| 80 | Aim_Right_Down |


操作上，对Anim_Space_Hip进行复制，通过最下方的帧导航到想要的帧。


[![clip_image001[5]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0015_thumb.png "clip_image001[5]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0015.png)


然后在帧导航条上点击右键，先删除左边的所有帧，再删除右边的所有帧


[![clip_image002[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024_thumb-1.png "clip_image002[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0024-1.png)


这样就能得到9个只有一帧的动画了，全部选中，然后在右键菜单中使用集合编辑功能。


[![clip_image003[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0034_thumb-1.png "clip_image003[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0034-1.png)


然后对AdditiveSettings属性进行调整


[![clip_image004[4]](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0044_thumb.png "clip_image004[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image0044.png)


回到刚刚新建的AnimOffset，与BlendSpace类似，设定两个轴向的名称和范围


[![clip_image005](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image005_thumb-1.png "clip_image005")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image005-1.png)


然后将刚刚生成的9个动作拖放到关键插值点上去


[![clip_image006](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image006_thumb-1.png "clip_image006")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image006-1.png)


这样就可以了。


### 动画蓝图


接下来，到动画蓝图中对AnimOffset进行使用。


首先添加两个Float变量，分别命名Aim_Yaw和Aim_Pitch


然后到动画图表中，添加AnimOffset的使用


[![clip_image007](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image007_thumb-1.png "clip_image007")](https://blog.ch-wind.com/wp-content/uploads/2017/11/clip_image007-1.png)


这时，在动画蓝图的预览中就可以对AimOffset进行调试了。


如果要实际使用的话，还要在BlueprintUpdateAnimation事件或者其他地方，对这两个值进行更新。由于我这边是做的TopDown，就不继续操作了。


## Montage


其他的一些动画，包括射击动画、装备切换动画都需要用到Montage。


这些动画都是与具体的资源相关性比较强的，在原型制作阶段制作的话就不会进行更多的时间投入了。


包括换枪、持枪、射击在内的动画要使用Motage，是因为身体的基本动作是一致的，不可能为每一个状态做一个对应的动画。


基本的装备切换，都是通过在Montage中添加动画通知，然后将物品切换Socket来做的。


由于只是要做一个动画蓝图来做原型用，而且要使用Montage的话，就必须从资源开始就有做好的规划，在没有进一步需求的情况下暂时就不会继续做下去了。


Montage的教程很多，直接搜索就可以了:D。


