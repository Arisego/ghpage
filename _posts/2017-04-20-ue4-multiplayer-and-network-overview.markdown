---
layout: post
status: publish
published: true
title: UE4网络连接与多人游戏
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1599
wordpress_url: http://blog.ch-wind.com/?p=1599
date: '2017-04-20 23:03:17 +0000'
date_gmt: '2017-04-20 15:03:17 +0000'
tags:
- UE4
- MultiPlayer
- Replication
---
UE4的Replication系统在设计上非常的高效和迅速，要制作联网游戏相关功能的话使用起来也很方便。  

当前UE4版本为4.15.0。


## 概述


蓝图中的GameMode是自带支持Replication系统的，GameMode也是整个Replication系统在逻辑设计上的中心。如果在设计游戏时，不需要联网功能，目前引擎已经提供了一个新的基类GameModeBase来使用。


网络模式相关的官方文档在[[这里](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/index.html)]。


网络模式的调试可以在PIE中进行，点击调试旁边的下拉三角就可以进行设置。Server的模式分为DedicatedServer和ListenServer，如果在多客户端模式下进行屏幕调试输出，会发现输出会自动表明输出者的身份，在源代码中可以找到它的实现方式：



```
UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, false);
FString Prefix;
if (World)
{
  if (World->WorldType == EWorldType::PIE)
  {
    switch(World->GetNetMode())
    {
      case NM_Client:
        Prefix = FString::Printf(TEXT("Client %d: "), GPlayInEditorID - 1);
      break;
      case NM_DedicatedServer:
      case NM_ListenServer:
        Prefix = FString::Printf(TEXT("Server: "));
      break;
      case NM_Standalone:
      break;
    }
  }
}
```

这个宏也可以自己拿来做一些判断用，例如区分独立服务器与监听服务器。


另外，如果要使用官方模板进行功能测试的话需要注意：


TopDown模板的角色移动是基于NavMesh的，而这个机制本身是不支持直接联网的，因此角色不会移动。


而默认的Blank模板的Pawn是没有CharacterMoveMentComponent的，当然也就不会同步角色移动。


## 属性复制


Replication系统的核心是复制，“真正”的UWorld更新是在Server上运行的，而Client上的UWorld则接受来自Server的复制更新，同时Client也会进行一定的“预测”，但是一切状态值以Server上的为准。这样的设计下，只要采用合理的逻辑，就可以杜绝作弊。


UE4中Replication在设置完成后是自动运行的，在使用时只要留意，凡是需要所有客户端都获得的状态更新，包括Spawn、Replicate的值，都必须在服务器上进行。在客户端上进行修改只会让他们在下一次同步时被覆盖掉。


### 开启复制


属性复制可以在Actor的属性面板中开启


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image.png)


C++中则需要在构造函数中指定



```
bReplicates = true;
```

开启复制之后，对于具体的属性，只要指定为可复制即可：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-1.png)


其中Replicated就是复制模式，而RepNotify会在属性被变更时触发一个通知事件，非常的有用。在蓝图下，这个事件会自动生成：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-2.png)


而在C++模式下，就要做一些额外的设定操作，除了指定属性可复制之外



```
UPROPERTY(Replicated)
uint32 bFlag:1;
```

还要设置同步属性表



```
void AReplicatedActor::GetLifetimeReplicatedProps(TArray< FLifetimeProperty > & OutLifetimeProps) const
{
DOREPLIFETIME(AReplicatedActor, bFlag);
DOREPLIFETIME(AReplicatedActor, IntegerArray);
}
```

如果要使用RepNotify的话，就必须在UPROPERTY宏中进行指定



```
UPROPERTY(ReplicatedUsing=OnRep_Flag)
uint32 bFlag:1;
```

然后实现这个函数方可。


### 条件复制


Replication有一个重要的设置是条件复制，在蓝图中可以看到选项  

[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-3.png)


意思都比较明显，关于Owner以及Simulated、Autonomous的意思在下面会有说明，而Replay指代的是官方的回放系统，如果没有使用到的话就可以不用管它。


C++中要调整这个属性则需要用到属性表：



```
void AActor::GetLifetimeReplicatedProps( TArray< FLifetimeProperty > & OutLifetimeProps ) const
{
  DOREPLIFETIME_CONDITION( AActor, ReplicatedMovement, COND_SimulatedOnly );
}
```

在C++中还可以使用额外的自定义标志位来进行更新控制：



```
void AActor::PreReplication( IRepChangedPropertyTracker & ChangedPropertyTracker )
{
  DOREPLIFETIME_ACTIVE_OVERRIDE( AActor, ReplicatedMovement, bReplicateMovement );
}
```

但是这样可能会降低效率，更详细的说明可以参照[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/Actors/Properties/Conditions/index.html)]。另外，在文档中有说明，属性表是无法在同步确立之后进行修改的。


### 参数设置


Replication中还有一些可选参数，其中比较重要的是Relevant机制，这个机制通过判定Actor当前是否与Player相关来有效的削减同步的数据量


Always Relevant会使得Actor始终被同步到各个客户端


Net Use Owner Relevancy则会让Actor的同步相关性与持有者相同


Only Relevant To Owner使得Actor只与自己的持有者保持相关


这里Owner的定义指代持有其的PlayerController或者Pawn，而是否相关的判定机制是可以重载的，在类中对IsNetRelevantFor函数进行重载即可。


还有一个特殊的标志位是bTearOff，一旦Server设置了这个值，Replication机制会将控制权交给所有的Client，实质上Actor就变成了不同步的物体，由各个Client进行控制。


而ReplicateMovement将会使得物体的移动被同步，也就是速度、位置这些信息。


bNetLoadOnClient会使得物体在Server上加载/Spawn后在Client上被自动加载。


## 远程调用


远程函数调用提供Clinet与Server之间的函数调用桥梁，调用模式分为三种：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-4.png)


选中蓝图中的函数就能看到这个设置，它们之间的区别如下：



> NetMulticast: 多路传送，由服务器调用所有的客户端，比如用于播放特效
> 
> 
> Server: 在服务器上运行，只有角色标志为ROLE_Authority或ROLE_AutonomousProxy的Actor才能调用
> 
> 
> Client: 在其所属的客户端上运行
> 
> 


其中，Server函数还可以提供额外的校验函数以方便对传输到服务器的值进行检测，这个设置只能在C++中使用，蓝图中并未看到相关选项：



```
UFUNCTION(Server, Reliable, WithValidation)
void Server_ReliableFunctionCallThatRunsOnServer();   UFUNCTION(Client, Reliable)
void Client_ReliableFunctionCallThatRunsOnOwningClientOnly();   UFUNCTION(NetMulticast, Unreliable)
void Client_UnreliableFunctionCallThatRunsOnAllClients();
```

对函数进行实现



```
void AReplicatedActor::Server_ReliableFunctionCallThatRunsOnServer_Implementation()
{
}
bool AReplicatedActor::Server_ReliableFunctionCallThatRunsOnServer_Validate()
{
   // 返回FALSE的话该Server函数就不会被执行
   return true;
}
void AReplicatedActor::Client_ReliableFunctionCallThatRunsOnOwningClientOnly()
{
}   
void AReplicatedActor::Client_UnreliableFunctionCallThatRunsOnAllClients_Implementation()
{

}
```

函数还可以选择是否为可靠函数，UnReliable的设定将会使得引擎在网络带宽压力大的情况下丢弃这个函数的执行。


应当尽量避免频繁的远程调用以及在远程调用中直接传输并设置Server参数的行为，而只将输入传递到Server。


## 游戏架构


官方的指引文档中就有介绍过游戏架构,但实际上在做单机游戏时,将逻辑放在很多类中其实是等效的,这点会让人很迷惑。其实架构中的许多类是在多人模式下才会体现出他们的不同的，详细的内容可以看[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/Blueprints/index.html)]。


* GameInstance: 不参与网络复制，作为游戏实例而存在，在关卡切换载入时依然存在，可以用于存储用户本身的数据
* GameMode: 只存在于Server上，核心逻辑存在于这里
* GameState: 在Server和所有Client之间复制，用于存储当前游戏相关的数据
* PlayerController: 每个Client只持有自己的PlayerController，并与Server进行同步
* PlayerState: 存储每个Player的信息，会同步到所有的Client。
* Pawns: 与所有的Client同步，但是与PlayerController以及PlayerState不同的是，Pawn死亡之后会被销毁，直到Respawn为止。


### Role与同步


Server和Client都可以使用Role系统来判断持有的Actor状态，Role被分为四种


ROLE_Authority：对Actor拥有控制权


ROLE_None：不参与网络复制


ROLE_SimulatedProxy：接受来自服务器更新的模拟控制器，使用已知信息进行预判


ROLE_AutonomousProxy：接受来自玩家的直接控制，配合玩家输入进行预判


客户端的模拟预判可以有效防止网络延迟引起的Lag，但是在处理角色动作，尤其是Blink之类的操作时，依然会导致奇怪的现象。


为了防止这些现象，官方对CharacterMovmentComponent作了增强，这个类会维护一个动作列表，在同步时，Client会被要求进行动作列表的重放，而不是直接更新位置。详细的可以参考[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/CharacterMovementComponent/index.html)]。


## Misc


UE4提供了服务器进行无缝和非无缝关卡切换的函数，其具体的限制和功能可参看[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/Travelling/index.html)]。


同时，为了提供轻便的服务器状况查询，而不是被强制加载关卡，UE4有提供Online Beacons的功能，由于不会用到就没有继续研究了，详情见[[官方文档](https://docs.unrealengine.com/latest/CHN/Gameplay/Networking/OnlineBeacons/index.html)]。


