---
layout: post
status: publish
published: true
title: UE4项目迁移笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1771
wordpress_url: http://blog.ch-wind.com/?p=1771
date: '2017-06-05 21:38:21 +0000'
date_gmt: '2017-06-05 13:38:21 +0000'
tags:
- UE4
---
UE4本身的版本升级比较频繁，这就会导致有时候手里的或是网上下载的项目需要进行版本迁移。


通常情况下，如果是在小的版本之间迁移，尤其是跟着官方的步伐进行更新的话，都不会遇到什么大问题。但是如果在现在版本是4.16的情况下，要对4.7版本的项目进行迁移的话，就会有很多问题。


这次遇到的问题就是从网上下载的示例项目版本太旧，需要进行大的版本迁移。原本以为不会有什么太多麻烦，不想却还是花了很多时间，因此在这里记录一下。


## Build Rules


对项目进行编译，非常幸运，首先只遇到了几个Warning：



```
1>E:\Ues\GAS\Source\GAS\GAS.Build.cs : warning : Module constructors should take a ReadOnlyTargetRules argument (rather than a TargetInfo argument) and pass it to the base class constructor from 4.15 onwards. Please update the method signature.
1>E:\Ues\GAS\Source\GAS.Target.cs : warning : SetupBinaries() is deprecated in the 4.16 release. From the constructor in your .target.cs file, use ExtraModuleNames.Add("Foo") to add modules to your target, or set LaunchModuleName = "Foo" to override the name of the launch module for program targets.
1>E:\Ues\GAS\Source\GASEditor.Target.cs : warning : SetupBinaries() is deprecated in the 4.16 release. From the constructor in your .target.cs file, use ExtraModuleNames.Add("Foo") to add modules to your target, or set LaunchModuleName = "Foo" to override the name of the launch module for program targets.
```

UE4最近的两次版本升级中对BuildRule进行了变更，所以在这里只要按照提示进行修改就可以了。只是官方的提示多少有些简略，实际操作是类似这样的。


*.build.cs



```
public class GAS : ModuleRules
{
-    public GAS(TargetInfo Target)
+    public GAS(ReadOnlyTargetRules Target) : base(Target)
```

*.Target.cs



```
public class GASTarget : TargetRules
{
-    public GASTarget(TargetInfo Target)
+    public    GASTarget(TargetInfo Target) : base(Target)
     {
        Type = TargetType.Game;
-    }
-
-    //
-    // TargetRules interface.
-    //
-
-    public override void SetupBinaries(
-          TargetInfo Target,
-          ref List<UEBuildBinaryConfiguration> OutBuildBinaryConfigurations,
-          ref List<string> OutExtraModuleNames
-          )
-    {
-          OutExtraModuleNames.Add("GAS");
+          ExtraModuleNames.Add("GAS");
```

要留意的是，TargetRule有两个配置文件，一个是给Game的一个是给Editor的。


改了之后就没有提示了。


## IWYU


既然升级了BuildRules，那就自然会要使用官方在4.15新推出的号称减少50%编译时间的IWYU了。


这个技术似乎是优化了预编译头的处理机制，但是使用起来需要自己进行定义和设置，并不是升到4.15以上就能全面享用的优势呢。


首先要做的是到*.build.cs中，在ModuleRules中添加一行，类似这样：



```
// Copyright 1998-2016 Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class GAS : ModuleRules
{
    public GAS(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

       // Some other code def

    }
}
```

添加这行修改预编译头机制后，编译必然会遇到很多类似这样的错误：



```
1>E:\Ues\GAS\Source\GAS\DamageExecution.cpp(1): error : Expected DamageExecution.h to be first header included.
1>E:\Ues\GAS\Source\GAS\GASAttributeSet.cpp(1): error : Expected GASAttributeSet.h to be first header included.
1>E:\Ues\GAS\Source\GAS\GASBlueprintLibrary.cpp(1): error : Expected GASBlueprintLibrary.h to be first header included.
```

新的PCH机制要求cpp文件必须首先包含自己的头文件，按照提示一个一个对源文件进行修改就好了。


此外还会遇到很多类型未定义以及由此引发的其他错误，如果有VA的话，可以对应着进行添加包含。要注意的是，连FString这样的基础类型都会有这个问题，所以还是颇为防不胜防。


官方推荐的是在项目的头文件中包含



```
#include “CoreMinimal.h”
```

当然必要的时候可能需要包含



```
#include “EngineMinimal.h”
```

如果项目中使用到了UEngine的话，可以选择包含



```
#include “Engine/Engine.h”
```

但是，实际上，如果对引擎比较深的地方的类进行了继承的话，最后还是得包含



```
#include "Engine.h"
```

要不然可能会被报错到引擎的源代码里面去。


进行包含调整之后，基本就编译通过了。


## Load Module Error


原本以为编译通过了就万事大吉了，没想到在运行项目时却遇到了无法打开的问题……


使用VS进行调试运行，会看到这样的错误：



```
[2017.06.04-02.48.31:217][ 0]LogModuleManager:Warning: ModuleManager: Unable to load module 'E:/Ues/GAS/Binaries/Win64/UE4Editor-GAS-Win64-DebugGame.dll' because the file couldn't be loaded by the OS.
```

首先当然是怀疑dll文件不存在，但是实际上dll文件是存在的，那么问题出在哪里了呢？


求助万能的Google，终于找到了调试的方法。


这个时候需要使用微软官方的Debugging Tools for Windows，按照微软官方描述该工具被包含在WDK和Windows SDK中，因此直接[install the Windows SDK](http://go.microsoft.com/fwlink/p?LinkID=271979)，在安装的时候只勾选Debugging Tools for Windows就好了。


安装完成之后打开其中的一个名为Global Flags的工具，进行配置：


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image001_thumb-1.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/06/clip_image001-1.png)


只要选择Show Loader Snaps就好了，保存选项，重启电脑。


然后重新在VS中调试运行项目，在上一次遇到错误的地方就可以看到：



```
2264:05b0 @ 00793859 - LdrpSearchPath - ENTER: DLL name: UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793859 - LdrpComputeLazyDllPath - INFO: DLL search path computed: D:\Code\UE_4.16\Engine\Binaries\Win64;E:/Ues/GAS/Binaries/Win64;C:\Windows\SYSTEM32;C:\Windows\system;C:\Windows;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;D:\Tools\Git\cmd;C:\Program Files (x86)\Windows Live\Shared;D:\Tools\SVN\bin;D:\Code\Python\Scripts\;D:\Code\Python\;C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps;;D:\Tools\Microsoft VS Code\bin
2264:05b0 @ 00793859 - LdrpResolveDllName - ENTER: DLL name: D:\Code\UE_4.16\Engine\Binaries\Win64\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793859 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793859 - LdrpResolveDllName - ENTER: DLL name: E:/Ues/GAS/Binaries/Win64\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793859 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793859 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\SYSTEM32\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793859 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793859 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\system\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793859 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793859 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\system32\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\System32\Wbem\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Windows\System32\WindowsPowerShell\v1.0\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: D:\Tools\Git\cmd\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Program Files (x86)\Windows Live\Shared\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: D:\Tools\SVN\bin\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: D:\Code\Python\Scripts\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: D:\Code\Python\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpResolveDllName - ENTER: DLL name: D:\Tools\Microsoft VS Code\bin\UE4Editor-GameplayAbilities.dll
2264:05b0 @ 00793875 - LdrpResolveDllName - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpSearchPath - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrpProcessWork - ERROR: Unable to load DLL: "UE4Editor-GameplayAbilities.dll", Parent Module: "E:\Ues\GAS\Binaries\Win64\UE4Editor-GAS.dll", Status: 0xc0000135
“UE4Editor.exe”(Win32): 已卸载“E:\Ues\GAS\Binaries\Win64\UE4Editor-GAS.dll”
2264:05b0 @ 00793875 - LdrpLoadDllInternal - RETURN: Status: 0xc0000135
2264:05b0 @ 00793875 - LdrLoadDll - RETURN: Status: 0xc0000135
[2017.06.04-03.19.55:171][ 0]LogModuleManager:Warning: ModuleManager: Unable to load module 'E:/Ues/GAS/Binaries/Win64/UE4Editor-GAS.dll' because the file couldn't be loaded by the OS.
```

错误原因原来是UE4Editor-GameplayAbilities.dll找不到了，但是这个是引擎提供的内容，为什么会找不到呢？


费了一阵脑筋之后才想起来，似乎从某个版本开始，GamePlayAbility由引擎的Module转变为了Plugin，目的是为了避免不需要这个系统的项目包含不必要的内容。


因此直接对项目文件进行编辑，将下面的内容：



```
{
    "FileVersion": 3,
    "EngineAssociation": "",
    "Category": "",
    "Description": "",
    "Modules": [
    {
        "Name": "GAS",
        "Type": "Runtime",
        "LoadingPhase": "Default",
        "AdditionalDependencies": [
            "GameplayAbilities",
            "Engine"
        ]
    }
    ]

}
```

改为：



```
{
    "FileVersion": 3,
    "EngineAssociation": "4.16",
    "Category": "",
    "Description": "",
    "Modules": [
        {
            "Name": "GAS",
            "Type": "Runtime",
            "LoadingPhase": "Default",
            "AdditionalDependencies": [
                "Engine"
            ]
        }
    ],
    "Plugins": [
        {
            "Name": "GameplayAbilities",
            "Enabled": true
        }
    ]
}
```

重新编译，这样一来终于能够运行了。


不过Module的加载错误因项目而异，遇到这种错误还是必须使用GFlag进行调试才行。


最后，不要忘记在GFlag中把调试选项关掉，要不然调试运行速度会很感人的。


