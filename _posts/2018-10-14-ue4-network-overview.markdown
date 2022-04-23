---
layout: post
status: publish
published: true
title: UE4网络底层概览
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2600
wordpress_url: https://blog.ch-wind.com/?p=2600
date: '2018-10-14 20:47:27 +0000'
date_gmt: '2018-10-14 12:47:27 +0000'
tags:
- UE4
- NetWork
---
日常使用的话不会接触到这块，最近刚好接触到，所以在此做下整理。


当前UE4版本为4.20。


UE4的网络部分，主要有RPC和值同步两种逻辑。其中在代码上有更多的维护的是值同步，因为RPC基本上是调用的时候就发出去，可优化的成分不高。而值同步就涉及同步频率、状态差分这些的维护成本，所以会有更多的逻辑在背后。


## 网络结构


虚幻本身的网络结构各个层次的封装还是比较好的，基本不会出现层次之间混杂导致难以定制的情况。


### 总体结构


结构上，每一个Actor通过ActorChannel注册到Connection来进行网络相关的操作。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/10/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/10/image.png)


在逻辑上每一个Connection对应的是一个客户端和服务端之间的远程连接，而NetDriver向下的话就只是对网络底层操作的封装。


在这里，首先从最底层开始。


### FSocket和SocketSubSystem


FSocket是对网络底层的封装，对于上层需要的网络状态查询、发包、收包这些操作，全部都封装在了这里。


与平台相关的底层全部隐藏掉，同时可以方便实现如steam网络接入这样的接入模式。


一般情况下的连接实际使用的是FSocketBSD，是对底层Socket API的直接封装。


#### FSocket工厂类


SocketSubSystem是对UE4网络上层可见的FSocket工厂类，上层调用时不关心FSocket的具体实现是什么。而是通过预先配置好的SocketSubsytem来直接创建FSocket的基类指针。


在多平台实现上，和其他的系统基本是类似的。例如在Android上，实际使用的是FSocketSubsystemAndroid，而在IOS上则是FSocketSubsystemIOS。


具体而言，在SocketSubsystem的Module初始化时，会使用一个被宏区分的系统对应的SubSystem



```
// Initialize the platform defined socket subsystem first
DefaultSocketSubsystem = CreateSocketSubsystem( *this );
```

这样一来，通过ISocketSubsystem::Get获得默认的SocketSubSystem的时候就能取得对应平台的实现了。


#### IPv4和IPv6


在4.21之前向下FSocketSubsystemBSD会有Ipv6和Ipv4两个不同的实现，在IOS上继承的是FSocketSubsystemBSDIPv6，而Android的是FSocketSubsystemBSD。但是4.21将这两个协议栈合在了一起，避免了在进行具体实现和使用时的一些困扰。


关于IPv6和IPv4的问题，其实在Socket这一层，切换起来的难度并不大。



> IPv4 connections can be handled with the v6 API by using the v4-mapped-on-v6 address type; thus a program needs to support only this API type to support both protocols. This is handled transparently by the address handling functions in the C library.
> 
> 


IPv4到IPv6有很多过渡的协议、地址格式，但是实际如果在Socket这里用v6 API的话，只需要关注IPv4-mapped-on-IPv6就可以了：



> The address notation for IPv6 is a group of 8 4-digit hexadecimalnumbers, separated with a ':'. "::" stands for a string of 0 bits.Special addresses are ::1 for loopback and ::FFFF:<IPv4 address> for IPv4-mapped-on-IPv6.
> 
> 


实际测试，将API直接替换掉基本没有什么问题。主要会有麻烦的，还是一些平台相关的问题。上面的两个引用来自[[Man7](http://man7.org/linux/man-pages/man7/ipv6.7.html)]，关于IPv6 Socket API的一些其他描述也可以参看该文档。


### NetDriver和Connection


UNetDriver是进行网络处理的核心，有一个比较特殊的UDemoNetDriver，是用于回放录制系统的，不会发送数据。


NetDriver是和UWorld绑定的，无论是客户端还是服务器只会有一个。而Connection是对应客户端和服务器的连接的。对于客户端，只会有一个连接到Server的Connection，而服务器则对应每一个客户端维护一个Connection。



```
/** Connection to the server (this net driver is a client) */
UPROPERTY()
class UNetConnection* ServerConnection;

/** Array of connections to clients (this net driver is a host) */
UPROPERTY()
TArray<class UNetConnection*> ClientConnections;
```

NetDriver和Connection不是完全的上下层的关系，实际上这两个类在进行数据发送时使用的都是自己定义的LowLevelSend。Connection更多的意义上是标识，在这之上的连接是有既定的发送者和接收者的。



```
void UIpConnection::LowLevelSend(void* Data, int32 CountBytes, int32 CountBits)

void UIpNetDriver::LowLevelSend(FString Address, void* Data, int32 CountBits)
```

在实际的网络连接中，一般情况下使用的对应类就是UIpNetDriver和UIpConnection。


#### 逻辑关系


在更新上，Connection由NetDriver负责更新。NetDriver本身的更新由UWorld驱动



```
/** Event to gather up all net drivers and call TickDispatch at once */
FOnNetTickEvent TickDispatchEvent;

/** Event to gather up all net drivers and call TickFlush at once */
FOnNetTickEvent TickFlushEvent;

/** Event to gather up all net drivers and call PostTickFlush at once */
FOnTickFlushEvent PostTickFlushEvent;
```

NetDriver的TickDispatch负责从注册的Socket上取出数据包，并进一步分发到对应的Connection中去。在服务器上，对于不同的数据包，默认是使用客户端的IP地址来区分要分发的Connection的。如果没有找到对应的Connection，且符合开新链接的条件的话，就会建立新的连接并开始连接初始化的流程。


TickFlush是负责进行值复制逻辑的，会调用到ServerReplicateActors开始执行值复制。


PostTickFlush是在TickFlush之后执行的逻辑，主要进行一些网络发送相关的清理逻辑。


网络相关的Tick逻辑和TickGroup所组织的Tick逻辑是相对独立的，这三个Tick函数都是由UWorld直接进行分发的，而没有具体的TickGroup。


在逻辑上，TickDispatch在所有的Tick执行之前进行，而TickFlush和PostTickFlush则在所有的Tick执行之后进行执行。


RPC和ControlChannel上的控制信息由于有更高的实时性需求，不会经过这边的逻辑，会直接调用FlushNet进行数据发送。


#### 状态维护


UNetConnection自己维护一组时间戳用于监视连接的状态，这些时间在InitBase中进行统一的初始化：



```
StatUpdateTime= Driver->Time;
LastReceiveTime= Driver->Time;
LastReceiveRealtime= FPlatformTime::Seconds();
LastGoodPacketRealtime= FPlatformTime::Seconds();
LastTime= FPlatformTime::Seconds();
LastSendTime= Driver->Time;
LastTickTime= Driver->Time;
LastRecvAckTime= Driver->Time;
ConnectTime= Driver->Time;
```

Driver->Time是由NetDriver维护的帧时间，在TickDispatch中进行更新。


LastReceiveTime的更新发生在UNetConnection::ReceivedRawPacket调用到UNetConnection::ReceivedPacket之后，也就是每一次有效的数据包从Driver分发到Connection的时候就会进行更新。这个时间戳在UNetConnection::HandleClientPlayer中也会进行更新，这个函数是在本地对玩家登陆进行处理的。


相对的，LastSendTime就比较单纯，只是在UNetConnection::FlushNet中更新，但是这个时间只是发送数据包的时间，无法确认发送是否成功。LastRecvAckTime在每次收到ACK的时候进行更新，这个时间戳并用于Standby Cheat的检测。


[Standby Cheat](https://www.urbandictionary.com/define.php?term=standby)是Listen Server的时候的一种作弊方式，指的是联机的主机端恶意的影响网络数据收发来获得优势的行为。主要的检测逻辑在`UNetDriver::UpdateStandbyCheatStatus`中，检测分为三种Bad Ping、Rx(收包问题)、Tx(发包问题)。详细的逻辑没有深究，因为现在没有Listen Server的需求。


#### Channel


在Connection之上，针对每个需要进行发送的Actor会有ActorChannel的概念。


Actor的值复制逻辑最终由UActorChannel来负责维护和执行，实际进行数据对比的是FObjectReplicator。


Connection上还会有一个特别的控制Channel，为UControlChannel，这个Channel负责对连接本身进行控制。UControlChannel的作用是对整个Connection进行控制，最主要的逻辑作用是在连接建立过程中的控制处理。所有的控制信息都被定义成NMT_Hello这样的宏。


如果要自定义控制信息，可以参考源码中的注释：



```
/** network control channel message types
*
* to add a new message type, you need to:
* - add a DEFINE_CONTROL_CHANNEL_MESSAGE_* for the message type with the appropriate parameters to this file
* - add IMPLEMENT_CONTROL_CHANNEL_MESSAGE for the message type to DataChannel.cpp
* - implement the fallback behavior (eat an unparsed message) to UControlChannel::ReceivedBunch()
*
* @warning: modifying control channel messages breaks network compatibility (update GEngineMinNetVersion)
*/
```

控制信息的DEFINE_CONTROL_CHANNEL_MESSAGE_* 定义都在DataChannel.h中。进一步的使用可以查看NMT_Hello这种比较简单的控制信息的处理方式。


不过一般情况下应该很少会用到自定义控制信息，有需要特殊控制信息的话，可以先考虑使用NMT_GameSpecific。


还有一种独特的UVoiceChannel，不过感觉一般不会用到。


## 连接建立


连接建立过程在客户端上主要由UPendingNetGame这个类进行负责，在连接确立之后，这个类就功成身退了。


本地试图连接远程关卡时，UEngine就会建立UPendingNetGame开始进行远程关卡的载入。UPendingNetGame负责建立NetDriver，并进行一系列的初始连接操作，在完成连接之后，UPendingNetGame会从UEngine脱离控制。


UPendingNetGame自身的Tick来源于UEngine::TickWorldTravel，在WorldContext上有PendingNetGame时就会更新其状态，直到操作失败或者完成操作。


客户端要连接到服务器，在建立起值复制和RPC发送的UConnection之前，在逻辑上主要有以下两个步骤：


### PacketHandler握手


PacketHandler是注册在NetDriver和NetConnection上的数据包底层处理类，一般用于与上层逻辑无关的数据包加密、握手以及其他的一些特殊处理。这个处理逻辑在4.20的时候结构还不完整，能在一些函数上看到Work in progress, don't use yet的注释。


在连接建立阶段，首先的操作就是对所有需要握手的PacketHandler进行握手操作。这个逻辑由PacketHandler::BeginHandshaking负责。在客户端由UPendingNetGame调用，在服务端由UIpNetDriver::TickDispatch在新建到客户端的链接时进行调用。


在默认的情况下，这个过程中主要就是StatelessConnectHandlerComponent。


StatelessConnectHandlerComponent是一个使用Cookie来防止Dos和数据重放的PacketHandler。因此，这个Component是所有PacketHandler的前置，在服务端新建连接前会首先确保这个Component完成握手才会构建UConnection并调用PacketHandler::BeginHandshaking。


这样就可以确保到达服务器的数据包如果没有经过StatelessConnectHandlerComponent的握手的话就不会得到进一步的处理。


如果操作是按照正常流程的话，服务器收到的第一个包就是由客户端发起的StatelessConnectHandlerComponent的握手包。


PacketHandler的操作不是完全对称的，有



```
Handler::Mode Mode = Driver->ServerConnection != nullptr ? Handler::Mode::Client : Handler::Mode::Server;

```

对其进行区分。


### ControlChannel


在完成PacketHandler的握手之后，UConnection已经建立，由Control Channel中的控制信息来接管接下来的初始化过程。此时在服务端是由UWorld来主要负责处理控制信息的。


#### NMT_Hello


连接过程同样由客户端发起，UPendingNetGame在PacketHandler握手完成后会发送NMT_Hello，开始连接初始化过程。


服务端在Connection建立时，InitRemoteConnection时会设置为等待状态：



```
SetClientLoginState( EClientLoginState::LoggingIn );
SetExpectedClientLoginMsgType( NMT_Hello );
```

NMT_Hello会携带客户端的字节序、Crc之后的客户端版本以及Url中的EncryptionToken。


#### 服务器响应Hello


服务端收到NMT_Hello之后，总共有三个步骤：


##### Version Check


首先会对其携带的版本数据进行校验，如果不一致的话，就会返回NMT_Upgrade，要求客户端升级之后再进行连接。


##### Encryption


接下来是可选的加密配置过程，如果携带空的EncryptionToken就会跳过这个步骤。


如果Hello携带了EncryptionToken，服务端却没有绑定OnReceivedNetworkEncryptionToken的话，就会返回NMT_Failure。


这个函数默认是绑在UGameInstance::ReceivedNetworkEncryptionToken上的，不过这个默认实现是直接返回失败的。


在客户端由一个相对的处理流程：



```
FNetDelegates::OnReceivedNetworkEncryptionToken.BindUObject(this, &ThisClass::ReceivedNetworkEncryptionToken);
FNetDelegates::OnReceivedNetworkEncryptionAck.BindUObject(this, &ThisClass::ReceivedNetworkEncryptionAck);
```

最终会使用Handler上的FEncryptionComponent来对数据进行处理，是否有这个包处理组件由net.AllowEncryption这个Console来决定。加密组件在Engine.ini中指定：



```
[PacketHandlerComponents]
EncryptionComponent=AESHandlerComponent
bEnableReliability=false
```

在引擎中搜索AESHandlerComponent能看到对应的加密组件的实现，以及还有RSAKeyAESEncryptionHandlerComponent、RSAEncryptionHandlerComponent、BlockEncryptionHandlerComponent、StreamEncryptionHandlerComponent这些组件，这里由于没有使用到，不再深究。


在UWorld::SendChallengeControlMessage的处理中可以看到，如果服务端的加密校验失败，会返回NMT_Failure，如果成功则会发送NMT_EncryptionAck到客户端并设置加密秘钥。


这里的FEncryptionKeyResponse是来源于UGameInstance::ReceivedNetworkEncryptionToken的，默认实现是直接Failure。


NMT_Failue一般都会携带具体的错误理由，可以按图索骥。


##### Challenge Client


如果没有提供加密的Key或者通过了加密的构造流程的话，会给客户端发送NMT_Challenge。


#### 登录操作


接下来的连接过程就比较简单了：


客户端收到Challenge之后会收集登录信息，然后发送NMT_Login。


服务器处理Login之后回复NMT_Welcome。


客户端收到NMT_Welcome后，会记录下其中携带的地图加载对应的关卡，并向服务器上报客户端的网速NMT_Netspeed。然后到下一个Tick，会对地图进行加载，加载成功时，会发送NMT_Join并断开UPendingNetGame与Context的关联。


服务器处理NMT_Join后，会建立Connection与PlayerController的关联，客户端和服务端的连接就完全建立起来了。之后的操作就是使用RPC进行了。


#### 其他控制操作


控制信息中还有一些其他的与连接建立过程关系不大的类型，在这里也稍微记录一下：


##### NMT_NetGUIDAssign


这个看注释似乎很有用



> Explicit NetworkGUID assignment. This is rare and only happens if a netguid is only serialized client->server (this msg goes server->client to tell client what ID to use in that case)
> 
> 


不过似乎没有实际作用，所有的调用会到达ResolvePathAndAssignNetGUID，这个函数的两个实现都没有作处理，在UPackageMapClient::ResolvePathAndAssignNetGUID中甚至能看到check(0)。


##### NMT_DebugText


可以让连接的另一端输出调试信息。这个是给NETDEBUGTEXT指令用的。


##### NMT_GameSpecific


会将发送的内容推送到HandleGameNetControlMessage，发送的内容为uint8和FString。用uint8来指定数据类型，FString来作为数据内容。基本能够满足需求。


## 数据收发


从最下往上看的话，数据在从Socket被取出后，首先会经过PacketHandler，然后到达NetDriver，在寻找到对应的Connection之后会通过ReceivedRawPacket将数据指针推送给对应的Connection。


#### PacketHandler


UNetConnection::ReceivedRawPacket的处理主要集中在PacketHandler上，默认的情况下，工作的只有StatelessConnectHandlerComponent。


加密组件需要自己开启，也可以自己定义一些组件来在数据包一层进行处理。由于这里的是RawData，所以比较适合做加密、压缩或者校验之类的。因为在这里处理的数据还和UE4上层的网络结构没有什么关系。


在数据从Connection进一步发送到UE4逻辑之前，PacketHandler有两个可以处理的接入点。


一个是Incoming，一个是IncomingHigh。这两个处理的逻辑位置有些不同。


InComing是直接处理的原始数据，而InComingHigh接入的是经过了序列化之后的FBitReader。


经过这两个步骤之后，FBitReader会被发送到UNetConnection::ReceivedPacket。


#### Bunch和Channel


ReceivedPacket这里会对Ack包和数据包进行区分处理。


Ack包会进入Ack处理逻辑。


数据包在作Ack处理后，被进一步的打包成FInBunch，在逻辑上这里的Bunch应当被称为RawBunch。之所以称为RawBunch，是因为UE4在数据包发送的时候会对上层过来的Bunch做分包处理。


RawBunch打包完成时，就已经获取了数据包对应的Channel，之后就会发送到UChannel::ReceivedRawBunch。


#### ReceivedRawBunch


由于网络收发的不确定性，这里会有Reliable的RawBunch的第一道关卡，对于到达的数据包的序列号不符合预期的情况，数据包会被缓存到



```
class FInBunch*        InRec;
```

这个缓存是有大小限制的



```
enum { RELIABLE_BUFFER = 256 }; // Power of 2 >= 1.
```

如果出现奇怪的丢包问题可以关注下Log的输出~


对于到达的有序RawBunch，则进入下一步处理：UChannel::ReceivedNextBunch


#### ReceivedNextBunch


到达了这里主要做的操作是对RawBunc进行合并，合并依赖的是以下标志位：



```
uint8   bPartial;           // Not a complete bunch
uint8   bPartialInitial;    // The first bunch of a partial bunch
uint8   bPartialFinal;      // The final bunch of a partial bunch
```

bPartialFinal为合并终止包。OutBunch和InBunch分开定义，VA会搜索不到。


合包时会有一个缓存，防止剩余包未到达的情况：



```
class FInBunch*        InPartialBunch;        // Partial bunch we are receiving (incoming partial bunches are appended to this)
```

完成包合并后的Bunch会被交由UChannel::ReceivedSequencedBunch处理。


UChannel::ReceivedSequencedBunch则进一步调用到Channel的虚函数ReceivedBunch。


#### ReceivedBunch


ActorChannel在得到Bunch之后进一步通过ProcessBunch将处理交到FObjectReplicator::ReceivedBunch中，在ReadFieldHeaderAndPayload解析之后，根据Filed信息来做更多的操作。



```
// Handle property
if ( UProperty* ReplicatedProp = Cast< UProperty >( FieldCache->Field ) ){...}
// Handle function call
else if ( Cast< UFunction >( FieldCache->Field ) ){...}
else
{
UE_LOG( LogRep, Error, TEXT( "ReceivedBunch: Invalid replicated field %i in %s" ), FieldCache->FieldNetIndex, *Object->GetFullName() );
return false;
}
```

这样，数据包就到达了UE4中的RPC和属性同步处理逻辑了。


在ProcessBunch中还有一个FNetworkGUID相关的逻辑，这个是一开始Actor初始化网络连接时会用到的处理流程。需要进一步了解的话，可以参考这个函数：



```
/**
*Standard method of serializing a new actor.
*For static actors, this will just be a single call to SerializeObject, since they can be referenced by their path name.
*For dynamic actors, first the actor's reference is serialized but will not resolve on clients since they haven't spawned the actor yet.
*The actor archetype is then serialized along with the starting location, rotation, and velocity.
*After reading this information, the client spawns this actor in the NetDriver's World and assigns it the NetGUID it read at the top of the function.
*
*returns true if a new actor was spawned. false means an existing actor was found for the netguid.
*/
bool UPackageMapClient::SerializeNewActor(FArchive& Ar, class UActorChannel *Channel, class AActor*& Actor)
```

#### 数据发送


发送数据的过程基本上和接收数据的过程相反。不过在分包之后到发送RawBunch的过程更为简单一些。因为这里不会有序列的问题，只有在RawBunch发送之后会有一个Ack维护和重发的逻辑。


与InRec对应的缓存为OutRec，同样会应用缓存数量上限。


RPC会在发送时不会等待TickFlush，而是会直接调用Channel的SendBunch并立即调用FlushNet。只有两种情况例外，一种是函数本身被标记为ForceQueue的，另一种是非Reliable的多播函数。


多播函数官方并不建议使用Reliable，因为会导致相距很远、已经休眠的Channel重新被打开并在发送完毕之后又被关闭。


对于不立即调用的RPC，会被缓存并在之后走值复制的逻辑进行发送。



```
FObjectReplicator::QueueRemoteFunctionBunch

PackageMapClient->AppendExportBunches( OwningChannel->QueuedExportBunches );
```

RPC的发送还涉及将参数进行NetSerializer发送的过程，这里没有深究，如有需要可以从UNetDriver::ProcessRemoteFunctionForChannel入手。


## 值复制处理


值复制的数值对比部分的实际逻辑执行由FObjectReplicator::ReplicateProperties负责。


在ActorChannel确立之后，对于像是int、float这样的属性，只要进行简单的内存对比就可以知道有没有修改并进行发送了。


但是对于TArray这样的“动态”内容，就需要更多的处理。另外，当前版本的引擎是不提供TMap与TSet的值复制逻辑的。


在初始构造连接时的复制时或者RPC进行参数传递时会进行NetSerializer，而在之后的值复制过程中，会对值与之前的值进行对比，使用NetDeltaSerializer来判别变动了量并只对这些值进行发送。


当然，实际在进行的时候会有很多类和机制上的处理，但是大体上就是这个样子。想要进一步了解其执行方式的话，可以看SerializeProperties_r和CompareProperties_r。对于RPC可以参考以下函数：



```
// RPC support
void InitFromFunction( UFunction * InFunction );
void SendPropertiesForRPC( UObject* Object, UFunction * Function, UActorChannel * Channel, FNetBitWriter & Writer, void* Data ) const;
void ReceivePropertiesForRPC( UObject* Object, UFunction * Function, UActorChannel * Channel, FNetBitReader & Reader, void* Data, TSet<FNetworkGUID>& UnmappedGuids) const;

// Struct support
void SerializePropertiesForStruct( UStruct * Struct, FArchive & Ar, UPackageMap    * Map, void* Data, bool & bHasUnmapped ) const;
void InitFromStruct( UStruct * InStruct );

// Serializes all replicated properties of a UObject in or out of an archive (depending on what type of archive it is)
ENGINE_API void SerializeObjectReplicatedProperties(UObject* Object, FArchive & Ar) const;
```

对于TArray，有一个专门的逻辑进行处理，主要在CompareProperties_Array_r中。会对数组进行判定，只对“改变”了的数值进行复制。如果只是简单的值修改的话，只会复制修改的部分。如果是在尾部添加和删除的话也不会有太大的数据量。但是如果是将中间的某个值删除的话，会被视为那个值之后的所有量都变动了，所以也并不是万能的。


因此官方还提供了一个FastArray来应对一些特殊的情况。


### 自定义NetSerialization


为了提供一些自定义的结构的值复制逻辑变更，NetSerialization和NetDeltaSerialization是可以自定义的。


NetSerialization用于将整个结构序列化，这个其实在引擎内部的使用非常多，可以通过FVector_NetQuantize来参考如何进行实现。


NetDeltaSerialization用于生成状态差分，这个貌似只有FastArray在用。


### FastArray


快速值复制的数组，其快速并不反应在初始的NetSerialization上，而是通过NetDeltaSerialization在进行差分对比的时候比TArray更加快速。


但是相对的，也会有缺点，那就是通过FastArray进行的值复制是不会保证数组在服务端和客户端之间的次序一致性的。


想要进一步使用FastArray同步逻辑的，可以参考NetSerialization.h中的注释，里面有一步一步的指导如何使用这个复制方法。


总体上，我们要做的其实只是定义一个支持这个复制方式的Struct而已，然后在发生了变动的时候，调用对应的接口就好了。引擎中有几处有使用到FastArray，参考FLobbyPlayerStateInfoArray也可以获得一些具体用法相关的知识。


## 4.20的优化项


这两个优化项记得是当时GDC上有说的从Fortnite合入的。


### SignificanceManager


一个单独的用来更新物体之间的相关性的类。


需要自己在合适的地方调用Update，而这个USignificanceManager::Update就是整个处理逻辑的核心。它会调用我们定义的优先级计算函数，之后对计算结果进行排序处理。


使用时需要注意的是，这个类本身并不提供性能提升，而是会对优先级进行管理，方便其他系统对性能进行调整。


另外，在注册到Manager的时候要留意EPostSignificanceType的传入值，可能会导致FPostSignificanceFunction的调用异步到达。而FSignificanceFunction原本就是异步的，所以不能在里面进行一些可能导致死锁的操作，或者默认假定它是单线程的。


从代码看



```
SignificanceManagerClass = LoadClass<USignificanceManager>(nullptr, *GetDefault<USignificanceManager>()->SignificanceManagerClassName.ToString());
```

这个类和UNetDriver那些一样，可以通过配置指向自己重载的基类。


具体的使用方法可以参考[[官方文档](https://docs.unrealengine.com/en-us/Engine/Performance/SignificanceManager)]。


### ReplicationGraph


这个是直接介入到UNetDriver中的优化类，要使用这个类可以通过配置来重新导向：



```
[/Script/OnlineSubsystemUtils.IpNetDriver]
ReplicationDriverClassName="/Script/MyGame.MyReplicationGraph"
```

或者将自己的构造函数绑定到



```
UReplicationDriver::CreateReplicationDriverDelegate()
```

这个Delegate上。


这个优化的作用，官方是这样描述的



```
UReplicationDriver is a base class that can be used for implementing custom server replication logic.
UReplicationGraph is an implementation of UReplicationDriver that provides a replication system optimized for games with large actor and player counts.
```

总体上而言，就是可以实现自定义的值复制逻辑。官方给出的使用示例是：



> 1. 将Actor通过位置聚合在一起提供更新判定，例如MMO中的独立的房间或者区域
> 
> 
> 2. 对于独特的休眠物体进行分组管理，例如场景中的树，虽然只在被破坏的时候需要状态更新，却又不能降低更新频率
> 
> 
> 3. 如果玩家可以推动或拾起物体，可以将它们的更新聚集到持有者上
> 
> 
> 4. 可以将需要常态更新的物体聚合在一个组内，避免不必要的相关性检查
> 
> 
> 5. 将对于指定Actor永远不需要和一直需要的相关性聚集在一起
> 
> 


逻辑上主要替换的是



```
/**
* Called to replicate any relevant actors to the connections contained within this net driver
*
* Process as many clients as allowed given Engine.NetClientTicksPerSecond, first building a list of actors to consider for relevancy checking,
* and then attempting to replicate each actor for each connection that it is relevant to until the connection becomes saturated.
*
* NetClientTicksPerSecond is used to throttle how many clients are updated each frame, hoping to avoid saturating the server's upstream bandwidth, although
* the current solution is far from optimal.  Ideally the throttling could be based upon the server connection becoming saturated, at which point each
* connection is reduced to priority only updates, and spread out amongst several ticks.  Also might want to investigate eliminating the redundant consider/relevancy
* checks for Actors that were successfully replicated for some channels but not all, since that would make a decent CPU optimization.
*
* @param DeltaSeconds elapsed time since last call
*
* @return the number of actors that were replicated
*/
ENGINE_API virtual int32 ServerReplicateActors(float DeltaSeconds);
```

也就是说替换的是值复制从NetDriver到Channel为止的判定逻辑，对于Fortnite这种据说同步物体达到50000个左右的大规模Actor的值同步很有作用。


默认情况下的同步数据收集是会直接对所有的Actor进行遍历的，这个逻辑相对单纯，无法进行复杂的关系设定。而ReplicationGraph引入了Node来对Actor进行关系管理，这个Node也可以自己进行定义。这样就可以通过更加复杂的逻辑来控制Actor的复制关系。尽可能的减少浪费。


可以通过UBasicReplicationGraph看基本的功能是如何接入到UNetDriver系统中去的，据说ShooterGame中有更加详细的实现。需要更多信息也可以参考[[官方文档](https://docs.unrealengine.com/en-US/Engine/Networking/ReplicationGraph)]。


