---
layout: post
status: publish
published: true
title: UWidget封装SWidget到UMG
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1457
wordpress_url: http://blog.ch-wind.com/?p=1457
date: '2015-09-11 19:11:13 +0000'
date_gmt: '2015-09-11 11:11:13 +0000'
tags:
- UE4
- UMG
- Slate
---
为了使用UMG中的一些高级或便利特性，需要将制作好的Slate控件封装到UWidget中去。  

当前UE4版本4.8.3。


将Slate封装到UMG中去有很多的好处，因为在代码中对需要重用的控件进行不断的重新布局是一件非常繁琐的事情。同时，UMG也有在3D空间中进行显示这样的高级功能。


由于UMG本身就是对Slate的封装，所以这个过程可以参照UE4的源代码进行研究。


这里所做的是尝试对上一回所做的文件目录树进行封装。


直接上代码


CListViewWidget.h



```
#pragma once
#include "CListViewWidget.generated.h"
UCLASS()
class TEST_MP_API UCListViewWidget : public UWidget
{
  GENERATED_UCLASS_BODY()
public:

#if WITH_EDITOR
  // UWidget interface
  virtual const FSlateBrush* GetEditorIcon() override;
  virtual const FText GetPaletteCategory() override;
  virtual void OnCreationFromPalette() override;
  // End UWidget interface
#endif

protected:
  // UWidget interface
  virtual TSharedRef<SWidget> RebuildWidget() override;
  virtual void OnBindingChanged(const FName& Property) override;
  // End of UWidget interface

protected:
  TSharedPtr<class SDDFileTree> MyFileTree;
};
```

封装类直接继承自UWidget即可，剩下的就是对UWidget中的函数进行实现。


CListViewWidget.cpp



```
#include "Test_mp.h"
#include "SDDFileTree.h"
#include "CListViewWidget.h"

/** GENERATED_UCLASS_BODY() */
UCListViewWidget::UCListViewWidget(const FObjectInitializer& ObjectInitializer)
: Super(ObjectInitializer)
{
  bIsVariable = false;
}

/** <编辑器属性 */
#if WITH_EDITOR

// <图标
const FSlateBrush* UCListViewWidget::GetEditorIcon()
{
  return FUMGStyle::Get().GetBrush("Widget.TextBlock");
}

// <分类目录
const FText UCListViewWidget::GetPaletteCategory()
{
  return NSLOCTEXT("Testmp", "Custom", "Ch_Custom");
}

// <创建时的默认值
void UCListViewWidget::OnCreationFromPalette()
{
;
}

#endif

TSharedRef<SWidget> UCListViewWidget::RebuildWidget()
{
  MyFileTree = SNew(SDDFileTree).OwnerHUD(nullptr);

  return MyFileTree.ToSharedRef();
}

void UCListViewWidget::OnBindingChanged(const FName& Property)
{
  Super::OnBindingChanged(Property);

  if (MyFileTree.IsValid())
  {
    ;
  }
}
```

在所有的函数中，RebuildWidget()是最重要的。


参看UWidget的源代码可以发现，所有对被封装的SWidget的引用都是通过这个函数获得的，因此在这里面写上SWidget对应的构造生成就可以了。


OnBindingChanged函数是用于属性代理通知的，这里是简单的封装，没有提供属性代理，因此直接return也是可以的。


在WITH_EDITOR宏中的是编辑器属性，用于封装后的UWidget在蓝图编辑器中显示。具体每一个函数的含义已经在注释中了。


将上面的代码编译通过之后，就可以在UMG的编辑器中看到我们添加的控件了：


将CListViewWidget拖动到控件蓝图上，并在HUD中展示此控件蓝图，就能在项目中与其他UMG控件一样使用了：


这样以来Slate的使用就会变得方便很多。


