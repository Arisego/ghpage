---
layout: post
status: publish
published: true
title: Hello Slate
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1472
wordpress_url: http://blog.ch-wind.com/?p=1472
date: '2015-08-18 19:56:34 +0000'
date_gmt: '2015-08-18 11:56:34 +0000'
tags:
- UE4
- Slate
---
UE4中通常的游戏内逻辑使用UMG就可以了，当需要一些独特的功能时就会需要用到Slate。


当前UE4版本4.8.3。


Slate是UE4的用户界面系统，UE4编辑器的大部分界面都是由Slate构建的。同时，在编辑器中使用的UMG也是在Slate的基础上封装的。


本文参照官方社区文档[Slate, Hello](https://wiki.unrealengine.com/Slate,_Hello)完成。


## 准备工作


要使用Slate，第一步是将其API开放到项目。在项目对应的Build.cs中将下面的代码的注释去掉即可



```
// Uncomment if you are using Slate UI

PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });
```

根据UE4版本的不同如果没有这行的直接加上就好了。


## SlateWidget


创建用于显示文字的Slate控件。


Slate控件的一些特殊的宏和界面定义方式的详情可以参考官方的[Slate概述](https://docs.unrealengine.com/latest/CHN/Programming/Slate/Overview/index.html)。


StandardSlateWidget.h



```
#pragma once
#include "Test_mp.h" /* <项目头文件 */

class SStandardSlateWidget: public SCompoundWidget
{
SLATE_BEGIN_ARGS(SStandardSlateWidget){}

/*<参照下面的OwnerHUD的声明 */
SLATE_ARGUMENT(TWeakObjectPtr<class AHUD>,OwnerHUD)


SLATE_END_ARGS()

public:
////////////////////////////////////////////////////////////////////////////////////////////////////
/////<每一个控件都必须要有这个函数
/////<构建控件及其子控件
void Construct(const FArguments& InArgs);
private:
////////////////////////////////////////////////////////////////////////////////////////////////////
/////<指向控件的持有者Hud
/////<使用弱引用持有HUD的指针，因为HUD是使用强引用来持有Widget的。
/////<如果双方都为强引用的话将会导致解构时形成循环引用并引发内存泄露
TWeakObjectPtr<class AHUD> OwnerHUD;

};
```

StandardSlateWidget.cpp



```
#include "Test_mp.h"
#include "Plugin/StandardSlateWidget.h"
 
void SStandardSlateWidget::Construct(const FArguments& InArgs)
{
    OwnerHUD = InArgs._OwnerHUD;
 
    ChildSlot
        .VAlign(VAlign_Fill)
        .HAlign(HAlign_Fill)
        [
            SNew(SOverlay)
            + SOverlay::Slot()
            .VAlign(VAlign_Top)
            .HAlign(HAlign_Center)
             [
                 SNew(STextBlock)
                 .ShadowColorAndOpacity(FLinearColor::Black)
                 .ColorAndOpacity(FLinearColor::Red)
                 .ShadowOffset(FIntPoint(-5, 5))
                 .Font(FSlateFontInfo("Veranda", 24))
                 .Text(FText::FromString("Hello, Slate!"))
             ]
        ];
 
}
```

在这里使用OwnerHUD并不是必须的，主要的作用是作为参数传递的示范。


## HUD


通过自定义一个HUD用于Slate控件的展示。添加HUD代码没有什么特殊的地方。


添加好之后直接在BeginPlay中将Widget输出到屏幕即可。


StandardHud.h



```
#pragma once
#include "GameFramework/HUD.h"
#include "StandardHUD.generated.h"
 
class SStandardSlateWidget;
 
UCLASS()
class AStandardHUD : public AHUD
{
    GENERATED_BODY()
 
public:
    AStandardHUD();
    TSharedPtr<SStandardSlateWidget> myUIWidget;
 
    void BeginPlay();
};

```

StandardHud.cpp



```
#pragma once
 // Fill out your copyright notice in the Description page of Project Settings.   
 #include "Test_mp.h" 
 #include "Plugin/StandardSlateWidget.h" 
 #include "Plugin/StandardHUD.h"   
 
AStandardHUD::AStandardHUD() 
{   

}

void AStandardHUD::BeginPlay() 
{     
    SAssignNew(myUIWidget, SStandardSlateWidget).OwnerHUD(this);       
    if (GEngine->IsValidLowLevel())     
    {         
        GEngine->GameViewport->AddViewportWidgetContent(SNew(SWeakWidget).PossiblyNullContent(myUIWidget.ToSharedRef()));     
    }       
    if (myUIWidget.IsValid())     
    {         
        myUIWidget->SetVisibility(EVisibility::Visible);     
    } 
}

```

## 最终结果


原始的教程中还有自定义GameMode的部分，在这里就不执行了。直接在编辑器中将HUD指定为刚刚定义的StandardHud即可。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/08/image_thumb4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/08/image4.png)


点击运行即可在屏幕上方看到“Hello, Slate!”的文字输出了。


