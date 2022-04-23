---
layout: post
status: publish
published: true
title: 网站迁移小记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2786
wordpress_url: https://blog.ch-wind.com/?p=2786
date: '2020-03-31 23:10:36 +0000'
date_gmt: '2020-03-31 15:10:36 +0000'
tags: []
---
由于Linode的线路实在过慢，后来迁移到Hostker上了。


Hostker的主机还算是快吧，主要是Linode那边没有CN2之类的线路，导致国内访问大部分时候都比较慢。


Hostker的香港主机试用了下，确实延迟很低。但是访问网站还是很慢，不知道是带宽问题还是别的什么问题。最后换到了日本的线路。


迁移同时被wordpress提示php版本不够，顺便一起升级了，主要遇到三个问题。


## IPv6配置


Hostker这边Ipv6地址不是自动配置的，需要自己设置。


由于我对服务器配置一直是一知半解，着实苦战了一番。


这边是ubuntu18，需要替换/etc/netplan/01-netcfg.yaml



```
network:
    ethernets:
        ens3:
            addresses:
                - 106.28.186.237/25
                - xxxx:5040:8:4::36cb:caf0/48
            gateway4: 106.28.186.129
            gateway6: xxxx:5040:8::1
            nameservers:
                addresses: [8.8.8.8, 1.1.1.1]
            dhcp4: false
            dhcp6: false

    version: 2
    renderer: networkd
```

在尝试错误的过程中



```
netplan try
netplan --debug generate
```

两个指令比较有用


## 数据库创建


以前都是用web控制的单php文件数据库管理的。


这次怎么都连不上，似乎是安全策略变了，于是直接通过mysql语句来创建了数据库：



```
CREATE DATABASE mywpdb;
CREATE USER 'xxuser'@'localhost' IDENTIFIED BY 'greatpassword';
GRANT ALL ON mywpdb.* TO 'xxuser'@'localhost';
```

## 数据库替换


PHP升级过后，之前一直在使用的代码格式化展示插件不能用了，后面换成了EnlighterJS。


但是这样一来所有的旧文章就都无法正确的显示了。因此必须对标签进行替换。


之前替换https链接只要简单的执行REPLACE 就可以了，这次由于比较复杂，稍微搜索了一番才找到方法。


虽然有看到没有正则替换之类的功能的描述，好在这边用的是MariaDb的最新版本，似乎有[[正则替换功能](https://mariadb.com/kb/en/regexp_replace/)]：



```
UPDATE copy_wp_posts
SET post_content=REGEXP_REPLACE(post_content,'(<pre[^>]*>)','<pre class="EnlighterJSRAW" data-enlighter-language="null">')
WHERE post_content REGEXP '<pre\s*.*>'
```


 这样的话就成功完成替换了。 



