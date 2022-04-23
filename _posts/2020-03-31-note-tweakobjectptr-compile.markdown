---
layout: post
status: publish
published: true
title: 记录TWeakObjectPtr的一个比较坑的编译报错
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2781
wordpress_url: https://blog.ch-wind.com/?p=2781
date: '2020-03-31 22:17:22 +0000'
date_gmt: '2020-03-31 14:17:22 +0000'
tags:
- UE4
- Smart Pointer
---
最近在使用TWeakObjectPtr时遇到了一个比较奇怪的编译报错，记得之前解决过，后面又忘记了，所以这次记录下来。


为了防止UObject的生命周期混乱问题，官方的建议是加上UProperty。但是有的时候考虑到引用关系的维护，我们不希望使用UProperty来维护指针。


而且，如果一个指针并不会给蓝图使用却加上了UProperty的话，会无端的感觉很“重”。


如果不希望控制指针的生命周期，而又希望维护引用的话，可以使用TWeakObjectPtr。如果希望自己保护生命周期的话，可以使用TSharedPtr。TSharedPtr记得如果使用不当的话会有二次释放的问题，不过现在记不清楚触发方式了。


这边还是回答奇怪的编译错误上吧。


## 编译错误


在对裸指针进行保护时，使用TWeakObjectPtr后出现了这样的报错：



```
2>xxx\engine\source\runtime\core\public\UObject/WeakObjectPtrTemplates.h(55): error C2338: TWeakObjectPtr can only be constructed with UObject types
2>xxx\engine\source\runtime\core\public\UObject/WeakObjectPtrTemplates.h(50): note: while compiling class template member function 'TWeakObjectPtr<AAwesomeActor,FWeakObjectPtr>::TWeakObjectPtr(const T *)'
2>        with
2>        [
2>            T=AAwesomeActor
2>        ]
2>Project\(62): note: see reference to function template instantiation 'TWeakObjectPtr<AAwesomeActor,FWeakObjectPtr>::TWeakObjectPtr(const T *)' being compiled
2>        with
2>        [
2>            T=AAwesomeActor
2>        ]
2>Project\(62): note: see reference to class template instantiation 'TWeakObjectPtr<AAwesomeActor,FWeakObjectPtr>' being compiled
```

编译器似乎不认识我们的AAwesomeActor，使用各种forward declaration反而让问题越来越复杂。


但是我们又不想破坏include隔离，还是少许有些尴尬。


## 原因


其实这个错误是因为一个“坏”习惯造成的，通常为了避免忘记写初始化的情况，我们会给指针赋个初始值，改造之后就变成了这样：



```
TWeakObjectPtr<AAwesomeActor> MyAwesomeActor = nullptr;
```

这样的话就导致模板编译的时候进入了“错误”的分支，在WeakObjectPtrTemplates.h中报错的行上面其实可以看到解释：



```
// This static assert is in here rather than in the body of the class because we want
// to be able to define TWeakObjectPtr<UUndefinedClass>.
static_assert(TPointerIsConvertibleFromTo<T, const volatile UObject>::Value, "TWeakObjectPtr can only be constructed with UObject types");
```

结论上来说，只要不加初始化就可以了，让模板编译走默认的构造函数就不会进到这里。



```
TWeakObjectPtr<AAwesomeActor> MyAwesomeActor;
```

也就是说，这里初始化就会造成画蛇添足的效果。


有时候比较着急的时候一下子想不起来就真的比较郁闷。


