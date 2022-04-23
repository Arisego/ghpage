---
layout: post
status: publish
published: true
title: Ubuntu下Lnmp环境安装配置PhalconPHP
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 1186
wordpress_url: http://blog.ch-wind.com/?p=1186
date: '2015-03-28 15:15:02 +0000'
date_gmt: '2015-03-28 07:15:02 +0000'
tags:
- phalcon
- lnmp
---
Lnmp在快速搭建网站环境方面特别方便，基本不用自己去研究各个软件的安装和配置。由于对Linux半生不熟，在安装Phalcon时却遇到了一些问题，在这里总结下经验。


当前Lnmp版本:1.1。当前Phalcon版本:1.3.4。PHP版本：5.6.6。


要使用PhalconPHP，升级下php版本比较好，按照lnmp官方的提示进行即可。


Phalcon的缓存系统可以使用Memcache，在升级了php版本之后，如果使用官方的安装脚本会有问题。将原本从48行开始的版本检测语句添加新的php版本即可：



```
if echo "$cur_php_version" | grep -q "5.2." 
then 
sed -i 's#extension_dir = "./"#extension_dir = "/usr/local/php/lib/php/extensions/no-debug-non-zts-20060613/"\nextension = "memcache.so"\n#' /usr/local/php/etc/php.ini 
elif echo "$cur_php_version" | grep -q "5.3." 
then 
sed -i 's#extension_dir = "./"#extension_dir = "/usr/local/php/lib/php/extensions/no-debug-non-zts-20090626/"\nextension = "memcache.so"\n#' /usr/local/php/etc/php.ini 
elif echo "$cur_php_version" | grep -q "5.4." 
then 
sed -i 's#extension_dir = "./"#extension_dir = "/usr/local/php/lib/php/extensions/no-debug-non-zts-20100525/"\nextension = "memcache.so"\n#' /usr/local/php/etc/php.ini 
elif echo "$cur_php_version" | grep -q "5.6." 
then 
sed -i 's#extension_dir = "./"#extension_dir = "/usr/local/php/lib/php/extensions/no-debug-non-zts-20131226/"\nextension = "memcache.so"\n#' /usr/local/php/etc/php.ini 
else 
&nbsp;&nbsp;&nbsp; echo "Error: can't get php version!" 
&nbsp;&nbsp;&nbsp; echo "Maybe your php was didn't install or php configuration file has errors.Please check." 
&nbsp;&nbsp;&nbsp; sleep 3 
&nbsp;&nbsp;&nbsp; exit 1 
fi
```

通过apt-get install php5-phalcon安装的Phalcon是编译给PHP5.4的，由于没有实际使用过所以也不知道该Phalcon的版本是多少。按照官方的要求进行编译安装：



```
git clone --depth=1 git://github.com/phalcon/cphalcon.git

cd cphalcon/build

sudo ./install
```

这个时候会遇到错误，大体意思是找不到php目录。打开install脚本进行编辑，在第64行按照提示添加php-config



```
/usr/local/php/bin/phpize && ./configure  --with-php-config=/usr/local/php/bin/php-config --enable-phalcon && make && make install && echo -e "\nThanks for compiling Phalcon!\nBuild succeed: Please restart your web server to complete the installation"
```

这个时候安装就能正确进行了，安装完成之后在php.ini中添加


extension = phalcon.so


重置lnmp，在phpinfo()中就能看到Phalcon已经启用成功。


[![image](https://blog.ch-wind.com/wp-content/uploads/2015/03/image_thumb.png "image")](https://blog.ch-wind.com/wp-content/uploads/2015/03/image.png)


使用lnmp的添加域名脚本添加好之后，需要对生成的配置文件进行修改。如果处理不当将可能导致以下两种情况：


1. 所有的控制器都无法访问，全部被当作index/index来处理
2. 无法正常的通过get、getQuery等函数获取url参数，全部返回null


具体的设定可以参考官方的[安装说明](http://docs.phalconphp.com/zh/latest/reference/nginx.html)进行，下面给出的是本次配置服务器所使用的配置。



```
server 
    { 
        listen 80; 
        #listen [::]:80; 
        server_name www.xxxx.com xxxx.com; 
        index index.html index.htm index.php default.html default.htm default.php; 
        set $root_path '/home/wwwroot/www.xxxx.com/public'; 
        root $root_path;

        location / { 
            try_files $uri $uri/ /index.php?_url=$uri&$args; 
        }

        location ~ \.php$ { 
                try_files $uri =404; 
                fastcgi_split_path_info ^(.+\.php)(/.+)$; 
                fastcgi_pass  unix:/tmp/php-cgi.sock; 
                fastcgi_index index.php; 
                fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name; 
                include fastcgi.conf; 
        }

 

        location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$ 
        { 
            root          $root_path; 
            expires      30d; 
        }

 

        location ~ .*\.(js|css)?$ 
        { 
            root          $root_path; 
            expires      12h; 
        }

        location ~ /\.ht { 
            deny all; 
        } 
    }
```

同时对Router进行设置：



```
$di->set('router', function () use($routes) {

    $router = new \Phalcon\Mvc\Router(); 
    $router->setUriSource(\Phalcon\Mvc\Router::URI_SOURCE_SERVER_REQUEST_URI);

    return $router; 
});
```

上面的步骤完成后，Phalcon就已经能够正常的在Lnmp上运行了。


