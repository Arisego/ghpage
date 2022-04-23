---
layout: post
status: publish
published: true
title: 关于VS2012运行时的crtIsTailoredApp出错bug
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 613
wordpress_url: http://blog.ch-wind.com/?p=613
date: '2013-08-02 13:05:59 +0000'
date_gmt: '2013-08-02 05:05:59 +0000'
tags: []
---
前段遇到了这个问题，个人感觉有点奇葩。


在网上也基本找不到什么资料，后来终于解决，于是拿出来分享下，希望对同样碰到这个问题的童鞋有所帮助。


问题是这样的，由vs2012Release输出的程序。在本机(win7)可以运行，在另一台电脑(xp)上也可以运行。但是把程序搬到另一台win7电脑上时却没有办法运行。报错提示是这样的：


[![错误提示](https://blog.ch-wind.com/wp-content/uploads/2013/08/201308021255441-300x129.jpg)](https://blog.ch-wind.com/wp-content/uploads/2013/08/201308021255441.jpg)


大体意思大家大概都能看出来，就是在dll上没有办法定位到__ctrIsTailoredApp的入口点。这种问题一般都是由于dll的版本不对引起的，可是一般情况下根本就不会出现这个问题，因为这个dll是vs2012运行库里面的。在经过一番思索之后我发现了问题的所在，那就是我自己的vs2012是只打到update2补丁的，而微软官网的运行库是update3的。这个上面的不同就比较让人郁闷了，以前我们的习惯是，vs的运行库不论版本怎么变更基本编译出来的东西都是能用的。但是显然的，对于vs2012的运行库不是这样的。因为我将vs升到update3之后就没有问题了。


将两个版本的msvcr110放到exescope中会发现其版本号确实是不同的，大概是因为vs2012本身在发布的 时候由于某些大家都知道的方面设计上有些超前，导致后来大更新不断，以至于各个版本之间出现了比较大的断代问题。这个问题有两个解决方案：


1.把自己的vs升到最新的update3.


2.按照传统将自己vs目录中的redistribute连同程序一起发布，当然能静态编译是最好了。


这样的话就能保证程序在编译时使用的运行时库和程序被运行时会调用的运行时库版本一致了。这里吐槽下，既然有这个问题，微软居然直接不提供update3之前的运行库的官方下载，让我等不关注版本变迁的盗版用户小白很是受到伤害啊……虽然是自找的。


