---
layout: post
status: publish
published: true
title: Slate中图标的使用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1524
wordpress_url: http://blog.ch-wind.com/?p=1524
date: '2015-08-18 12:53:15 +0000'
date_gmt: '2015-08-18 04:53:15 +0000'
tags:
- UE4
- Slate
- Icon
---
在Slate控件中，图标的使用除了直接引用图片外，还是有一些其他便利的方法的。


当前UE4版本4.8.3。


目前官方的版本已经到4.9.0了，但是由于FMod并没有更新对应版本的插件，项目无法迁移，故而依然使用4.8.3版本。


## 自带图标


UE4自带的图标在对SWidget进行封装时比较容易遇到。UWidget在编辑器中的显示图标使用的就是自带的图标系统。通常为对如下的函数进行覆盖实现：



```
const FSlateBrush* UCListViewWidget::GetEditorIcon() 
{     
  return FUMGStyle::Get().GetBrush("Widget.TextBlock"); 
}
```

这些图标都是在引擎内部预定义的，通过搜索就能看到这些图标的定义。



```
// UMGStyle.cpp  

Style->Set("Widget.NativeWidgetHost", new IMAGE_BRUSH(TEXT("NativeWidgetHost"), Icon16x16));
```

其中IMAGE_BRUSH是同一个文件中定义的宏



```
#define IMAGE_BRUSH( RelativePath, ... ) FSlateImageBrush( Style->RootToContentDir( RelativePath, TEXT(".png") ), __VA_ARGS__ )
```

ICON16x16也同样是宏定义，再次就不赘述了。


自带图标也可以直接在控件中进行使用



```
const FSlateBrush *m_Icon = FUMGStyle::Get().GetBrush("Palette.Icon");
 
return SNew(STableRow< FFileListItemPtr >, OwnerTable)
[
SNew(SHorizontalBox)
    + SHorizontalBox::Slot()
    .HAlign(HAlign_Left)
    .AutoWidth()
    [
        SNew(SImage)
        .Image(m_Icon)
    ]
    + SHorizontalBox::Slot()
    .HAlign(HAlign_Left)
    [
        SNew(STextBlock)
        .Text(FText::FromString(Item->GetDisplayName()))
        .Font(FSlateFontInfo(FPaths::EngineContentDir() / TEXT("Slate/Fonts/Roboto-Bold.ttf"), 12))
    ]
];
```

## Icon Font


Icon Font添加图标确实非常的方便，UE4编辑器中也有使用到Font Awesome作为图标显示。


由于Font Awesome比较有名，项目中使用的也是它。


C++中的使用


要在C++中使用Font Awesome，首先要对UFont对象进行生成。



```
FontAwesome = Cast<UFont>(StaticLoadObject(UFont::StaticClass(), NULL, TEXT("Font'/Game/Resource/Font/fontawesome-webfont.fontawesome-webfont'")));
```

其中Font部分为直接对导入的字体进行引用复制所得。接下来只要使用STextBlock来使用相应的图标就可以了



```
return SNew(STableRow< FFileListItemPtr >, OwnerTable)
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .HAlign(HAlign_Left)
        .AutoWidth()
        .Padding(FMargin(0.0f, 3.0f, 1.0f, 0.0f))
        [
            SNew(STextBlock)
            .Font(FSlateFontInfo(FontAwesome, 12))
            .Text(FText::FromString(FString(Item->IsDirectory ? TEXT("\xf07b" /*fa-folder*/) : TEXT("\xf15b" /*fa-file*/))))
        ]
        + SHorizontalBox::Slot()
        .HAlign(HAlign_Left)
        .Padding(FMargin(3.0f, 3.0f, 0.0f, 0.0f))
        [
            SNew(STextBlock)
            .Text(FText::FromString(Item->GetDisplayName()))
            .Font(FSlateFontInfo(FPaths::EngineContentDir() / TEXT("Slate/Fonts/Roboto-Bold.ttf"), 12))
        ]
 
    ];
```

上面的代码是实现的列表的元素显示，最终的结果如下：


![image](http://web.archive.org/web/20151103082816im_/http://blog.ch-wind.com/wp-content/uploads/2015/09/image_thumb.png "image")


如果要在蓝图中进行使用的话，需要首先将字体的使用制定为对应的Icon Font。


通常Icon Font在提供的时候都会有每一个图标对应的Unicode编码，Font Awesome的编码集在[[这里](https://web.archive.org/web/20151103082816/https://fortawesome.github.io/Font-Awesome/cheatsheet/)]。


Font Awesome的编码集页面是可以直接复制对应的字符的，但是也有只提供了编码集的情况出现。


只要有编码集就可以对Icon进行使用了，要输入对应的Unicode码有很多种方式，这里提供两种。


Win+R输入并运行charmap，在其中选择对应的图标并复制其Unicode码。


在Word中输入对应的Unicode码，选中这些值按Alt+X就可以实现转换。


由于UE4编辑器中使用的字体并非对应的Icon Font，所以会以乱码显示，不过并不影响实际使用。


## 排版


使用到图标的时候有时需要对布局进行控制，布局的具体操作可以参看官方的[Slate控件文档](https://web.archive.org/web/20151103082816/https://docs.unrealengine.com/latest/CHN/Programming/Slate/Widgets/index.html)。


其中需要注意的是，Padding布局使用的是数据结构FMargin。作用参看FMargin本身的构造函数定义即可，只是Padding参数本身对FMargin进行了封装，光看官方的例子会有一定的迷惑性。


对于FMargin，当参数为4个时分别对应Left, Top, Right, Bottom；为2个时对应Horizontal和Vertical；为1个时则对应所有方向。


另外要注意的是在列表中AutoWidth必须手动指定，并不像文档中所描述的一样是默认启动的。


