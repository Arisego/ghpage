---
layout: post
status: publish
published: true
title: UE4中的Physx物理
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1659
wordpress_url: http://blog.ch-wind.com/?p=1659
date: '2017-05-03 23:15:23 +0000'
date_gmt: '2017-05-03 15:15:23 +0000'
tags:
- UE4
- 物理
- Substeping
---
为了保证物理引擎能够更精准的模拟，UE4有提供Physics Sub-Stepping功能，同时引擎也有提供相应的接口方便自行进行物理操作。


当前UE4版本4.16 P1。


UE4中对物理引擎的接口暴露还是相当多的，只是一般情况下不会使用到而已。


## Sub-Stepping


UE4的物理分步是所谓的半锁定步长形式的，无论如何分步的主要作用是提高物理模拟的精确度。针对的情况是，在不同的设备上，发布的程序可能会以不同的帧率运行。在有的设备上有可能会被进行奇怪的垂直同步设定，这些都有可能导致与帧率同步的物理模拟出现神奇的处理结果。


物理分步功能目前还不是特别完善，在代码中能看到注释：



> This feature is still experimental. Certain functionality might not work correctly
> 
> 


Sub-Stepping的设置在项目设置>Engine>Physics中。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-2.png)


在默认的情况下，不启用分布，作用于物理引擎的设定是Max Physics Delta Time。当前值是0.033333，也就是说物理引擎本身的运行不小于每秒30帧。


当启用了物理分步之后，引擎将会在每一帧中进行分步计算，当帧率下降到一帧时间大于最大分步数*最大分步时间的情况下，引擎将不再进行分步计算而是等待。无论如何，过小的物理分步将会导致更高的运算负荷，而且从某种程度上也并不是必要的。


引擎中有的与物理有关的代码中有提供bAllowSubstepping这样的选项来进行区分，当调用这些函数的来源是物理分步发出的事件时才需要将其置为FALSE。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-3.png)


物理分步还有三个扩展的属性，这些属性是分步时进行分步之间进行加权的平滑处理的。


## Async Scene


分步选项中还有一个Stepping Async的开关，这个选项是作用于Async Scene的，就是说是否对Async Scene进行分步计算。


但是Async Scene本身是需要另外开启的


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-4.png)


在Physx中，有区分Synchronous与Asynchronous两种模式，而UE4中对其都有支持。Synchronous scene是通常的物理模拟发生的地方。而Asynchronous中存放的一般是可破坏物品等静态的、与游戏逻辑关联不大的物品。


静态的物品是同时存在于这两个Scene中的，而动态物品可以通过选项设定到Async Scene中。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-5.png)


但是静态物品会无视这个选项的，在碰撞中可以选择让物体在移动时也在Async Scene中检测碰撞。


## Custom Physics


UE4中有提供介入物理引擎的方式，通过在bodyinstance或者PhysicsScene中定义的下面的函数进行事件绑定就好了：



```
void AddCustomPhysics(FCalculateCustomPhysics& CalculateCustomPhysics);
```

与基本的Event Dispatcher的实现一样，要使用这个功能首先要声明一个



```
FCalculateCustomPhysics OnCalculateCustomPhysics;
```

而与通常的事件不同的是，AddCustomPhysics必须在每次Tick时都进行绑定，这样它才会在接下来的物理执行中被调用。


通常的Tick的[TickGroup](https://blog.ch-wind.com/ue4-time-mange/#TickGroup)都是在PrePhiscs中的，也就是说这个注册是针对每一个引擎Tick循环进行的。



```
void UMyStaticMeshComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
  GetBodyInstance()->AddCustomPhysics(OnCalculateCustomPhysics);
}
```

而自己要定义的事件则绑定到OnCalculateCustomPhysics中就行了



```
OnCalculateCustomPhysics.BindUObject(this, &UMyStaticMeshComponent::MyCustomPhysx);
```

分发器本身的定义是



```
DECLARE_DELEGATE_TwoParams(FCalculateCustomPhysics, float, FBodyInstance*);
```

在使用自定义物理时，需要注意，一些物理相关的类型是无法进行蓝图暴露的。如果强行暴露给蓝图，例如添加UCLASS之类的修饰的话，就会不经提醒出现这样的报错:



> Unrecognized type 'FCalculateCustomPhysics' - type must be a UCLASS, USTRUCT or UENUM
> 
> 
> Inappropriate '*' on variable of type 'FBodyInstance', cannot have an exposed pointer to this type.
> 
> 


其实只要把蓝图暴露的修饰符去掉就可以了。


另外如果要直接调用Physx的API的话，就必需在项目的build.cs中添加"PhysX"和"APEX" 这两个Module的包含，类似下面这样就可以了



```
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "PhysX", "APEX" });
```

这样的话就可以通过



```
PRigidBody = GetBodyInstance()->GetPxRigidBody_AssumesLocked();
```

来进行Physx的API调用了。


## Damping and Force


Physx对球体的运动模拟上有些许问题，通常的建议是对球体作用Linear Damping和Angular Damping让其运动停止。


但是如果在对物理真实度要求较高的情况下就会有一个问题，那就是Damping在速度较高时减速比速度较低时快，而在速度接近零时需要一定的时间才能够停住运动。当然，如果Damping很高的情况下也是会直接停的。


所以我们可以通过对RigidBody直接施加力量来达到减速的效果。


但是通常情况下最好不要直接对速度进行修改，而是通过AddForce之类的操作间接的对速度进行操作。因为物理引擎内部很多模拟计算是以“当前”速度为基准进行的，如果直接进行速度的设置，可能会导致一些计算的结果不太真实。而AddForce的话就可以将加速度等计算交由物理引擎自行处理。



```
void UNewStaticMeshComponent::SetBallVelocity(FVector fvVelocity, bool bAdd /*= false*/)
{
   if (bAdd && fvVelocity.Size() == 0.0f) return;

  UE_LOG(LogTemp, Log, TEXT("[UNewStaticMeshComponent] SetBallVelocity: speed %s and %s add"), *fvVelocity.ToString(), bAdd?TEXT("is"):TEXT("not"));
  PxVec3 PNewVel = U2PVector(fvVelocity);
  if (bAdd)
  {
    PRigidBody->addForce(PNewVel, physx::PxForceMode::eVELOCITY_CHANGE);
  }
  else
  {
     PRigidBody->setLinearVelocity(PNewVel);
  }
}
```

这里需要注意的是，Physx与UE4的setLinearVelocity调用形式虽然是相同的，但第二个参数的意义是不同的。Physx的第二参数并不是Add to velocity而是auto wake。详细的addForce之类的可以参照[[Physx文档](http://docs.nvidia.com/gameworks/content/gameworkslibrary/physx/apireference/files/classPxRigidBody.html)]。


这样的话再添加上一些接触判定逻辑就可以实现自己的球体运动模拟了。


## 源码


一些更多的细节部分请参考[[Github](https://github.com/steinkrausls/PhysxTest)]上的源码，里面只保留了测试代码，有些多余的代码没有完全去掉~


