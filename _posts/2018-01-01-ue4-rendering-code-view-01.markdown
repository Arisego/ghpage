---
layout: post
status: publish
published: true
title: UE4渲染代码逻辑总结（上）
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2198
wordpress_url: http://blog.ch-wind.com/?p=2198
date: '2018-01-01 00:01:54 +0000'
date_gmt: '2017-12-31 16:01:54 +0000'
tags:
- shader
- UE4
---
本文是对UE4中渲染代码逻辑的总结。


当前使用的UE4版本为4.18.3。


本文内容是之前提到的这段时间的笔记的总结，内容主要来自于社区文章、官方文档以及引擎源码的阅读。


由于渲染系统比较复杂，没有时间遍历所有的代码，很多地方掺杂了自己的臆测，如有错误，欢迎指正。


## FShader


FShader是负责Shader的代码端基类，继承自FDeferredCleanupInterface。


### 结构


**FDeferredCleanupInterface**


FDeferredCleanupInterface这个基类是用于游戏线程与渲染线程的同步的，只有一个纯虚函数：FinishCleanup。


由于渲染用的资源在两边都有在使用，所以当要删除一个资源时，会向渲染线程推送资源删除请求，同时通过BeginCleanup将其加入待删除列表，等到渲染线程结束时FinishCleanup就会被调用，这时候就可以安全的在游戏线程中完全释放资源了。


除了FShader之外，其他与渲染有关的资源如FLightMap以及FShadowMap等都有继承自这个类。


**FShaderResource**


这个类也继承自FDeferredCleanupInterface，如其名称，它负责保管Shader编译之后的资源。


为了减小材质编译等对资源的占用，同一个FShaderResource会被多个FShader引用。例如Material Function就利用了这个机制。


### 使用


FShader共有两种类型的之类，分别是FGlobalShader与FMaterialShader，对应不同的使用用途。


**FGlobalShader**


这个是全局的Shader，只允许存在一个实例。


渲染的核心Shader部分有许多就是FGlobalShader。


**FMaterialShader**


这个是用于具体材质的Shader，会拥有很多实例。


进一步被实现为FMeshMaterialShader，可以将Mesh的顶点数据引入到Shader端。


## 渲染数据


渲染数据通过FPrimitiveSceneProxy经由结构FVertexFactory绑定到Shader上。


### FVertexFactory


这个类负责将顶点数据从C++端带到Shader端，继承自FRenderResource，是渲染资源的一种。


**FLocalVertexFactory**


提供本地空间到全局空间的转换，Static Mesh以及Cables、Procedual Mesh等都使用的是它。


**FGPUBaseSkinVertexFactory**


这个是Skeletel Mesh用的，因为需要一些更多的数据。但是似乎还要配合继承自LocalVertexFactory的FGPUSkinPassthroughVertexFactory。


**FLandscapeVertexFactory**


Landscape是基于VTF(Vertex Texture Fetch)，使用高度图来修改顶点位置实现的，所以需要额外的处理。


**FParticleVertexFactoryBase**


粒子系统用的。


### FPrimitiveSceneProxy


这个类似UPrimitiveComponent在渲染线程中的对应版本，负责维护每个Component在渲染线程上需要的数据。


UE4的核心类大多有自己在渲染线程中的对应




| 游戏线程 | 渲染线程 |
| --- | --- |
| UWorld | FScene |
| UPrimitiveComponent | FPrimitiveSceneProxy / FPrimitiveSceneInfo‬ |
| ULocalPlayer | FSceneViewState |
| ULightComponent | FLightSceneProxy / FLightSceneInfo |


不同的UPrimitiveComponent类通过重载CreateSceneProxy()来创建自己的FPrimitiveSceneProxy。


**UCableComponent**


非常的直观，在CreateSceneProxy()中直接创建FCableSceneProxy，然后进行初始化。


然后在SendRenderDyamicData_Concurrent()中将数据发送到渲染线程并借由SetDynamicData_RenderThread进行数据构造。


**UImagePlateFrustumComponent**


由于始终只是在渲染面向摄像的2D材质，所以不需要VertexFactory。


所以FImagePlateFrustumSceneProxy只是在GetDynamicMeshElements时返回演算的结果。


## Drawing Policy


### FDepthDrawingPolicy


这个Drawing Policy工作于depth-only通道时，负责将Mesh的opaque和masked的深度信息写出。


通过调用



```
VertexShader = InMaterialResource.GetShader<TDepthOnlyVS<false> >(VertexFactory->GetType())
```

DrawingPolicy便找到了对应的shader，并将vertex factory传了进去。


在需要Tessellation的情况下，还会另外获取HullShader和DomainShader



```
HullShader = InMaterialResource.GetShader<FDepthOnlyHS>(VertexFactory->GetType());
DomainShader = InMaterialResource.GetShader<FDepthOnlyDS>(VertexFactory->GetType());
```

代码的分支很多，但是作用还是比较明显的。


其中还有SetSharedState和SetMeshRenderState两个函数负责传递参数。


### FBasePassDrawingPolicy


这个是在basepass通道时处理Mesh，根据不同的光照类型会有不同的处理



```
template<typename LightMapPolicyType>
class TBasePassDrawingPolicy : public FBasePassDrawingPolicy
```

这个类才算是本体的感觉吧。


会根据不同的光照类型获取不同的Base pass的shader，这里的光照类型并不是单纯的编辑器中设置的类型，而是实际在Shader中用于计算的光照模型



```
enum ELightMapPolicyType
{
LMP_NO_LIGHTMAP,
LMP_PRECOMPUTED_IRRADIANCE_VOLUME_INDIRECT_LIGHTING,
LMP_CACHED_VOLUME_INDIRECT_LIGHTING,
LMP_CACHED_POINT_INDIRECT_LIGHTING,
LMP_SIMPLE_NO_LIGHTMAP,
LMP_SIMPLE_LIGHTMAP_ONLY_LIGHTING,
LMP_SIMPLE_DIRECTIONAL_LIGHT_LIGHTING,
LMP_SIMPLE_STATIONARY_PRECOMPUTED_SHADOW_LIGHTING,
LMP_SIMPLE_STATIONARY_SINGLESAMPLE_SHADOW_LIGHTING,
LMP_SIMPLE_STATIONARY_VOLUMETRICLIGHTMAP_SHADOW_LIGHTING,
LMP_LQ_LIGHTMAP,
LMP_HQ_LIGHTMAP,
LMP_DISTANCE_FIELD_SHADOWS_AND_HQ_LIGHTMAP,
// Mobile specific
LMP_MOBILE_DISTANCE_FIELD_SHADOWS_AND_LQ_LIGHTMAP,
LMP_MOBILE_DISTANCE_FIELD_SHADOWS_LIGHTMAP_AND_CSM,
LMP_MOBILE_DIRECTIONAL_LIGHT_AND_SH_INDIRECT,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT_AND_SH_INDIRECT,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT_CSM_AND_SH_INDIRECT,
LMP_MOBILE_DIRECTIONAL_LIGHT_CSM_AND_SH_INDIRECT,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT_CSM,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT_WITH_LIGHTMAP,
LMP_MOBILE_MOVABLE_DIRECTIONAL_LIGHT_CSM_WITH_LIGHTMAP,
// LightMapDensity
LMP_DUMMY
};
```

GetUniformBasePassShaders负责完成差分，最终通过LightMapPolicyType就会得到不同的basepass的shader，不同的basepass的shader中，使用的vertex factory也就不同了。


### DrawingPolicyFactory


这是一组负责生成DrawingPloicy的工厂类，但是他们都没有各自的基类，而是对应自己的功能有稍微有些不同的实现。


在FDepthDrawingPolicyFactory::AddStaticMesh能够看到一个FStaticMesh是如何被注册到FScene中去的。


而这个调用来自FStaticMesh::AddToDrawLists，在其中能够看到FStaticMesh在通过各种DrawingPolicyFactory来进行Shader的关联注册。


而之后，在渲染线程中，FDepthDrawingPolicyFactory::DrawStaticMesh之类的函数就会被调用来进行渲染。


### FPrimitiveSceneInfo


对DrawingPolicyFactory的调用最终来自FPrimitiveSceneInfo，这个类与FPrimitiveSceneProxy 是一对一的关系，是最终注册到FScene的数据结构。


在FScene::UpdatePrimitiveTransform_RenderThread中能够看到渲染线程是如何通过FPrimitiveSceneProxy ::GetPrimitiveSceneInfo来更新与FScene的关系的。


## C++到Shader的绑定


上面这些类是在C++中负责渲染逻辑的，而为了最终代码与Shader之间能够相互交流需要进行绑定。


### 绑定帮助宏


UE4中有一组宏来帮助绑定C++类与Shader代码。


#### FShader绑定



```
IMPLEMENT_MATERIAL_SHADER_TYPE(TemplatePrefix,ShaderClass,SourceFilename,FunctionName,Frequency)
```

这个是实际将C++的类与Shader进行绑定的宏。


在引擎中能够看到很多这个宏，例如



```
IMPLEMENT_MATERIAL_SHADER_TYPE(,FVelocityVS,TEXT("/Engine/Private/VelocityShader.usf"),TEXT("MainVertexShader"),SF_Vertex);
```

这个宏将FVelocityVS绑定到VelocityShader.usf中，而MainVertexShader是shader端的入口函数。


最后一个ShaderFrequency感觉上更加接近Shader的类型：



```
enum EShaderFrequency
{
SF_Vertex            = 0,
SF_Hull                = 1,
SF_Domain            = 2,
SF_Pixel            = 3,
SF_Geometry            = 4,
SF_Compute            = 5,

SF_NumFrequencies    = 6,

SF_NumBits            = 3,
};
```

第一个参数用于宏的进一步模板化，在上面的BasePass进行绑定的时候就能看到



```
IMPLEMENT_BASEPASS_LIGHTMAPPED_SHADER_TYPE
```

这个宏对这个参数的使用。


#### VertexFactory绑定



```
IMPLEMENT_VERTEX_FACTORY_TYPE(FactoryClass,ShaderFilename,bUsedWithMaterials,bSupportsStaticLighting,bSupportsDynamicLighting,bPrecisePrevWorldPos,bSupportsPositionOnly)
```

这个宏将VertexFactory绑定到对应的shader中去


例如



```
IMPLEMENT_VERTEX_FACTORY_TYPE(FGPUSkinPassthroughVertexFactory, "/Engine/Private/LocalVertexFactory.ush", true, false, true, false, false);
```

这个绑定使得FGPUSkinPassthroughVertexFactory与LocalVertexFactory.ush进行关联，能够看到有很多不同的VertexFactory绑定到了这里，而且VertexFatory在各个不同的ush里面都有定义。


这是因为前面有提到MeshShader是有很多实例，每一个实例会根据自己的光照类型、数据类型进行不同的绑定。


### Shader Plugin


从UE4.17开始，已经可以在插件中自己定义Shader并进行调用了。不过UE4的核心渲染流程依然没有开放，所以想要自定义Shader Model之类的话还是必须对源码进行修改。


详细的操作可以参考[[官方文档](https://docs-origin.unrealengine.com/latest/INT/Programming/Rendering/ShaderInPlugin/QuickStart/index.html)]，不过官方文档的操作没有进行充分的解释，只是教你怎么把引擎插件的LensDistortion插件给拷贝并修改成自己的插件，不过刚好可以方便对Shader绑定进行理解。


#### 基础重载


ShouldCache用于定义是否在指定的平台要编译这个材质。


ModifyCompilationEnvironment用于在特定的平台上添加自己的定义，但是示例中直接就加进了两个自己的定义



```
OutEnvironment.SetDefine(TEXT("GRID_SUBDIVISION_X"), kGridSubdivisionX);
OutEnvironment.SetDefine(TEXT("GRID_SUBDIVISION_Y"), kGridSubdivisionY);
```

#### 参数绑定


可以看到FLensDistortionUVGenerationShader继承自FGlobalShader，然后添加了



```
FShaderParameter PixelUVSize;
FShaderParameter RadialDistortionCoefs;
FShaderParameter TangentialDistortionCoefs;
FShaderParameter DistortedCameraMatrix;
FShaderParameter UndistortedCameraMatrix;
FShaderParameter OutputMultiplyAndAdd;
```

几个成员，然后在构造中绑定



```
PixelUVSize.Bind(Initializer.ParameterMap, TEXT("PixelUVSize"));
RadialDistortionCoefs.Bind(Initializer.ParameterMap, TEXT("RadialDistortionCoefs"));
```

第二个参数是参数在Shader中的名称。


之后就可以通过



```
SetShaderValue(RHICmdList, ShaderRHI, PixelUVSize, PixelUVSizeValue);
SetShaderValue(RHICmdList, ShaderRHI, DistortedCameraMatrix, CompiledCameraModel.DistortedCameraMatrix);
```

来进行修改了。


