---
layout: post
status: publish
published: true
title: Slate文件目录树基础实现
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1542
wordpress_url: http://blog.ch-wind.com/?p=1542
date: '2015-08-19 14:52:43 +0000'
date_gmt: '2015-08-19 06:52:43 +0000'
tags:
- UE4
- Slate
---
目前UMG中并没有提供TreeView类，要使用TreeView必须使用Slate。


当前UE4版本4.8.3。


TreeView在UE4编辑器中被广泛的使用，但是出于某些不可知的原因无法在UMG中进行直接使用。鉴于制作复杂度较高的界面需要使用到Slate，对Slate进行专门的研究是有必要的。


本文参照Unreal官方社区文档[Slate, Tree View Widget](https://web.archive.org/web/20151103022132/https://wiki.unrealengine.com/Slate,_Tree_View_Widget,_Ex:_In-Editor_File_Structure_Explorer)完成。


请注意：原始文档中并没有给出具体的文件浏览器实现，而是提供了作为其基础的目录树使用方式。


## 目录树数据结构


要实现目录树并不需要太复杂的数据结构，实现基本的功能即可。


TreeView中本身需要的数据是数组型的，这里定义的数据结构是节点使用的。


DDFileTreeItem.h



```
#pragma once

typedef TSharedPtr< class FDDFileTreeItem > FDDFileTreeItemPtr;

/**
* <目录树节点
*/

class FDDFileTreeItem
{
public:

/** @return <返回父节点 */
const FDDFileTreeItemPtr GetParentCategory() const
{
  return ParentDir.Pin();
}

/** @return <返回节点的路径【只读】 */
const FString& GetDirectoryPath() const
{
  return DirectoryPath;
}

/** @return <返回显示名称【只读】 */
const FString& GetDisplayName() const
{
  return DisplayName;
}

/** @return <返回子节点【只读】 */
const TArray< FDDFileTreeItemPtr >& GetSubDirectories() const
{
  return SubDirectories;
}

/** @return <返回可写入的子节点引用 */
TArray< FDDFileTreeItemPtr >& AccessSubDirectories()
{
  return SubDirectories;
}

/** <为当前节点添加子目录 */
void AddSubDirectory(const FDDFileTreeItemPtr NewSubDir)
{
  SubDirectories.Add(NewSubDir);
}

public:
/** <构造函数 */

FDDFileTreeItem(const FDDFileTreeItemPtr IN_ParentDir, const FString& IN_DirectoryPath, const FString& IN_DisplayName)
: ParentDir(IN_ParentDir)
, DirectoryPath(IN_DirectoryPath)
, DisplayName(IN_DisplayName)
{

}

private:

/** <父节点引用; */
TWeakPtr< FDDFileTreeItem > ParentDir;

/** <完整路径 */
FString DirectoryPath;

/** <显示名称 */
FString DisplayName;

/** <子节点数组 */
TArray< FDDFileTreeItemPtr > SubDirectories;

};
```

 


节点的数据结构较为简单，直接在头文件中对函数进行了实现。


## 目录树Slate控件


由于原始文档中提供的代码中引用的Engine是不必要的，故而在这里直接替换成了较为通用的HUD引用，这样就不会导致代码有项目相关性了。


这里先上代码，其他的一些说明放在代码后面。


SDDFileTree.h



```
#pragma once

/* <节点数据结构 */

#include "DDFileTreeItem.h"

typedef STreeView< FDDFileTreeItemPtr > SDDFileTreeView;

/**
* <目录树Slate
*/

class SDDFileTree : public SCompoundWidget
{

public:

SLATE_BEGIN_ARGS(SDDFileTree){}

SLATE_ARGUMENT(TWeakObjectPtr<class AHUD>, OwnerHUD)

SLATE_END_ARGS()

public:

TWeakObjectPtr<AHUD> OwnerHUD;

/** <刷新目录 */

//bool DoRefresh;

public:

void Construct(const FArguments& InArgs);

/** Destructor */
~SDDFileTree();

/** @return <返回当前被选中的目录 */
FDDFileTreeItemPtr GetSelectedDirectory() const;

/** <选择目录 */
void SelectDirectory(const FDDFileTreeItemPtr& CategoryToSelect);

/** @return <返回节点是否展开 */
bool IsItemExpanded(const FDDFileTreeItemPtr Item) const;

private:

/** <生成单个节点元素 */
TSharedRef<ITableRow> DDFileTree_OnGenerateRow(FDDFileTreeItemPtr Item, const TSharedRef<STableViewBase>& OwnerTable);

/** <获得子节点 */
void DDFileTree_OnGetChildren(FDDFileTreeItemPtr Item, TArray< FDDFileTreeItemPtr >& OutChildren);

/** <当选中项发生变化时 */
void DDFileTree_OnSelectionChanged(FDDFileTreeItemPtr Item, ESelectInfo::Type SelectInfo);

/** <构建目录树数据 */
void RebuildFileTree();

/** <重写Tick方便以后实现目录刷新 */
virtual void Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, const float InDeltaTime) override;

private:

/** <TreeView控件 */
TSharedPtr< SDDFileTreeView > DDFileTreeView;

/** <目录树的数据 */
TArray< FDDFileTreeItemPtr > Directories;

};
```

 


SDDFileTree.cpp



```
#include "Test_mp.h"
#include "SDDFileTree.h"
#include "DDFileTreeItem.h"

void SDDFileTree::Construct(const FArguments& InArgs)
{
  OwnerHUD = InArgs._OwnerHUD;
  RebuildFileTree(); /* <构建目录树数据 */

  //Build the tree view of the above core data
  DDFileTreeView =
    SNew(SDDFileTreeView)
    .SelectionMode(ESelectionMode::Single) // 只允许选中一个项目
    .ClearSelectionOnClick(false) // 不允许不选中内容
    .TreeItemsSource(&Directories)
    .OnGenerateRow(this, &SDDFileTree::DDFileTree_OnGenerateRow)
    .OnGetChildren(this, &SDDFileTree::DDFileTree_OnGetChildren)
    .OnSelectionChanged(this, &SDDFileTree::DDFileTree_OnSelectionChanged)
;

    /*
    // Expand the root  by default
    for( auto RootDirIt( Directories.CreateConstIterator() ); RootDirIt; ++RootDirIt )
    {
      const auto& Dir = *RootDirIt;
      DDFileTreeView->SetItemExpansion( Dir, true );
    }

    // Select the first item by default
    if( Directories.Num() > 0 )
    {
      DDFileTreeView->SetSelection( Directories[ 0 ] );
    }

    */

    ChildSlot.AttachWidget(DDFileTreeView.ToSharedRef());
}

SDDFileTree::~SDDFileTree()
{

}

void SDDFileTree::RebuildFileTree()
{
  Directories.Empty();
  //~~~~~~~~~~~~~~~~~~~
  //Root Level
  TSharedRef<FDDFileTreeItem> RootDir = MakeShareable(new FDDFileTreeItem(NULL, TEXT("RootDir"), FString("RootDir")));
  Directories.Add(RootDir);
  TSharedRef<FDDFileTreeItem> RootDir2 = MakeShareable(new FDDFileTreeItem(NULL, TEXT("RootDir2"), FString("RootDir2")));
  Directories.Add(RootDir2);
  //~~~~~~~~~~~~~~~~~~~

  //Root Category
  FDDFileTreeItemPtr ParentCategory = RootDir;

  //Add
  FDDFileTreeItemPtr EachSubDir = MakeShareable(new FDDFileTreeItem(ParentCategory, "Joy", "Joy"));
  RootDir->AddSubDirectory(EachSubDir);

  //Add

  EachSubDir = MakeShareable(new FDDFileTreeItem(ParentCategory, "Song", "Song"));
  RootDir->AddSubDirectory(EachSubDir);

  //Add

  FDDFileTreeItemPtr SongDir = MakeShareable(new FDDFileTreeItem(ParentCategory, "Dance", "Dance"));
  EachSubDir->AddSubDirectory(SongDir);

  //Add

  SongDir = MakeShareable(new FDDFileTreeItem(ParentCategory, "Rainbows", "Rainbows"));
  EachSubDir->AddSubDirectory(SongDir);
  //Add
  EachSubDir = MakeShareable(new FDDFileTreeItem(ParentCategory, "Butterflies", "Butterflies"));
  RootDir->AddSubDirectory(EachSubDir);

  //Refresh

  if (DDFileTreeView.IsValid())
  {
    DDFileTreeView->RequestTreeRefresh();
  }

}

TSharedRef<ITableRow> SDDFileTree::DDFileTree_OnGenerateRow(FDDFileTreeItemPtr Item, const TSharedRef<STableViewBase>& OwnerTable)
{
  if (!Item.IsValid())
  {
    return SNew(STableRow< FDDFileTreeItemPtr >, OwnerTable)
      [
        SNew(STextBlock)
          .Text(NSLOCTEXT("Your Namespace", "twns", "THIS WAS NULL SOMEHOW"))
      ];

  }

  return SNew(STableRow< FDDFileTreeItemPtr >, OwnerTable)
    [
      SNew(STextBlock)
        .Text(FText::FromString(Item->GetDisplayName()))
        .Font(FSlateFontInfo(FPaths::EngineContentDir() / TEXT("Slate/Fonts/Roboto-Bold.ttf"), 12))
        .ColorAndOpacity(FLinearColor(1, 0, 1, 1))
        .ShadowColorAndOpacity(FLinearColor::Black)
        .ShadowOffset(FIntPoint(-2, 2))
    ];
}

void SDDFileTree::DDFileTree_OnGetChildren(FDDFileTreeItemPtr Item, TArray< FDDFileTreeItemPtr >& OutChildren)
{
  const auto& SubCategories = Item->GetSubDirectories();
  OutChildren.Append(SubCategories);
}

//Key function for interaction with user!
void SDDFileTree::DDFileTree_OnSelectionChanged(FDDFileTreeItemPtr Item, ESelectInfo::Type SelectInfo)
{
  //Selection Changed!
  UE_LOG(LogTemp, Warning, TEXT("Item Selected: %s"), *Item->GetDisplayName());
}

FDDFileTreeItemPtr SDDFileTree::GetSelectedDirectory() const
{
  if (DDFileTreeView.IsValid())
  {
     auto SelectedItems = DDFileTreeView->GetSelectedItems();
     if (SelectedItems.Num() > 0)
     {
       const auto& SelectedCategoryItem = SelectedItems[0];
       return SelectedCategoryItem;
     }

  }
  return NULL;
}

void SDDFileTree::SelectDirectory(const FDDFileTreeItemPtr& CategoryToSelect)
{
  if (ensure(DDFileTreeView.IsValid()))
  {
      DDFileTreeView->SetSelection(CategoryToSelect);
  }
}

//is the tree item expanded to show children?
bool SDDFileTree::IsItemExpanded(const FDDFileTreeItemPtr Item) const
{
  return DDFileTreeView->IsItemExpanded(Item);
}

void SDDFileTree::Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, const float InDeltaTime)
{
  // Call parent implementation
  SCompoundWidget::Tick(AllottedGeometry, InCurrentTime, InDeltaTime);
  //can do things here every tick
}
```

代码的结构还是比较清晰的，这里需要注意的是，针对TreeView的事件是在控件本身生成的时候注册的。


其中，OnGenerateRow事件是STreeView和SListView的必须事件。当控件需要进行元素显示时，会对这个函数进行调用，获得需要显示的元素。


另外，代码中的OnSelectionChanged函数缺乏必要的安全检测，在使用中需要留意。


用于显示的数据是在Construct中通过调用RebuildFileTree()函数生成的。


## 最终结果


完成了上面的步骤之后，直接在HUD中对控件进行展示即可。



```
SAssignNew(DDFileTree, SDDFileTree).OwnerHUD(this);

if (GEngine->IsValidLowLevel())
{
  GEngine->GameViewport->AddViewportWidgetContent(SNew(SWeakWidget).PossiblyNullContent(DDFileTree.ToSharedRef()));
}

if (DDFileTree.IsValid())
{
  DDFileTree->SetVisibility(EVisibility::Visible);
}
```

启动预览，由于没有进行布局，可以在最上方看到目录树的展示。


[![U10$_IA57URMV_PO0]6[JUC](https://blog.ch-wind.com/wp-content/uploads/2017/03/U10_IA57URMV_PO06JUC_thumb.png "U10$_IA57URMV_PO0]6[JUC")](https://blog.ch-wind.com/wp-content/uploads/2017/03/U10_IA57URMV_PO06JUC.png)


至此，目录树的基本功能已经实现。


