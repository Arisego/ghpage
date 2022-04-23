---
layout: post
status: publish
published: true
title: UE4人物同步机制小结
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2737
wordpress_url: https://blog.ch-wind.com/?p=2737
date: '2019-11-24 12:25:50 +0000'
date_gmt: '2019-11-24 04:25:50 +0000'
tags:
- UE4
- 移动
---
虚幻自带的人物网络同步移动机制在结构上有些复杂，这边刚好最近有接触到，稍微整理下逻辑。


当前的UE4版本为4.23。


由于部分描述可能是来自项目魔改引擎的经验，所以可能会与实际引擎的工作方式稍有出入。


按照Role的不同，人物在主控端、服务器端和模拟端分别使用不同的逻辑进行移动模拟。这里只记录了DS的情况，如果是Listen Server的话，在一些细节的部分会稍微有些不同，由于目前没有具体的接触过，便没有详细的考究过。


在机制上，操作者(ROLE_AutonomousProxy)首先进行移动，然后将移动数据发送到服务器(ROLE_Authority)，服务器进行模拟后判定是否接受操作者上报的位置，并在一帧的末尾将新的角色位置信息同步到模拟端(ROLE_SimulatedProxy)。


## 服务器


服务器在处理上的逻辑相对比较单纯一些，虽然主控端会根据不同的情况使用不同的RPC来对数据进行发送。到最后都会归结到两个函数上：`ServerMoveOld`和`ServerMove`。


这两个函数的内部逻辑很相似，其中，ServerMove负责主要的移动数据处理，而ServerMoveOld则处理旧的关键包，详细的逻辑整理在主控端逻辑中。


服务器使用`FNetworkPredictionData_Server_Character`来对移动状态进行维护。很多计算的中间和缓存量都会保存在这个数据结构里面。


另外，逻辑上，服务器在没有接受到主控端上报的情况下，是不会进行移动模拟的。为了防止出现一些问题，有一个[ForcePositionUpdate](https://blog.ch-wind.com/ue4-characer-move-note/#ForcePositionUpdate)的机制来对服务端行为进行保护。


### ServerMoveOld


目前所有的移动都是走的非可靠包发送的，而ServerMoveOld就是为了防止关键性的移动包被丢包而存在的一个保险机制。


这个函数的处理相对简单，只作了两个服务器同步的核心处理。


#### 时间戳转验证和转换


为了保证移动计算的精度，虚幻在移动上报中使用的时间戳并不是光卡时间。而是一个经过回转处理的时间戳。这个设定值是:



```
/** Minimum time between client TimeStamp resets.
 !! This has to be large enough so that we don't confuse the server if the client can stall or timeout.
 We do this as we use floats for TimeStamps, and server derives DeltaTime from two TimeStamps. 
 As time goes on, accuracy decreases from those floating point numbers.
 So we trigger a TimeStamp reset at regular intervals to maintain a high level of accuracy. */
UPROPERTY()
float MinTimeBetweenTimeStampResets;
```

整个时间戳检查的逻辑都在VerifyClientTimeStamp这个函数中，同时在检查到回转发生的情况下也会对NetworkPredictionData中还会用到的时间戳进行回转处理。


#### 服务端模拟


在经过时间戳验证后，会根据上报的时间戳来计算一个`DeltaTime`。


虚幻有自带一个时间补偿的反加速机制，但是由于粒度有点粗，所以并没有用过。在没有触发这个机制的情况下，会根据本次的时间戳于上一次的时间戳差来计算一个差值。


当然，服务器不会无限度的接受客户端的`DeltaTime`，考虑到丢包和作弊的情况，有一个 `MaxDeltaTime`会对单次处理的最大时间差作限制，这个值的设置是0.125s。


取出Delta后，就会调用[MoveAutonomous](https://blog.ch-wind.com/ue4-characer-move-note/#i-19)进行移动的模拟。


### ServerMove


这个函数承担了服务器移动模拟的更多的检查工作，在主控端上报上，由于会出现合包的情况，会有传入位置是特殊的(1,2,3)的情况，例如在ServerMoveDual_Implementation中就有：



```
ServerMove_Implementation(TimeStamp0, InAccel0, FVector(1.f,2.f,3.f), PendingFlags, ClientRoll, View0, ClientMovementBase, ClientBaseBone, ClientMovementMode);
ServerMove_Implementation(TimeStamp, InAccel, ClientLoc, NewFlags, ClientRoll, View, ClientMovementBase, ClientBaseBone, ClientMovementMode);
```

如果在ServerMove作了特殊处理的话需要留意。


与ServerMoveOld相比，这个函数中多作了几个处理：


#### 状态检查和旋转处理


通过调用NotifyServerReceivedClientData来检查服务器是否处在可以接受移动包的状态。


同时在执行移动模拟前会将旋转状态传到Controller那边去作处理。


#### 位置受理检查


主要在ServerMoveHandleClientError中进行的一个检查，这里的检查结果将会决定服务器是否接受上报的移动，如果不接受的话会对主控端进行修正。如果接受位置且有设置ClientAuthorativePosition的话，会将服务器的位置设置到上报的位置上去。


对位置的受理或者修正并不是在这里进行的，而是会将标志位以及必要的信息存在ServerData中，之后再进行处理。


这边的结果其实有时候比较难以预知，因为前面的ServerMoveOld并没有作这个检查，导致服务器的模拟基础难以预期。


这些检查的结果也是缓存在ServerData中的。


##### 调用频率控制


这个频率控制是基于ServerData中的LastUpdateTime的，这个时间会在服务器决定对客户端进行修正时更新。



```
APlayerController* PC = Cast<APlayerController>(CharacterOwner->GetController());
if( (ServerData->LastUpdateTime != GetWorld()->TimeSeconds))
{
  const AGameNetworkManager* GameNetworkManager = (const AGameNetworkManager*)(AGameNetworkManager::StaticClass()->GetDefaultObject());
  if (GameNetworkManager->WithinUpdateDelayBounds(PC, ServerData->LastUpdateTime))
  {
    return;
  }
}
```

也就是说，在当前帧没有修正过主控端位置的情况下，检查是否最近修正过主控端位置。如果有配置对应的频率限制的话，会不进行受理检查。在这种情况下，服务器的移动状态与ServerMoveOld的处理有些类似。


当然，在ServerData中的强制更新标签等状态也会一直保留，等到下一次进入这个函数会继续起作用。


##### 差异检查


在检查之前会对地板状态进行处理，主要是对动态地板的位置转换，以及对客户端明明在Walking却没有地板的情况进行修正。


如果此时ServerData中有设置bForceClientUpdate为True的话，就强制进行位置修正。其他情况则会调用ServerCheckClientError对主控端和服务端的移动状态进行比对。


比对的主要逻辑在ServerCheckClientError中，主要就是对两端的位置差异进行比较，如果超过了阈值则会触发修正。以及，如果两端的MovementMode不一致，则也会强制的触发修正。


是否受理会决定ServerData中bAckGoodMove的值，影响之后下发数据到主控端的分支选择。


以及，如果开启了对应选项的话，在受理的同时也会更新服务器的位置到上报位置。


### ForcePositionUpdate


在逻辑上，服务器在收到客户端的数据包之前是不会进行移动的。


但是如果实际上这样运行的话，会有很多问题。例如，如果玩家在跳到空中之后掉线或者屏蔽ServerMove的话，就可能会一直留在空中了。


因此，在PlayerController中，有一个额外的ForcePositionUpdate的逻辑。


这个逻辑会根据配置的MAXCLIENTUPDATEINTERVAL来对移动状态进行检查，如果有一段时间没有收到客户端的ServerMove的话，会强制调用ForcePositionUpdate来对服务器的运动进行模拟。



```
const float TimeSinceUpdate = GetWorld()->GetTimeSeconds() - ServerData->ServerTimeStamp;
const float PawnTimeSinceUpdate = TimeSinceUpdate * GetPawn()->CustomTimeDilation;
if (PawnTimeSinceUpdate > FMath::Max<float>(DeltaSeconds+0.06f, AGameNetworkManager::StaticClass()->GetDefaultObject<AGameNetworkManager>()->MAXCLIENTUPDATEINTERVAL * GetPawn()->GetActorTimeDilation()))
{
  //UE_LOG(LogPlayerController, Warning, TEXT("ForcedMovementTick. PawnTimeSinceUpdate: %f, DeltaSeconds: %f, DeltaSeconds+: %f"), PawnTimeSinceUpdate, DeltaSeconds, DeltaSeconds+0.06f);
  const USkeletalMeshComponent* PawnMesh = GetPawn()->FindComponentByClass<USkeletalMeshComponent>();
  if (!PawnMesh || !PawnMesh->IsSimulatingPhysics())
  {
    // We are setting the ServerData timestamp BEFORE updating position below since that may cause ServerData to become deleted (like if the pawn was unpossessed as a result of the move)
    // Also null the pointer to make sure no one accidentally starts using it below the call to ForcePositionUpdate
    ServerData->ServerTimeStamp = GetWorld()->GetTimeSeconds();
    ServerData = nullptr;

    NetworkPredictionInterface->ForcePositionUpdate(PawnTimeSinceUpdate);
  }
}
```

最终会调用到PerformMovemen来进行移动的模拟。


### 数据下发


这里指的主要是针对主控端的数据下发，模拟端的数据是通过正常的值复制逻辑进行的。也就是说是在`PreReplicate`阶段通过`GatherCurrentMovement`收集到`ReplicatedMovement`然后值复制下行的。


服务器上单帧内，可能会收到很多ServerMove的移动包，其处理结果会被缓存到ServerData之中。


这个逻辑的核心处理逻辑在SendClientAdjustment中，会在引擎的数据下发阶段，在ServerReplicateActors中直接通过PlayerController调用到。


ServerData中影响最大的数据是bAckGoodMove，这个标记为True时，就只会调用ClientAckGoodMove来通知主控端服务器已经接受了本次移动，这里下发的是客户端上行的时间戳。如果标记为False，则会对主控端进行修正，根据情况的不同会走不同的RPC进行下发以保证只会发送必要的数据。


两种下发方式都有各自的频率控制，详细的逻辑可以在UCharacterMovementComponent::SendClientAdjustment进行查看。


## 主控端


主控端是接受玩家直接控制的，所以在逻辑上是最为复杂的。


所以，与服务器不同，并不是单纯的一个ServerData的缓存，而是一个SavedMoves的数组在对移动状态缓存。


### 服务器状态接收


从单帧的时序上，最早执行的是服务器状态回复包的检查。


#### AckGood


如果服务器回报的是AckGoodMove的话，在整体的逻辑上会比较简单。就只是根据回复的时间戳，到历史队列中找到对应的移动包，并将在其之前的缓存包全部删除掉。因为既然服务器已经接受了这个包，那么之前的移动缓存就没有用了，这个逻辑在UCharacterMovementComponent::ClientAckGoodMove_Implementation中。


#### Adjust


如果是修正包的话，情况会稍微有些复杂。不过与服务器类似的是，虽然有很多RPC的通道，到最后会归结到到`ClientAdjustPosition`中。当然不同的RPC会有一些独自的处理，不过由于没有使用过RootMotion之类的，这边只记录与移动逻辑有光的部分。


数据修正时首先还是对本地缓存进行更新，这里有个特殊的丢包处理。


如果下发的标志中有表明地板信息而下发的地板指针却是空的话，则会认定地板还没有值复制成功，暂时不处理这个修正。


之后同样的会根据时间戳对缓存数据进行删除，并通过OnClientCorrectionReceived发送事件出去。


然后会将本地位置和状态都设置到服务器下发的位置上去，同时设置ClientData标签bUpdatePosition为True。这个标签是为了之后重放移动准备的，由于移动重放操作还是比较重的，而且如果每个修正操作都会设置位置的话，在单次的RPC中设置就没有什么意义，因为如果又收到一个修正包的话就只是凭空的浪费了运算过程。


### 缓存重放


在进行了位置修正的情况下，需要对缓存的移动进行重放。


这个操作是在TickComponent中执行的。


移动的重放最后也是调用MoveAutonomous，在重放操作中会对必要的数据进行缓存并在之后重新设置回去。



```
// Save important values that might get affected by the replay.
const float SavedAnalogInputModifier = AnalogInputModifier;
const FRootMotionMovementParams BackupRootMotionParams = RootMotionParams; // For animation root motion
const FRootMotionSourceGroup BackupRootMotion = CurrentRootMotion;
const bool bRealJump = CharacterOwner->bPressedJump;
const bool bRealCrouch = bWantsToCrouch;
const bool bRealForceMaxAccel = bForceMaxAccel;
CharacterOwner->bClientWasFalling = (MovementMode == MOVE_Falling);
CharacterOwner->bClientUpdating = true;
bForceNextFloorCheck = true;

// Replay moves that have not yet been acked.
UE_LOG(LogNetPlayerMovement, Verbose, TEXT("ClientUpdatePositionAfterServerUpdate Replaying %d Moves, starting at Timestamp %f"), ClientData->SavedMoves.Num(), ClientData->SavedMoves[0]->TimeStamp);
for (int32 i=0; i<ClientData->SavedMoves.Num(); i++)
{
  FSavedMove_Character* const CurrentMove = ClientData->SavedMoves[i].Get();
  checkSlow(CurrentMove != nullptr);
  CurrentMove->PrepMoveFor(CharacterOwner);
  MoveAutonomous(CurrentMove->TimeStamp, CurrentMove->DeltaTime, CurrentMove->GetCompressedFlags(), CurrentMove->Acceleration);
  CurrentMove->PostUpdate(CharacterOwner, FSavedMove_Character::PostUpdate_Replay);
}

if (FSavedMove_Character* const PendingMove = ClientData->PendingMove.Get())
{
  PendingMove->bForceNoCombine = true;
}

// Restore saved values.
AnalogInputModifier = SavedAnalogInputModifier;
RootMotionParams = BackupRootMotionParams;
CurrentRootMotion = BackupRootMotion;
```

逻辑上还是比较单纯的，虽然看上去会处理很多数据，但是由于主控端每帧只会对自己做一次这个操作，运算消耗还是在可控制范围内的。


### 移动并上报


在移动重放之后，会在ReplicateMoveToServer中对当帧的移动进行模拟并上报。


#### 状态更新


由于真正的移动操作就只是调用PerformMovement，所以实际上这个函数主要处理的移动上报和缓存更新。


在`UpdateTimeStampAndDeltaTime`中进行时间戳的更新，主要处理的是CurrentTimeStamp的累计、时间戳回转以及必要的Clamp操作。


接下来，会从缓存的移动中，以IsImportantMove为标准尝试寻找出一个最旧的关键移动包作为OldMove。


#### 移动模拟


这里会有一个PendingMove和NewMove的逻辑，主要的目的是尝试对移动进行合并，减少不必要的数据传输。


在移动之前，会对PendingMove进行检查，如果通过了CanCombineWith的话，就会对NewMove进行CombineWith操作来将移动操作合并。


PendingMove本身是在移动后生成的，如果单次移动满足条件，就会尝试进行缓存并不再继续进行发包操作。



```
const bool bCanDelayMove = (CharacterMovementCVars::NetEnableMoveCombining != 0) && CanDelaySendingMove(NewMovePtr);

if (bCanDelayMove && ClientData->PendingMove.IsValid() == false)
{
  // Decide whether to hold off on move
  const float NetMoveDelta = FMath::Clamp(GetClientNetSendDeltaTime(PC, ClientData, NewMovePtr), 1.f/120.f, 1.f/5.f);

  if ((MyWorld->TimeSeconds - ClientData->ClientUpdateTime) * MyWorld->GetWorldSettings()->GetEffectiveTimeDilation() < NetMoveDelta)
  {
    // Delay sending this move.
    ClientData->PendingMove = NewMovePtr;
    return;
  }
}
```

### 数据上行


数据上行在之后通过CallServerMove进行，这里能看到一些用于移动丢包测试的Console。


在CallServerMove中的逻辑其实就只是根据不同的情况调用不同的RPC进行数据上报，MoveOld是单独通过ServerMoveOld进行的，NewMove虽然操作会有不同，最后都会抵达ServerMove。


这里其实主要的区分是在PendingMove上，如果合并包失败的话，这边就会使用Dual的RPC，将两次移动一并带上去。


### Misc


有一个特殊的标签`bIgnoreClientMovementErrorChecksAndCorrection`可以暂停掉服务器和主控端的修正处理流程。


`FlushServerMoves`会将所有缓存的移动全部作为NewMove通过CallServerMove发送出去，不过当前只有UE4自带的技能系统有使用到。


## 模拟端


模拟端的角色移动是被动的，在逻辑上特殊的地方，其实只有一个Mesh与Actor分离插值的过程。


### 值复制


模拟端的处理是从值复制的OnRep操作开始的，通常这个操作在OnRep_ReplicatedMovement中传递到ACharacter::PostNetReceiveLocationAndRotation；对于有动态地板的情况，会在OnRep_ReplicatedBasedMovement中。作为插值参考的ReplicatedServerLastTransformUpdateTimeStamp是单独值复制的。


对于值复制的处理分为两个主要的部分：SmoothCorrection和OnUpdateSimulatedPosition。


#### SmoothCorrection


在插值模式为需要插值的情况，这里会对Mesh与Actor的偏差MeshTranslationOffset以及MeshRotationOffset进行更新。


有两个限制值，保证Actor本身的新的位置与当前的位置的偏差NewToOldVector不会过大的拉大插值距离：



```
const float DistSq = NewToOldVector.SizeSquared();
if (DistSq > FMath::Square(ClientData->MaxSmoothNetUpdateDist))
{
  ClientData->MeshTranslationOffset = (DistSq > FMath::Square(ClientData->NoSmoothNetUpdateDist))
    ? FVector::ZeroVector
    : ClientData->MeshTranslationOffset + ClientData->MaxSmoothNetUpdateDist * NewToOldVector.GetSafeNormal();
}
else
{
  ClientData->MeshTranslationOffset = ClientData->MeshTranslationOffset + NewToOldVector;
}
```

之后就是将UpdatedComponent的位置移动到新的位置，这里有一个帮助类FScopedPreventAttachedComponentMove，保证移动操作不会变更Mesh的位置。


接下来就是一些时间戳的维护操作，主要是确保SmoothingClientTimeStamp与SmoothingServerTimeStamp能够在一个合理的容错范围内。


#### OnUpdateSimulatedPosition


这边的逻辑比较单纯，只是作一些状态设置。


如果位置发生了变动的话，会将`bJustTeleported`设置为true。


如果下发的运动状态没有速度却发生了位置改变的话，会对目标位置作一次`EncroachingBlockingGeometry`检查，如果位置被修正了的话，会启用`bSimGravityDisabled`标志，防止之后的模拟导致不可预知的下坠。


### SimulatedTick


模拟端的插值和模拟逻辑由TickComponnet在SimulatedTick中进行。


#### 执行移动


模拟移动的逻辑在SimulateMovement中，这个函数与PerformMovement相比，进行了大幅的简化。


对于SkipProxyPredictionOnNetUpdate开启了的情况，如果当前帧进行了网络更新，则不会进行移动模拟。


如果有相应的标签的话，会尝试对网络下发的移动状态进行应用以及对地板进行更新。


在状态设置过之后，就会调用MoveSmooth来进行模拟端的移动模拟。


#### Mesh位置插值


这个过程分为两个部分，SmoothClientPosition_Interpolate负责逻辑更新，SmoothClientPosition_UpdateVisuals负责实际的Mesh位置移动。


由于插值过程中的Mesh移动不会Sweep，所以会有穿墙的可能性，但是由于位置是由服务器下发的，所以实际上穿墙的情况还是比较短暂和罕见的。


插值的位置可以使用p.NetVisualizeSimulatedCorrections来进行一定程度的观察。


插值模式主要在Linear和Exponential上，这两者除了计算方式不同之外，Linear会在插值过程中有一定的“预测”作用，所以在取舍上需要留意。


## 移动模拟


移动模拟的逻辑，主要在MoveAutonomous中，而在模拟端有一个弱化的MoveSmooth。


在实际的使用中，有的逻辑会在处理状态之后直接调用到PerformMovement中，基本上主控端和服务器都会最后使用到PerfromMovement，而模拟端只会使用MoveSmooth。


除了状态的准备之外，PerformMovement最后的移动逻辑以StartNewPhysics的计算为中心，而模拟端用的MoveSmooth则使用了一个弱化的计算方式。


在MoveAutonomous中会使用bClientUpdating来决定是否对Mesh姿态进行更新。有几个比较特别的处理需要留意


**CompressedFlags**


这里面会对一些特殊的移动状态进行压缩，当前默认的有bPressedJump和bWantsToCrouch。服务器在解开这些标志位之后会尝试让移动进入对应的状态。


**ApplyAccumulatedForces**


移动模拟并不会实际执行物理模拟，所以对于AddForce等一些列物理操作，会缓存起来，最后在这里实际的叠加到模拟中去。


**HandlePendingLaunch**


这边是和上面的冲量系列一样，对物理操作的“模拟”。


**加速度**


会有一个AnalogInputModifier的处理以及MaxAcceleration和竖直加速度清理的操作，加速度最后会反应到速度计算上。


### StartNewPhysics


这个才是真正意义上进行移动模拟的地方，会根据不同的MovementMode来对移动进行按照DeltaTime的分段模拟，同时也会处理移动模式的切换和继续模拟。


具体的过程可以实际在函数中进行观测。


操作上，首先是通过CalcVelocity来计算速度，包括了对AI Path Follow的处理以及正常玩家操作的处理。同时会对Friction等进行计算，保证阻力等被正常应用到速度计算中。


#### FindFloor


如果在移动之后没有地板信息的话，会通过这个函数来寻找地板。


其中一个关键性的函数时ComputeFloorDist，由于其中有两种模式的计算。一种是通过向下的LineTrace，另一种是通过胶囊体的Sweep，对于一些不符合预期的站在物体的边缘或卡进动态物体的情况，可以在这里检查和作特殊处理。


对于Walking的情况，如果地板变更的话，会有一个HandleWalkingOffLedge的处理。对于新找到的地板不能站立的情况，会尝试回退单次模拟、改变方向或者尝试跳跃。这里的单次模拟是指StartNewPhysics内部分割后的模拟。


#### MoveAlongFloor


这个是Walking时用来进行角色移动的函数，到这里其实代码上的逻辑还是比较清晰的，这里就不多作赘述了。其中有一个SlideAlongSurface的处理，是一个在移动模拟中比较常用到的贴边移动函数。里面除了ComputeSlideVector之外，还有一个TwoWallAdjust的回避处理，如果感兴趣的话可以深入的看一下，不过实际上如果没有出问题的话，这边的细节处理一下就会忘记了……


这里面还有一个非常精细的StepUp然后StepDown的操作，详细的逻辑可以查看UCharacterMovementComponent::StepUp。


通常如果移动进入奇怪的状态的话，从MoveAlongFloor来检查比较好。


### MoveSmooth


相比StartNewPhyscis，这个给模拟端用的函数逻辑非常简单。


如果是在地面上移动的话，会使用MoveAlongFloor来更新，否则直接用SafeMoveUpdatedComponent来移动并作StepUp和SlideAlongSurface的操作。


此外UCharacterMovementComponent::SimulateMovement也会作一些基本的状态更新，在移动模拟之后会对地板和Faling状态进行更新。


## 总结


这边没有办法列出很多细节，而且实现方式也会随着版本出现变化，所以记录下来主要是方便进行快速的逻辑查找。


移动模拟在三个端各自有不同的逻辑，所以在出现问题时有时候查起来会比较头痛，希望这里的内容至少能够帮助缩短到达问题原因的路径~


