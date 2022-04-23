---
layout: post
status: publish
published: true
title: UE4物理位置偏差小记两则
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2901
wordpress_url: https://blog.ch-wind.com/?p=2901
date: '2020-05-24 11:20:32 +0000'
date_gmt: '2020-05-24 03:20:32 +0000'
tags:
- UE4
- Physx
---
UE4的运动模拟在使用过程中有时会出现位置不在预期的情况。


虽然并不是会造成很大的问题，但是在需要使用精确位置的时候就会出现一些偏差。


当前UE4版本为4.25.0。


## 抛体运动


在不使用物理模拟移动物体时，包括SetActorLocation的sweep，都会使用到UPrimitiveComponent::MoveComponentImpl进行移动。sweep的好处是移动的结果会保证不会有穿插。


但是这种运动方式在快速移动时会有一点小问题，就是它在作碰撞回避之后的位置并不是完全贴紧目标碰撞体表面的。


主要原因是在发生碰撞后的PullBackHit中：



```
static void PullBackHit(FHitResult& Hit, const FVector& Start, const FVector& End, const float Dist)
{
    const float DesiredTimeBack = FMath::Clamp(0.1f, 0.1f/Dist, 1.f/Dist) + 0.001f;
    Hit.Time = FMath::Clamp( Hit.Time - DesiredTimeBack, 0.f, 1.f );
}
```

之后执行位置回退时，会使用这个计算的Time



```
NewLocation = TraceStart + (BlockingHit.Time * (TraceEnd - TraceStart));
```

也就是说，如果你是在进行子弹模拟的话，这个回避之后的位置有可能离碰撞表面会比较远。


这个时候使用返回的HitResult中的ImpactPoint或者Location反而更加接近一些。


## 骨骼位置


对于依赖于动画更新的骨骼而言，其物理体的位置与其渲染位置是会存在一个微小的偏差的。如果项目中使用了一些特定的优化的话，这个偏差可能会被放大。在使用的时候需要注意。


取到的位置不在预期点主要由以下两个函数引发：


### UpdateKinematicBonesToAnim


当我们调用USkinnedMeshComponent::GetBoneTransform的时候，其实并不是去取物理世界中取骨骼的位置。我们取到的结果决定于两个值，一个是当前的ComponentToWorld，另一个是缓存的GetComponentSpaceTransforms。


而GetComponentSpaceTransforms本身是一个维护的双缓冲系统，其更新依赖于USkinnedMeshComponent::FlipEditableSpaceBases。


也就是说，在实际更新过程中，这两者有一个过期就会导致出现偏差。


实际去更新物理位置的逻辑在USkeletalMeshComponent::UpdateKinematicBonesToAnim中能够找到。


作一个简单的测试，在USkeletalMeshComponent::UpdateKinematicBonesToAnim中直接return。然后在运行时使用pvd连接引擎，你会发现移动角色之后，骨骼在物理世界的位置并没有发生移动。此时渲染的位置却已经移动了。


### setKinematicTarget


在UpdateKinematicBonesToAnim中还有另一个可能会影响到实际使用的更新，就是setKinematicTarget，如果在移动骨骼的时候没有设置Teleport的话，就会使用这个函数进行物理设置。


按照[[Physx的文档](https://docs.nvidia.com/gameworks/content/gameworkslibrary/physx/apireference/files/classPxRigidDynamic.html#4464d188e7a1e94582c9cf35da9bbc93)]描述，这里面其实有个类似缓存的机制



> The move command will result in a velocity that will move the body into the desired pose. After the move is carried out during a single time step, the velocity is returned to zero. Thus, you must continuously call this in every time step for kinematic actors so that they move along a path.
> 
> 
> This function simply stores the move destination until the next simulation step is processed, so consecutive calls will simply overwrite the stored target variable.
> 
> 
> The motion is always fully carried out.
> 
> 


也就是说，“真实”的物理位置会在下一次模拟之后才会更新。


### 安全的获取方式


要“正确”的取到想要的位置，只要使用bodyinstance的GetUnrealWorldTransform就可以了。其中第二个参数bForceGlobalPose就是区分是否取setKineMaticTarget的位置。


如果是要渲染位置，还是用GetBoneTransform就可以。


## 总结


由于引擎其实是按帧模拟的，更多的时候，位置偏差其实发生在更新次序问题上。


所以除非在特殊情况下，还是不要在意比较好……


