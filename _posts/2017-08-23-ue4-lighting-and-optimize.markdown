---
layout: post
status: publish
published: true
title: UE4光照及优化
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1952
wordpress_url: http://blog.ch-wind.com/?p=1952
date: '2017-08-23 15:00:16 +0000'
date_gmt: '2017-08-23 07:00:16 +0000'
tags:
- UE4
- Rendering
- Lighting
---
UE4的光照系统很强大，效果也很好，但是在场景复杂度较高或者开放世界的情况下，很容易造成性能瓶颈。


当前UE4版本为4.17.1。


光照系统的大部分应用都可以在[[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/LightingAndShadows/index.html)]中找到，这里的大部分内容是对官方Lighting系列[[视频1](https://www.youtube.com/watch?v=jCsrWzt9F28)][[视频2](https://www.youtube.com/watch?v=nm1slxtF_qA)]的总结。


## 静态光照


UE4的静态光照是在光照构建中进行预计算的部分，会对预计算的光照结果进行存储，例如光照贴图、阴影贴图这样的形式，可以在运行时支付较低的效率而获得较好的光照结果。


静态光照可以在世界设置中可以进行关闭


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-7.png)


### Lightmass Importance Volume


这个是预计算光照用的Volume，LightMass的光照计算在点击“构建光照”之后会产生光照贴图。


控制良好的预计算光照可以让场景变得美观的同时降低动态光照的成本，但是在控制不好的时候就会造成贴图空间爆炸。


LightMass Importance Volume是用来控制预计算精度的，很明显的一点是，加上之后在空间内部会生成更多的间接光照缓存点，使得间接光照的效果变得更好。


### SSAO


世界设定中还有一个LightMass相关的功能


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-8.png)


LightMass这里的AO就是SSAO，由于是工作在屏幕空间的后期计算，要进行探索的话可以在PostProcess中进行调整测试。


还有一个额外的选项


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-9.png)


打开之后可以使得PrecompoutedAOMask材质节点变为有效，这样就可以使用AO的数据来对场景内物体之间的混合效果进行控制。


详细的可以看这个选项的注释。



更正：


这里是错误的，LightMass选项里的AO选项是给预计算光照的，Generate Ambient Occlusion Material这个选项打开的PrecompoutedAOMask也是预计算光照的结果反映到材质中的方式。SSAO是工作在屏幕空间的一种PostProcess效果，与预计算光照是不同的。


感谢@裕 的指正~



### 间接光照缓存


间接光照缓存的作用是通过缓存某个点的间接光照，将其作用于经过该处的动态物体上，以获得好的间接光照效果。


在Movable的物体以及角色上可以对间接光照的计算类型进行设定


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-10.png)


ILCQ为Point的时候就是一个点，Volume就是很多点。


在物体移动时，这些生成的点将根据自己所处的位置，通过周围的间接光照缓存点进行插值并计算出间接光照。


虽然插值点多的话间接光照效果会变好，但使用何种形式需要根据性能和需求进行权衡。


可以使用



> r.cache.drawinterplotionpoint 1
> 
> 
> r.cache.updateeveryframe 1
> 
> 


这两条指令来预览缓存插值点的生成。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-11.png)


对于角色的光照缓存还有一个另外的


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-12.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-12.png)


用于提高区域计算精度的体积。


### Capsule Shadows


这个是专门为骨骼模型设计的投影优化方式，在骨骼的Lighting属性中能够看到相关的选项：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-13.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-13.png)


要使用必须在骨骼网格中指定用于投影的Physics Asset。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-14.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-14.png)


使用这种方式可以防止一般较为复杂的角色模型在进行投影计算时产生过多的消耗，尤其是同一个场景内有很多角色模型的情况。


## 光照问题


在光照的结果上，有时会出现并非预期的结果。在进行场景构建、模型制作时需要预先做好一些预防工作。


### Indirect Seams


间接光照的运算结果在模型之间的接缝处会出现不自然的裂缝


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-15.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-15.png)


这种的主要原因是两个Mesh之间虽然是平滑的，但是在间接光照进行阴影计算时并不知道这些信息。


可以通过在世界设置中调节间接光照的质量和平滑度来减少这种现象


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-16.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-16.png)


提高间接光照质量会加重光照构建的成本，而如果过于提高平滑度的话，会导致间接光照的很多细节被丢弃。


所以一个更好的解决方案是，在构建关卡时，如果是一个平滑的面的话就直接使用一个整体的模型来做，而不是用好几个模型拼接而成。


### UV Seams


这个是由于模型的UV没有很好的接合造成的，由于邻近的顶点在UV上并不连接，在进行间接光照计算时，产生的结果就没有办法很好的利用这些信息。


根据官方的说明，提高间接光照质量并不会解决UV Seams的问题。


这个问题更多的是在建模上进行解决。


不要生成这样的UV


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-17.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-17.png)


而是尽量保持邻接信息


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-18.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-18.png)


### Bleeding


光照泄露的主要原因是光照贴图的分辨率造成的


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-19.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-19.png)


像这样室外的光照感觉上就像直接透过到了室内，显然不符合预期。


虽然通过修改光照贴图的分辨率来进行应对，但是这样就相当于绕过了问题的来源。


更根本的解决方法是，让“地板”与房间的尺寸匹配，这样在光照计算时，房间的地板就不会接收到外部的光的光照计算。


## TIPS


UE4的光照系统中有一些通用的工具和功能，可以方便的对光照进行布置。


### LPV


Light Propagation Volumes目前处于开发阶段，但是在光照相关的属性的很多部分都能看到它的对应属性。


这个体积主要的作用是，在动态光照中对间接光照之类的效果进行光线传播运算。


功能上非常的有用，因为有时候确实会需要在动态光照中有间接光照这样的效果来加强场景的真实性。


更多的内容可以参考官方的[[LPV文档](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/LightingAndShadows/LightPropagationVolumes/index.html)]。


这里需要注意的是LPV虽然从命名上看起来像是一个体积控件，但是其实并不存在这样一个Volume，其属性是在PostProcess中进行修改的。


在开启之后可以在


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-20.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-20.png)


打开LPV的属性可视化。


### CSM


Cascade Shadow Map是UE4阴影贴图的使用方式，在Far Shadow、Dynamic Shadow和Static Shadow中使用了这个机制。


这个机制的主要作用是，在不同的距离层级，使用不同精度的阴影贴图。


在设定CSM的同时，还可以对过渡效果进行调节


[![clip_image001[15]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00115_thumb.png "clip_image001[15]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00115.png)


对应的CSM数量被设置为0的话，就相当于关闭了相应的阴影类型。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-21.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-21.png)


CSM的计算范围可以通过在显示中打开


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-22.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-22.png)


这个选项来进行预览


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-23.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-23.png)


类似这样，可以在调节相关属性的时候有一个好的可视化工具。


### Emissive Material


自发光颜色的材质是通过HDR来实现泛光效果的，因此它本身并不参与光照运算。


通过在使用了自发光颜色材质的物体上打开


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-24.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-24.png)


可以让其能够照亮周围环境，但仅限于静态光照。当物体是Movable时，没有办法开启这个选项。


视频中实现的类型于动态照亮的效果是通过在物体上绑定一个改变GI的PP来实现的，然后两个PP之间的Blending就会改变空间内的灯光造成的影响，形成类似于被物体本身照亮的效果。


### Error Coloring


错误着色可以用于排查静态光照计算时报出的UV方面的错误，因为光照构建时只是提示物体上有UV的Overlapping和Wrapping有时候还是很难找到对应的问题的，尤其是模型并不是自己构建的情况下。


[![clip_image001](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image001_thumb.png "clip_image001")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image001.png)


打开这个选项之后要将光照质量调整为预览，才能看到错误着色。


[![clip_image001[5]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0015_thumb.png "clip_image001[5]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0015.png)


重新构建一次光照，就能看到


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-25.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-25.png)


橙色的部分是Overlapping而绿色的部分是Wrapping。


### Volumetric Lighting


这是类似于聚光灯的[[Light Shaft](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/LightingAndShadows/LightShafts/index.html)]的效果，官方的Blueprint示例工程中也有类似的名为GodRay的效果实现。


在引擎内容中搜索LightBeam就能找到


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-26.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-26.png)


这里的模拟方式是在类似光束效果的模型上贴上一个Translucent贴图。


虽然半透明材质的消耗比普通的材质高，但是在实现光束效果上却是很高的成本节约。


## 动态光照


动态光照是实时计算的光照，如果关闭了光照预计算的话，所有的光照计算都是实时生成的。如果没有启用LPV的话，静态光照中的间接光照缓存无法使用的情况下，有时候也会造成画面质量的下降。


### Distance Filed


距离场在动态光照的优化和填补中有相当大的作用，距离场的基本原理就是在模型的周围向外扩散而成的距离场。


[![clip_image001[7]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0017_thumb.png "clip_image001[7]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0017.png)


距离场的生成需要在项目设置中进行开启，虽然距离场生成后会产生额外的存储成本，但是可以在动态光照优化中起到很大的作用。


利用距离场生成的阴影的成本会比动态光照的阴影低很多，通常情况下，将动态光照的作用范围调小


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-27.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-27.png)


然后在基本上看不到阴影差别的距离上使用距离场生成的阴影进行替代可以很好的降低动态光照对场景的消耗。


事实是，大部分情况下，动态光照的阴影和距离场的阴影，在中距离上基本上没有什么太大的差别。


#### Distance field resolution


Distance field resolution这个属性是用于调整距离场的精细度的，在Mesh自己的设置里面可以找到。


稍微增加一点就会有明显的提升，重要的是平衡的选择，远距离物体完全没有必要性。


[![clip_image001[9]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0019_thumb.png "clip_image001[9]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image0019.png)


#### RayTraced DistahceField Shadows


对于需要柔和的渐变光照的情况，可以使用


[![clip_image002](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image002_thumb.png "clip_image002")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image002.png)


打开只有在下面的属性可以调节因距离而变化的边缘阴影的效果。


#### SelfShadow


当物体的自身投影出问题的时候可以试着调节


[![clip_image003](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image003_thumb.png "clip_image003")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image003.png)


来进行修正。


#### Two-Sided Distance Field Generation


一般在Foliage上会使用到的属性，如果觉得生成的DF数据形成的投影不够浓密的话，可以打开这个选项。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-28.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-28.png)


双面计算会产生额外的成本，在有必要的情况下使用即可，不过也可以考虑使用下面的替代物品。


#### 距离场替代物品


使用一个替代的物品来计算距离场，通常也是在Foliage中使用到，可以降低树的面多造成的性能影响。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-29.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-29.png)


### Contact Shadow


这个是Light Source中的属性


[![clip_image001[11]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00111_thumb.png "clip_image001[11]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00111.png)


设置成0以上的值的话就会进行接触阴影的计算，这个计算时工作在屏幕空间的。


由于是工作在屏幕空间，在物体距离较远时阴影的损失也不会变的严重。


可以用于填补默认的级联阴影的距离损失，也就是说，可以调低级联阴影，降低阴影消耗。


### Light Function


光照函数相对阴影计算而言的成本是很低的，所以在实现云的投影的时候通常会使用光照函数。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-30.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-30.png)


官方的优化建议中也有说明，如果多个组合光源的效果可以用光照函数来替代的话，可以很好的提高效率。


### Distance Filed AO


这个是天空光特有的功能，天空光可以利用距离场的生成数据进行环境光的投影计算


[![clip_image001[13]](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00113_thumb.png "clip_image001[13]")](https://blog.ch-wind.com/wp-content/uploads/2017/08/clip_image00113.png)


只有当天空光是可移动的时候才能使用。


### IES


IES的成本比光照函数还低一些，可以实现一些低成本的投影效果。


有助于关闭不必要的光照投影，例如只是用于模拟灯罩、遮挡的投影，或者干脆是车灯这样的效果。


IES的使用可以参照官方的[[IES文档](https://docs.unrealengine.com/latest/CHN/Engine/Rendering/LightingAndShadows/IESLightProfiles/index.html)]。


### Far Shadow


这是与通常的静态光照和动态光照相反的一种阴影模式，主要是为了保持在远景上的投影来使得场景看起来更有真实感。


通常在Landscape上开启使用，对于需要的物体，也可以开启使用。注意，要在对应的光源上也开启Far Shadow才行。


### 设置


在项目设置中个，有一个关闭静态光照的总开关


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-31.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-31.png)


不过通常在对应的地图的世界设置中进行关闭更加具有可控制性一些。


还有针对移动端CSM的专有设定


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-32.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-32.png)


## 优化


UE4提供了一些用于场景优化的工具，像是LOD和Mipmap这样的机制在场景优化的时候就比较实用。


### Cull Distance Volume


这个是一个用于裁剪的体积，其内部的物体在远离玩家的时候回直接被裁剪掉，不参与渲染。


由于动态光照的性能消耗与参与计算的面数成比例，这样就可以起到一定的优化作用了，思路基本和LOD相同。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-33.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-33.png)


CullDistance的属性比较简单，每个数组的元素表示的是物体大小小于该值的，应该在里玩家多少距离处隐藏。这里的数据虽然会被按照顺序使用，但是实际上打乱顺序也没有关闭。


不过有两个问题需要留意


首先，必须在PIE以上的状态Cull Distance Volume才会起作用。在编辑器内必须按G进入游戏预览模式才能看到效果。


然后，必须有一个cull distance为0的设置赋给一个大的size，如上面的(1000,0)，否则当距离到达最远的Distance时，会裁剪掉内部的所有物体，包括天空球、大气雾这些实际上没有Size的物体。


### Foliage Culling


Foliage的Culling属性可以在每一个独立的Foliage上进行设置


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-34.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-34.png)


如上面的Cull Distance设定，在没有使用PerinstanceFadeAmount的情况下，采用的裁剪距离时1000。


从500~1000的范围内PerInstanceFadeAmount由1~0进行变化，这样就可以在材质中对Foliage进行一个Fade的过程，而不是直接突兀的从边界消失。


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/08/image_thumb-35.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/08/image-35.png)


使用PerInstanceFadeAmount配合Translucent的Mask替代方案DitherTemporalAA，可以实现较好的过渡效果。


## 总结


光照是渲染中的一个很重要的部分，如果没有处理好的话，不仅场景不好看，还极其的影响效率，是非常需要注意的一个部分。


