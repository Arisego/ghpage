---
layout: post
status: publish
published: true
title: UE4资源重定向
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 1632
wordpress_url: http://blog.ch-wind.com/?p=1632
date: '2017-04-26 22:14:24 +0000'
date_gmt: '2017-04-26 14:14:24 +0000'
tags:
- UE4
- ActiveClassRedirects
---
在混合使用C++和蓝图进行编码时，有时会因为代码的变动而导致蓝图无法正确的识别基础的类。此时可以使用资源重定向进行解决。


当前UE4版本4.15.1。


如果是在内容管理器中进行删除、重命名、移动等操作的话，引擎会尝试自动执行重定向，或者给出提示。只要不操作失误的话就不会有什么大问题。


但当C++定义的基类由于各种原因不存在时，由于引擎不会给出提示，有时就会出现灾难性的结果，比如这样：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-11.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-11.png)


或者更严重的，变成这样：


[![SNAGHTMLf68450](https://blog.ch-wind.com/wp-content/uploads/2017/04/SNAGHTMLf68450_thumb.png "SNAGHTMLf68450")](https://blog.ch-wind.com/wp-content/uploads/2017/04/SNAGHTMLf68450.png)


由于蓝图的基类不存在了，这时候就算强行打开蓝图类，也有可能会变成奇怪的情况。引擎本身无法识别基类，蓝图的类型判定就会出错，即便有替换的目标类也无法进行指定。想要将基类指定为AActor都无法进行。如果此时有作为替换的类的话，就可以求助于资源重定向了。


## 重定向配置


资源重定向可以在配置文件DefaultEngine.ini中设定，这个文件位于项目目录下Config目录中。


在其中找到[/Script/Engine.Engine]，如果没有的话直接添加即可，按照如下格式添加即可：



```
[/Script/Engine.Engine]
+ActiveClassRedirects=(OldClassName="OceanManager",NewClassName="/Script/Ocean.OceanManager")
+ActiveClassRedirects=(OldClassName="WaveSetParameters",NewClassName="/Script/Ocean.WaveSetParameters")
+ActiveClassRedirects=(OldClassName="WaveParameter",NewClassName="/Script/Ocean.WaveParameter")
```

其中OldClassName为旧的类名称，不用指定Package名称，而NewClassName则必须指定Package名称。


Package名称一般就是项目的名称，如果类是定义在插件中的话，就是插件的名称。上面的格式中，Ocean就是项目的名称。


重定向配置还有一个额外的参数：



```
+ActiveClassRedirects=(OldClassName="MyClass",NewClassName="MyClassParent",InstanceOnly="true")
```

可以为重定向提供一个过渡的阶段，只有类的实例会被替换成新的类，而原有的类依然继续存在。


## 合并重定向


包括内容管理器自动进行的重定向在内，长期累积之下，项目中就会累积很多重定向，这个时候就需要用到清理功能。清理重定向的功能在内容管理器中就可以使用，在任何一个目录上点击右键就可以看到：


[![image](https://blog.ch-wind.com/wp-content/uploads/2017/04/image_thumb-12.png "image")](https://blog.ch-wind.com/wp-content/uploads/2017/04/image-12.png)


同时也可以使用命令行工具进行清理



```
UE4Editor.exe "E:\Ues\Trace" -run=FixupRedirects –testonly
```

[![SNAGHTML9585f4](https://blog.ch-wind.com/wp-content/uploads/2017/04/SNAGHTML9585f4_thumb.png "SNAGHTML9585f4")](https://blog.ch-wind.com/wp-content/uploads/2017/04/SNAGHTML9585f4.png)


不过在有的时候还是会出现C++类重新指定失败的情况，所以一般在重定向操作之后，如果已经没有必要继续使用旧类的情况下，当时就把重定向清理掉比较好。


