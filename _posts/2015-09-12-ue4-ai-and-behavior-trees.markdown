---
layout: post
status: publish
published: true
title: UE4中AI与行为树
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1519
wordpress_url: http://blog.ch-wind.com/?p=1519
date: '2015-09-12 10:38:57 +0000'
date_gmt: '2015-09-12 02:38:57 +0000'
tags:
- UE4
- AI
---
UE4的AI系统使用行为树作为中心进行，同时搭配场景查询系统帮助AI快速获取周围环境状况。


在UE4中，Pawn是可以由玩家或者AI控制的基础类。通常使用的Character类就是对Pawn类的一个具体实现。


就像玩家通过PlayerController控制Character一样，AI则通过AIController来控制Character。


AIController为AI对Pawn进行操作的核心类，但是AI的主要逻辑是在行为树中进行的。


## 行为树


UE4的行为树实现是事件驱动的，相比逐帧的有限状态机之类的实现，能够更好的控制AI运行的成本。


官方有提供行为树的入门指南，按照[官方指南](https://docs.unrealengine.com/latest/CHN/Engine/AI/BehaviorTrees/QuickStart/index.html)一步一步操作的话，就能初步熟悉行为树的工作原理了。


行为树的节点分为Composite、Task、Decorator、Service这四种。还有一个比较特殊的节点为Root，是行为树执行的起点。其本身是没有属性的，选中Root节点展示的是行为树本身的属性。


### Blackboard


根据官方描述，Blackboard是AI的“记忆”。其中以键值的形式存储各种数值、对象以供行为树使用。


对于行为树而言，Blackboard类是非常重要的类，它是用于行为树本身与“外界”进行交互的媒介之一，同时也是各个节点之间进行数据交互的中介存储器。


### Task


实际任务执行节点，可以通过蓝图或代码进行自定义，官方的入门指南中有对Task进行定义的例子。


引擎自带了一些基本的Task节点可供使用，功能包括移动AI、延时等待以及进行场景查询等。详细的自带节点可以参考[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/AI/BehaviorTrees/NodeReference/Tasks/index.html)。


### Composite


对任务进行组合的节点，目前只有三种：


**Selector**


从左到右执行子节点，直到遇到一个子节点返回成功为止，此时返回成功，其他情况都返回失败。


直观的看，就是选择器，从节点中由左向右找到第一个能够成功执行的子节点，如果没有的话就返回失败。


**Sequence**


从左到右执行子节点，直到某一个子节点返回失败，此时返回失败，其他情况则返回成功，例如全部执行完成则返回成功。


总体而言，就是按序对子节点进行执行，但是如果有一个子节点失败的话，就放弃并返回失败。


**Simple Parallel**


在节点的子任务执行的同时，在后台运行另一个子任务。


可以选择属性来控制是否要等待后台的任务完成，还是在主任务完成时直接结束后台任务。


### Decorator


装饰器，在Task或者Composite中使用，为节点的执行添加条件。


可以自己进行定义，官方也提供了较多的基础装饰器。包括冷却、限时、Blackboard值检测、强制成功等许多常用功能。详细的可以参照[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/AI/BehaviorTrees/NodeReference/Decorators/index.html)。


### Service


服务，只能被附加到Composite节点上。当该Composite被执行时，会按照设定的频率不断的执行。


通常用于更新Blackboard的值，就像官方的指南中，用来更新玩家的位置和引用。


## 场景查询系统


在行为树中，AI可以通过Run EQS Query的Task来对周围的环境进行查询以形成判定。


官方也为场景查询系统的入门提供了指南，可以参考[这里](https://docs.unrealengine.com/latest/CHN/Engine/AI/EnvironmentQuerySystem/QuickStart/index.html)。


### Nav Mesh


Nav Mesh是场景查询系统运行的基础，但是即便不使用Run EQS Query节点，Nav Mesh也是必须的。因为Move to之类的需要寻路的行为树节点也是需要Nav Mesh的生成数据的。


通过按P键可以切换导航网格的生成结果预览，绿色的地方就是生成了路径的地方。


### EQS Testing Pawn


用于对EQS进行调试的节点，将其拖放到Nav Mesh生成区域的相应的位置，就会在该处执行属性中设置的场景查询。


结果的展示通过彩色的球体来表现，蓝色的球体表示失败的或是返回false的布尔查询，由绿到红的颜色区间则对应返回数值的区间变化。


### Generators


EQS的基础节点，用于查询的基础的生成器。


生成器的结果被称为Items，包括返回的实际的Actor以及生成的位置。


当前的几种自带的生成器可以参考[官方文档](https://docs.unrealengine.com/latest/CHN/Engine/AI/EnvironmentQuerySystem/NodeReference/index.html#generators)。生成器是可以通过蓝图或者C++自行定义的。


### Tests


在Generators中使用的节点，对Generators生成的Items进行进一步的测试。以便筛选出想要的结果。


Tests只能通过C++进行定义，当前并没有蓝图实现的方法。


在上面的文档的地址中就能看到当前系统自带的测试节点。


### Contexts


在Generators和Tests中可能会被用到的上下文。在EQS的指南中，就有为Distance测试提供的PlayerContext，方便EQS通过与玩家的距离进行评分。


可以通过蓝图或者C++进行自定义。


## 总结


总体而言，UE4提供的AI系统的逻辑性还是比较清晰的。理解了其逻辑之后，要在游戏中添加AI就比较简单了。


不过要在行为树的基础上实现复杂的AI逻辑还是需要经验和想象力的。


