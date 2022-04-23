---
layout: post
status: publish
published: true
title: Blender到UE4笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2831
wordpress_url: https://blog.ch-wind.com/?p=2831
date: '2020-04-11 19:51:28 +0000'
date_gmt: '2020-04-11 11:51:28 +0000'
tags:
- UE4
- Blender
---
Blender导出FBX到UE4的路径有些常见的问题，每次碰到都重新去找原因造成时间浪费，于是这边记录下。


当前UE4版本为UE4.25.0；当前Blender版本为Blender2.82a。
Blender最近升级到2.8了，有不少变化，不过一些基本的操作还是一样的。


## 导出导入


### Smooth Group


导入的时候提示没有SmoothGroup，需要修改FBX的默认导出选项


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2020/04/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2020/04/clip_image001.png)


这样就不会提示了


### Bind pose


导入UE4时提示



> The following bones are missing from the bind pose:
> 
> 
> This can happen for bones that are not vert weighted. If they are not in the correct orientation after importing,
> 
> 
> please set the "Use T0 as ref pose" option or add them to the bind pose and reimport the skeletal mesh.
> 
> 
> 


按照提示直接勾选Use T0 as ref pose，就不会提示了，结果没有明显变化。


是否有隐藏问题还不是很确定。


### 贴图丢了


这个是Blender2.8的新坑，主要是材质节点的组织方式变了。


从[[官方社区的讨论](https://developer.blender.org/T68399)]来看，这个似乎不是BUG而是一个特性。


2.8的[[API变更记录](https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Modules)]里面可以看到，导出使用的帮助类为bpy_extras.node_shader_utils。对于导出失败的材质，实际使用这个helper去尝试获取材质，就会发现无法正确的获取到贴图信息。主要原因是一些复杂的材质使用逻辑导致的，对于只是将Blender当作文件转换工具的用户而言就有些困扰了呢。


暂时没有什么特别好的解决方案，对于没有特别必要升级2.8的情况可以回到2.79……


### 贴图扭曲


模型导入后，部分贴图效果有微妙的扭曲感。在一些部位能明显的看到贴图出现了偏移。在对Blender内的UV进行查看后，发现在整个路径中，UV的值过大了。虽然说在理论上这并不会造成问题，但是实际是在导入UE4后出现了较为明显的UV偏差。


详细的发生原因没有时间去细究，不确定问题是在Blender侧还是UE侧，通过使用脚本在Blender中直接将UV全部裁剪到0~1的范围内解决了问题。



```
import bpy

for ts_mesh in bpy.data.meshes:
    print(ts_mesh.name)
    for ts_uvlayer in ts_mesh.uv_layers:
        print(ts_uvlayer)
        for ts_data in ts_uvlayer.data:
            ts_uv = ts_data.uv
            ts_uv.x = ts_uv.x % 1.0
            ts_uv.y = ts_uv.y % 1.0
            print(ts_data.uv)


```

### 光照模式下出现断层


在UnLit模式下模型正常，光照模式下出现一个明显的断层。


这种时候可以对GBuffer进行可视化来排查问题


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/04/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/04/image-4.png)


这次遇到的是法线贴图的处理方式有问题，能够明显看到在World Normal的可视化里面有一个断层，导致Detail Light那边同样出现了断层。


问题是法线贴图的混合，法线贴图不能通过简单的加法或者乘法来混合，UE4有提供混合节点BlendAngleCorrectedNormals，直接使用即可~


## 材质节点


Blender和UE4的材质节点有很多不同的地方，需要至少保证一些数学计算是一致的


### Rgb to bw


似乎是在做灰度转换的样子，[[官方Rgb_to_bw文档](https://docs.blender.org/manual/en/latest/compositing/types/converter/rgb_to_bw.html)]没有给出详细的计算方式。到源码里面的utils.py找到了



```
def rgb_to_bw(r, g, b):
    """Method to convert rgb to a bw intensity value."""
    return 0.35 * r + 0.45 * g + 0.2 * b
```

参照着实现


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/04/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/04/image-3.png)


### Invert


按照[[Invert Node](https://docs.blender.org/manual/en/latest/render/shader_nodes/color/invert.html)]的描述，就是反转，但是有一个factor的参数，暂时采用svm_invert.h的实现



```
ccl_device float invert(float color, float factor)
{
  return factor * (1.0f - color) + (1.0f - factor) * color;
}
```

没有配置factor的话就是OneMinus


### Mix


Mix等效于UE4的Interp节点。


## 功能差异


这次遇到一个Blender和UE4之间节点上的表现差异导致的误操作，在UE4里面，材质节点是这样的：


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/04/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/04/image-5.png)


这里面RGB和下面的R\G\B是指向同样的值的，而在Blender里面，如果有这样的节点


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/04/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/04/image-6.png)


这个时候Color和R\G\B其实是完全不同的东西，如果在进行材质功能映射的时候一定不要按照UE4这边的习惯去理解~




