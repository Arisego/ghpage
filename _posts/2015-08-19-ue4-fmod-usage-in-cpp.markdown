---
layout: post
status: publish
published: true
title: UE4中C++模式FMod的使用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1516
wordpress_url: http://blog.ch-wind.com/?p=1516
date: '2015-08-19 07:48:29 +0000'
date_gmt: '2015-08-18 23:48:29 +0000'
tags:
- c++
- UE4
- FMod
---
FMod在为UE4提供音效便利的同时，有提供底层的API来方便更加详尽的需求。


当前UE4版本4.9.2；FMod版本1.07.00。


目前版本下对FMod的使用和之前进行UE4与FMod音乐可视化验证的时候并没有什么不同，这里主要是总结下使用中遇到的问题。


## 编码问题


编码问题主要出在中文路径的处理上，UE4内部使用的是UTF-16编码。


因此，将通过Save&Load之类保存起来的路径提供给FMod使用的时候，需要对字符编码进行转换。



```
// 传入参数：const FString& FileFullPath

std::stringstream dts;
dts << TCHAR_TO_UTF8(*FileFullPath);
result = system->createStream(dts.str().c_str(), FMOD_LOOP_NORMAL | FMOD_2D, 0, &sound);
```

关于字符编码，在使用Tag系统的时候还是会遇到。



```
int NumTags;
result = sound_to_analyse->getNumTags(&NumTags, NULL);
if (result != FMOD_RESULT::FMOD_OK) break;
if (NumTags <= 0) break;
FMOD_TAG MusicTag;
for (int mTag = 0; mTag < NumTags; ++mTag){ sound_to_analyse->getTag(NULL, mTag, &MusicTag);
std::stringstream ts;
ts << "Tag:";
ts << MusicTag.name;
ts << " Type:";
ts << MusicTag.type;
ts << " Data:";
ts << std::string((char*)MusicTag.data);
ts << " DataLength:";
ts << MusicTag.datalen;
ts << "\n"; OutputDebugStringA(ts.str().c_str()); } result = sound_to_analyse->getTag("TITLE", 0, &MusicTag);
```

这里目前似乎是有BUG存在的，通过getTag对音乐的标签进行读取时，如果标签是非英文字符的话，读取出来的字符编码无法被正常的解析。并不是读写方式的问题，通过断点直接查看内存的话会看到其中的编码不符合文档中所描述的编码格式。


因此建议音乐的预览图片使用FMod来读取APIC的tag，而其他的tag使用别的库进行读取，例如使用TagLib。


## APIC图片读取


音乐文件的预览图片信息一般存储于APIC标签中，要将读取出的图片数据展示到界面上。可以借助ImageWrapper和SImage来实现。



```
// 变量定义
TSharedPtr ImageTitle;
IImageWrapperPtr ImageWrapper;
UTexture2D* mImageHolder;
FSlateDynamicImageBrush* mSlateDyn;
// 实际读取
result = sound_to_analyse->getTag("APIC", 0, &MusicTag);
if (result != FMOD_RESULT::FMOD_OK) break;
TArray RawFloatImgData;
RawFloatImgData.AddUninitialized(MusicTag.datalen);
FMemory::Memcpy(RawFloatImgData.GetData(), MusicTag.data, MusicTag.datalen*sizeof(uint8));
EImageFormat::Type MusicFormat = EImageFormat::PNG;
char tc = RawFloatImgData[1];
if (tc == 'i'){
tc = RawFloatImgData[7];
switch (tc)
{
case 'j':
case 'J':
MusicFormat = EImageFormat::JPEG;
break;
case 'b':
case 'B':
MusicFormat = EImageFormat::BMP;
break;
default:
break;
}
}
IImageWrapperModule& ImageWrapperModule = FModuleManager::LoadModuleChecked(FName("ImageWrapper"));
ImageWrapper = ImageWrapperModule.CreateImageWrapper(MusicFormat);
if (!ImageWrapper.IsValid()) break;
if (!ImageWrapper->SetCompressed(RawFloatImgData.GetData(), RawFloatImgData.Num())) break;
OutputDebugStringA("APIC Read Success\n");
const TArray* UncompressedBGRA = NULL;
if (!ImageWrapper->GetRaw(ERGBFormat::BGRA, 8, UncompressedBGRA)) break;
OutputDebugStringA("APIC UTexture2D OK\n");
mImageHolder = UTexture2D::CreateTransient(ImageWrapper->GetWidth(), ImageWrapper->GetHeight(), PF_B8G8R8A8);
void* TextureData = mImageHolder->PlatformData->Mips[0].BulkData.Lock(LOCK_READ_WRITE);
FMemory::Memcpy(TextureData, UncompressedBGRA->GetData(), UncompressedBGRA->Num());
mImageHolder->PlatformData->Mips[0].BulkData.Unlock();
mImageHolder->UpdateResource();
mSlateDyn = new FSlateDynamicImageBrush(mImageHolder, FVector2D(ImageWrapper->GetWidth(), ImageWrapper->GetHeight()), FName("tabActiveImage"));
ImageTitle->SetImage(mSlateDyn);
```

由于部分的变量的初始化没有复制过来，代码仅作交流用。


## 播放回调


如果有需要对音乐播放的状态进行追踪，例如在音乐播放完成后进入积分画面的话。使用FMod提供的回调系统是一个不错的解决方案。



```
channel->setMode(FMOD_LOOP_OFF);
if (result != FMOD_RESULT::FMOD_OK) break;
result = channel->setCallback(FModHolders::EndCallBack);
if (result != FMOD_RESULT::FMOD_OK) break;
```

由于设置回调时并没有指定回调类型，故而在回调函数内部对事件进行过滤



```
FMOD_RESULT FModHolders::EndCallBack(FMOD_CHANNELCONTROL *chanControl, FMOD_CHANNELCONTROL_TYPE controlType, FMOD_CHANNELCONTROL_CALLBACK_TYPE callbackType, void *commandData1, void *commandData2)
{
if (controlType == FMOD_CHANNELCONTROL_TYPE::FMOD_CHANNELCONTROL_CHANNEL){
if (callbackType == FMOD_CHANNELCONTROL_CALLBACK_TYPE::FMOD_CHANNELCONTROL_CALLBACK_END){
// 处理代码
```

这里需要注意的是，回调函数本身的声明必须要是Static的。



```
static FMOD_RESULT F_CALLBACK EndCallBack(FMOD_CHANNELCONTROL *chanControl, FMOD_CHANNELCONTROL_TYPE controlType, FMOD_CHANNELCONTROL_CALLBACK_TYPE callbackType, void *commandData1, void *commandData2);
```

