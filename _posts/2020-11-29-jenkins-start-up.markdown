---
layout: post
status: publish
published: true
title: Jenkins初步使用记录
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 3105
wordpress_url: https://blog.ch-wind.com/?p=3105
date: '2020-11-29 11:10:44 +0000'
date_gmt: '2020-11-29 03:10:44 +0000'
tags:
- Jenkins
---
Jenkins这个工具似乎在流程中使用的还挺多的，于是就找了些时间试用了下。


使用的Jenkins版本是2.266。


[Jenkins](https://www.jenkins.io/)的官方网站，初看还是有点上个世代的感觉的。至少和其他的CI工具相比，不是那么的重视界面。


不过Jenkins的主要优势是开源免费，对于只是需要自动化流程的小规模工作室而言还是有不少优势的。毕竟流程跑起来最重要的是功能，界面只要能表达清晰、流畅使用就足够了。


下面主要记录一些遇到的问题，安装过程这些可以参考官方网站。


## Root权限运行


一开始没搞明白Jenkins的使用方式，其实如果流程依赖于svn或者git的话，是不需要root权限的。


Jenkins的运行用户可以在配置中修改：



> vi /etc/sysconfig/jenkins
> 
> 


修改



> $JENKINS_USER="root"
> 
> 


出于保守起见，同时修改目录权限：



> chown -R root:root /var/lib/jenkins
> 
> 
> chown -R root:root /var/cache/jenkins
> 
> 
> chown -R root:root /var/log/jenkins
> 
> 


然后重启Jenkins



> /etc/init.d/jenkins restart ps -ef | grep jenkins
> 
> 


这样之后就能正常的对有权限的目录进行访问了。


由于后面发现不需要Root权限，把配置改回去之后，把目录权限直接全部开放：



> chmod -R 777 /var/lib/jenkins
> 
> 
> chmod -R 777 /var/cache/jenkins
> 
> 
> chmod -R 777 /var/log/jenkins
> 
> 


## 错误捕捉


Jenkins在运行脚本时，遇到了明明脚本报错却将job视为成功的情况。


主要原因是，在脚本头部具有 `#!/bin/bash` 。由于jenkins会将脚本放在一个临时sh文件里面执行，导致这样无法捕获到错误，移除`#!/bin/bash`即可，无需指定命令解释器。


或者，在脚本头部（ `#!/bin/bash`后面）加入命令：`set -o errexit` 或者 `set -e`。


## 编译错误


这个问题的表现有点奇怪：直接在命令行中执行指定的脚本，编译过程可以正常通过。但是Jenkins使用同样的脚本却无法正确的完成编译。


最后发现是CMake自动选择的编译器不同造成的，Jenkins在运行时获取的环境变量与在命令行中的环境变量不同。


分别执行`echo $PATH`会发现输出的内容不一致。


虽然CMake本身支持强制指定编译器路径，不过考虑到通用性，可以直接在Jenkins中设定环境变量参数。


[![jenkins-path](https://blog.ch-wind.com/wp-content/uploads/2020/11/image.png)](https://blog.ch-wind.com/wp-content/uploads/2020/11/image.png)


这样就能正常通过编译了。


## Bash记录


由于之前对bash不是很熟悉，过程中找到一些有帮助的bash命令记录在这里记录一下


### 读取Svn信息



```
REVISION=`svn info | grep 'Last Changed Rev' | tr -d 'Last Changed Rev: '`
echo $REVISION
```

### 写入到文件


直接写入：



```
echo "hello" > logfile.txt
```

附带输出：



```
echo "hello" | tee logfile.txt printf "hello" | tee logfile.txt
```

### 读取文件第一行



```
line="$(head -1 logfile.txt)"
```

## 插件安装


插件安装遇到了很多奇怪的问题，无论使用官方的发布版本还是docker版本都无法正确的安装。


搜索了下，找到的建议里面，无论是设置proxy参数还是修改镜像地址都无法完成安装。


表现上看，网络测试是通的，但是下载对应的插件包就是失败。可是使用wget去下载对应的路径又能成功，由于报错语焉不详，无法进一步寻找原因，最后只能使用手工下载安装包并直接在后台手动安装的方式。


由于需要按照依赖来按顺序安装，所以需要一个一个的去自己找。应该是可以写成脚本的形式来自动进行的，只是由于只是稍微试用，就没有仔细纠结了。而且正常的话，就算手工安装也花不了多少时间。不如说搜索如何解决自动安装失败问题的过程反而花了更多时间……


