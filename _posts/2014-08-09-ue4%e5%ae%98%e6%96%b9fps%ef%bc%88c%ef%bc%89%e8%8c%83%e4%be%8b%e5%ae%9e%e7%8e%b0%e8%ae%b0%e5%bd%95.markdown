---
layout: post
status: publish
published: true
title: UE4官方FPS（C++）范例实现记录
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 950
wordpress_url: http://blog.ch-wind.com/?p=950
date: '2014-08-09 20:59:00 +0000'
date_gmt: '2014-08-09 12:59:00 +0000'
tags:
- c++
- UE4
---
看完Digital Tutors的UE4教程之后，参照官方wiki的教程文章把FPS的范例实现了一遍。于是趁热打铁，用文字的形式记录和总结一下。


教程原文地址：<https://wiki.unrealengine.com/First_Person_Shooter_C%2B%2B_Tutorial>。


使用的UE版本是4.4版，按照教程中的顺序来：


1. 新建项目


直接新建一个空白项目，不要默认的资源文件。项目名**FPSProject**，为了方便后面代码的复制粘贴。在这里不做变更。


新建后点保存，将地图保存为**FPSMap**。


然后有一个步骤是在**Game>Project Settings**>**Maps & Modes**中将编辑器默认地图设置为刚刚保存的**FPSMap**。


这一步在操作的时候不知为何自动被添加了一块地板，总之不影响操作，直接无视。


2. 创建GameMode


粗略的浏览了下文档之后，发现GameMode大概相当于游戏规则的核心管理类。大体上的地位相当于cocos2d中的Scene。如下图：


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2014/08/clip_image001_thumb.jpg "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2014/08/clip_image001.jpg)


在菜单**File**下**Add Code to Project**中新建一个类，基类选择为**GameMode**。选择编辑会自动打开VS2013。这个时候intellisense会报错，按照官方的建议，直接无视即可。原因似乎是有的文件要到编译的时候才会生成，这里的情况问题出在"FPSGameMode.generated.h"上。


在生成的类中覆盖掉BeginPlay函数，并在屏幕上输出HelloWolrd。关闭UEEditor，在VS中进行代码编译。要注意如果不关闭编辑器的话，VS会无法写入文件导致失败。


生成完毕之后重新打开UE，在配置中的**Game>Project Settings>Maps & Modes**将Default Mode设置为**FPSGameMode**。


3. 创建角色


和上面一样，添加代码命名**FPSCharacter**，继承Charater。和上面的步骤几乎没什么不同，继承BeginPlay并输出调试文字。


完成操作之后在FPSGameMode的构造函数中添加DefaultPawnClass = AFPSCharacter::StaticClass()。


4. 玩家操作


UE的操作接口分为**Axis Mappings**和**Action Mapings**，分别对应连续输入的方向控制操作和离散输入的按键操作。设定在项目配置中的Input项内进行。


接口的作用是将硬件输入绑定到特定的名称上，然后由Charater类来注册。主要提供一个映射的操作来隔离游戏逻辑和硬件操作，很常见的引擎输入控制模式，基本上按照文档描述没有遇到什么问题。


途中有介绍到**UFUNCTION**、**UCLASS**、**UPROPERTY**这几个宏，它们的作用是将特定的函数、类、属性暴露给引擎，代码中出现这几个宏的代码变动时必须要在VS中重新编译。


5. 为角色添加网格


新建一个BlusPrint继承刚刚建立的**FPSCharater**。通过BluePrint的编辑器将Mesh设置为下载并导入的人物模型。没什么特别的问题。


需要在VC中将玩家的Chara修改为刚刚新建的BluePrint,看起来有点繁琐，不过也就是复制粘贴一下。


添加完后会发现视角有点低，通过添加一个UCameraComponent来解决。根据文档描述，个类就是作为摄像机的配置而存在的。


6. 为角色添加第一人称网格


在这个游戏模式的定义中，玩家是看不见自己的身体网格的，只能看见自己的手。似乎和通常遇到的FPS有点不一样，不过Demo就是这么定义的。


和上一步没啥不同，关键性的部分是调整可见性的语句。


7. 子弹和射击


新建一个继承自Actor的类，创建碰撞形态和移动逻辑的Component，并且设定生命周期为3秒。



```
// Use a sphere as a simple collision representation
CollisionComp = PCIP.CreateDefaultSubobject<USphereComponent>(this, TEXT("SphereComp"));
CollisionComp->InitSphereRadius(15.0f);
CollisionComp->BodyInstance.SetCollisionProfileName("Projectile");
CollisionComp->OnComponentHit.AddDynamic(this, &AFPSProjectile::OnHit);
RootComponent = CollisionComp;

// Use a ProjectileMovementComponent to govern this projectile's movement
ProjectileMovement = PCIP.CreateDefaultSubobject<UProjectileMovementComponent>(this, TEXT("ProjectileComp"));
ProjectileMovement->UpdatedComponent = CollisionComp;
ProjectileMovement->InitialSpeed = 3000.f;
ProjectileMovement->MaxSpeed = 3000.f;
ProjectileMovement->bRotationFollowsVelocity = true;
ProjectileMovement->bShouldBounce = true;
ProjectileMovement->Bounciness = 0.3f;

// Die after 3 seconds by default
InitialLifeSpan = 3.0f;
```

通过BluePrint继承这个类，并且在BluePrint编辑器中添加Component并附上网格，同时要关闭其碰撞。因为基类中已经有了碰撞逻辑的实现。


关于碰撞方面，不知为何碰撞组的管理是在ini文件中进行配置的，这个留到以后再研究。


子弹的发射还有一个添加瞄准准星的HUD的过程，大体过程就是绘制，没别的了。是否HUD类能够处理鼠标事件目前不明。


8. 角色动画


角色动画通过状态机来管理，工作在BluePrint中进行。没有用到C++代码，可视化的调整状态机的逻辑，非常的方便。


[![image](https://blog.ch-wind.com/wp-content/uploads/2014/08/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2014/08/image.png)


总体而言算是大致的了解了UE4用C++的方式来搭建游戏的过程，不过详细的API的熟悉还是需要一定的时间过程。作为开头，刚好到此为止。


