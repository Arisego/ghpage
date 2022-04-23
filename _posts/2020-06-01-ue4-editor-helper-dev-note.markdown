---
layout: post
status: publish
published: true
title: UE4编辑器帮助开发记录
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2911
wordpress_url: https://blog.ch-wind.com/?p=2911
date: '2020-06-01 16:09:00 +0000'
date_gmt: '2020-06-01 08:09:00 +0000'
tags:
- UE4
---
UE4的编辑器帮助类对于开发一些小功能加快开发速度挺有用的。


当前使用的UE4版本为4.25。


## 命令行支持


要支持命令行，不仅仅需要继承UCommandlet。还要注意类的命名，否则可能会无法正确的执行：



> LogInit: Error: xxxxx looked like a commandlet, but we could not find the class.
> 
> 


主要是因为命名必须采用xxxxxxCommandlet的形式，因为在FEngineLoop::PreInitPreStartupScreen中作了特殊处理



```
if (Token.StartsWith(TEXT("run=")))
{
    Token.RightChopInline(4, false);
    if (!Token.EndsWith(TEXT("Commandlet")))
    {
        Token += TEXT("Commandlet");
    }
}
```

对于传入的参数可以使用帮助函数进行解析



```
TArray<FString> Tokens;
TArray<FString> Switches;
TMap<FString, FString> ParamVals;

const TCHAR* Parms = *Params;
UCommandlet::ParseCommandLine(Parms, Tokens, Switches, ParamVals);
```

## Console相关


console对于编辑器内调试还是挺有帮助的，尤其是console var，简直调试利器，尤其是你的项目编译一次要十几分钟的时候……


### Console帮助


这个记得以前在社区有看到生成的方法，但是这次在网上搜了很久才找到方法。


其实很简单，在console里面输入help，就会自动在你项目目录里面生成几乎所有的console的说明文档了。还自带搜索过滤功能……


不过这个生成的其实不全，这次刚好用到的几个没提到的有：


net SOCKETS 输出所有打开的UChannel


net DUMPSERVERRPC 输出所有的ServerRpc


net NETFLOOD 发送 NMT_Netspeed 256次


net NETDEBUGTEXT 使用DebugText发送数据，参考NotifyControlMessage


net NETDISCONNECT 触发连接断开


### 添加Console支持


虽然现在编辑器有Python支持了，但是自定义的函数注册Console会比python轻快些，尤其只是一些不成体系的小帮助函数。



```
static void _Import_Curve(const TArray< FString >& InArgs);

static FAutoConsoleCommand ImportXxxToCurve(
    TEXT("aio.curvim"),
    TEXT("Import xxx to target, argument [curve asset ref] "),
    FConsoleCommandWithArgsDelegate::CreateStatic(&_Import_Curve),
    ECVF_Cheat);
```

传入的数组就是入参表。同类的还有FAutoConsoleCommandWithWorld和FAutoConsoleCommandWithOutputDevice的样子，不过没有使用过。


这边主要做一些自定义的资源导入导出指令，所以并不需要World呢。


