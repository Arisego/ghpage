---
layout: post
status: publish
published: true
title: UE4的配置界面写入
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1972
wordpress_url: http://blog.ch-wind.com/?p=1972
date: '2017-10-14 19:05:31 +0000'
date_gmt: '2017-10-14 11:05:31 +0000'
tags:
- UE4
- Config
- Setting
---
UE4的Config系统使用起来很方便，但是如果要让制作出来的插件/项目更方便的让其他人设置，就需要将其写到编辑器的配置列表中。


当前使用的UE4版本为4.18.0 P4。


这里的内容是以[Conifg系统](https://blog.ch-wind.com/ue4-config-usage/)的使用为前提的，只是简略的记录了插件制作过程中，将Conifg注入到编辑器界面的过程。


## UDeveloperSettings


让配置类继承自UDeveloperSettings是最简单的配置实现方式。


不过在测试和使用的过程中遇到过很多次无法增量编译编辑器的情况，需要对项目进行重新生成。


目前还不是很确定问题是出在UDeveloperSettings这边还是由于4.18的预览bug引起的。


类似于这样的定义就可以让配置出现在项目配置中



```
UCLASS(config = ElLog, defaultconfig, meta = (DisplayName = "ElLog"))
class UElLogSettings : public UDeveloperSettings
```

不过这样的方式有一个缺点，那就是他只能出现在配置的“引擎”分类中，并没有看到能够调整目录的地方。


## ISettingsModule


其实UE4本身有提供配置的注册接口，只要通过这个接口就能将配置类注册到设定UI中去了：



```
void RegisterSettings()
{
  UE_LOG(LogTemp,Log,TEXT("[NS_ELLOG] RegisterSettings()"));
  if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
  {
    SettingsModule->RegisterSettings("Project", "Plugins", "ELLog",
      LOCTEXT("TileSetEditorSettingsName", "EasyLog Settings"),
      LOCTEXT("TileSetEditorSettingsDescription", "Configure the setting of easylog plugin."),
      GetMutableDefault<UElLogSettings>());
    UE_LOG(LogTemp, Log, TEXT("[NS_ELLOG] RegisterSettings(): Stp"));
  }
}

void UnregisterSettings()
{
    if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
    {
        SettingsModule->UnregisterSettings("Project", "Plugins", "ELLog");
    }
}
```

由于这里使用的时候是在插件中，直接在StartupModule()和ShutdownModule()中进行注册和解注册就可以了。


注意这里的配置是会覆盖的，如果使用了引擎内部相同的配置名称可能会发生奇怪的现象。


RegisterSettings函数中的各个参数的意义都比较明显，直接看注释就能明白了。



> * @param ContainerName 配置的分类，目前只有Editor和Project两个，分别对应编辑器设置和项目设置两个界面
> 
> 
> * @param CategoryName 配置的目录，这个是在上面两种界面中的目录，比如引擎、游戏等。
> 
> 
> * @param SectionName 配置的名称，就是显示在左侧目录树上的名称
> 
> 
> * @param DisplayName 配置的显示名称
> 
> 
> * @param Description 配置的描述
> 
> 
> * @param SettingsObject 实际承载这个配置的配置类
> 
> 
> * @return 会返回注册后的配置展示类，失败的话会返回Nullptr
> 
> 


上面的代码注册后就能在项目设置中看到了


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/10/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/10/image.png)


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/10/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/10/image-1.png)


需要注意的是，ISettingModule这个类型是编辑器使用的，在Shipping模式下无法使用，所以在相关的代码附近注意加上WITH_EDITOR的宏来进行差分。


通常情况下这样就可以了，不过由于插件的类型原因，这里还是有一个问题。


## Loading Phase


UE4中的模块都有载入时机的概念，在uplugin文件中可以进行配置。


目前可用的载入时机有



> PostConfigInit：引擎初始化阶段，在配置系统初始化完成后
> 
> 
> PreLoadingScreen：引擎初始化阶段，可以在这里挂入LoadingScreen的注册
> 
> 
> PreDefault：引擎初始化阶段，在Default阶段之前
> 
> 
> Default：引擎初始化阶段，此时所有的游戏模块加载已经完成
> 
> 
> PostDefault：引擎初始化阶段，在Default阶段之后
> 
> 
> PostEngineInit：引擎初始化完成后
> 
> 
> None：不会自动加载
> 
> 


这几个加载阶段有的在文档中描述不是很明确，由于没有实际使用到，所以就没有深入看过。当遇到相应需求的时候，再进行判断比较合适。


这里由于ELLog本身是Log的插件，所以为了尽可能早的加载完成，就选择了PostConfigInit阶段。


但是在这个阶段，SettingModule其实并没有完成加载，所以无法成功完成注入到配置系统中的工作。


因此需要借助额外的引擎接口才行



```
//NS_ELLOG::RegisterSettings();
FCoreDelegates::OnFEngineLoopInitComplete.AddStatic(&NS_ELLOG::RegisterSettings);
```

在StartupModule()中不直接进行注册，而是注册到引擎初始化完成的Delegate上，这样就可以在SettingModule加载完成之后执行注册了。


以上的代码都可以在[ELLog插件](https://github.com/Arisego/ELLog)中找到，因此这里就不多贴代码了。


