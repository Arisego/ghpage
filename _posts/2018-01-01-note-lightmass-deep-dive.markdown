---
layout: post
status: publish
published: true
title: 深入LightMass系列笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2239
wordpress_url: http://blog.ch-wind.com/?p=2239
date: '2018-01-01 23:59:33 +0000'
date_gmt: '2018-01-01 15:59:33 +0000'
tags:
- UE4
- Lighting
---
UE4使用Lightmass对光照进行预计算，以节省动态光照计算的成本。


本文是EpicJapan的LightMass Deep Dive系列的总结，与之前更新的文章有重叠的地方可能会略过，如有需要可以参看[[原始的PPT](https://www.slideshare.net/EpicGamesJapan/lightmass-lightmap-epic-games-japan)]。


内容本身的UE4版本为4.13，当前UE4版本4.18。


其实这个系列讲的内容并不多，只是使用了很多配图，让人能非常直观的对Light Mass的计算进行理解。


预计算光照主要的组成部分有3个：Light Map、Shadow Map和Precomputed Light Volume。


## Light Map


光照贴图是静态光照最重要的部分，当前关卡生成的光照贴图可以在World Settings一栏里面看到。


### Point/Spot/Directional Light


#### Direct Light


直接从光源所在处打出射线进行计算，对于有光源半径的光而言会多做一些计算。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image.png)


#### Indiret Light


间接光照的计算核心是光子映射算法，详细的实现分为以下步骤


##### Photon Mapping


首先从光源向周围放射光子，对命中表面的光子进行记录，并按照一定的条件进行光子反射。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-1.png)[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-2.png)


这个反射过程会重复多次，最终形成在物体表面的很多光子数据。


##### Final Gathering


从纹素出发，沿着光子的反射路径回溯性的收集光照信息。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-3.png)


在收集过程中并不会从自己周围收集，因为这部分的光照已经在直接光照中计算过了。


##### Irradiance Caching


要对场景中所有的纹素进行收集的话，不仅花费时间，且由于反弹并不是均匀的所以会有很多噪点。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-4.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-4.png)


所以这个时候就需要将收集的光照缓存起来，然后以插值的方式来收集光照数据。


当然上面的只是大致过程，其中还有很多细节上的优化，例如：


**Adpative Samping**


如果在收集时，光子路径的相邻点间隔较大的情况，会增加额外的射线进行光照数据收集。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-5.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-5.png)


### Sky Light


天空光照稍微有些不同，并不会进行Photon Mapping。


#### Direct Light


在Final Gathering时直接将SkyLight当作二次反射的光源进行光照收集。


对于场景中窗口过小导致收集到的间接光照不足时，可以添加LightMass Portal以放出更多的收集射线。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-6.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-6.png)


#### Indirect Light


天空光的间接光照则是对光照进行一个更小规模的MiniFinalGather。


不过这个说法可能不适用于当前版本，因为从4.18开始，天空光也可以接收多次反弹的间接光照了。


## Shadow Map


这个系列并没有介绍阴影贴图，Shadow Map并不是为Static Light准备的，而是为Stational Light准备的。


在进行光照计算时，每一个动态的物体，都会根据自己的bound box与stational light的朝向关系，将Shadow Map合成到光照运算结果中去。


因此，如果Stational Light影响的动态物体特别多的时候，其效率是非常低下的。有时候考虑直接换为Dynamic Light反而更好。


## Precomputed Light Volume


这个主要是在场景中生成预计算的间接光照缓存点，这样动态的物体就可以从中取得数据并插值得到自己的间接光照。


插值的方式中，ILCQ Point是根据物体当前的位置进行的，所以如果物体有一定的大小且移动速度较慢的话，就容易产生可见的阴影跳变。相对的ILCQ Volume由于使用多个点进行插值处理，运算成本会变高，尤其是对于非常大的物体。


### 缓存数据


PLV的数据是具有方向性的球谐函数


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-7.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-7.png)


在计算的时候分为上下两个半球进行计算


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-8.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-8.png)


计算方法是，在进行光照预计算的时候，对指定的缓存点，将直接光照与Final Gathering的值缓存起来。


### 缓存点的生成


生成方式总共分为三种


#### Surface Light Sample


这个是最单纯的，从每个Mesh的表面沿着法线方向进行缓存点添加。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-9.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-9.png)


可以通过配置文件进行行为修改。


#### Detail Volume Sample


在世界中拖放Lightmass Character Indirect Detail Volume生成的缓存点。


这个Volume拖放之后会在内部生成缓存点。


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-10.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-10.png)


#### Uniform Volume Sample


Lightmass Importance Sample这个Volume是在场景内全局性的生成缓存点


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/01/image_thumb-11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/01/image-11.png)


## Usage


演讲中介绍了不少静态光照的配置技巧，这里只列出之前没有列出过的。


**反光板**


直接将聚光灯打到一块板子上，只让间接光照计算影响到静态光照计算。


**Compress Lightmaps**


这个光照贴图的压缩是有损的，如果关掉的话效果会变好，但是贴图体积会放大4倍左右。


**Lightmap Resolution**


光照贴图的分辨率在配置时要注意，比最小的纹素小的光照细节无法被捕捉。


Static Lighting Level Scale


这个配置会影响到整个LightMass的计算，同样的如果导致小于RecordRadius的光照细节无法被捕捉。


**Use Emissive For Static Lighting**


这个的光照计算和天空光一样是不会进行Photon Mapping的。


 


以及最后给出的配置和性能影响


* Static Lighting Level Scale = 1→ 0.1
* Num Indirect Lighting Bounces =3→20
* Indirect Lighting Quality = 1→10
* Indirect Lighting Smoothness=1.0→1.0
* Lighting Quality = Production Build Time


光照计算时间15m57s →4h10m24s


不过这个的演讲者是做建筑展示的，所以对静态光照的要求比较高，并没有考虑到游戏运行的成本。


## 总结


了解了静态光照的计算方法之后，在对其进行调整，尤其是要修改config.ini的时候非常的有帮助。


至少比盲目的调节选项然后等待漫长的光照计算之后来观察结果要好很多。


