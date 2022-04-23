---
layout: post
status: publish
published: true
title: UE4游戏Package记录（Windows）
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1469
wordpress_url: http://blog.ch-wind.com/?p=1469
date: '2015-08-01 19:45:05 +0000'
date_gmt: '2015-08-01 11:45:05 +0000'
tags:
- UE4
- Package
---
最近对UE4的Package功能进行了使用，整体而言打包功能比想象中复杂一些，限于设备原因只做了Windows和Android的打包。


当前使用的UE4版本为4.10.1。


面向Windows的打包相对简单，基本只要直接使用即可。


## 视频设定


主要的问题之一是，当前无法在引擎中对游戏的目标分辨率进行设置，在某些情况下会导致打包的效果和PIE的效果相差很大。不过引擎在C++中有提供接口来进行相关的控制，一般在GameMode的BeginPlay中直接调用就可以设置成功了。



```
do{

    if(GEngine == nullptr) break;

    UGameUserSettings* Settings = GEngine->GameUserSettings;

    if (Settings == nullptr) break;

    int32 Width = 1920, Height = 1080;

    Settings->RequestResolutionChange(Width, Height, EWindowMode::Type::Windowed, false);

    Settings->ConfirmVideoMode();

    //Settings->RevertVideoMode(); // 本操作可以取消分辨率更改

    Settings->SetScreenResolution(Settings->GetLastConfirmedScreenResolution());

    Settings->SetFullscreenMode(Settings->GetLastConfirmedFullscreenMode());

    Settings->SaveSettings();

     Settings->ScalabilityQuality.AntiAliasingQuality = 3;     // Epic

     Settings->ScalabilityQuality.ResolutionQuality = 3;     // Epic

    Settings->ApplyNonResolutionSettings();

    Settings->SaveSettings();

}while(false);
```

 


上面的ScalabilityQuality是可以在编辑器中进行设定的，对应关系如下


[![UE4游戏Package记录（Windows）](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/12/image.png)[![UE4游戏Package记录（Windows）](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/12/image1.png)


另外名为Screen Percentage的属性是在PostProcess的属性中进行设置的。以及，如果要修改抗锯齿的方式，也需要在PostProcess中进行。


## 运行黑屏


打包之后运行直接黑屏的话可能是由很多原因引起的，不过如果是在打包测试的过程中直接使用新项目，或者之前没有进行过设置变更的话，还是可能遇到。原因是没有对默认地图进行设置，主要表现是，完全的黑屏，但是调试输出却可以显示在屏幕上。


在【项目设置>>项目>>地图&模式】中进行修改即可。


[![UE4游戏Package记录（Windows）](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/12/image2.png)


## 莫名的链接错误


这个错误的出现几率比较低，而且链接错误有很大的可能性是其他原因引起的，所以排查起来很麻烦。如果之前都是正常的却突然出现类似这样的情况：



> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: [1/1] Link Test_mp.exe
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool:      ڴ      F:\Unreal\Test_mp 4.10\Binaries\Win64\Test_mp.lib  Ͷ    F:\Unreal\Test_mp 4.10\Binaries\Win64\Test_mp.exp
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: UELinkerFixups.cpp.obj : error LNK2019:  ޷        ⲿ     "void __cdecl EmptyLinkFunctionForGeneratedCodeOnlineSubsystemSteam(void)" (?EmptyLinkFunctionForGeneratedCodeOnlineSubsystemSteam@@YAXXZ)   ÷    ں    "void __cdecl UELinkerFixups(void)" (?UELinkerFixups@@YAXXZ)  б
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: UELinkerFixups.cpp.obj : error LNK2019:  ޷        ⲿ     "void __cdecl EmptyLinkFunctionForStaticInitializationUE4Game(void)" (?EmptyLinkFunctionForStaticInitializationUE4Game@@YAXXZ)   ÷    ں    "void __cdecl UELinkerFixups(void)" (?UELinkerFixups@@YAXXZ)  б
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: UELinkerFixups.cpp.obj : error LNK2019:  ޷        ⲿ     "void __cdecl EmptyLinkFunctionForStaticInitializationOnlineSubsystemNull(void)" (?EmptyLinkFunctionForStaticInitializationOnlineSubsystemNull@@YAXXZ)   ÷    ں    "void __cdecl UELinkerFixups(void)" (?UELinkerFixups@@YAXXZ)  б
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: UELinkerFixups.cpp.obj : error LNK2019:  ޷        ⲿ     "void __cdecl EmptyLinkFunctionForStaticInitializationOnlineSubsystemSteam(void)" (?EmptyLinkFunctionForStaticInitializationOnlineSubsystemSteam@@YAXXZ)   ÷    ں    "void __cdecl UELinkerFixups(void)" (?UELinkerFixups@@YAXXZ)  б
> 
> 
> MainFrameActions: 打包 (Windows (64位)): UnrealBuildTool: F:\Unreal\Test_mp 4.10\Binaries\Win64\Test_mp.exe : fatal error LNK1120: 4    ޷        ⲿ
> 
> 


可以尝试在打包设定中勾选Full Rebuild


[![UE4游戏Package记录（Windows）](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/12/image3.png)


不过需要注意的是，如果使用的是源码版的引擎的话，会消耗大量的时间。


## 杂项记录


打包的过程中还遇到了一些其他的错误，这里姑且记录一下。


在打包完成之后运行游戏始终出现这样的错误：



> Windows 无法访问指定设备、路径或文件。您可能没有合适的权限访问这个项目。
> 
> 


最后解决办法是把安全软件给关掉，有的安全软件会在没有任何提示的情况下将文件给隔离/删除掉。


还有一个错误是在Ship打包的时候，运行游戏出现错误：



> Failed to open descriptor file ‘../../../Blank-Win64-Shipping/Blank-Win64-Shipping.uproject’
> 
> 


这个似乎是打包功能的Bug引起的，又或者就是这样的设定。总之将对应的文件名进行修改就可以了，修改运行文件本身的文件名也是可以的。


