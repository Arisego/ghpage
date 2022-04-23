---
layout: post
status: publish
published: true
title: UE4渲染代码逻辑总结（下）
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2209
wordpress_url: http://blog.ch-wind.com/?p=2209
date: '2018-01-02 00:02:45 +0000'
date_gmt: '2018-01-01 16:02:45 +0000'
tags:
- shader
- UE4
- Rendering
---
前面的内容都集中在C++端了，这边的内容会往Shader靠的更近一些。


由于感觉上很多东西要全部梳理明白会花费很多时间却又没有多大用处，所以这里的内容实际上进行了精简，因此比预定的短了很多。


## Shader端


虚幻使用HLSL作为Shader的语言，引擎核心的Shader都可以在引擎目录的Shader文件夹下找到。


其中ush为Shader头文件，而usf为Shader的源文件。由于Shader部分的代码基本属于引擎渲染的核心部分，要全部理解起来就有些费时间了。


所以这里只是按照其与C++部分接洽的结构进行粗略的探索。


### VertexFatory


VertexFatory是C++端将数据推送到Shader端的途径，在Shader文件夹中能够看到以下的几个：



> VectorFieldVisualizationVertexFactory.ush
> 
> 
> ParticleSpriteVertexFactory.ush
> 
> 
> ParticleGPUSpriteVertexFactory.ush
> 
> 
> ParticleBeamTrailVertexFactory.ush
> 
> 
> NiagaraMeshVertexFactory.ush
> 
> 
> NiagaraSpriteVertexFactory.ush
> 
> 
> MeshParticleVertexFactory.ush
> 
> 
> LocalVertexFactory.ush
> 
> 
> LandscapeVertexFactory.ush
> 
> 
> GpuSkinVertexFactory.ush
> 
> 


分别对应不同的使用情况，从命名上基本就能看出其用途。


Niagara是UE4的下一代粒子系统，目前版本可以在插件中打开，但是功能似乎并不完全，也没有文档，没有办法使用。


另外，这里的Shader与FVertexFatory并不是一一对应的关系。使用相同的渲染路径的类会在这里共用Shader。


如LocalVertexFactory.ush就被FLocalVertexFactory、FEmulatedInstancedStaticMeshVertexFactory、FInstancedStaticMeshVertexFactory、FGPUSkinPassthroughVertexFactory和FSplineMeshVertexFactory共同使用。


**FVertexFactoryInput**


这个数据结构是来自C++端的数据输入。在不同的Shader头文件中可能会有不同的定义，使用方式上自然也会有不同。


也有一些通用的Shader函数被定义来处理输入数据，如GetVertexFactoryIntermediates, VertexFactoryGetWorldPosition, GetMaterialVertexParameters。


**FBasePassVSOutput**


这个是另一个比较特殊的结构，由于不同的渲染路径可能在Vertex Shader结束后使用的路径是不同的。


所以也能看到对这个结构的不同定义。


### Material


所有的材质最终都会被编译成Shader，在材质编辑器中也能够看到材质的Shader预览。


#### 材质蓝图


用于将材质蓝图编译成Shader的模板在MaterialTemplate.ush中，查看这个文件的话，会看到有很多地方都是直接写成%s的。


这些都是由引擎将材质蓝图中的节点填充到这里的，例如



```
/**
* Parameters calculated from the pixel material inputs.
*/
struct FPixelMaterialInputs
{
%s
};
```

可能会被填写成



```
/**
* Parameters calculated from the pixel material inputs.
*/
struct FPixelMaterialInputs
{
MaterialFloat3 EmissiveColor;
MaterialFloat Opacity;
MaterialFloat OpacityMask;
MaterialFloat3 BaseColor;
MaterialFloat Metallic;
MaterialFloat Specular;
MaterialFloat Roughness;
MaterialFloat3 Normal;
MaterialFloat4 Subsurface;
MaterialFloat AmbientOcclusion;
MaterialFloat2 Refraction;
MaterialFloat PixelDepthOffset;

};
```

想要详细的了解的话可以在材质编辑器中修改材质，然后预览HLSL代码并与MaterialTemplate.ush对比以了解更多的内部工作原理。


#### 数据获取


在材质完成编译之后，渲染路径中就可以在需要时对材质中定义的相应的属性进行获取了。



```
half3 BaseColor = GetMaterialBaseColor(PixelMaterialInputs);
half  Metallic = GetMaterialMetallic(PixelMaterialInputs);
half  Specular = GetMaterialSpecular(PixelMaterialInputs);
```

不同的shader根据不同的渲染路径将数据最终填充到GBuffer中，以便进行进一步的计算。


#### 计算


在GBuffer的生成过程前、过程中、过程后，都有很多复杂的计算。


这些过程包括各种裁剪、光照以及PostProcess，由于并非是要进行这些逻辑的修改或者扩展，便不再深究下去了。


## 渲染逻辑


有了渲染用的C++端和Shader端代码之后，终于可以开始进行渲染工作了。


### FDeferredShadingSceneRenderer


对于PC端的延迟渲染，最终负责进行渲染工作的就是这个类了。


渲染的调用来源为FRendererModule::BeginRenderingViewFamily，可以看到有些编辑器的缩略图也会调用这个函数进行渲染，和玩家看到的游戏界面有关的渲染调用来自UGameViewportClient::Draw。


BeginRenderingViewFamily这个函数内在进行一些渲染的准备后，将实际渲染的函数扔到渲染线程



```
ENQUEUE_UNIQUE_RENDER_COMMAND_ONEPARAMETER(
FDrawSceneCommand,
FSceneRenderer*,SceneRenderer,SceneRenderer,
{
  RenderViewFamily_RenderThread(RHICmdList, SceneRenderer);
  FlushPendingDeleteRHIResources_RenderThread();
});
```

然后就实际执行渲染



```
SceneRenderer->Render(RHICmdList);
```

基本上渲染的主要逻辑就在这个函数中。


### RenderShadowDepthMaps


这个是SceneRenderer->Render中对深度贴图生成，从中可以看出渲染是如何最终使用Shader的。


比较关键的调用之一是ProjectedShadowInfo->RenderDepth(RHICmdList, this, SetShadowRenderTargets, ShadowDepthRenderMode_Normal);


这个函数进一步调用FProjectedShadowInfo::RenderDepth并继而调用FProjectedShadowInfo::RenderDepthInner


而这之中会有SceneRenderer->Scene->WholeSceneReflectiveShadowMapDrawList.DrawVisible


而这个WholeSceneReflectiveShadowMapDrawList就是一张DrawingPolicy列表了，到了这里就能与Shader相关的类型联系上了。


### 渲染流程


关于渲染的流程，到了这一步其实就和之前看到的差不多了，因此这里不做赘述。


下面的内容直接引用自官方文档，所以不保证与当前版本的内容匹配：




| 操作 | 描述 |
| --- | --- |
| GSceneRenderTargets.Allocate | 按需要重新分配全局场景渲染目标，使其对当前视图足够大。 |
| InitViews | ‭通过多种剔除方法为视图初始化基元可见性，设立此帧可见的动态阴影、按需要交叉阴影视锥与世界场景（对整个场景的阴影或预阴影）。 |
| PrePass / Depth only pass | RenderPrePass / FDepthDrawingPolicy。渲染遮挡物，对景深缓冲区仅输出景深。该通道可以在多种模式下工作：禁用、仅遮蔽，或完全景深，具体取决于活动状态的功能的需要。该通道通常的用途是初始化 Hierarchical Z 以降低 Base 通道的着色消耗（Base 通道的像素着色器消耗非常大）。 |
| Base pass | RenderBasePass / TBasePassDrawingPolicy。渲染不透明和遮盖的材质，向 GBuffer 输出材质属性。光照图贡献和天空光照也会在此计算并加入场景颜色。 |
| Issue Occlusion Queries / BeginOcclusionTests | 提出将用于下一帧的 InitViews 的延迟遮蔽查询。这会通过渲染所查询物体周围的相邻的框、有时还会将相邻的框组合在一起以减少绘制调用来完成。 |
| Lighting | 阴影图将对各个光照渲染，光照贡献会累加到场景颜色，并使用标准延迟和平铺延迟着色。光照也会在透明光照体积中累加。 |
| Fog | 雾和大气在延迟通道中对不透明表面进行逐个像素计算。 |
| Translucency | 透明度累加到屏外渲染目标，在其中它应用了逐个顶点的雾化，因而可以整合到场景中。光照透明度在一个通道中计算最终光照以正确融合。 |
| Post Processing | 多种后期处理效果均通过 GBuffers 应用。透明度将合成到场景中。 |


直接阅读FRendererModule::BeginRenderingViewFamily就可以看到UE4是如何对渲染通路进行处理的，其中有的较为简单的就会直接调用Shader进行处理，较为复杂的就会有相应的过程封装。


### Rendering paths


根据官方文档的描述，渲染路径分为Dymaic和Static两种。其中动态的速度会更慢些但是拥有更多的控制选项。


FPrimitiveSceneProxy会在GetViewRelevance中返回相关性标志，这样在渲染时引擎就会决定是否调用DrawDynamicElements和DrawStaticElements。


大致看来，static rendering path会在物体被加入FScene的时候，就将自己加入到绘制列表中。而dynamic rendering path由于可以做一些动态处理，并在DrawDynamicElements中提供了回调，所以就没有办法利用缓存机制了。


可以看到很多类似这样的调用


PrimitiveSceneInfo->Proxy->GetDynamicMeshElements(InViewFamily.Views, InViewFamily, ViewMask, Collector);


而SceneRender中也能看到GatherDynamicMeshElements这样的函数。


感觉上Static的渲染路径指的应该是FScene中大量存在的模板化的列表TStaticMeshDrawList。


不过由于这方面几乎找不到资料，文档中没有更加详细的说明，社区也基本看不到讨论，要从源码中回溯其意图就比较费时了，所以便没有进一步深究。


## 总结


到了这里，这个UE4的渲染逻辑就能有一个大致的草图了。


虽然其中还有更多的细节和详细是实现，也只有到了需要的时候再深入了解了。毕竟这部分已经是引擎开发者的工作，而太过于深入就没有意义了。


