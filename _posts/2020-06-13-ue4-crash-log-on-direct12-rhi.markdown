---
layout: post
status: publish
published: true
title: UE4在DX12 RHI上崩溃两例记录
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2917
wordpress_url: https://blog.ch-wind.com/?p=2917
date: '2020-06-13 11:22:38 +0000'
date_gmt: '2020-06-13 03:22:38 +0000'
tags:
- UE4
- Direct12
---

主要是发生在global shader的自定义上，如果你没有使用的话估计原因不太一样~



  

  





当前使用UE版本为UE4.25.1。




原本在理解上感觉UE4的RHI封装应当是一致的，但实际情况还是会有些不同。




结论上看，在Direct12的RHI上有一些更加严格的限制，如果不注意的话就会出现问题。




## 参数顺序




Dx12的RHI要求Vertex Shader和Pixel Shader的参数顺序是一致的，也就是说OutPut的次序就是Input的次序，否则就会出现以下错误





```
Fatal error: [File:D:/Build/++UE4+Licensee/Sync/Engine/Source/Runtime/D3D12RHI/Private/D3D12Util.cpp] [Line: 581] hr failed at D:/Build/++UE4+Licensee/Sync/Engine/Source/Runtime/D3D12RHI/Private/Windows/WindowsD3D12PipelineState.cpp:697 with error E_INVALIDARG
UE4Editor.exe has triggered a breakpoint.
```



调整参数次序后不再出现。





```
void MainVS(
    in uint GlobalVertexId : SV_VertexID,
-    out float4 OutPosition : SV_POSITION,
-    out float2 OutUV : TEXCOORD0	
+    out float2 OutUV : TEXCOORD0,
+    out float4 OutPosition : SV_POSITION
    )
{
	OutPosition = float4(kSpriteVertices[GlobalVertexId], 0, 1);
	OutUV = kQuadUVs[GlobalVertexId];
}



void MainPS(
    in noperspective float2 IntUV : TEXCOORD0,
    in float4 SvPosition : SV_POSITION,
    out float4 OutColor : SV_Target0
    )
{
    OutColor = float4(1,IntUV.r,0,1);
}
```



## SetGraphicsPipelineState




这个错误应当与初始化次序有关，主要是Vertex Shader等的参数必须在SetGraphicsPipelineState之后调用，否则就会出现一下错误





```
Ensure condition failed: CachedShader == VertexShader [File:D:/Build/++UE4+Licensee/Sync/Engine/Source/Runtime/D3D12RHI/Private/D3D12Commands.cpp] [Line: 38] Parameters are being set for a VertexShader which is not currently bound
UE4Editor.exe has triggered a breakpoint.
```



注意调整下次序就可以了，类似这样的[[改动](https://github.com/Arisego/UnrealLive2D/commit/ab8f25a34a2f9c491014ba33474eadd06c9a288a)]就可以了。





```
        GraphicsPSOInit.BoundShaderState.VertexShaderRHI = VertexShader.GetVertexShader();
        GraphicsPSOInit.BoundShaderState.PixelShaderRHI = PixelShader.GetPixelShader();

+       SetGraphicsPipelineState(RHICmdList, GraphicsPSOInit);


        VertexShader->SetParameters(RHICmdList, VertexShader.GetVertexShader(), ts_BaseColor, tsr_TextureRHI);
        PixelShader->SetParameters(RHICmdList, PixelShader.GetPixelShader(), ts_BaseColor, tsr_TextureRHI);


        //////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////////////
-       SetGraphicsPipelineState(RHICmdList, GraphicsPSOInit);



        RHICmdList.SetStreamSource(0, ScratchVertexBufferRHI, 0);
```



大的逻辑上并没有什么问题，应该也不会出现RHI封装语义不一致的问题。都是一些细节上的约定没搞明白造成的。



