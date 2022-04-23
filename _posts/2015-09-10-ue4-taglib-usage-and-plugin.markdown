---
layout: post
status: publish
published: true
title: UE4中Taglib使用及插件制作
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1482
wordpress_url: http://blog.ch-wind.com/?p=1482
date: '2015-09-10 20:21:07 +0000'
date_gmt: '2015-09-10 12:21:07 +0000'
tags:
- UE4
- Taglib
- 插件
---
UE4使用第三方库时，为了方便跨平台编译、避免冲突和多次复用，将其制作成插件是不错的选择。


当前UE4版本为4.10.1。


## Taglib的使用


Taglib是一个用于读取多媒体文件标签的第三方库，之所以会使用到，是因为当前FMod在读取含有非英文的标签会得到错误的结果。


Taglib需要自己使用CMake进行配置和编译。如果只是在Windows下使用的话，最简单的方法是直接引用生成的.lib文件。在项目的.build.cs中，ModuleRules的实现里面添加：





```
PublicIncludePaths.Add("F:/Libs/taglib-master/include/taglib");

PublicAdditionalLibraries.Add("F:/Libs/taglib-master/taglib/Release/tag.lib");
```

然后在需要使用的地方使用Taglib即可







```
#define TAGLIB_STATIC

#include "fileref.h"

#include "tag.h"

#include "tpropertymap.h"

// ……

/** TagLib Fetch Tag */

MusicItem->AlubmName = "";

MusicItem->ArtistName = "";

TagLib::FileRef TLFile(*MusicFullPath);

if (!TLFile.isNull() && TLFile.tag()){

    OutputDebugStringA("TagLib Fetch Reading Begin.\n");

    TagLib::Tag *tag = TLFile.tag();

    std::wstring tWsName = tag->title().toWString();

    if (tWsName.length()>0)    MusicItem->SetDisplayName(tWsName.c_str());

    MusicItem->AlubmName = tag->album().toWString().c_str();

    MusicItem->ArtistName = tag->artist().toWString().c_str();

}

else{

    OutputDebugStringA("TagLib Fetch Fails.\n");

}

/** TagLib Fetch Tag - End */
```

 




但是这样的方法在进行Android之类的平台上的编译时，会遇到很多麻烦。因此将其制作为UE4插件是最好的解决方法。


## UE4插件制作


UE4的插件制作一直都处在WIP的状态，直到4.9版本开始，官方文档才变更为了可以使用的状态。因此，为了避免研究了之后官方大规模的更新，到了现在才开始研究。


UE4插件的制作相对还是比较简单的，在引擎中，官方就已经提供了4个示例插件，以其为基础进行插件开发即可。


插件的代码布局和UE4的游戏项目差不多，只有在Public中定义的类对外界才是可见的。详细的插件系统介绍可以参照[[官方文档](https://docs.unrealengine.com/latest/CHN/Programming/Plugins/)]。


插件的描述文件中最重要的地方是Modules中的Type参数，这个参数是决定插件的加载类型的。通常情况下，如果是在实际游戏逻辑中使用的插件的话，这里需要修改为Runtime。


如果是在项目的Plugins目录中添加插件目录进行开发的话，需要重新生成下项目文件


这样才能在vs中看到插件。还有比较容易忘记的是，直接继承自UObject的类，必须定义Blueprintable才可以在编辑器中可见。


## Taglib改造


将taglib的源代码整个扔到Private目录中去，并在.build.cs中添加包含路径





```
            PrivateIncludePaths.AddRange(

                new string[] {

                    "TagLibs/Private","TagLibs/Private/taglib", "TagLibs/Private/taglib/toolkit", "TagLibs/Private/taglib/asf", "TagLibs/Private/taglib/mpeg", "TagLibs/Private/taglib/ogg", "TagLibs/Private/taglib/ogg/flac", "TagLibs/Private/taglib/flac", "TagLibs/Private/taglib/mpc", "TagLibs/Private/taglib/mp4", "TagLibs/Private/taglib/ogg/vorbis", "TagLibs/Private/taglib/ogg/speex", "TagLibs/Private/taglib/ogg/opus", "TagLibs/Private/taglib/mpeg/id3v2", "TagLibs/Private/taglib/mpeg/id3v2/frames", "TagLibs/Private/taglib/mpeg/id3v1", "TagLibs/Private/taglib/ape", "TagLibs/Private/taglib/wavpack", "TagLibs/Private/taglib/trueaudio", "TagLibs/Private/taglib/riff", "TagLibs/Private/taglib/riff/aiff", "TagLibs/Private/taglib/riff/wav", "TagLibs/Private/taglib/mod", "TagLibs/Private/taglib/s3m", "TagLibs/Private/taglib/it", "TagLibs/Private/taglib/xm"

                }

                );
```

要添加的比较多，主要是因为Taglib本身使用的就是这样的方法，稍微有点麻烦。




添加完路径之后，首先遇到的错误是



> 2>EXEC : error : The first include statement in source file ‘F:\Unreal\PluginDev\Plugins\TagLibs\Source\TagLibs\Private\taglib\mpeg\id3v2\id3v2header.cpp’ is trying to include the file ‘iostream’ as the precompiled header, but that file could not be located in any of the module’s include search paths.
> 
> 


这个错误的来源乍看之下很奇怪，其实在项目中有时候也会遇到。修正方法是，在cpp文件中首先包含模块头文件。





```
#include "TagLibsPrivatePCH.h"
```

添加了上面的文件之后，就会遇到Taglib内部大规模的namespace引发的错误，这一部分只能是一个一个的对命名空间进行控制修改了。




命名空间修正之后，会遇到如下错误



> error C2872: “DWORD”: 不明确的符号
> 
> 


在UE4内部有对DWORD进行禁止使用的机制，这里需要重新开启。开启的方法是使用UE4内部提供的机制。





```
#include "AllowWindowsPlatformTypes.h"

#include <windows.h>

#include "HideWindowsPlatformTypes.h"
```

这样的话就可以使用DWORD等了。




在编译过程中还会遇到



> 4310:编译器执行的转换将截断数据
> 
> 


这个错误出现点有点多，直接让编译器忽略比较快。



```
#pragma warning(disable: 4310)
```

经过上面的几个步骤，基本就可以正常的通过编译了。只是在打包的时候会有这样的错误：



> UnrealBuildTool: ERROR: Couldn’t find referenced module ‘PluginName’
> 
> 


或者



> Plugin ‘PluginName’ failed to load because module ‘PluginName’ could not be found. Please ensure the plugin is properly installed, otherwise consider disabling the plugin for this project
> 
> 


这时候需要在Development下对代码进行一次重新编译。


这样的话就可以在Windows下正常的使用了。


## Android平台


插件在Android平台打包时会遇到很多编译器相关的错误，需要进行一些修正。


首先遇到的错误是



> error : delete called on ‘const TagLib::FileRef::FileTypeResolver’ that is abstract but has non-virtual destructor [-Werror,-Wdelete-non-virtual-dtor]
> 
> 


这个错误原本是warning，据说是taglib为了保证其自身的向下兼容性等原因而遗留的。


因此，修正方法是让编译器忽略这个warning。直接在模块头文件上加上





```
#if defined(__clang__)

#pragma clang diagnostic ignored "-Wdocumentation"

#pragma clang diagnostic ignored "-Wshadow"

#pragma clang diagnostic ignored "-Wdelete-non-virtual-dtor"

#pragma clang diagnostic ignored "-Wunused-function"

#define HAVE_SNPRINTF

#endif
```



## RTTI


整个改造过程最麻烦的问题出在了RTTI上，Taglib内部大量的使用了dynamic_cast进行类型检测，而不是使用virtual来进行函数重载。


而UE4和大多数游戏引擎一样，出于效率原因是禁止使用RTTI的，好在UE4提供了可以单独在插件和项目中打开RTTI的方法。


在插件的.build.cs中添加如下所示的代码即可：





```
namespace UnrealBuildTool.Rules

{

    public class TagLibs : ModuleRules

    {

        public TagLibs(TargetInfo Target)

        {

            bUseRTTI = true; // 打开RTTI

            // ... ...
```



但是，这个开关对Android是没有作用的，我们需要编辑引擎源码进行修正。在AndroidToolChain.cs中，将所有的



```
Result += " -fno-rtti";
```

改为



```
if (!CompileEnvironment.Config.bUseRTTI) Result += " -fno-rtti";
```

混合使用RTTI的情况下需要注意的是，根据编译器的不同，将定义了virtual的多态类型在两种不同的编译方式之间混合使用时，其结果是不可预知的。具体而言可能会出现类似下面的错误：



> error: undefined reference to ‘typeinfo for UObject’
> 
> 
> error: cannot pass object of non-trivial type ‘FString’ through variadic function; call will abort at runtime [-Wnon-pod-varargs]
> 
> 


结论上，就是在插件中要尽量避免使用UE4内部的类。详细的技术上的原因可以参照[这里]。


## 插件使用


插件制作完成后，使用起来就比较简单了。如果要在代码中使用TagLibs插件的话，在.build.cs中添加



```
PrivateDependencyModuleNames.AddRange(new string[] { "TagLibs" });
```

然后在要使用的类，一般是蓝图函数库的文件中添加包含



```
#include "ITagLibs.h"
```

以及使用



```
ITagLibs::Get().GetMusicInfo(args…)
```

即可。


其他详情可参见完成的Taglib插件源码，已上传至[[Github](https://github.com/steinkrausls/UE4-TagLibs)]。


