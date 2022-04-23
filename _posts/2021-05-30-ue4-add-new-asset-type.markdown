---
layout: post
status: publish
published: true
title: UE4新增Asset类型
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 3508
wordpress_url: https://blog.ch-wind.com/?p=3508
date: '2021-05-30 21:15:20 +0000'
date_gmt: '2021-05-30 13:15:20 +0000'
tags:
- UE4
---
想要在编辑器里面添加新的Asset类型，算是比较常见又不是经常使用的需求。


当前UE4版本为4.26.2。


虽然本身并不复杂，但是每次添加的时候如果项目中没有相关的代码，就又要去查一次。不然总是会在一些奇怪的地方卡住导致在编辑器中无法使用的情况。因此在这里记录一下，方便下次查找。


## UFactory继承


首先需要继承UFactory，直接用UE4添加类，或者自己写即可。


覆盖掉下面的函数：



```
virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn) override;
virtual bool ShouldShowInNewMenu() const override;
```

ShouldShowInNewMenu直接返回True则可用在编辑器的右键新建的菜单中出现。


FactoryCreateNew则直接新建一个对应类型的Object即可：



```
return NewObject<UMyObjectType>(InParent, InClass, InName, Flags);
```

同时需要在构造函数中初始化一些设置



```

SupportedClass = UMyObjectType::StaticClass();
bCreateNew = true;
bEditAfterNew = true;

```

如果遇到了一些奇怪的链接问题，可以先检查下是否在模块的build.cs中包含了UnrealEd。



```
PrivateDependencyModuleNames.AddRange(
  new string[]
  {
    "CoreUObject",
    "Engine",
    "UnrealEd",
  }
);

```

## AssetTypeActions


之前的版本有上面的操作就可以了，但是目前4.26的版本需要额外的操作才能在编辑器中看到新建按钮。


定义一个新的类继承自`FAssetTypeActions_Base`，一个比较好的参考是`FAssetTypeActions_DataAsset`。



```
class FAssetTypeActions_DataAsset : public FAssetTypeActions_Base
{
public:
  // IAssetTypeActions Implementation
  virtual FText GetName() const override { return NSLOCTEXT("AssetTypeActions", "AssetTypeActions_DataAsset", "Data Asset"); }
  virtual FColor GetTypeColor() const override { return FColor(201, 29, 85); }
  virtual UClass* GetSupportedClass() const override { return UDataAsset::StaticClass(); }
  virtual uint32 GetCategories() override { return EAssetTypeCategories::Misc; }
};
```

无需额外的定义，之后在Module的Start的地方进行注册即可



```
void FAwesomeEdModule::StartupModule()
{
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    AssetTools.RegisterAssetTypeActions(MakeShareable(new FAwesomeAssetAction));
}
```

其中FAwesomeAssetAction就是新定义的AssetTypeAction。


## 总结


由于这种功能一般加一次就会不管了，下一次在别的地方要用到的时候才发现API已经变了。由于本身操作不是很熟悉，很难把握是自己操作有误还是其他因素引起的。


总之这边记录的是当前版本的可行操作，之后的版本不行的话就可以判断可能是API有改变。


