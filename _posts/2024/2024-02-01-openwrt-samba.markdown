---
layout: post
title:  OpenWrt设置局域网nas访问
tags: []
---

使用的版本：OpenWrt 23.05。

## 安装

基本按照官方的来就行了： https://openwrt.org/docs/guide-user/services/nas/usb-storage-samba-webinterface

里面有个samba的库已经过期了，直接在`系统/软件包`界面搜索samba就能找到新的了

![Alt text](/images/2024/image.png)

### 配置

配置要分两边配置，一个是`系统/挂载点`这边，首先要成功的挂载USB存储设备才行。

挂载成功后在`服务/网络共享`的共享目录这边添加新的就可以了，不同的硬盘可能会挂到不同的mnt点，无法访问的时候可以检查下。

![Alt text](/images/2024/image2.png)

### 一些小问题

移动硬盘不识别，需要额外安装`kmod-usb-storage-uas`。我这边应该是usb3.0的移动硬盘的协议问题引起的，没有详细的考究。

目录不可写的问题，试了下找到的方案都没什么用。查了下原因似乎是ntfs引起的，于是将硬盘格式化成ext4就成功访问了。

## 开放Wan口访问

由于路由结构的问题，电脑是与路由器平级的，所以需要开放wan口才能访问。

直接配置`/etc/config/firewall`

```ini
config rule
    option name 'Open Samba on WAN'
    option src 'wan'
    option proto 'tcp udp'
    option dest_port '137 138 139 445'
    option target 'ACCEPT'
```

这之前有参照官方的建议设置防火墙，如果设置了没用可以参考下：https://openwrt.org/docs/guide-user/services/nas/cifs.server 。