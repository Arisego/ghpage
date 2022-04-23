---
layout: post
status: publish
published: true
title: Blog迁移准备中
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2560
wordpress_url: https://blog.ch-wind.com/?p=2560
date: '2018-09-08 23:37:20 +0000'
date_gmt: '2018-09-08 15:37:20 +0000'
tags:
- lnmp
- wordpress
---
最近不知为何托管的主机商那边似乎宕机了比较长的时间的样子。


原本在主机这一块，一直都没打算再去折腾。因为没有以前那么多时间来照顾这方面了，所以前段发现主机经常访问不稳定的时候，也没有太过于在意，只是将域名托管到了CloudFlare。


## 问题依旧


CloudFlare这边虽然访问速度会有所下降，但是至少能够提供一定的稳定性保证。毕竟这边虽然一直有在更新，但是每天的访问量其实并不高，基本都是靠搜索引擎的自然流量。所以偶尔访问不稳定的话，也不会有什么太大的问题。


但是没想到似乎还是出了些问题，这周连续好几天回家之后发现怎么都连不上网站，虽然连不上是常见的状况，但连续无法访问还是有些在意。


然后，发现现在的网络环境真的是和以前完全不一样了。


首先，一个比较常见和还算可以理解的一点，就是CloudFlare对网络状况的虚报。基本上CloudFlare这边看到的访问量和Google Analytics的数据比起来会多出一些。


但是问题是，实际从9月1日起，网站这边在很多区域就已经进入完全无法访问的状态了，可以从GA的数据看到：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image.png)


但是同期CloudFlare的数据是这样的


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-1.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-1.png)


完全没有看到网站的可访问性出了问题，仿佛一切都是那么的美好。


另外比较惊讶的一点是，Google WebMaster不知什么时候改版了，目前的WebMaster是不会通知你网站已经宕掉的。所以像我一样，依赖于WebMaster的宕机通知来了解网站情况的童鞋们一定要留意了。


起初有怀疑是CloudFlare这边的问题，所以中途将NS记录重新指向了DNSPod。但是过了一两天发现还是有问题，于是直接修改Hosts，发现果然还是虚拟主机商挂掉了……


怎么说呢，这个问题还是比较厉害的。由于是老牌主机商了，所以当时也没在意。后面转移网站数据的时候发现，最新的数据似乎丢失了。估计应该是主机商那边连续性的遇到了什么问题。但是现在每天都没有什么时间来搞网站这方面，更加没有精力再到处去找新主机商。原本也打算就这样算了，但是没想到主机商那边也是从头到尾没有一点反应。想来或许是认为会在虚拟主机商这里托管的其实都是些无人问津的小站，所以站长不主动去敲客服，就会假装什么都没有发生过。这样的态度难免让人有些心寒，搞得好像是贪便宜将网站挂到虚拟主机商这边的自己的不对一样了。


诚然会挂虚拟主机商的网站大抵都没有好好的在进行商业运营，很多网站最多坚持个一两年，等域名到期了也就自然消灭了。因此虚拟主机商这边都会有很严重的超卖现象，就算偶尔出现几个小时的无法访问，说实话也很少会被注意到。但是我认为这样的服务态度是不行的，会自己花精神去买域名、买空间、搭网站、然后去写些什么，且不论之后会不会放弃，至少站长本人在这件事情上是付出了真心的努力的。出现了如此严重的连续宕机，甚至数据都是好久之后才能恢复的情况，连一封告知都没有，就这样假装岁月静好实在是让人无法接受。


因此，我打算重新迁徙到别的地方去，但是现在真的没有时间精力去找空间了，所以估计会花费比较长的时间。好在手里有一张腾讯云的优惠券，于是干脆的先跑到腾讯云上避难了。


## 迁移记录


为了方便下次迁移时能够快速的动作，而不是像这次一样要重新去翻以前的笔记以及到处搜索，将这次的过程完全记录了下来。


首先还是使用最习惯的Ubuntu Lts，当前版本是16。


开通之后用Winscp接入putty直接登录，然后首先设定su密码。



```
sudo passwd
```

之后直接su，这样虽然有些不符合规范，但是确实比较方便。


### LNMP


接着就是lnmp的安装，虽然之前比较习惯与用别人分享的脚本，但是一来不是马上能找到。二来有的脚本是要自己下载源码进行编译的，有的会给出很多选择。


但是我现在不想选择，我只想说，「一番いいのを頼む 」。


反正我就架个WordPress，顶多接入个Phalcon，有必要选那么多吗？直接上版本号最高的官方编译版就好了~


首先，违反常识的先装php，因为要用nginx，所以不直接装php，而是装php-fpm，要不然会给你带个Apache。



```
add-apt-repository ppa:ondrej/php
apt-get update
apt-get install php-fpm
```

然后上nginx



```
add-apt-repository ppa:nginx/development
apt install software-properties-common
apt-get update
apt-get install nginx

```

最后我也不知道MySql哪个版本好，干脆上了还有印象的MariaDB。



```
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
sudo add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://ftp.yz.yamagata-u.ac.jp/pub/dbms/mariadb/repo/10.2/ubuntu xenial main'

apt update
apt install mariadb-server
```

装完以上这些，直接访问服务器IP应该就能看到欢迎页面了。再稍微写个phpinfo()的测试页面就知道php正不正常了。


一般情况下默认配置的nginx基本不可能挂掉，顶多就是php解析有问题。这个时候直接去改nginx的默认配置文件就可以了，在/etc/nginx里面。


不需要急着去查资料，基本上nginx官方已经给写好了，只要按照注释里面的提示去掉一些注释就可以了。改完记得重启服务，配置不对基本就重启不了~



```
service nginx restart
```

比较容易出问题的是php-fpm的名称，很容易坑，因为安装的时候叫php-fpm，但是实际使用时却是：



```
fastcgi_pass unix:/var/run/php/php7.2-fpm.sock;
```

这个真的很坑，因为nginx的配置里面没有说明，看命名方式似乎会跟着php的版本变？


### Wordpress


这个直接下载解压了，WordPress是业界知名安装简单的，虽然迁移网站会有些麻烦，不过也只是移动文件而已。



```
wget https://wordpress.org/latest.tar.gz
tar -xzvf latest.tar.gz
```

为了方便，首先将文件夹权限设一下



```
chown www-data.www-data . -R
```

这里有个问题，为了方便其实我的目录权限其实777的，但是有的时候对于wordpress还是不足够。


有时候PHP的disable func也会导致问题，不过这次并没有遇到。


然后就是自己建立数据库了，虽然CPanel的主机商比较爱装phpMyAdmin，但是自己用的话推荐这个[[adminer](https://www.adminer.org/#download)]。一个文件搞定一切~


操作上也比较简明，有了数据库装WordPress就是简单的五步了。


WordPress现在的版本好像对目录权限要求有点高，主要是也不会出什么问题，就是网站访问速度会变慢……所以趁早chown比较好。


### 数据迁移


数据迁移就是搬，基本不会有问题。不过这次是由https环境搬到http环境，所以之前的一些配置造成了问题，这里全部回退掉


首先


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-2.png)


这个必须改回来，要不然会自动跳到https上。


还有这个：


[![image](https://blog.ch-wind.com/wp-content/uploads/2018/09/image_thumb-3.png "image")](https://blog.ch-wind.com/wp-content/uploads/2018/09/image-3.png)


以及将之前替换掉的文章内的图片的引用换回来，在adminer里面执行sql语句就好：



```
UPDATE wp_posts SET 'post_content' = REPLACE ('post_content', 'src="https://blog.ch-wind.com', 'src="http://blog.ch-wind.com');
UPDATE wp_posts SET 'post_content' = REPLACE ('post_content', 'href="https://blog.ch-wind.com', 'src="href://blog.ch-wind.com');

```

以及由于主题是自己写的，所以randompic.php里面的写死的链接也要改一下


### WindowLiveWriter


之后就是最后一个坑，没想到wlw竟然无法提交文章。不停的给我报



> parse error. not well formed
> 
> 


错误代号-32700……起初以为是WordPress的新bug，但是在本地装好环境发现没问题。最后几经波折才找到，是php-xml没有装……真想吐槽：你报错能智能点吗



```
apt-get install php-xml
```

这样就解决了。


## 避难完成


这样将文章推到blog上，避难就算完成了。之后要找个好的停放地点才行。


