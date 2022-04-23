---
layout: post
status: publish
published: true
title: UE4与FMod音乐可视化验证
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1272
wordpress_url: http://blog.ch-wind.com/?p=1272
date: '2015-05-21 12:09:36 +0000'
date_gmt: '2015-05-21 04:09:36 +0000'
tags:
- UE4
- FMod
---
制作音游的一个重要步骤，就是验证引擎的相关技术特性，以此来决定是否更换引擎或者更改设计。


当前UE版本4.7.6；FMod版本1.06.02；


由于需要播放用户提供的音乐文件，所以需要读取用户设备上的文件。在翻阅文档之后，发现可以使用PlatformFileManager读取外部文件相关信息，同时也有获取目录信息的相关接口。



```
FString CompleteFilePath = "H:/music/test.mp3";
if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*CompleteFilePath))
{
OutputDebugStringA("Error");
return 0;
}

const int32 FileSize = FPlatformFileManager::Get().GetPlatformFile().FileSize(*CompleteFilePath);
```

通过上面的代码，成功获得文件大小。外部文件相关验证完成。


接下来就是音乐播放相关的实现了，FMod在UE4上有插件实现。基本可以满足使用需求。


下载并将FMod插件解压到UE4目录之后，首先在项目的*.Build.cs中添加下面的代码



```
public class mpop : ModuleRules
{
public mpop(TargetInfo Target)
{
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore" });

PrivateDependencyModuleNames.AddRange(new string[] { "FMODStudio" });
}
}
```

这样一来在需要使用到FMod地方进行文件包含就不会遇到报错了



```
#include "fmod_studio.hpp"
```

如果在编译时遇到LNK1181之类的编译错误，建议按照提示查找FMod插件中是否提供了对应的Lib文件。如果没有的话可能需要重新编译插件或者使用更早期有提供的版本。


使用FMod底层API的第一步是得到一个底层的API System，根据使用方式的不同有两条路径。


**获取插件系统**


适合与EndPlay和BeginPlay之类的事件挂钩进行使用。不需要自主使用update，插件内部已经有更新机制了。



```
result = IFMODStudioModule::Get().GetStudioSystem(EFMODSystemContext::Runtime)->getLowLevelSystem(&system);

if (result != FMOD_RESULT::FMOD_OK) break;

result = system->getVersion(&version);

if (result != FMOD_RESULT::FMOD_OK) break;
```

**自主创建系统**


适合配合单例模式使用，和插件建立的系统相对独立。不过依然不需要自己进行update操作。与直接获取不同的是，需要自己进行初始化操作。



```
result = FMOD::System_Create(&system);

if (result != FMOD_RESULT::FMOD_OK) break;

result = system->getVersion(&version);

if (result != FMOD_RESULT::FMOD_OK) break;

result = system->init(32, FMOD_INIT_NORMAL, extradriverdata);    // <进行初始化

if (result != FMOD_RESULT::FMOD_OK) break;
```

系统创建之后，音乐播放使用createsound即可



```
result = system->createSound("H:/music/test.mp3", FMOD_LOOP_NORMAL | FMOD_2D, 0, &sound);
if (result != FMOD_RESULT::FMOD_OK) break;

result = sound->getNumSubSounds(&numsubsounds);
if (result != FMOD_RESULT::FMOD_OK) break;

if (numsubsounds)
{
sound->getSubSound(0, &sound_to_play);
if (result != FMOD_RESULT::FMOD_OK) break;
}
else
{
sound_to_play = sound;
}

result = system->playSound(sound_to_play, 0, false, &channel);
if (result != FMOD_RESULT::FMOD_OK) break;
```

要对音乐进行可视化，最基础的数据获取方式是对音乐进行快速傅里叶变换（FFT）。FMod本身有提供FFT的功能，因此直接使用即可，无需再造车轮。FMod提供的FFT是DSP的一种，可以加载在Channel、ChannelGroup、ChannelControl上。这里，我们选择在系统创建并初始化之后直接加载到ChannelGroup上。



```
FMOD::ChannelGroup *mastergroup;

result = system->createDSPByType(FMOD_DSP_TYPE_FFT, &fftdsp);
if (result != FMOD_RESULT::FMOD_OK) break;

result = system->getMasterChannelGroup(&mastergroup);
if (result != FMOD_RESULT::FMOD_OK) break;

result = mastergroup->addDSP(0, fftdsp);
if (result != FMOD_RESULT::FMOD_OK) break;
```

在每一次Ontick时进行FFT数据的获取：



```
FMOD_DSP_PARAMETER_FFT *fft;

char* ts = new char[40];
fftdsp->getParameterData(FMOD_DSP_FFT_SPECTRUMDATA, (void **)&fft, 0, 0, 0);
OutputDebugStringA("<FMODHolders> - Update Begin -\n");
for (int channel = 0; channel < fft->numchannels; channel++){
OutputDebugStringA("> -c-");
for (int bin = 0; bin < fft->length; bin++)
{
float val = fft->spectrum[channel][bin];
sprintf(ts, "> spec: %f \n", val);
OutputDebugStringA(ts);
}
}
OutputDebugStringA("<FMODHolders> - Update End -\n");
delete ts;
```

开始播放之后就可以看到fft数据已经正常输出了。


为了方便对fft的数据进行解析，需要获得采样率。



```
system->getSoftwareFormat(&tnp, NULL, NULL);
```

这样基本上音乐数据一块的验证就完成了。


