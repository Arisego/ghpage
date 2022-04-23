---
layout: post
status: publish
published: true
title: UE4补丁与DLC
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1646
wordpress_url: http://blog.ch-wind.com/?p=1646
date: '2017-05-01 18:32:13 +0000'
date_gmt: '2017-05-01 10:32:13 +0000'
tags:
- UE4
- Release
- Patch
- DLC
- UnrealPak
---
UE4的打包操作本身还是比较简单的，但是考虑到发布之后的升级与补丁，却还是有一些麻烦。


当前UE4版本为4.16 P1。


在动手做东西之前，先了解一下UE4本身对于打包系统的架构是很重要的，否则如果到了Release的阶段发现代码设计上很多地方与系统有冲突的话就会很麻烦。就像是等到开始做联网版本的游戏时才发现很多机制、功能的设计都与UE4的Replication架构不符的话就会需要大幅度的代码变更。


## Unreal Frontend


虚幻的打包操作在[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Deployment/index.html)]中有进行描述，一切打包相关的工作，都以Unreal Frontend为核心进行。当然，Unreal Frontend还提供了部署、自动化测试等功能。


总体而言，Unreal Frontend的功能还不成熟，很多选项的设定让人费解，也没有提供足够的文档说明，所以可能会遇到一些奇怪的BUG。最麻烦的是，到目前为止，DLC系统依然处于WIP状态，使用起来有很多的不便。


目前主要会使用到的是Project Launcher模块，在下方的Custom Lanch Profiles区域的右边有加号按钮，可以在那里添加自定义的打包配置。配置大致分为以下区域：


**Project**


选择打包操作的目标项目，由于Unreal Frontend的设置是全局的，所以在一个项目中配置了之后在其他项目中也可以使用。


**Build**


选择是否构建，以及构建的模式，并提供了是否构建UAT（Unreal Automation Tool）的选项。UAT主要提供一些自动化测试方面的功能，根据社区一些用户的反馈来看，需要源码版本引擎才能正常的使用。


**Cook**


烘焙相关选项，一般都是用By the book选项然后勾选相关目标平台。


进行Release/Patch/DLC打包的操作都在By the book选项下。其他的一些详细的可选项功能可以参考[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Deployment/Cooking/index.html)]。


**Package**


是否打包以及如何打包，这里需要注意的是当前版本下对DLC进行打包是会出现BUG的，报错如下：



> Program.Main: ERROR: AutomationTool terminated with exception: System.Exception: Couldn't update resource
> 
> 


搜索之后发现似乎是一个[[BUG](https://issues.unrealengine.com/issue/UE-42880)]，因此目前对DLC可以不需要打包，而是自己将生成的文件进行拷贝就可以了。


打包的生成目录在Saved\StagedBuilds\中。


**Archive**


归档，引擎会在打包后将打包好的内容拷贝到指定的目录去。不使用的话不要勾选就可以了。


**Deploy**


部署，提供了几种部署渠道，可以部署到目前可用的设备上。不使用的话可以直接选中Not Deploy。


**Launch**


测试运行的形式，可以对服务端模式、语言环境、初始地图等进行设置。


## 打包模式


打包模式目前有Release、Patch、DLC三种，其中DLC处于WIP状态，并没有足够的文档支持，而且今后可能会有不少变动。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image.png)


### Release Version


UE4提供的Release的概念是通常的发行版本控制，勾选Create a release version of the game for distribution就可以开启了。而Patch与DLC都是以某个Release版本为基础进行打包的。


因此使用Release打包的时候就必须填Name of the new release to create，而Path与DLC则必须填写Release version this is based on。


DLC是不可以选中Create a release version这个选项的，会报错：



> Program.Main: ERROR: AutomationTool terminated with exception: AutomationTool.AutomationException: Can't create a release version at the same time as creating dlc.
> 
> 


而选中了这个选项还填写based on version的话也会报错：



> Program.Main: ERROR: AutomationTool terminated with exception: AutomationTool.AutomationException: Only staged builds can be paked, use -stage or -skipstage.
> 
> 


这个错误也会出现在使用Iterative cooking选项时，如果使用这个选项同时又勾选使用Pak的话，根据当前烘焙缓存的状况不同，也会报这个错。


### Generate patch


生成补丁，目前一个Release下只能有一个补丁，对于生成的pak文件，补丁中带后缀_P，会被优先加载并覆盖。同样的pak文件，多加一个_P的话优先级就会更高。


在Mount函数中，可以看到



```
if ( PakFilename.EndsWith(TEXT("_P.pak")) )
{
  PakOrder += 100;
}
```

凡是以_P结尾的pak文件，会获得额外的100优先级。在进行Patch打包时，引擎也会自动的加上这个后缀。


这里有一个问题，如果勾选了Store all content in a single file的情况下，即便是在不同的Release版本之间，_P的patch也会被优先加载。还没有测试过如果去除了Save package without versions选项是否会有这样的现象。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-1.png)


### Iterative cooking


增量烘焙必须去掉勾选Save package without versions，否则launch按钮会变成灰色，提示：



> unversioned build cannot be incremental
> 
> 


这里面的Iterative cooking目前只能在同一个Release版本中进行增量烘焙，如果Releasse的版本迁移了的话，是不能在版本之间进行增量烘焙的，强行勾选会被拒绝操作：



> Program.Main: ERROR: AutomationTool terminated with exception: AutomationTool.AutomationException: Can't use iterative cooking / deploy on dlc or patching or creating a release
> 
> 


官方的说明是这样的：



> The asset registry and pak file will be needed for any future patches or DLC to check against.
> 
> 


也就是说保存的content注册关系是为了DLC和patch而存在的，并没有说可以作为Release之间的版本迁移的依据。


使用Iterative cooking时还有一点需要注意，那就是引擎当前无法区分Ship和DevelopMent之间的烘焙结果，如果切换Build模式时没有去掉这个选项的话，就会导致烘焙资源的混杂，出现类似如下错误：



> Assertion failed: GDefaultMaterials[Domain] != NULL [File:D:\Build\++UE4+Release-4.16+Compile\Sync\Engine\Source\Runtime\Engine\Private\Materials\Material.cpp] [Line: 429]  
> 
> Cannot load default material 'engine-ini:/Script/Engine.Engine.DefaultMaterialName'
> 
> 


另外，使用增量会导致不在当前选择的地图内容也会被Build进来，但是无论如何，项目设定中的默认地图都是会别build进来的。


### Build DLC


UE4中的DLC是以Plugin的形式进行实现的，DLC Name那里填写的就是插件的名称，是不能随便乱填的。


插件的话在Plugins窗口直接新建就可以了，如果是蓝图项目的话，只会有一个Content Plugin，选择他就可以了。另外，似乎在打包时如果有地图存在的话，没有被地图引用的资源就不会被打包，需要注意。


打包DLC中如果出现



> Cook: LogInit:Display: LogCook:Error: Engine or Game content ../../../Engine/Content/Tutorial/Foliage/Foliage_Intro_Tutorial.uasset is being referenced by DLC!
> 
> 
> Cook: LogInit:Display: LogCook:Error: Engine or Game content ../../../Engine/Content/Tutorial/SubEditors/DestructibleMeshEditorTutorial.uasset is being referenced by DLC!
> 
> 


之类的BUG，可以尝试勾选Include engine content。


关于DLC，一些旧的资料中会提到Plugin形式无法被引擎自动加载，目前测试过已经没有这个现象了。即便是在Release之后添加的Plugin，在做DLC的打包之后，直接扔到项目目录中也会被自动加载。不知是否是因为使用DevelopMent打包的关系。


由于当前Package DLC不知为何会报错，类似这样



> UATHelper: Packaging (Windows (64-bit)): Program.Main: ERROR: AutomationTool terminated with exception: System.Exception: Couldn't update resource
> 
> 


其实Pak已经打包成功了，直接Achive即可。


[![msohtmlclipclip_image001[4]](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0014_thumb.png "msohtmlclipclip_image001[4]")](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0014.png)


将生成的内容直接复制到打包程序里面，就会被自动加载了，即便Release打包的时候并没有这个DLC的Plugin也是可以的。


## 补丁形式


官方在Patch的文档中有提到补丁的覆盖优先，由于Patch是从Release的版本开始进行差分的，如果两个Patch都是针对整个游戏的话，那么前一个Patch就没有意义了，可以删除。


这样一来，为了防止每次更新的内容过大，我们就必须对项目的组织进行设计，目前我们可以通过Maps或者Chunks来做内容差分管理。


### Maps


在进行打包时，被打包地图及其所引用的资源有改变的都会被打包，只是是否会被游戏采用取决于Pak的加载优先级。


而不被选中的地图中，即便相关资源有变动，也不会被打包到Patch中去，但是DefaultMap始终都会被打包。


各个地图打包之后除了DefaultMap之外都是独立的，无论命名成什么都会被自动加载，而_P的优先级会被应用到整个Pak文件上。


而目前，只要在扫描目录里面的pak文件，都会被自动加载。从FPakPlatformFile::Initialize的调用中看到，除了在SHIPPING模式下提供的命令行外，有如下的目录会被添加到扫描中：



> OutPakFolders.Add(FString::Printf(TEXT("%sPaks/"), *FPaths::GameContentDir()));
> 
> 
> OutPakFolders.Add(FString::Printf(TEXT("%sPaks/"), *FPaths::GameSavedDir()));
> 
> 
> OutPakFolders.Add(FString::Printf(TEXT("%sPaks/"), *FPaths::EngineContentDir()));
> 
> 


也就是说，可以在一开始打包时，只选中Default地图，之后其他的地图可以每个或每组地图单独选中，然后打包成Patch改成地图名称的形式添加到游戏中去。


这样一来，就可以很方便的添加后续的地图内容到发布版本中去了，只是多少还需要维护一个文件列表。


总体而言，使用一个空地图作为程序本体，将通用的逻辑、材质放到其中，其他地图大致保持各自独立。这样每次就可以对对应的模块进行更新替换就行了。


### Chunks


Chunks这个功能可以在编辑器中指定内容将会被打包到哪一个Patch中去，但是这个功能必须在编辑器设定中Genera>Experiment中打开：


[![msohtmlclipclip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image001_thumb.png "msohtmlclipclip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image001.png)


打开选项之后，就可以在内容管理器的右键菜单中看到：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-6.png)


Chunk相关的选项了。对不同的资源设定了Chunk之后就可以在打包时选中这个功能，打包之后就会有不同的分包了。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-7.png)


Chunk功能必须在Pak开启时使用，因为不Pak打包的话，原本的项目文件就已经足够Chunk了。


另外，如果要使用Http chunk install功能的话，不要将Default Map放到Chunk中去，否则由于本地不会保留那些Chunk，程序将会由于没有Default Map而无法开启。


如果对在Patch的时候也使用chunk的话，将会对不同的chunk包生成Patch，但是即使该chunk包的内容没有改变，也依然会生成一个1K的Dammy。


不过这其中最大的限制是，对chunk进行patch时只能针对Release时在AssetRegistry注册过的地图，如果添加没有注册过的地图则无法打包成功。



> Program.Main: ERROR: AutomationTool terminated with exception: AutomationTool.CommandUtils+CommandFailedException: Command failed (Result:3): D:\Code\UE_4.16\Engine\Binaries\Win64\UnrealPak.exe F:\Ue_Patch\1.0_nomap\WindowsNoEditor\P001\Content\Paks\P001-WindowsNoEditor_P.pak -create="C:\Users\Admin\AppData\Roaming\Unreal Engine\AutomationTool\Logs\D+Code+UE_4.16\PakList_P001-WindowsNoEditor_P.txt" -encryptionini -enginedir="D:\Code\UE_4.16\Engine" -projectdir="E:\Ues\P001" -platform=Windows -abslog="C:\Users\Admin\AppData\Roaming\Unreal Engine\AutomationTool\Logs\D+Code+UE_4.16\PakLog_P001-WindowsNoEditor_P.log" -installed -order=E:\Ues\P001\Build\WindowsNoEditor\FileOpenOrder\CookerOpenOrder.log -UTF8Output -generatepatch=E:\Ues\P001\Releases\5.0\WindowsNoEditor\P001-WindowsNoEditor.pak -tempfiles=D:\Code\UE_4.16\TempFiles -multiprocess -patchpaddingalign=2048. See logfile for details: 'UnrealPak-2017.05.07-11.00.34.txt'
> 
> 


会出现类似这样的错误。


### Http Chunks Install


在使用Chunk的基础上，还可以进一步的使用Http Chunks Install功能，这个功能通常被用于移动端的碎片化安装功能


[![msohtmlclipclip_image001[6]](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0016_thumb.png "msohtmlclipclip_image001[6]")](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0016.png)


不过在桌面端也可以进行使用。其实实现中并没有支持断点续传，不过事实上，分块下载本身就在一定程度上充当了断点续传的功能。


使用起来也比较简单，直接勾选并填写输出路径、版本名称之类的就可以了。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-13.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-13.png)


不过要注意确保其输出目录是确实存在的，和其他的目录设定不同，这里是会进行写入检测的。


另外，在Chunk Version Name里面输入之后记得敲回车才能确认输入。这里的输入框功能有点奇怪，直接填完之后点别的地方不会确认输入，会直接清空。


如果是移动端打包的话，无需添加配置文件，直接点击添加按钮盘的下拉三角即可：


[![msohtmlclipclip_image001[1]](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0011_thumb.png "msohtmlclipclip_image001[1]")](https://blog.ch-wind.com/wp-content/uploads/2017/05/msohtmlclipclip_image0011.png)


打包成功的话会在输出目录输出类似这样的内容：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-8.png)


Http chunk install的功能也是以一个chunk为目标进行的，只是每个chunk会被分成更小的块，方便传输。也就是说，要使用这个功能，还是需要有一个自行设计的文件列表来进行版本管理的。


要进行碎片安装，直接对某个文件执行Request Content：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-9.png)


这里面填写的URL对应的就是上面生成的那些内容，需要自行部署到服务器上。


如果Success的话，会返回一个Mobile Pending Content的引用，继续


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-10.png)


如果成功的话就可以对这个引用进行Mount了


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/05/image_thumb-11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/05/image-11.png)


这样就可以使用这个包的内容了，这套函数本身会检测本地有没有pak文件，有的话就不会进行下载了。


上面填写的Install Directory在windows下是以项目内容目录下的PersistentDownloadDir为基础的，所以填写../Content/Paks/的话就可以到达自动加载目录，下次游戏运行时包中的内容就可以直接使用了。不过要留意的是，如果被自动加载了的话，那个文件就无法被直接替换掉了。


## 总结


由于UE4并未提供Release版本之间的增量功能，要实现地图下载之类的功能的话，可以使用DLC或者分Map打包。如果现在的打包实在无法满足需求的话，也可以选择自己用UnreakPack进行打包并自行进行Mount管理来进行补正，有这个需求的话可能会遇到FPackageName::RegisterMountPoint之类函数的使用。不过相信打包功能在之后的版本更新中会有所增强，如果不是有紧急的打包需求的话，不建议跳这个坑。


