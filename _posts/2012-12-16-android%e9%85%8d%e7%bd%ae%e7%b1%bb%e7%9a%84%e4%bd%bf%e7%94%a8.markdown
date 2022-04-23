---
layout: post
status: publish
published: true
title: Android配置类的使用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 528
wordpress_url: http://blog.ch-wind.com/?p=528
date: '2012-12-16 12:45:44 +0000'
date_gmt: '2012-12-16 04:45:44 +0000'
tags:
- Android
- 配置类
---
Android本身提供了应用保存配置的机制，虽然有时我们会希望自己来控制配置的过程，但是利用系统自带的配置也是一个不错的选择。


最重要的是，由于是系统自带的功能，所以调用起来比较简单。而不用只是为了一两个变量就自己去写配置文件的读取和写入这些东西。现在写东西比较偷懒，基本每次都是复制下面的代码然后改改就用了。



```
//保存配置信息
SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
SharedPreferences.Editor editor = settings.edit();
editor.putString("preferences", mPreferences);
editor.commit();

//读取配置信息		
SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
String mPreferences = settings.getString("preferences", DEFULT_PRES);
```

关于getSharedPreferences()，第一个参数是配置文件本身的标识，只要提供字符串就可以了。第二参数则是标识配置文件的读写权限的，一般情况下用0就好了，文档对这个参数的描述是这样的：



```
Operating mode. Use 0 or MODE_PRIVATE for the default operation, MODE_WORLD_READABLE and MODE_WORLD_WRITEABLE to control permissions. The bit MODE_MULTI_PROCESS can also be used if multiple processes are mutating the same SharedPreferences file. MODE_MULTI_PROCESS is always on in apps targetting Gingerbread (Android 2.3) and below, and off by default in later versions.
```

操作模式是一个bit flag，具体的值对应关系为



```
MODE_PRIVATE           ---  0000
MODE_WORLD_READABLE    ---  0001
MODE_WORLD_WRITEABLE   ---  0010
MODE_MULTI_PROCESS     ---  0100
```

仔细看一下的话就会发现，正如文档所描述的，只有MODE_MULTI_PROCESS这个标识是API Level11之后才有的。这个设定是为了打开配置文件的多进程同时访问功能，大概是随着android版本和对应设备性能的提升才会出现的设计变更。不过大体上程序都不会异步去访问配置，也很少会有多个程序读取相同的配置文件的情况，所以使用的机会比较少。但是既然是bit flag的话，平时就一直设成4就好了。如果想保险起见的话那就先判定一下就好了。



```
int __sdkLevel = Build.VERSION.SDK_INT;
SharedPreferences __sp = $context.getSharedPreferences(SETTING_NAME, (__sdkLevel > Build.VERSION_CODES.FROYO) ? 4 : 0);
```

 


