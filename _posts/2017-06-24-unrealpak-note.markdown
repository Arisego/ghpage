---
layout: post
status: publish
published: true
title: UnrealPak的使用笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1790
wordpress_url: http://blog.ch-wind.com/?p=1790
date: '2017-06-24 19:37:17 +0000'
date_gmt: '2017-06-24 11:37:17 +0000'
tags:
- UE4
- UnrealPak
- Pak
---
UE4的打包可以通过编辑器直接进行，但是当要实现一些特殊的目标，例如热更新等时，就需要自己使用UnrealPak进行才行。


当前使用UE4版本4.16，所有打包**仅**在Shiping模式下测试过。


## UnrealPak


UnrealPak在整个打包过程中位于最后面的一个过程，在编辑器中打包的话可以通过输出判断打包的各个阶段。在编译、烘焙之后，如果有勾选Use Pak这个选项的话，引擎就会尝试将以上两个过程中生成的内容打包到Pak中去。


UnrealPak.exe位于引擎目录下Engine/Win64中，运行程序，在错误提示中有给出基本的使用方法：



> UnrealPak <PakFilename> -Test
> 
> 
> UnrealPak <PakFilename> -List
> 
> 
> UnrealPak <PakFilename> -Extract <ExtractDir>
> 
> 
> UnrealPak <PakFilename> -Create=<ResponseFile> [Options]
> 
> 
> UnrealPak <PakFilename> -Dest=<MountPoint>
> 
> 
> UnrealPak GenerateKeys=<KeyFilename>
> 
> 
> UnrealPak GeneratePrimeTable=<KeyFilename> [-TableMax=<N>]
> 
> 
> UnrealPak <PakFilename1> <PakFilename2> -diff
> 
> 
> UnrealPak -TestEncryption
> 
> 
> Options:
> 
> 
> -blocksize=<BlockSize>
> 
> 
> -bitwindow=<BitWindow>
> 
> 
> -compress
> 
> 
> -encrypt
> 
> 
> -order=<OrderingFile>
> 
> 
> -diff (requires 2 filenames first)
> 
> 
> -enginedir (specify engine dir for when using ini encryption configs)
> 
> 
> -projectdir (specify project dir for when using ini encryption configs)
> 
> 
> -encryptionini (specify ini base name to gather encryption settings from)
> 
> 
> -encryptindex (encrypt the pak file index, making it unusable in unrealpak without supplying the key)
> 
> 


整个程序大致的功能就是可以解压和打包Pak文件：


### GenerateKeys


生成加密Key到文件中，RSA用于对Pak进行签名。


P：用于RSA的素数p


Q：用于RSA的素数q


### GeneratePrimeTable


生成素数表，


TableMax：生成表的停止（最大）数值，默认值10000


### TestEncryption


测试加密算法的执行，并不检测具体的Key和文件。


### TEST


对Pak文件进行检测，会对每一个文件进行SHA1校验。


signed：Pak是否已签名


### List


列出文件。


SizeFilter：文件的大小过滤器，会对大于这个大小的文件进行总Size的统计。


signed：Pak是否已签名


### Diff


对比两个Pak文件


nouniques：通过指定nouniquesfile1、nouniquesfile2，是否列出Unique的文件


signed：Pak是否已签名，不能分开指定。


### Extract


解包。


signed：Pak是否已签名


### 构建


blocksize：块大小，MB或KB单位


bitwindow：压缩的窗口大小，这个值越大压缩的效果越好，同时消耗的性能也越高。


patchpaddingalign：是否在进行Patch时启用对齐，不patch时对齐时自动的。


encryptindex：加密索引，使得文件索引在不提供key的情况下无法解密。


order：文件读取顺序列表，这个order在cook时会自动生成，一般不用自己提供。uexp会被加上序列值1 << 29和ubulk会被加上1 << 30。没有提供order的其他文件将获得 (1 << 28)。


sign：对Pak进行签名的RSA的key


 


#### create


文件列表，可在其中单独指定compress和encrypt，但是如果在命令行中指定了的话，就会被强制使用到所有文件。可以是目录或是使用*通配符。


generatepatch：生成Patch |同时可使用 TempFiles来指定临时目录


compress：压缩


encrypt：加密


 


#### dest


替换Pak中的MountPoint。


 


### 加密和压缩


Pak采用RSA进行签名，AES进行加密，SHA1进行校验。


加密的流程没有测试，加密的参数可以在ini文件Encryption中进行设置，要使用ini配置的话，需要指定-encryptionini。或者，可以直接在命令行中提供加密参数：



```
-Sign=filename

```

或者



```
-sign=0x123456789abcdef+0x1234567+0x12345abc
```

其中第一个数是Exponent，第二个数是Module，第三个数是公钥的Exponent



```
-aes=blabla
```

来提供AES加密秘钥。


 


当前的ProjectLauncher打包，会自动添加-encryptionini，但是只要没有提供Encryption.ini，或者[[Ini配置](https://blog.ch-wind.com/ue4-config-usage/#i)]不正确，就不会进行加密。配置文件的内容应该是类似这样的：



```
[Core.Encryption]
SignPak=True
EncryptPak=True
rsa.publicexp=blablabla
rsa.privateexp=blablabla
rsa.modulus=blablabla
aes.key=blablabla
```

由于没有实际测试过，所以不是很明确Encryption的配置能否被打包后的程序自动加载。如果出现了问题，可以检查下CoreDelegate中的：



```
static FPakEncryptionKeyDelegate& GetPakEncryptionKeyDelegate();
static FPakSigningKeysDelegate& GetPakSigningKeysDelegate();
```

引擎在Mount时会从这两个Delegate中获取加密相关的信息，在CoreDelegate的Cpp中有提供



```
void RegisterEncryptionKey(const char* InEncryptionKey)
{
  FCoreDelegates::GetPakEncryptionKeyDelegate().BindLambda([InEncryptionKey]() { return InEncryptionKey; });
}

void RegisterPakSigningKeys(const char* InExponent, const char* InModulus)
{
  static FString Exponent(ANSI_TO_TCHAR(InExponent));
  static FString Modulus(ANSI_TO_TCHAR(InModulus));

FCoreDelegates::GetPakSigningKeysDelegate().BindLambda([](FString& OutExponent, FString& OutModulus)
{
  OutExponent = Exponent;
  OutModulus = Modulus;
});
}
```

如果没有办法成功注册解密的话，可以尝试模仿引擎代码进行注册来调试一下。


 


不过事实上这些功能如果只是打包的话基本不用深究，在使用Project Launcer进行打包时，可以看到编辑器对UnrealPak的调用，将其复制出来，然后进行相应的修改就可以了。


在进行测试的时候需要注意，UE4对于Asset的加载是有要求的，如果是Shiping烘焙的内容，是无法在编辑器中加载的，必须统一内容的打包格式。


## Mount


Pak在运行时通过Mount将内容读取到游戏中，如果不希望Pak文件被自动加载的话，可以不将其放到[[自动加载目录](https://blog.ch-wind.com/ue4-patch-release-dlc/#Maps)]中。


手动加载Pak文件时，通常采用的Mount方法有两种。


### 手动Mount



```
EL_LOG(TEXT("[AShipIssueGameModeBase] LoadPakMount(): %s"), *PakPath);
FString SaveContentDir = PakPath;
UE_LOG(LogTemp, Log, TEXT("[AShipIssueGameModeBase]  ----------- LoadPak: %s --------------"), *SaveContentDir);

//获取当前使用的平台,这里使用的是WIN64平台
IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
//初始化PakPlatformFile
FPakPlatformFile* PakPlatformFile = new FPakPlatformFile();
PakPlatformFile->Initialize(&PlatformFile, TEXT(""));
FPlatformFileManager::Get().SetPlatformFile(*PakPlatformFile);

//获取Pak文件
FPakFile PakFile(&PlatformFile, *SaveContentDir, false);

//设置pak文件的Mount点.
FString MountPoint("../../../[ProjectName]/");
UE_LOG(LogTemp, Log, TEXT("[AShipIssueGameModeBase] - Mount Path: %s"), *MountPoint);
EL_LOG(TEXT("[AShipIssueGameModeBase] Mount Path: %s"), *MountPoint);

PakFile.SetMountPoint(*MountPoint);
//对pak文件mount到前面设定的MountPoint
if (PakPlatformFile->Mount(*SaveContentDir, 0, *MountPoint))
{
  UE_LOG(LogTemp, Log, TEXT("[AShipIssueGameModeBase] - Mount Success"));
  EL_LOG(TEXT("[AShipIssueGameModeBase] Mount Success"));

}
```

这个方法可以手动指定MountPoint，但是通常情况下，除非很确定自己打包了什么，否则很容易丢失各个Asset之间的引用。


### CoreDelegate


这个是最近的版本添加的帮助函数，比上面的方法更加的简单实用。



```
if (FCoreDelegates::OnMountPak.IsBound())
{
  if (FCoreDelegates::OnMountPak.Execute(PakPath, 4, nullptr))
  {
     EL_LOG(TEXT("[AShipIssueGameModeBase] LoadPakDelegate(): OnMountPak.Execute Successful."));
     GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, TEXT("OnMountPak.Execute Successful."));
  }
  else
  {
    EL_LOG(TEXT("[AShipIssueGameModeBase] LoadPakDelegate(): OnMountPak.Execute Falied."));
    GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, TEXT("OnMountPak.Execute Falied."));
  }
}
else
{
  EL_LOG(TEXT("[AShipIssueGameModeBase] LoadPakDelegate(): OnMountPak.IsBound() Falied"));
  GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Red, TEXT("OnMountPak.IsBound() Falied"));
}
```

使用这个方法会将内容Mount到内容根目录，引擎内部加载Pak文件也是使用的这个方法。


## 路径与引用


一般情况下使用同一个项目打包的Pak文件，只要打包正确，进行Mount都不会有什么问题。


而如果使用其他项目进行打包的话，可能会存在一些引用丢失的问题。通常的表现是，使用Mount后的路径可以打开地图，但是地图内物品的材质等关联属性全部都丢失了。


这个问题通常都是路径问题引起的，另外，在Cook目录中会有AssetRegistry，这个文件是UE用来保存各个Asset之间的引用的，在网上有看到Mount时要自己加载并注册的描述，但是目前版本测试下似乎是会自动加载的。至少在没有主动加载AssetRegistry的情况下，引用已经是正常的了，但是如果出现了引用丢失的问题，可以从这个方面进行一下检查。而且使用CoreDelegate进行Mount的话，是不需要关心这个的。


在打包时主要的路径问题来自于打包时的处理机制，UnrealPak会尝试从所有待打包的文件中提取公共的目录作为根目录。而这个根目录之后会被挂在MountPoint之下，那么如果配置有不正确的话，必然会丢失引用。如果引用丢失了的话，对打包的根目录检查也是必要的。在使用-create=<ResponsFile>进行打包时，可以在每个文件列的后面指定打包的目标目录，可以一定程度的上解决这个问题。


### 实际使用


注意：这里记录的是目前项目中使用的路径，并不代表这是一个“好”的方法。因为UnrealPak自主打包无论如何都不会优雅，如果没有紧急的打包需求，建议等官方的Chunk机制等一系列打包功能完善之后直接使用~


首先，对目标项目ShipIssue进行打包，从Log中拷贝UnrealPak的记录：



```
D:\Code\UE_4.16\Engine\Binaries\Win64\UnrealPak.exe F:\Ue_Patch\1.0_nomap\WindowsNoEditor\ShipIssue\Content\Paks\ShipIssue-WindowsNoEditor.pak -create="C:\Users\Administrator\AppData\Roaming\Unreal Engine\AutomationTool\Logs\D+Code+UE_4.16\PakList_ShipIssue-WindowsNoEditor.txt" -encryptionini -enginedir="D:\Code\UE_4.16\Engine" -projectdir="E:\GameDev\ShipIssue" -platform=Windows -abslog="C:\Users\Administrator\AppData\Roaming\Unreal Engine\AutomationTool\Logs\D+Code+UE_4.16\PakLog_ShipIssue-WindowsNoEditor.log" -installed -order=E:\GameDev\ShipIssue\Build\WindowsNoEditor\FileOpenOrder\CookerOpenOrder.log -UTF8Output -multiprocess -patchpaddingalign=2048
```

然后，将要打包的项目FreePatch进行Cook之后，对拷贝的命令修改：



```
D:\Code\UE_4.16\Engine\Binaries\Win64\UnrealPak.exe F:\Ue_Patch\1.0_nomap\WindowsNoEditor\ShipIssue\Content\Paks\Free.pak -create="E:\PakScript\list.txt" -encryptionini -enginedir="D:\Code\UE_4.16\Engine" -projectdir="E:\GameDev\ShipIssue" -platform=Windows -abslog="C:\Users\Administrator\AppData\Roaming\Unreal Engine\AutomationTool\Logs\D+Code+UE_4.16\PakLog_ShipIssue-WindowsNoEditor.log" -installed -order=E:\GameDev\FreePatch\Build\WindowsNoEditor\FileOpenOrder\CookerOpenOrder.log -UTF8Output -multiprocess -patchpaddingalign=2048
```

Order指令的文件可以直接使用Cook出来的，list.txt直接写：



```
"E:\GameDev\FreePatch\Saved\Cooked\WindowsNoEditor\FreePatch\*" "../../../ShipIssue/*" –compress
```

目标目录写成目标项目的目录，这样的话打包出来的pak文件在自动加载和使用CoreDelegate加载后都能保持正确的引用。


如果保留原项目名



```
"E:\GameDev\FreePatch\Saved\Cooked\WindowsNoEditor\FreePatch\*" "../../../FreePatch/*" –compress
```

需要Mount时自己将MountPoint指定到../../../ShipIssue/，自动加载和CoreDelegate加载会加载到../../../FreePatch/导致无法读取到地图中物体引用的材质。


因此并不推荐这样做~


通常情况下，只要mount之后的路径在/ShipIssue/下的结构与原本在Content/下的结构相同，材质之类的引用就不会丢失。丢失的情况，一般从路径方面检查下先比较好。



更新：由于Pak的加载确实有些迷，经常会有朋友发邮件或者留言来问我。但是从打包到加载的过程中的可变量太多，我也无法准确的知道每个人遇到的问题。所以在这里将测试打包用到的代码分离成一个插件。


其实插件本身并不复杂，只是在使用UFS的API遍历访问而已。主要的作用是可以方便对加载过程的理解和问题的排查。详情请参考[[UE4文件查看插件](https://blog.ch-wind.com/ue4-pak-file-view/)]。



