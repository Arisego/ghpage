---
layout: post
status: publish
published: true
title: UE4游戏Package记录（Android）
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1463
wordpress_url: http://blog.ch-wind.com/?p=1463
date: '2015-08-01 19:27:14 +0000'
date_gmt: '2015-08-01 11:27:14 +0000'
tags:
- UE4
- Package
---
Android的打包比Windows下要稍微麻烦一些，因为使用的编译器不同导致的问题也就多了起来。


当前使用的UE4版本为4.10.1。


## 基本步骤


UE4打包Android的教程官方是有提供的，可以看[这里](https://docs.unrealengine.com/latest/INT/Platforms/Android/GettingStarted/)。


下面只是简单的做一下总结的感觉，首先需要进行的是相关环境的安装。android sdk、ndk以及很多其他的东西，直接使用引擎自带的安装器就可以一次性搞定了。安装器在引擎如下的目录中可以找到



> [ENGINE INSTALL LOCATION]\Engine\Extras\Android\CodeWorksforAndroid-1R6u1-windows.exe
> 
> 


开发必备环境的设定可以看[[这里](https://docs.unrealengine.com/en-us/Platforms/Android/Reference)]。


根据网络情况的不同，安装时间可能会比较长。


安装好之后其实就可以进行Android打包了，如果之前进行过Windows打包的话，基本不需要额外的设置。


## 插件问题


Android打包过程中很容易遇到的问题是插件上的，例如，如果在项目中有使用FMod的话，就需要进行一些额外的工作。


首先我们需要的是排查工具，在Android的SDK中有提供可以用于错误排查的工具。路径位于sdk的tools目录中，使用monitor.bat即可。


为了使用方便，在LogCat中添加新的过滤器


[![](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb-2.png)](https://blog.ch-wind.com/wp-content/uploads/2015/12/image-2.png)


就可以方便的对UE4的输出记录进行排查了。


如果在项目中有使用FMod的话，游戏在Android上是无法直接打开的，查看输出记录可以看到


[![](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb-3.png)](https://blog.ch-wind.com/wp-content/uploads/2015/12/image-3.png)


FMod的库文件没有被正确的找到，其实这是由于没有正确的按照FMod官方的配置说明进行配置导致的。在FMod的文档中其实是有说明的，不过没有到打包这一步的时候也并不需要进行配置。


当前FMod的Android打包需要对UE4的打包设置进行修改才行，首先，我们需要去GitHub上下载源码版的引擎。


并对UEDeployAndroid.cs进行修改，在CopyPluginLibs函数的末尾，添加如下的代码：





```
Console.WriteLine("Plugin Deployment");

List<string> PluginLibraryReferences = new List<string>();

foreach (PluginInfo Plugin in Plugins.ReadAvailablePlugins(UnrealBuildTool.GetUProjectFile()))

{

    string AndroidDirectory = Path.Combine(Plugin.Directory, "Binaries/Android");

    string DeployFile = Path.Combine(AndroidDirectory, "deploy.txt");

    if (File.Exists(DeployFile))

    {

        Console.WriteLine("Using Plugin Deployment file '{0}'", DeployFile);

        string DestLibraryDirectory = Path.Combine(UE4BuildPath, "libs/armeabi-v7a");

        string DestJarDirectory = Path.Combine(UE4BuildPath, "libs");

        foreach (string Name in File.ReadAllLines(DeployFile))

        {

            Console.WriteLine("Have file entry '{0}'", Name);

            string PluginFileExt = Path.GetExtension(Name);

            if (PluginFileExt == ".so")

            {

                string SourceFile = Path.Combine(AndroidDirectory, Name);

                string DestFile = Path.Combine(DestLibraryDirectory, Name);

                Console.WriteLine("Copying plugin .so file '{0}' to '{1}'", SourceFile, DestFile);

                if (File.Exists(DestFile))

                {

                    File.Delete(DestFile);

                }

                File.Copy(SourceFile, DestFile);

                // Also remember it for GameActivity

                PluginLibraryReferences.Add(Name);

            }

            else if (PluginFileExt == ".jar")

            {

                string SourceFile = Path.Combine(AndroidDirectory, Name);

                string DestFile = Path.Combine(DestJarDirectory, Name);

                Console.WriteLine("Copying plugin .jar file '{0}' to '{1}'", SourceFile, DestFile);

                if (File.Exists(DestFile))

                {

                    File.Delete(DestFile);

                }

                File.Copy(SourceFile, DestFile);

            }

        }

    }

}

// Enter all .so references into GameActivity java file

if (PluginLibraryReferences.Count != 0)

{

    Console.WriteLine("Adding Plugin Deployment library references");

    String GameActivityFileName = Path.Combine(UE4BuildPath, "src/com/epicgames/ue4/GameActivity.java");

    List<string> ActivityContents = new List<string>(File.ReadAllLines(GameActivityFileName));

    int LoadLibraryIndex = -1;

    for (int i = 1; i < ActivityContents.Count; ++i)

    {

        if (ActivityContents<i>.Contains("System.loadLibrary"))

        {

            LoadLibraryIndex = i;

            break;

        }

    }

    if (LoadLibraryIndex != -1)

    {

        // Insert in reverse order

        PluginLibraryReferences.Reverse();

        foreach (string Reference in PluginLibraryReferences)

        {

            Console.WriteLine("Adding library reference {0} at line {1}", Reference, LoadLibraryIndex);

            string ShortName = Path.GetFileNameWithoutExtension(Reference);

            if (ShortName.StartsWith("lib")) // Without the lib prefix

            {

                ShortName = ShortName.Substring(3);

            }

            ActivityContents.Insert(LoadLibraryIndex, String.Format("\t\tSystem.loadLibrary(\"{0}\");", ShortName));

        }

    }

    File.WriteAllLines(GameActivityFileName, ActivityContents.ToArray());

}

// PLUGIN DEPLOYMENT END
```

这样一来就可以正常的进行运行工作了，不过由于使用了源码版，有时候编译时间就会比较长了。所以建议在项目打包的时候再进行设置。



FMod还有一些其他需要注意的打包事项，例如Bank文件目录等的设定，由于没有使用到那些功能所以没有进行尝试，详情可参照[FMod官方文档]。


## 目录访问



当前UE4在Android下默认是没有提供访问整个设备的文件的接口的，但是如果是音乐游戏之类的游戏的话，就会需要用到这样的功能。


在AndroidFile.cpp中，我们可以看到，所有的函数都有提供AllowLocal的参数，但是FAndroidPlatformFile在进行IPhysicalPlatformFile的接口实现时使用的却全部是默认的False。AllowLocal参数最终是传递给PathToAndroidPaths这个函数的，因此，直接在该函数中添加



```
AllowLocal = true;
```

强制打开本地路径访问即可。同时，这个文件中有开放两个在调试文件访问时比较实用的宏，有需要的时候可以打开



```
#define LOG_ANDROID_FILE 1
#define LOG_ANDROID_FILE_MANIFEST 1
```

另外需要注意的是，FPaths提供的一些函数在Android下并不能很好的运行，经常返回不符合预期的结果。


目前观测到的有



> FPaths::ConvertRelativePathToFull需要使用IAndroidPlatformFile::GetPlatformPhysical().FileRootPath进行代替
> 
> 
> FPaths::GetPath会对根目录返回空字符串
> 
> 
> FPaths::IsDrive会对所有的一级目录返回True
> 
> 


使用的时候需要千万注意。


## 功能限制


UE4在移动模式下是有很多功能限制的，如果游戏是面向移动平台的话，最好在添加新功能的时候使用移动平台模拟进行测试，否则到最后就可能真的积重难返了。


目前遇到的限制有：



> APEX的破碎物体无法作用
> 
> 
> 部分粒子特效无法显示
> 
> 


UE4对移动设备的兼容性也是需要在事先进行调查的，官方的说明在[这里](https://docs.unrealengine.com/latest/INT/Platforms/Android/DeviceCompatibility/index.html)。


引擎自带的示例项目在没有安装第三方插件的情况下，是可以直接通过的，用来测试环境的配置是否正确非常方便。官方的TPS示例的打包结果如下：


[![](https://blog.ch-wind.com/wp-content/uploads/2015/12/image_thumb-4.png)](https://blog.ch-wind.com/wp-content/uploads/2015/12/image-4.png)


总体而言UE4的移动端表现还是非常不错的。


