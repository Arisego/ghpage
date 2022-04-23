---
layout: post
status: publish
published: true
title: 精确时间戳整理
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2583
wordpress_url: https://blog.ch-wind.com/?p=2583
date: '2018-09-15 22:11:20 +0000'
date_gmt: '2018-09-15 14:11:20 +0000'
tags:
- UE4
- TimeStamp
---
当需要进行类似定时抢购或者用户操作验证时，就需要获得用户的精确时间戳。


当前使用的UE4版本为4.20。


首先，对于时间戳，这里需要的是满足这两个条件：


1. 它是自然增加的，不会因为正常操作回转


2. 它与现实时间具有同等的流速，不会突然跳变。


基本上就是通常意义上的MONOTONIC的时钟了，不过这个词的具体意义我也不是很明确就是了~


从wiki上的解释来看：



> In mathematics, a monotonic function(or monotone function) is a function between ordered sets that preserves or reverses the given order. This concept first arose in calculus, and was later generalized to the more abstract setting of order theory.
> 
> 


Monotonic似乎只有保持单调上升的定义，不过这里还是借用下吧。


## 时间戳的获取


如果要使用上面的两个条件的话，关卡时间记录的TimeSeconds是不行的，因为它在游戏暂停的时候是不增加的。而RealTimeSeconds，虽然其间接来源是FPlatformTime::Seconds，但是中间会有演算的精度丢失，要使用的话不如直接使用FPlatformTime::Seconds。


FPlatformTime::Seconds在大部分情况下都是可用的，但是它有不同的平台实现，在实际使用时还是会遇到平台相关问题。


### Windows


在Windows平台上，FPlatformTime::Seconds使用的是QueryPerformanceCounter。这是一个硬件时钟，不会受到用户时间调整、系统挂起等各种操作的影响，Windows上还可以使用TSC来获取CPU时钟，这个时钟微软并不推荐使用，因为它会受到CPU频率动态调整等硬件调节的影响。


详细的说明可以参照微软的官方说明：[Acquiring high-resolution time stamps](https://docs.microsoft.com/en-us/windows/desktop/sysinfo/acquiring-high-resolution-time-stamps)。


### Linux


在Linux平台上有一个通用的时间获取函数clock_gettime，可以获得各种类型的时钟值。


这个函数的具体用法可以参考[clock_gettime](http://man7.org/linux/man-pages/man2/clock_gettime.2.html)的文档，UE4在使用时会首先对各个类型的时钟进行一次效率对比，因为在不同的Linux内核版本上可能会有性能的差异，或者是没有实现的时钟出现。



```
{ CLOCK_REALTIME, "CLOCK_REALTIME", 0 },
{ CLOCK_MONOTONIC, "CLOCK_MONOTONIC", 0 },
{ CLOCK_MONOTONIC_RAW, "CLOCK_MONOTONIC_RAW", 0 },
{ CLOCK_MONOTONIC_COARSE, "CLOCK_MONOTONIC_COARSE", 0 }

```

这四种时钟的不同在文档中有描述，这里作一个简要的整理：



> CLOCK_REALTIME: 这个时钟获取的是时钟时间，会受到系统时间调整和NTP的影响。
> 
> 
> CLOCK_MONOTONIC: 不会受到系统时间调整影响的时钟，记录的是从一个未指定的起始时间到现在的时间，但会受adjtime和NTP的影响。
> 
> 
> CLOCK_MONOTONIC_RAW: 比MONOTONIC更加严格，甚至不会受到adjtime和NTP的影响。2.6.28内核以上才有。
> 
> 
> CLOCK_MONOTONIC_COARSE: 一个更快速和低精确度的MONOTONIC时钟，需要系统架构支持。2.6.32内核以上才有。
> 
> 


这里有个问题，就是NTP。由于对Linux不是很熟悉，所以对NTP很为困惑。NTP简单的来看就是联网对时机制，从结果上看最终与adjtime一样，并不会导致CLOCK_MONOTONIC回转，只会让这个时钟变得更加接近世界时间，会造成时间计算的频率发生变化计让算结果出现一些小的不连续。而CLOCK_MONOTONIC_RAW则更接近于硬件时间，更加适合于硬件相关的监测或者线程同步。详细的说明可以参考[[这里](https://stackoverflow.com/a/14270415)]。


结论上看，就是CLOCK_MONOTONIC基本就够用了。


### Android


由于Android的内核就是Linux的，所以使用的也是clock_gettime，不过这里并没有作时钟性能的比较，而是直接取用的CLOCK_MONOTONIC。大概是因为Android所基于的Linux内核版本是确定的吧。


Android在JavaApi一层是有提供elapsedRealtime函数来获取系统启动至今的时间的。从Android的源码[[变更记录](https://android.googlesource.com/platform/system/core/+log/master/libutils/SystemClock.cpp)]上来看，这个API的实现经历过不少的变更。


最后采用的是使用clock_gettime的CLOCK_BOOTTIME来实现的，在过去的时代，Linux内核似乎有过bug，导致通过获得的CLOCK_BOOTTIME有问题。而在这个提交之后：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-4.png)


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-5.png)


又开始重新回归了CLOCK_BOOTTIME，由于这个变更过程，所以不是很确定clock_gettime在旧版本Android上究竟会受到怎样的影响。从Android本身的变更上看：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-6.png)


由于UE4对Android的API Level是从18还是19开始的，Linux内核已经到了3.0以上，应当对用于时间戳的CLOCK_MONOTONIC不会产生影响才对。如果在实际中遇到问题的话，就只能依赖于AndroidJavaEnv::GetJavaEnv来获取JavaAPI了。


在Android上使用FPlatformTime::Seconds有一个需要注意的问题，Androd平台使用clock_gettime的实现是4.20之后的版本才有的！如果你工作在4.20之前的版本的话，FPlatformTime::Seconds的实现是使用的默认的FGenericPlatformTime，只是单纯的将系统当前时间转换为秒数。


### IOS


在IOS10之后，IOS有将clock_gettime从内核暴露出来，所以如果是针对之后的版本的话，是没有问题的。但是在IOS10之前是没有这个函数的，所以UE4在TimeSeconds中使用的是mach_absolute_time。


这个时钟有一个问题，那就是它会随着IOS锁屏而停止。


因此在IOS上如果想要获取一个MONOTONIC的时钟，实际上需要使用一个Trick：



```
#include <sys/sysctl.h>
static int64_t us_since_boot() {
  struct timeval boottime;
  int mib[2] = {CTL_KERN, KERN_BOOTTIME};
  size_t size = sizeof(boottime);
  int rc = sysctl(mib, 2, &boottime, &size, NULL, 0);
  if (rc != 0) {
    return 0;
  }
  return (int64_t)boottime.tv_sec * 1000000 + (int64_t)boottime.tv_usec;
}

- (int64_t)us_uptime
{
  int64_t before_now;
  int64_t after_now;
  struct timeval now;
  after_now = us_since_boot();
  do {
    before_now = after_now;
    gettimeofday(&now, NULL);
    after_now = us_since_boot();
  } while (after_now != before_now);
  return (int64_t)now.tv_sec * 1000000 + (int64_t)now.tv_usec - before_now;
}
```

因为IOS的系统启动时间和当前时间记录都是会受系统时间变更影响的，所以它们的差值就能代表固定的时间流逝值。


上面的while是为了防止在两次时间获取之间发生时间变动而设定的，否则有可能在极其偶然的情况下导致获得的时间出现问题。


这个Trick来源于[[stackoverflow](https://stackoverflow.com/a/40497811)]，从大家评论的验证结果上看，并没有什么问题出现。


## 浮点数精度问题


在上面的实现中，我们获得的时间戳都是由uint64的秒数单位构成然后转化到double空间的。


这里就会有一个传统的问题，那就是浮点精度溢出。在结论上，如果使用double来作为秒数的时间戳，且时间戳是基于开机的UpTime的话，是不需要处理浮点数精度问题的。


### IEEE754


现代计算机对浮点数的存储基本遵循一个统一的标准，这是算法之前的事情，这里面有着许多关于数学和硬件实现的相关问题，不过已经离我们这样的程序员很远了。


简单的讲，计算机对浮点数的存储采用的是科学计数法。


实际存储的格式为：


double


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-7.png)


float


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-8.png)


上面两张图来自维基百科~


抛开实际进行浮点数表示的复杂实现的细节进行粗略的估算的话，在小数点位数为0位时，我们能从dobule中获得的精确的自然数与uint52相当，从float中能获得的则为uint23，由于float自带符号位，所以范围可以再乘以2。


那么把同等位数的int转化到同等位数的浮点数的话，一定是会引起精度丢失的。


简化的来看float能够表示的连续的正整数应该在2的23次方左右，也就是大概到8388608，要保留至少两位小数的话，就是83886。将这个作为秒数来计算，大概为23.3个小时。当然，实际的浮点数表示肯定能够容纳更多的数值空间。但是至少说明，在以天为单位的情况下，float用来表示秒数是有丢失精度的危险的。


由于服务器可能在20fps左右进行tick，那么单帧间隔在0.05秒左右，如果不能保证这个精度被表示到的话，很有可能造成运算混乱。


而如果是double的时间戳的话，使用这样的简化推算的话，两位数的精度可以维持521249956.8715天，也就是说能够在大概100万年内都不需要担心精度问题。由于时间戳使用的是system up time，所以如果真的会出问题的话，我们应该担心的是其他的方面~


不过这个推算只是一个大致的直观估计，想要更详细的了解这个主题的话，可以参考[[Sun Studio 11: 數值計算指南](http://math.ecnu.edu.cn/~jypan/Teaching/books/sun_nc.pdf)]中附录D对《[What every computer scientist should know about floating-point arithmetic](https://dl.acm.org/citation.cfm?id=103163)》的翻译。


### UE4中的一些处理


UE4的TickTime的Delta的直接来源是FPlatformTime::Seconds() ，这个是double的，所以不会有什么问题。


#### TimeSeconds


但如果是使用UE4本身的UWorld的时间登记GetWorld()->TimeSeconds 的话，是有可能遇到时间戳精度丢失的。不过要绕过UE4的保护机制，达到精度丢失的程度的话，还是需要一些特定的条件的。


从代码中看的话，UE4对TimeSeconds的保护只有这里有：



```
AGameModeBase::ProcessServerTravel
---------------------------------------------------------------
// Force an old style load screen if the server has been up for a long time so that TimeSeconds doesn't overflow and break everything
bool bSeamless = (bUseSeamlessTravel && GetWorld()->TimeSeconds < 172800.0f); // 172800 seconds == 48 hours
```

这个函数是在地图加载的时候调用的，也就是如果UWorld的生命周期超过了48个小时的话，就不允许SeamlessTravel，而是要求UWorld强制重新构建了。


#### MoveTimeStamp


在角色移动组件中，有服务端和客户端的时间戳处理。这里官方在处理的时候引入了一个自动的回转机制



```
// Reset TimeStamp regularly to combat float accuracy decreasing over time.
if( CurrentTimeStamp > CharacterMovementComponent.MinTimeBetweenTimeStampResets )
{
  UE_LOG(LogNetPlayerMovement, Log, TEXT("Resetting Client's TimeStamp %f"), CurrentTimeStamp);
  CurrentTimeStamp -= CharacterMovementComponent.MinTimeBetweenTimeStampResets;
```

官方的说明如下：



```
/** Minimum time between client TimeStamp resets.
!! This has to be large enough so that we don't confuse the server if the client can stall or timeout.
We do this as we use floats for TimeStamps, and server derives DeltaTime from two TimeStamps.
As time goes on, accuracy decreases from those floating point numbers.
So we trigger a TimeStamp reset at regular intervals to maintain a high level of accuracy. */
UPROPERTY()
float MinTimeBetweenTimeStampResets;
```

也就是说，为了防止float引起的浮点精度丢失，会在累计到这个时间后将时钟往回拨。因为物理运算对时间的精度非常的敏感，这个参数的默认值为240s。


理论上，使用这个时间戳也是可以实现部分功能的。但是由于它会回转，所以可能不适用于所有的情况，会有通用性的问题。另外，这个时间戳严重依赖于移动组件，很难理清其中的头绪，会在不必要的地方花费分离逻辑的成本以及造成逻辑在奇怪的地方耦合。


## 总结


时间戳的获取需要留心各个平台不同的实现，尤其是要小心FPlatformTime::Seconds()，由于平台实现不同它所能提供的保证是不同的。另外，如果对应的平台UE4本身没有对其进行实现的话，使用的会是默认的FGenericPlatformTime，是直接使用系统时间转化过来的秒数，极有可能不符合使用预期，一定要留心。


