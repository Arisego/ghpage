---
layout: post
status: publish
published: true
title: libRocket在cocos2d-x中使用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 569
wordpress_url: http://blog.ch-wind.com/?p=569
date: '2013-02-24 01:26:42 +0000'
date_gmt: '2013-02-23 17:26:42 +0000'
tags:
- cocos2d-x
---
libRocket是一个MIT协议开源的UI库，它最主要的理念是以css和html的形式来设计界面，可以极大的降低开发界面的成本。


之所以会接触到这个库是因为cocos2d-x的ui库可以说是正在建设中的状态，用起来多少有些不顺手。这个ui库用起来确实不错，只是最后和我的有所相差，经过考虑之后还是放弃了。不过这里还是把一些经验上的东西分享出来，希望能够对用的童鞋有所帮助。


libRocket本身是与显示层独立的，也就是说只要实现了相关接口，理论上它可以在所有的设备上运行。


首先是关于librocket自身的编译，这个库比较新，可以正常的在vs2010下编译通过。在编译过程中可能会需要freetype，如果想要正常的使用自带的例子程序，还需要zlib和libpng库，总之根据提示添加相应的配置项即可。没有什么特别需要注意的。一切完成之后，编译运行RocketInvader项目，将会看到下面的简易小游戏：


[![rocket_invaders](https://blog.ch-wind.com/wp-content/uploads/2013/02/rocket_invaders-300x206.jpg)](https://blog.ch-wind.com/wp-content/uploads/2013/02/rocket_invaders.jpg)


可以看到作为一个游戏需要的基本的ui组件都已经实现了，而且居然还可以用来实现一个简单的游戏逻辑，不过说实话这个游戏不是一般的变态……点开help可以看到的是整个库最让人满意的地方，就是富文本支持，而且完全是按照htlm标准来写的，用起来十分方便。


到了这一步librocket库基本就搞定了，现在就剩下将它与cocos2d-x相结合了。其实库中本来是提供了opengl的渲染接口的，但是只是简单的对其进行修改会发现完全无法显示，最后查了一下，发现要在es上渲染必须借助shader才行。总而言之直接上代码，虽然想要这么说。还是先解释一下要实现的接口吧。


我们要实现的接口除了消息传递之外总共有两个，分别是systeminterace和renderinterface，作用从字面即可理解。systeminterface的作用是提供基本的时间标定，就是说为librocket提供游戏已经运行的时间。但是cocos2d-x貌似没有提供这个功能，于是自己实现了个，代码如下



```
class CocoSystemInterface : public Rocket::Core::SystemInterface
{
private:
	struct cocos2d::cc_timeval begin;
public:
	virtual float GetElapsedTime(){
		struct cocos2d::cc_timeval now;
		cocos2d::CCTime::gettimeofdayCocos2d(&now,NULL);
		return cocos2d::CCTime::timersubCocos2d(&begin,&now)/1000;
	}

	void init(){
		cocos2d::CCTime::gettimeofdayCocos2d(&begin,NULL); 
	}

};
```

第二个需要实现的是渲染接口renderinterface，其间遇到了个问题，就是shader模式下回默认打开深度测试，所以必须把它关掉。否则在同样使用了深度测试的map等层上就会出现奇怪的显示bug。而且不关闭深度测试时，所有ui绘制将会处在最顶层，这和大多数设计都是冲突的。代码部分请看刚刚建立的[Git](https://github.com/steinkrausls/llibrocket-cocos2d-x)。


关于git库中的代码，只要包含RocketSingle.h就可以将RocketLayer当做普通的layer来使用了，注意由于是shader绘制的，原本的矩阵偏移并没有计算入内，所以setposition和setanchorpoint这类函数是不会其作用的。另外，父类ccsprite没有什么意义，因为不打算继续用了所以没有做下去，因此额外的，事件传递也没有做了。不过显示部分已经完整了。


关于librocket使用中的问题，那就是对中文字符的支持。在对应的Css或者Style中添加下面的配置就可以了。



```
font-charset: U+3300-9FFF,U+0020-007E;
```

但是有一个问题，librocket在对字符编码进行支持时是先将所有的字符图形读入缓存中然后在TextElement中使用的，这是为了照顾在运行时的效率。看下面的调用堆栈就能明显的看出来：


[![librocket](https://blog.ch-wind.com/wp-content/uploads/2013/02/librocket-300x168.jpg)](https://blog.ch-wind.com/wp-content/uploads/2013/02/librocket.jpg)


 


这样的直接结果就是初始化时的时间会变得特别长，因为中文字符的编码区间很大，所以会消耗大量的读入时间。虽然对于稍大型的游戏，只要加入loading界面也就是不到5s的时间。但是对于目前在做的小项目而言，这样长的载入时间对于用户而言是不可理喻的。所以最后便没有采用librocket，而是决定采用cocos2d-x原生的ui。只能下次做英文游戏或是更大型的东西的时候再考虑它了。


