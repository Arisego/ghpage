---
layout: post
status: publish
published: true
title: Blender插件制作笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 3062
wordpress_url: https://blog.ch-wind.com/?p=3062
date: '2020-09-26 21:07:30 +0000'
date_gmt: '2020-09-26 13:07:30 +0000'
tags:
- Blender
---
这里记录的都是Blender相关的，和Python基础错误关系不大。


当前的blender版本为2.83.5 。


暂时打算停留在lts版本上，主干的开发速度太快了，跟不上节奏


blender的api文档有些难以查询，有的时候想要特定的功能反而直接求助于搜索引擎比较快……


## UI禁用


对于有些UI需要禁用而不是不绘制的，直接操作UI的enabled属性就可以了。


UILayeout相关的文档可以在这里看到：<https://docs.blender.org/api/current/bpy.types.UILayout.html>


## 类型注册


所有的blender相关的类型必须经过register_class才能使用，要留意在插件解除注册的时候同时unregister_class。


对于需要注册的属性也同样，属性可以注册在Object上，这样每个物品都会有。注册在Scene上的属性只有Scene会有。


从别人的插件里面看到，把class放到一个列表里面统一操作的方式比较好：



```
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
```

## 物品选择


对于想要选择的物品，在UI中想要限定类型的话，需要在注册PointerProperty的时候指定



```
map_target: bpy.props.PointerProperty(
    type=bpy.types.Object,
    name="FollowTarget",
    poll=lambda self, obj: obj.type == 'ARMATURE' and obj != bpy.context.object
    )
```

这样的话，在进行属性显示时使用layout.prop就能只选择ARMATURE类型了。


## 属性


属性的变更需要注册update



```
source_follow_rotation: BoolProperty(
    update=OnSourceFollowTypeChange, default=True)


```

update传入时的self就是这个属性本身，很方便。


## UIList


ui基本上按照固定的流程来操作就不会有问题。


遇到问题比较多的是UIList，这个文档描述有些不清晰，导致使用上很多靠猜，而Python又没有类型检查，真的很苦恼。


官方的文档在这里：[https://docs.blender.org/api/current/bpy.types.UIList.html](https://docs.blender.org/api/current/bpy.types.UIList.html "https://docs.blender.org/api/current/bpy.types.UIList.html")


主要的问题是对初次接触的人很不友好，如果你和我一样对Python也不是很熟悉的话会一头雾水。原因是第一个例子太简单，而第二个例子太复杂。


其实，对于UIList而言，一般只要重载draw_item就可以了，在里面可以和其他UI一样执行绘制。


如果需要过滤功能的话，默认的就可以了。但是如果你需要过滤的属性不是name的话，才需要重写filter_items，不然过滤会不成功。


如果需要添加一些自定义的过滤的话，才需要最复杂的处理：额外的重载draw_filter来绘制额外的属性，在filter_itmes根据属性进行过滤。


列表示例：



```
# ListBox
# Show list of retarget cell
class QM_UL_ControlCell(UIList):
    """
    List box for retarget cells, this is the list in side panel
    """
    # Constants (flags)
    # Be careful not to shadow FILTER_ITEM!
    VGROUP_EMPTY = 1 << 0

    # Custom properties, saved with .blend file.
    use_filter_name_reverse: bpy.props.BoolProperty(name="Reverse Name", default=False, options=set(),
                                                    description="Reverse name filtering")

    use_order_name: bpy.props.BoolProperty(name="Name", default=False, options=set(),
                                           description="Sort groups by their name (case-insensitive)")

    use_filter_linked: bpy.props.BoolProperty(name="Linked", default=False, options=set(),
                                              description="Filter linked only")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        subrow = row.row(align=True)
        subrow.prop(item, "source_name", text="", emboss=False)

        subrow = subrow.row(align=True)
        if len(item.target_name) > 0:
            subrow.prop(item, "source_follow_location", text="",
                        toggle=True, icon="CON_LOCLIKE")
            subrow.prop(item, "source_follow_rotation", text="",
                        toggle=True, icon="CON_ROTLIKE")

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        icon = 'ZOOM_OUT' if self.use_filter_name_reverse else 'ZOOM_IN'
        subrow.prop(self, "use_filter_name_reverse", text="", icon=icon)

        icon = 'LINKED' if self.use_filter_linked else 'UNLINKED'
        subrow.prop(self, "use_filter_linked", text="", icon=icon)

        subrow = layout.row(align=True)
        subrow.label(text="Order by:")
        subrow.prop(self, "use_order_name", toggle=True)

    # Filter
    # 1. we use [source_name] not [name]
    # 2. provide filter for targeted cell
    def filter_items(self, context, data, propname):
        statelist = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, statelist, "source_name",
                                                          reverse=self.use_filter_name_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(statelist)

        # Filtering cell with target
        if self.use_filter_linked:
            for i, item in enumerate(statelist):
                if len(item.target_name) == 0:
                    flt_flags[i] &= ~self.bitflag_filter_item

        # Reorder by name
        if self.use_order_name:
            flt_neworder = helper_funcs.sort_items_by_name(
                statelist, "source_name")

        return flt_flags, flt_neworder

```

最终结果是这样的：


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/09/image_thumb-24.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/09/image-28.png)


主要起作用的其实就是


* draw_item: 绘制单个列表
* draw_filter: 绘制下面的过滤区域，这个不指定也会有一个默认的
* filter_item: 用于实际对列表的元素进行过滤


在列表绘制时可以指定列表元素和选中的index：



```
layout.template_list("QM_UL_ControlCell", "",
    qm_state, "quickmap_celllist",
    qm_state, "quickmap_celllist_index"
    )
```

这样就可以在选中指定列表元素时根据index的update来得到通知了。


## 文件读写


python对json的支持比较好，读写很方便。


文件本身需要让operator继承ExportHelper和ImportHelper才能分别进行blender封装好的文件操作。


本身很简单，网上随便就能找到例子，这里就不列出占位置了。


## Collection


这部分操作有点迷，在网上抄了一段代码直接用就好了：



```
# Collection Operate
def make_collection(collection_name):
    if collection_name in bpy.data.collections:  # Does the collection already exist?
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(
            new_collection)  # Add the new collection under a parent
        return new_collection
```

主要是collection的注册关系需要留意，不过别人封好了就不用管了~


