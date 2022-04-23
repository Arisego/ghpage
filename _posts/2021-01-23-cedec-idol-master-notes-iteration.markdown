---
layout: post
status: publish
published: true
title: CEDEC IdolMaster笔记-制作事例長期運用篇
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 3220
wordpress_url: https://blog.ch-wind.com/?p=3220
date: '2021-01-23 15:36:18 +0000'
date_gmt: '2021-01-23 07:36:18 +0000'
tags:
- Idolmaster
- CEDEC
---

CEDEC2020上Cygames关于CGSS的分享。







CGSS于2015年9月发布，登场角色数190人。运营到2020年，已经有了很多的迭代经验和功能进步。当前的版本中，资源数量也已经非常丰富：




* SSR服装模型数400以上
* 3D MV收录曲数200以上




演讲的内容主要是发布后版本迭代中的一些开发经验。




## 增加演唱会的真实感




示例：「お願い！シンデレラ (GRAND VERSION)」




演唱会的真实感是什么？




1. 应援声
2. 舞蹈之外的动作




应援声直接社内解决……在公司内招募志愿者的P进行收录。




舞蹈之外的动作，包括




* 舞台间移动
* 向P打招呼
* 角色间交互




为了达到提高真实感的目标，舞台移动以及招呼动作追加了60种以上的动作。




### 舞蹈之外的动作




一般的MV制作流程：




* 以歌曲为单位进行舞蹈摄影
* 舞蹈动作有1~5种(+a)，依据动作和表演等会有所增加




这里没玩过CGSS可能会有点费解，参考图片比较简单。




[![image-20210117113700856_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117113700856_thumb.png "image-20210117113700856_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117113700856.png)


有的歌曲是所有人的动作一样的，有的则每个人都不一样。而CGSS通常是5人一组的，所以是1~5种舞动动作。




「お願い！シンデレラ (GRAND VERSION)」：




* 在必要的地方进行分割摄影
* 为了突出动作的差别，即便是相似的动作也会改变表演动作多次摄影
* 舞蹈动作有3种(+60)




### 角色间交互




让偶像之间进行拍手动作，但是由于身高差可能会够不到……




[![image-20210117113816721_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117113816721_thumb.png "image-20210117113816721_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117113816721.png)


于是引入了IK。引入IK之后就可以解决很多交互问题：




对于存在身高差的角色，可以在不破坏动作的情况下进行交互。例如拍手、牵手等。




对于与场景固定物体交互，可以让角色在同一个位置进行。例如开门、看书、上下阶梯等。




## 演奏乐器




示例：「Unlock Starbeat」




### 体型差别




为了应对身高差的问题，根据身高的比例也有对应比例的乐器。




由于胸围大小有SS/S/M/L/LL的五种类型，让吉他和贝斯的背带位置可以对应的调节。




### 惯用手




提供左撇子用的乐器版本，以及让动作在加载的时候可以反过来。




动作反转加载时，角色的位置会有偏差，通过对摄像的位置也添加分歧来实现。




针对场上角色惯用手的区别，总共有4种摄像分歧：




[![image-20210117115550081_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117115550081_thumb.png "image-20210117115550081_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117115550081.png)


### 动捕方法




邀请参与演唱会的乐队成员进行动作捕捉。




手指的动作部分会由动画师手工编辑，所以手部的动作会另外的进行捕捉。




## 其他改进




### Multi Camera




通过多个摄像进行渲染，并使用mask进行切分。




大大的提高了演出效果。




[![image-20210117120404268_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117120404268_thumb.png "image-20210117120404268_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117120404268.png)


为了减少渲染负担，每个摄像只会渲染自己需要的那个部分。




[![image-20210117120519515_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117120519515_thumb.png "image-20210117120519515_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117120519515.png)


### Chara Motion Overwrite




在舞蹈的过程中，将角色的动画替换为别的动作。




这个其实主要是流程上的改进，原本的流程上，想要替换动作的话，就必须直接调整舞蹈数据，替换起来会很麻烦。负责摄像的人必须频繁的和负责动作的人进行交流确认，导致开发效率低下。




新的流程上，将动画切分成了Clip的形式，所以负责最终摄像的人就可以自由的进行调整，无需多余的交流成本。


[![](https://blog.ch-wind.com/wp-content/uploads/2021/01/ims-character-motion-300x75.png)](https://blog.ch-wind.com/wp-content/uploads/2021/01/ims-character-motion.png)





由于这里用的示例也是「お願い！シンデレラ GRAND VERSION」，所以应当就是前面摄影优化里面提到的分割摄影。




### 风模拟




有风的话会增加很多真实感。




模拟方式并不是基于物理的，而是以发束等为单元，分开时机周期性的添加力。这样的方法可以避免头发和衣服的模拟结果出现混乱，看起来也有随机的感觉。




这里说是担心バラバラ，感觉对于这种动画风的物理模拟，最怕的就是穿模了……




### 时间轴分歧




在特定的条件下，对摄像和动作进行分歧。




用于实现角色固有或者特定组合才会作的特别演出。




[![image-20210117121645737_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117121645737_thumb.png "image-20210117121645737_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117121645737.png)


## 服装




服装对于CGSS的角色魅力表现是非常重要的。有很多服装是为了配合角色的个性而制作出来的，其中也有自带特效的衣服。




服装制作时有两条规则需要遵守：




一、模型面数和贴图数量必须在规定范围内




* 基础颜色贴图一张，光照用贴图两张
* 如何在这个限制中达到表现目标就看各人的本领发挥了




二、必须能够对应所有的分镜、舞蹈动作




* 不能在MV中出现不自然的表现
* 行走、跑步、蹲下、靠近等动作时不能穿模




### 想要带子上的彩虹和星星动起来




示例：CGSS４周年纪念服装




这里面能看到之前说到的三张贴图的作用：




[![image-20210117123623250_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117123623250_thumb.png "image-20210117123623250_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117123623250.png)


由于只有三张贴图所以需要将彩虹和星星的控制用信息放进去。




彩虹的颜色变化写到了Color贴图上




星星的颜色变化信息则分成RPG通道写到了Spec贴图上。




[![image-20210117124654022_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117124654022_thumb.png "image-20210117124654022_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117124654022.png)


最后将控制参数暴露到shader外面，就可以了




[![image-20210117124255198_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117124255198_thumb.png "image-20210117124255198_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117124255198.png)


还有一些其他的特殊追加处理




长裙：在角色的下面添加了额外的碰撞用地板




翅膀：在角色身上添加了碰撞球，让翅膀自动回避




## ドレスコーデ




可以让玩家对服装的部件颜色进行自定义。




[![image-20210117130416518_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117130416518_thumb.png "image-20210117130416518_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117130416518.png)


可以调整颜色提升了表现力。




同时还添加了可以让所有人穿的上下可分开定制的通用服装。对于这种可拆分的通用服装，会根据体型差分制作不同的模型。




### 选色板




CGSS的服装贴图上包含了很多光照和阴影细节，用于体现立体感和质感，以及物体之间的投影和接触阴影，服装上的折痕阴影等。




对于用户自定义颜色，并不是单纯的调整一个颜色




[![image-20210117131345087_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131345087_thumb.png "image-20210117131345087_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131345087.png)


而是需要对于一个可选颜色，对应一组Diffuse(BaseColor)、Specular(光沢色)、Shadow(影色)。




[![image-20210117131458919_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131458919_thumb.png "image-20210117131458919_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131458919.png)


这样可以防止颜色出现破绽。




### 可分离通用服装




采用上下分离式的设计，所有角色可着装，可以添加更多的自由度




[![image-20210117131656334_thumb](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131656334_thumb.png "image-20210117131656334_thumb")](https://blog.ch-wind.com/wp-content/uploads/2021/01/image-20210117131656334.png)


采用分离式设计的主要原因是，对于同一套衣服，需要对应不同的体型准备模型。




当前【身長×体格×胸サイズ】共有17种，而T-Shirt就要作17x4个模型，考虑之后的服装添加的话，成本太高了。




分离的设计可以增加模型的通用性，同时也可以方便之后单独的添加新的部件。




## 3Dコミュ




アイドルマスター シンデレラガールズ スターライトスポット，应该是这个：





https://play.google.com/store/apps/details?id=com.bandainamcoent.cgstarlightspot



最长10分钟以上的场景，12个角色登场。有VR View和GYRO View两种模式。




### 偶像之间自然的交流




根据场景和其中的物品，让偶像之间做出复杂的交流。




在动捕摄影之前，事先对需要作的表演和移动路线进行预演。




预演可以有效的发现剧本和背景中不合理的部分，减少重新拍摄的次数，降低表演人员的负担。




角色和道具之间的位置的正确性，可以有效的提高表演的自然感。




### 让人感觉到偶像的真实存在




角色身上的音效发生点，在脸部/腰/右手/左手/脚上最大有五个。




使用Foley的手法，对动作音、道具音进行录制




引入ResonanceAudio SDK




添加对[Ambisonics](https://en.wikipedia.org/wiki/Ambisonics)格式环境音的支持




对于BGM，会根据场景采用不同的设置方式。




* 像是乐屋这种的，就采用从扬声器中释放的场景内音效
* 设定上是电脑空间的话则采用场景外音效




### 表现偶像所在的世界




在设计预期上




* 希望在场景内有很多偶像登场
* 乐屋中应当会有很多的镜子
* 特殊的世界观也希望能够体现出来
* 在较长的交流中也能够一直看下去而不需要返回现实




当然，为了表现出世界观，想要作的事情总是会有很多。但是必须考虑各种实现的成本。




#### 内存消耗




10分钟的长度以及12个模型，使用到的对话数量和动作数据都很多。




例如3D交流第二话，总共有330个对话，470种SE。




对于声音，将非常驻的声音按块区分，由时间轴来触发加载，在播放完后自动卸载，减少内存消耗。




#### FPS控制




希望保持在60帧




3D交流模式中物体太多导致FPS下降，12个模型同时渲染的负荷很重，VR模式则有额外1倍的消耗。




镜子：3D交流中玩家是不能移动的，对镜子内需要反射的物体进行限定，减少没有必要的绘制成本。




### 迭代效率提升




每一轮迭代的时间将会决定可以试错的回数，减少要素是最后的手段。




以MV的压力测试为例，通过Jenkins对以下的步骤进行自动化：




* apk/ipa的资源构建
* 连结到的设备上的自动执行
* 收集执行结果到Kibana进行分析



