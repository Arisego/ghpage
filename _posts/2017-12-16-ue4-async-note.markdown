---
layout: post
status: publish
published: true
title: UE4异步操作总结
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2150
wordpress_url: http://blog.ch-wind.com/?p=2150
date: '2017-12-16 16:37:44 +0000'
date_gmt: '2017-12-16 08:37:44 +0000'
tags:
- UE4
- Async
---
虚幻本身有提供一些对异步操作的封装，这里是对这段时间接触到的“非同步”的操作进行的总结。


当前使用的UE4版本为4.18.2。


在虚幻的游戏制作中，如果不是特殊情况一般不会有用到线程的时候。但是由于实际上虚幻内部是有着许多线程机制的。


例如通常的游戏引擎中游戏线程和渲染线程都是独立的，相互之间会存在一个同步的机制。


而物理线程与游戏线程之间的同步有时候也会导致游戏的表现与预期不一致。


通常会有线程同步需求的地方是网络相关的操作，但是实际上UE4已经对网络操作进行了封装，无需关心这个问题。


而游戏线程、渲染线程、物理线程内部也都已经有了封装，对游戏逻辑的构建基本是不可见的。


但是有时候还是会遇到需要使用线程相关逻辑的，这里就是这段时间内累计的“非同步”相关逻辑的总结。


## Tick


这个其实关于Tick的，虽然Actor是有默认的Tick函数的，Component与UMG也有对应的Tick机制。


但是如果是自定义的UObject或者Slate，要使用Tick机制的话就会有些麻烦。


例如，想要让自定义的Slate控件进行某种数据更新，而数据源本身并不提供通知机制的话就会有些麻烦。


虽然通过各种设计可以巧妙的绕过这个问题，但是有时候在类内部构建Tick机制才是最快速的解决方案。


### TimerManager


通过使用引擎提供的定时器机制，就可以进行自定义的Tick了：



```
GetWord()->GetTimerManager().SetTimer(
  m_hTimerHandle,
  this,
  &UNetPlayManager::TimerTick,
  1.0,
  true
);
```

这里需要能够获得UWorld的指针，如果是自定义的类型的话，就必须想办法提供有效的UWorld指针。


### FTickableGameObject


还有另一个方法，就是使用FTickableGameObject。


任何继承自FTickableGameObject的类型都会获得Tick的能力，就算不是虚幻原生的类型也可以使用，相当的便利。使用时继承自该类型，然后：



```
public:

/** <Tick接口函数 */
virtual void Tick(float DeltaTime) override;

virtual bool IsTickable() const override
{
  return true;
}

virtual bool IsTickableWhenPaused() const override
{
  return true;
}

virtual TStatId GetStatId() const override
{
  RETURN_QUICK_DECLARE_CYCLE_STAT(USceneCapturer, STATGROUP_Tickables);
}
```

继承一下基本的函数就可以了。


## 线程同步


UE4对操作系统提供的线程同步相关接口进行了一定的封装。


### Atomics


基本的接口可以在FPlatformAtomics找到，针对不同的平台，有不同的实现。



> InterlockedAdd
> 
> 
> InterlockedCompareExchange (-Pointer)
> 
> 
> InterlockedDecrement (-Increment)
> 
> 
> InterlockedExchange (-Pointer)
> 
> 


详细的可以参看其源码。也可以参看引擎内部的使用方式：



```
class FThreadSafeCounter
{
public:
  int32 Add( int32 Amount )
  {
    return FPlatformAtomics::InterlockedAdd(&Counter, Amount);
  }
private:
  volatile int32 Counter;
};
```

### FCriticalSection


用于对非线程安全的区域进行保护。



```
FCriticalSection CriticalSection;
```

声明之后在需要的地方进行锁操作即可，有提供作用域保护的封装：



```
FScopeLock Lock(&CriticalSection);
```

这样就不需要自己进行Lock和Unlock了，可以有效的防止误操作导致的Bug的出现。


### FSpinLock


锁操作，提供Lock，Unlock以及BlockUntilUnlocked等便利的操作。


其实内部就是对FPlatformAtomics::InterlockedExchange的一个封装。


构造函数的InSpinTimeInSeconds就是默认的锁等待间隔，默认值为0.1。


### FSemaphore


这个是对信号量的封装，但是似乎不建议使用。


而且并不是对于所有的平台都有实现的，通常建议使用FEvent进行代替。


### FEvent


这个相当于UE4封装的内部使用的互斥信号量机制，有基本的等待和唤醒操作。


### FScopedEvent


对FEvnet的封装，在注释上能够看到使用示例：



```
{
        FScopedEvent MyEvent;
        SendReferenceOrPointerToSomeOtherThread(&MyEvent); // Other thread calls MyEvent->Trigger();
        // MyEvent destructor is here, we wait here.
}
```

这个操作就是将MyEvent发送到其他线程，直到在其他的地方MyEvnet->Trigger()被调用为止，都不会离开这个作用域继续执行。


### 容器


包括TArray, TMap在内的几乎大部分的容器都不是线程安全的，需要自己对同步进行管理。


当然也能看到一些线程安全的封装，例如TArrayWithThreadsafeAdd。


**TLockFreePointerList**


这个是一系列的类型，在Task Graph系统中被使用到。如其名称是LockFree的。


**TQueue**


也是LockFree的，在初始化时可以指定线程同步的类型EQueueMode，分为Mpsc（多生产者单消费者）以及Spsc（单生产者单消费者）两种模式。


只有Spsc模式是contention free的。


仔细寻找的话UE4内部有实现很多便利的类型，例如TCircularQueue这种针对双线程，一个消费一个生产的线程安全类型。


### 工具类


**FThreadSafeCounter**


就是前面例子中的线程安全的计数器。


**FThreadSingleton**


为每一个线程创建一个实例。


**FThreadIdleStats**


用于统计线程空闲状态。


## 异步执行


UE4中对基本的线程操作进行了一定程度的封装，使用相应的Helper就可以无需关心线程的创建这些问题。


### AsyncTask


这个函数可以将一些简单的任务扔到UE4的线程池中去进行，不必关心具体的线程同步问题。



```
if(IsInGameThread())
{
  //….一些操作
}
else
{
  AsyncTask(ENamedThreads::GameThread, [=]()
  {
    //….一些操作
  });
}
```

其中第一个参数是发送到的线程的名称，通常一些工作线程是无法执行引擎中IsGameThread()保护或者其他隐形的游戏线程代码的，通过这个操作将其发送到游戏线程的话使用GameThread就可以了。


其实基本上的游戏逻辑中使用最多的就是这个函数了。


### RHICmdList


这是一组独特的宏，用于将操作发送到渲染线程进行操作。


主要是对Texture之类的数据在GPU以及GPU相关的指令进行执行。


例如：



```
if (IsInRenderingThread())
{
    // Initialize the vertex factory's stream components.
    FDataType NewData;
    NewData.PositionComponent = STRUCTMEMBER_VERTEXSTREAMCOMPONENT(InVertexBuffer, FPaperSpriteVertex, Position, VET_Float3);
    NewData.TangentBasisComponents[0] = STRUCTMEMBER_VERTEXSTREAMCOMPONENT(InVertexBuffer, FPaperSpriteVertex, TangentX, VET_PackedNormal);
    NewData.TangentBasisComponents[1] = STRUCTMEMBER_VERTEXSTREAMCOMPONENT(InVertexBuffer, FPaperSpriteVertex, TangentZ, VET_PackedNormal);
    NewData.ColorComponent = STRUCTMEMBER_VERTEXSTREAMCOMPONENT(InVertexBuffer, FPaperSpriteVertex, Color, VET_Color);
    NewData.TextureCoordinates.Add(FVertexStreamComponent(InVertexBuffer, STRUCT_OFFSET(FPaperSpriteVertex, TexCoords), sizeof(FPaperSpriteVertex), VET_Float2));
    SetData(NewData);
}
else
{
    ENQUEUE_UNIQUE_RENDER_COMMAND_TWOPARAMETER(
        InitPaperSpriteVertexFactory,
        FPaperSpriteVertexFactory*, VertexFactory, this,
        const FPaperSpriteVertexBuffer*, VB, InVertexBuffer,
        {
            VertexFactory->Init(VB);
        });
}
```

这样就可以保证只能在渲染线程执行的代码不会被其他线程执行到。


渲染线程还有一些需要注意的是，UE4中有的代码的执行其实是在渲染线程中的，如果没有留意的话会造成隐形的线程同步问题。例如通常UMG的OnPaint。


### FAsyncTask


这个是一组任务的封装类，是基本的任务单元，最简单的使用如下：


#### FAutoDeleteAsyncTask



```
class ExampleAutoDeleteAsyncTask : public FNonAbandonableTask
{
    friend class FAutoDeleteAsyncTask<ExampleAutoDeleteAsyncTask>;

    int32 ExampleData;

    ExampleAutoDeleteAsyncTask(int32 InExampleData)
        : ExampleData(InExampleData)
    {
        UE_LOG(LogTemp, Log, TEXT("[ExampleAutoDeleteAsyncTask] Construct()"));
    }

    void DoWork()
    {
        UE_LOG(LogTemp, Log, TEXT("[ExampleAutoDeleteAsyncTask] DoWork()"));
    }

    FORCEINLINE TStatId GetStatId() const
    {
        RETURN_QUICK_DECLARE_CYCLE_STAT(ExampleAutoDeleteAsyncTask, STATGROUP_ThreadPoolAsyncTasks);
    }
};
```

在完成定义后，可以有两种使用方式：



```
// 将任务扔到线程池中去执行
(new FAutoDeleteAsyncTask<ExampleAutoDeleteAsyncTask>(5))->StartBackgroundTask();

// 直接在当前线程执行操作
(new FAutoDeleteAsyncTask<ExampleAutoDeleteAsyncTask>(5))->StartSynchronousTask();
```

FAutoDeleteAsyncTask的一个优点是，在执行完成后会自动销毁，无需进行额外的关注。通常文件写入或者压缩数据之类的无须进行过程管理的操作可以交付给他执行。


#### FAsyncTask


这个才是本尊，由于不会自动删除，有需要进行额外操作的情况。



```
MyTask->StartSynchronousTask();

//to just do it now on this thread
//Check if the task is done :

if (MyTask->IsDone())
{
}

//Spinning on IsDone is not acceptable( see EnsureCompletion ), but it is ok to check once a frame.
//Ensure the task is done, doing the task on the current thread if it has not been started, waiting until completion in all cases.

MyTask->EnsureCompletion();
delete Task;
```

但是如果是使用StartBackgroundTask()的话依然不需要自己进行管理。


### FRunnable


这个是交付给线程的执行体封装，通常用于比AsyncTask更加复杂的操作。


分为Init(), Run(), Exit()三个操作，如果Init失败就不会执行Run()，Run()执行完成就会执行Exit()。



```
class FRunAbleTest : public FRunnable
{
    virtual uint32 Run() override
    {
        UE_LOG(LogTemp, Log, TEXT("[FRunAbleTest] Run()"));
        FPlatformProcess::Sleep(30);
        UE_LOG(LogTemp, Log, TEXT("[FRunAbleTest] Run(): Comp"));
        return 0;
    }

};
```

通常也可以只指定Run()，然后交付给线程：



```
FRunnable* tp_Runable = new FRunAbleTest();
mp_TestThread = FRunnableThread::Create(tp_Runable, TEXT("Test_01"));
```

就可以了。


### Async


这是另一个异步执行的宏，与AsyncTask有少许不同。


Async的简单的使用方式在注释中有提到



```
    // 使用全局函数
    int TestFunc()
    {
        return 123;
    }

    TFunction<int()> Task = TestFunc();
    auto Result = Async(EAsyncExecution::Thread, Task);

    // 使用lambda
    TFunction<int()> Task = []()
    {
        return 123;
    }

    auto Result = Async(EAsyncExecution::Thread, Task);


    // 使用inline lambda
    auto Result = Async<int>(EAsyncExecution::Thread, []() {
        return 123;
    }
```

第一个参数为执行的类型，TaskGraph是将其放到任务图中去执行，Thread则是在单独的线程中执行，TreadPool则是放入线程池中去执行。


这里并不能像AsyncTask一样指定目标的线程。


同时Async会返回一个TFuture<ResultType>，而ResultType则是传入的执行函数的返回值。



```
TFunction<int()> My_Task= []() {
    return 123;
};

auto Future = Async(EAsyncExecution::TaskGraph, My_Task);
int Result = Future.Get();
```

类似这样的调用即可。


## 总结


UE4提供的异步操作大体上分为TaskGraph和TreadPool的管理方式，通常较简单的任务交付给TaskGraph，复杂的任务交付给Thread。


对于Task，引擎会有自己的管理，将其分配给空闲的Worker Thread。同时Task之间的依赖关系也会被管理，并按照需要的顺序被执行。


其实TaskGroup和ThreadPool都是可以自己进行申请和管理的，但是并没有实际的进行研究。


因为理论上，除非有需求，应当尽量的让游戏逻辑保持简洁。再加上线程同步是要支付额外的成本的，因此，要尽量避免对异步逻辑的使用，即使使用，也要尽量的保持逻辑单纯。而且这两个系统本身是虚幻为编辑器而设计的，虽然开放给用户使用，但是就像GamePlayAbility系统一样。本身每个程序员都有自己的实现思路，也没有必要一定要使用这套系统。


毕竟游戏最终是用户体验，没有用户在意屏幕背后的逻辑实现是否”Geek”。


