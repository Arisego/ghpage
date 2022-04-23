---
layout: post
status: publish
published: true
title: UE4的Windows10升级记录
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1415
wordpress_url: http://blog.ch-wind.com/?p=1415
date: '2015-08-08 12:47:37 +0000'
date_gmt: '2015-08-08 04:47:37 +0000'
tags:
- UE4
- win10
---
一时冲动下把系统升级到windows10了，在这样的早期自然是遇到了很多问题。虽然Windows10早就发布了技术预览版，但是很多软件都因为技术上或是其他的什么问题而没有办法迅速的对操作系统的升级进行跟进。比如说支付宝到目前为止依然没有提供windows10的数字证书解决方案……


按照微软之前的宣传来看，win10似乎进一步加强了应用程序的权限控制。在默认运行的情况下，各个进程之间无法相互进行干涉。直接导致迅雷快鸟无法正常的进行加速，解决方案是把迅雷快鸟和迅雷都使用管理员权限运行。不过这种问题应该过一段时间就能解决了，一般“整合”的系统都会把这些功能给去掉。就像安装ghost版的win7的情况下基本不会遇到烦人的UAC一样。


不过这些都不是什么太重要的问题，升级了win10之后遇到的最大的麻烦来自UE4。


首先的一个问题是，UE4并不支持vs2015。赶时髦的安装了vs2015之后的结果是，最后又安装了一个vs2013……主要原因是在UE的编辑器中无法识别vs2015的c++编译器，导致无法对项目进行实时编译。


另有一个问题就是在使用vs打开项目时可能会遇到这样的报错：



> 1>------ 已启动生成: 项目: Test_mp, 配置: Development_Editor x64 ------
> 
> 
> 1> 系统找不到指定的路径。
> 
> 
> 1>C:\Program Files (x86)\MSBuild\Microsoft.Cpp\v4.0\V140\Microsoft.MakeFile.Targets(37,5): error MSB3073: 命令“"D:\Software\Epic Games\4.8\Engine\Build\BatchFiles\Build.bat" Test_mpEditor Win64 Development "F:\Unreal\Test_mp\Test_mp.uproject" -rocket”已退出，代码为 3。
> 
> 
> ========== 生成: 成功 0 个，失败 1 个，最新 0 个，跳过 0 个 ==========
> 
> 


这个错误之前也遇到过，其原因是ue4的安装目录改变了，导致编译时无法找到Build.bat。解决方案也很简单，只要打开UE4编辑器，在“文件”菜单下找到“刷新visual studio项目”即可。不过，如果之前关闭的时候是编译失败的话，这个时候是无法打开UE4编辑器的。要手动去修改项目的路径配置将会是一个很浩大的工程。不过，其实只要安装UE4的时候使用同样的路径就可以了……只不过重装系统的话，多少都会有些重新整理的冲动。另外的，在进行引擎版本升级的时候也会有类似的问题。故而在进行大版本迁移的时候最好保留一段时间的旧版本引擎。


当前UE4的正式版本为4.8.3。而4.9的预览版已经更新到P2了。


关于win10和vs2015，官方在[4.9预览版的更新说明](https://forums.unrealengine.com/showthread.php?78220-Unreal-Engine-4-9-Preview&p=342676#post342676)里是这样解释的：


* UE4.9预览版还不支持vs2015，当前Github上的vs2015支持功能处于试验状态，预计4.9.0版本释出
* UE4.9可以运行在win10上，但是还没有彻底的检验过
* DX12在UE4.9中处于试验状态，但是在Win10上可以通过 -D3D12参数开启


到目前为止，UE4.8.3在Win10上运行一切正常，没有遇到什么太大的问题。


Win10总体试用感觉还是不错的，如果短期内没有什么重大的问题的话，大概就会一直使用了~


