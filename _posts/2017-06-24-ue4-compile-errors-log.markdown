---
layout: post
status: publish
published: true
title: UE4错误笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1796
wordpress_url: http://blog.ch-wind.com/?p=1796
date: '2017-06-24 19:58:07 +0000'
date_gmt: '2017-06-24 11:58:07 +0000'
tags:
- UE4
- Error
---
记录了最近遇到的几个编译错误。


当前使用的UE4版本为4.15.3。


## C4530


这个错误是尝试在UE4中使用Try/Except引起的。


报错如下：



> warning C4530: C++ exception handler used, but unwind semantics are not enabled. Specify /EHsc
> 
> 


UE4默认的情况下不允许使用Exception。


AnswerHub有回答说要在build.cs中设置：



> UEBuildConfiguration.bForceEnableExceptions = true;
> 
> 


但是由于新版本的变更，这个属性变成只读了，现在需要这样设置：



> bEnableExceptions = true;
> 
> 


## C2039


某种意义上的老朋友，报错如下：



> 1>E:\UEPro\New_UI\Plugins\EasyLog\Source\EasyLog\Private\LogHolder.cpp(28): error C2039: “CreateDirectoryW”: 不是“IPlatformFile”的成员
> 
> 
> 1> f:\epic\ue_4.15\engine\source\runtime\core\public\GenericPlatform/GenericPlatformFile.h(160): note: 参见“IPlatformFile”的声明
> 
> 


UE4中这种错误报进引擎内部的，一般都是因为定义冲突引起的，需要针对包含关系进行排查。


这种与Win Api相关的，通常是由于UE4中对Windows.h的兼容引起的。有时也会报出DWORD未定义这样的错误。可以尝试使用引擎提供的帮助包含：



```
#include "AllowWindowsPlatformTypes.h"

#include "something_about_windows.h"

#include "HideWindowsPlatformTypes.h"
```

## C4596


这个错误其实是VS2017的版本更新的新功能造成的，报错如下：



> error C4596: 'Blablabla': illegal qualified name in member declaration
> 
> 


详细的原因可以查看MSDN关于[[permissive](https://docs.microsoft.com/en-us/cpp/build/reference/permissive-standards-conformance)]的文档，这个功能是为了让代码更加符合标准以提高代码的可移植性。


修正方式文档中已经有提供，通常都是类似这样的修改：



```
template <typename T_Ptr, typename Pred>

class RegistryWithPred : public AbstractRegistry<T_Ptr, std::vector<T_Ptr*>> {

public:
- typedef typename RegistryWithPred<T_Ptr, Pred>::iterator iterator;
- typedef typename RegistryWithPred<T_Ptr, Pred>::const_iterator const_iterator;
+ typedef typename /*RegistryWithPred<T_Ptr, Pred>::*/iterator iterator;
+ typedef typename /*RegistryWithPred<T_Ptr, Pred>::*/const_iterator const_iterator;

RegistryWithPred(void) {

}
```

