---
layout: post
status: publish
published: true
title: UE4项目笔记汇总
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2170
wordpress_url: http://blog.ch-wind.com/?p=2170
date: '2018-01-01 00:01:50 +0000'
date_gmt: '2017-12-31 16:01:50 +0000'
tags:
- UE4
- UMG
- 物理
---
这里是过去一段与项目有关的笔记汇总，把一些零零碎碎的给合在了一起。


由于项目一直停留在4.15，所以本文所有内容都是基于UE4.15.3的。


## 物理相关


由于做的项目对运动的精度要求比较高，所以和物理打了很长一段时间的交道。


在用UE4之前基本没接触过3D的物理引擎。好在之前有用过Box2D，一些基本的物理引擎原理还是有些了解的。


### 球体运动


遇到的第一个问题是球体运动相关的，Physx对球体运动的模拟有些糟糕。


主要表现是Friction对球体的速度影响相当的微妙，导致球的运动很难停下来。而如果使用LinearDumping和AngularDumping来进行速度制御的话，由于其并不是匀减速的，而且即便与Friction没有关系，运动也不真实。这部分的解决方案之前已经记录在[[UE4中的Physx物理](https://blog.ch-wind.com/ue4-physx-and-substepping/)]这篇文章中了，总之就是自己接管物理的部分运算。


更加区域的注册自己添加上摩擦力和反弹。途中遇到过很多问题，现在回头看的话，发现代码的实现还是不够简洁。


而且虽然一开始坚持想要存依靠公式来进行运动控制，但最后还是往里面添加了不少“黑魔法”……


### Foliage碰撞


后面出现的一个需求是关于Foliage的碰撞的，总体而言就是需要树的不同部分表现出不同的碰撞特性。


比如树叶区域进行Overlap，而树干区域进行Block。但是由于Foliage本身是一种Instanced的Actor，UE4在实现时，对于同一个FoliageType只能使用一个碰撞配置。


不过Instance主要是针对渲染而进行的一种优化方案，既然Foliage是可以进行碰撞的，那么在Physx world中肯定是有注册碰撞形态的。


几经探索之后终于找到解决方案，通过UE4提供的Physx底层Api，将Foliage Type实例化之后的碰撞形态取出，单独将Capsule的碰撞形态重新注册到Physx中去。


这里本来是想直接对PxActor的碰撞配置进行修改的，但是UE4在上层有封装，无法将Overlap的物体的碰撞响应传递出去。所以只有采取取出重新注册的方案。


但是由于场景中的Foliage实在是太多，在地图载入时进行整体性操作会导致不可接受的时间消耗，最后采用动态转化的方案，将玩家周围的Foliage取出，并拉取出Capsule来实现。


这里面有遇到一个困扰了很久的问题，那就是Capsule取出之后怎么都无法找到正确的对应Roation。几经周折才发现UE4中的Capsule和Physx中的Capsule是有不同的默认朝向的，需要手动进行一次转化才行：



```
static const PxQuat CapsuleRotator(0.f, 0.707106781f, 0.f, 0.707106781f);

PxQuat ConvertToPhysXCapsuleRot(const FQuat& GeomRot)
{
  // Rotation required because PhysX capsule points down X, we want it down Z
  return U2PQuat(GeomRot) * CapsuleRotator;
}

FQuat ConvertToUECapsuleRot(const PxQuat & PGeomRot)
{
 return P2UQuat(PGeomRot * CapsuleRotator.getConjugate());
}
```

## 屏幕偏移


就是要让FOV的计算有一个Offset，当时查了很多资料。只在AnswerHub找到一个旧版本的不是很完全的实现。


好在通过那个页面里的讨论找到了解决的方向，而不用自己深入到UE4的渲染代码中去找Hack Point。


最主要的问题是，讨论最后给出的Viewport的转换矩阵是错的，转换之后的结果并不能让人满意。UE4的渲染实现并不“标准”，所以使用通用的摄像投影矩阵还是无法实现类似视点中心偏移的效果。


最后终于在代码深处的BlendCamera中找到了UE4本身对视角偏移的处理，得出了“正确”的偏移矩阵



```
/** 计算投影矩阵 */
float t_fRatio = InCamera->AspectRatio;
if (!InCamera->bConstrainAspectRatio)
{
 t_fRatio = t_ScreenSize.X / t_ScreenSize.Y;
}

float t_fFov = InCamera->FieldOfView;
float t_fNear = GNearClippingPlane;

result = FReversedZPerspectiveMatrix(t_fFov * PI / 360.0f, t_fRatio, 1.0f, t_fNear);

if (Offset.IsZero())
{
 return true;
}

/** 将Offset规范到百分比 */
Offset.X /= (t_ScreenSize.X / 2.0f);
Offset.Y /= (t_ScreenSize.Y / 2.0f);

/** Clamp以避免“过度”偏移 */
Offset = FMath::Clamp(Offset, FVector2D(-1, -1), FVector2D(1, 1));

const float Left = -1.0f + Offset.X;
const float Right = Left + 2.0f;
const float Bottom = -1.0f + Offset.Y;
const float Top = Bottom + 2.0f;

result.M[2][0] = (Left + Right) / (Left - Right);
result.M[2][1] = (Bottom + Top) / (Bottom - Top);
```

不过，当时由于实现的比较急切，直接沿用讨论的方向，对Viewport类进行了重载，也使用了一些“黑魔法，虽然至今没有观测到副作用，但是现在想来，其实还是有其他的解决方案的。


## UI相关


UMG只实现了默认的几种常见的Widget，所以有很多需要实现的自定义控件。这个也算是UI开发的常态了，但是当时有两个问题还是困扰了一段时间。


### Slate的序列帧


UMG的序列帧实现在社区可以找到，但是当需要在LoadingScreen上播放序列帧时就会有麻烦。因为那个时候UMG系统还没有初始化完成，只能使用Slate。


在参考了UE4的进度条实现之后，找到了相关的接口：



```
FVector2D Min(FrameSize.X * Column, FrameSize.Y * Row);
FVector2D Max = Min + FrameSize;
FBox2D UVCoordinates(Min / TextureSize, Max / TextureSize);
UVCoordinates.bIsValid = true;

Brush.SetUVRegion(MoveTemp(UVCoordinates));
```

这样就可以实现序列帧的切换了。


### 2D画线


FSlateDrawElement::MakeLines有一个问题，那就是不知为何最后实现的时候Thickness这个参数是不起作用的。


因此要画粗线就必须自己想办法，虽然试过很多方法，包括参考UE4内部的线段AA实现，但是最后还是采用了最不优雅的解决方案：多画几次。



```
FVector2D DrawPosition;
for (; aTimes > 0; --aTimes)
{
 DrawPosition = FVector2D::ZeroVector;
 if (m_bIsVert) DrawPosition.Y = aTimes;
 else DrawPosition.X = aTimes;

 FSlateDrawElement::MakeLines(
  InContext.OutDrawElements,
  InContext.MaxLayer,
  InContext.AllottedGeometry.ToPaintGeometry(DrawPosition, FVector2D(1.0f,1.0f), 1.0f),
  tLine,
  InContext.MyClippingRect,
  ESlateDrawEffect::None,
  color,
  true,
  0.1f);
}
```

因为这样画出来的才是最平滑的，好在对粗细的要求并不高，否则可能会加大绘制的负担。


