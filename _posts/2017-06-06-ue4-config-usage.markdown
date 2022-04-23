---
layout: post
status: publish
published: true
title: UE4中Config的使用
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1777
wordpress_url: http://blog.ch-wind.com/?p=1777
date: '2017-06-06 20:12:22 +0000'
date_gmt: '2017-06-06 12:12:22 +0000'
tags:
- UE4
- Config
---
UE4中本身有一套非常成熟的INI文件配置机制，对于简单的属性配置，可以直接进行借用。


当前使用的UE4版本为4.15.2。


## 引擎配置


整个Config机制在引擎中最常见的地方就是引擎的配置本身了，项目配置与引擎配置，Localize的配置……这些都是通过这个机制进行的。


引擎自带的配置分类有以下这些：



> Compat（兼容性）
> 
> 
> DeviceProfiles（设备概述文件）
> 
> 
> Editor（编辑器）
> 
> 
> EditorGameAgnostic（编辑器游戏不可知论）
> 
> 
> EditorKeyBindings（编辑器按键绑定）
> 
> 
> EditorUserSettings（编辑器用户设置）
> 
> 
> Engine(引擎)
> 
> 
> Game(游戏)
> 
> 
> Input（输入）
> 
> 
> Lightmass
> 
> 
> Scalability（可扩展性）
> 
> 


配置文件是有加载优先的，按照官方文档提供的顺序，越靠后的值会覆盖前面的值。



> Engine/Config/Base.ini
> 
> 
> Engine/Config/BaseEngine.ini
> 
> 
> Engine/Config/[Platform]/[Platform]Engine.ini
> 
> 
> [ProjectDirectory]/Config/DefaultEngine.ini
> 
> 
> [ProjectDirectory]/Config/[Platform]/[Platform]Engine.ini
> 
> 
> [ProjectDirectory]/Saved/Config/[Platform]/Engine.ini
> 
> 


这个加载次序是以Engine配置为基础的。


关于这部分的详细可以参照[[官方文档](https://docs.unrealengine.com/latest/CHN/Programming/Basics/ConfigurationFiles/index.html)]。


## 自主调用


使用GConfig就可以对这个配置系统中的值进行查询和写入，要对配置进行读取的话可以使用：



```
if(!GConfig) return;

FString ValueReceived;
  GConfig->GetString(
  TEXT("/Script/Engine.WorldInfo"),
  TEXT("GlobalDefaultGameType"),
  ValueReceived,
  GGameIni
);
```

而写入的话，可以使用：



```
if (!GConfig) return;
GConfig->SetInt(
  TEXT("sectionname"),
  TEXT("key"),
  100,
  GGameUserSettingsIni
  );
GConfig->Flush(false, GGameUserSettingsIni);
```

这里使用的Get/Set是一系列函数，对应引擎内部的不同值，第四个参数是配置的名称，与上面给出的配置分类是对应的，应该，没有仔细的考证过。可以看到GGameUserSettingsIni附近有很多这样的定义：



```
FString                GEngineIni;                                                    /* Engine ini filename */

/** Editor ini file locations - stored per engine version (shared across all projects). Migrated between versions on first run. */
FString                GEditorIni;                                                    /* Editor ini filename */
FString                GEditorKeyBindingsIni;                                        /* Editor Key Bindings ini file */
FString                GEditorLayoutIni;                                            /* Editor UI Layout ini filename */
FString                GEditorSettingsIni;                                            /* Editor Settings ini filename */

/** Editor per-project ini files - stored per project. */
FString                GEditorPerProjectIni;                                        /* Editor User Settings ini filename */

FString                GCompatIni;
FString                GLightmassIni;                                                /* Lightmass settings ini filename */
FString                GScalabilityIni;                                            /* Scalability settings ini filename */
FString                GHardwareIni;                                                /* Hardware ini filename */
FString                GInputIni;                                                    /* Input ini filename */
FString                GGameIni;                                                    /* Game ini filename */
FString                GGameUserSettingsIni;                                        /* User Game Settings ini filename */
```

其实这种用法，使用起来相对有些麻烦，而且会把自己的配置和引擎的配置混在一起，其实还有更加简单的使用这个配置的方法：


## 扩展使用


这个特性是可以扩展给自己定义的类使用的，在UClass定义时制定Config即可，像是这样的感觉：



```
UCLASS(config=GameUserSettings, configdonotcheckdefaults)
class ENGINE_API UGameUserSettings : public UObject
```

其实上面那些自带的引擎配置就是在引擎中预先定义好的[名称]-[配置文件名]对应组。


这里面在定义时，config=custom，这样自己定义配置文件名称也是可以的。如果不想自己的配置和引擎的配置混在一起变得乱七八糟的话，这是一个很好的选择。


这样的好处是所有标记为UProperty的属性加上config标记都会被自动载入，在执行SaveConfig后就可以直接保存，不需要和配置的逻辑打交道。定义时就像这样的感觉：



```
UPROPERTY(config, EditAnywhere, Category="MouseProperties”)
uint32 bEnableFOVScaling:1;
```

在文件名的分配上，如果使用custom的话，配置文件就会被保存到custom.ini的命名规则下。如果一时之间找不到配置文件，可以使用这个文件名进行搜索。


这一系列的配置还有其他几个选项：



> perObjectConfig
> 
> 
> 使得配置变为针对每个Object的实例，而不是每个Class存一个配置块。
> 
> 
> configdonotcheckdefaults
> 
> 
> 配置了这个的话，config在读取的时候就不会去读取default配置。
> 
> 
> defaultconfig
> 
> 
> 配置只保存在default中
> 
> 


这里有一个概念就是Default，Default配置的读取是比较靠前的，通常保存在项目目录Config/[Custom]Default.ini中。这里有一个在测试时需要注意的，如果SaveConfig的值与Default值相同的话，那么就会不进行保存，该行配置会消失，因为与默认值一样了。


在进行配置文件操作和设定时，可以使用UpdateDefaultConfigFile()来写入到default值，而通常的配置可以使用SaveConfig()进行保存，因为SaveConfig是会自动进行Flush的，而另一个UpdateGlobal ConfigFile则局限性较强，但它可以确保写入路径是指向用户配置的。


要注意的是，如果在Shipping打包模式下，那么可以让用户和我们自己进行配置的ini文件将不会出现在项目目录中个，而是在"用户目录\AppData\Local\rg_unreal\Saved\Config\WindowsNoEditor\[custom].ini"中。


如果觉得这样有些Low的话，我们就需要绕回去：


## 自定义路径


仔细查看Config系统的源码，我们可以看到，ini的加载是在UObject中进行指定的。如果没有定义PerObjectConfig的话，配置是在CDO阶段就完成了的。如果定义了PerObject的话则会在UObject:: PostLoad中进行配置加载。


但是系统本身的GetConfigName是无法被重载的，好在引擎有暴露其他的接口，我们要对其使用只要自己在BeginPlay之类的事件中自己进行读写就可以了。


其实要使用的函数在上面已经用到了，只是在调用的时候使用的是默认参数罢了。



```
SaveConfig(CPF_Config, *ConfPath);
```

这样调用的话就可以将当前类中的配置保存到指定的路径去了，不用指定后缀名Ini也是可以的。


不过，出于保险起见，最好是在Save之后，刷新一下缓存



```
GConfig->Flush(false, ConfPath)
```

要读取的话也是同理，先刷新缓存



```
GConfig->Flush(true, ConfPath)
```

其实如果配置的读写都是在引擎内完成的话，是没必要在读取的时候刷缓存的。


但如果有在引擎外部修改配置文件，并希望配置“实时”的反映到读取中的话，就需要在读取前刷新一下缓存。


读取的话使用



```
ReloadConfig(NULL, *ConfPath)
```

就可以了，这里使用到的ConfPath都是FString。


## 总结


基本上配置存取使用官方的配置类就可以了，这里有一点很强大的是，似乎所有可以UPROPERTY化的引擎定义变量都可以写入到Config中，已经测试过TArray和TMap可以正常的进行读写。


但是像是UObject这类的并没有进行测试……不过引擎的配置中有大量的使用UAsset的引用，应当是毫无问题的。


不过，配置文件虽然有读写功能，但是它的定位本身并不适合用来存档。如果有这方面的需求请使用[[SaveGame类](https://docs.unrealengine.com/latest/CHN/Gameplay/SaveGame/index.html)]，蓝图与C++皆可使用。


