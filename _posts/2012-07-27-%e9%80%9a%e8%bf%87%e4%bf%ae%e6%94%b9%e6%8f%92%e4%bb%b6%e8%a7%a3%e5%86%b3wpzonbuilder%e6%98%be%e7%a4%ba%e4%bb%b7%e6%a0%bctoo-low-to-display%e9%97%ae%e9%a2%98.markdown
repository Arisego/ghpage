---
layout: post
status: publish
published: true
title: 通过修改插件解决wpzonbuilder显示价格too low to display问题
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 489
wordpress_url: http://blog.ch-wind.com/?p=489
date: '2012-07-27 21:49:31 +0000'
date_gmt: '2012-07-27 13:49:31 +0000'
tags:
- wpzonbuilder
- 自寻烦恼
---
今天用wpzonbuilder碰到个问题，本来是拉取过来的amazon价格数据，却不知道为什么显示着too low to display。


虽然是个细节上的问题，但是明明在网页说明上就给出了price range，list price超出了这个范围也没什么，但是关键的sale price却不显示这样就给人一种不靠谱的感觉。


于是试着google 了一下，发现这似乎是amazon的政策造成的。主要目的是为了保护amazon合作方的利益，防止打折的非常优惠的价格被到处扩散云云。也就是说没什么办法了，amazon的api给的就是too low to display。但是这样实在是太影响咱这个虽然很小但是也勉强算是个站的用户体验了吧！


于是翻起了wpzonbuilder的代码，打算对其进行改造，至少看着美观点。顺便把经验分享下，方便遇到同样问题的童鞋。


wpzonbuilder的显示需要修改的部分有两块，一个是在templates文件夹下面的对应的显示接口，我改的是inlinesingle.html这个，因为只用到了它；另一个是插件目录下的amzntemplates.php。


在amzntemplates.php里观察一下，在代码将价格和链接数据读取出来并输出之前对其进行检测并修改就行了。具体而言可以在代码的259行后插入如下代码：



```
if ($LowestNewPrice == "Too low to display.")
{ 
$LowestNewPrice = "<a style=\"color:red\" rel=\"nofollow\" target=\"_blank\" href=\"".$DetailPageURL_LINK."\" class=\"amzn_multititle\">Too Low to Display Here! Click me and goto Amazon to see it.</a>";
 }
```

这样一来就改成更加妥当的形式了，貌似wpzonbuilder是有官方支持文档，不过我是db用户所以就…。另外插件如果升级之后代码修改就会失效，虽然wp都这样姑且是需要提醒一下的。不过db用户不用担心这个问题呢。


[![](https://blog.ch-wind.com/wp-content/uploads/2012/07/00.jpg "00")](https://blog.ch-wind.com/wp-content/uploads/2012/07/00.jpg)


上面的就是显示结果了，没学过网页设计，所以效果不是很好呢，不过自己满意就行了。


