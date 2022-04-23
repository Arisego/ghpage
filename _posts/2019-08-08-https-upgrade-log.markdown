---
layout: post
status: publish
published: true
title: Https改造记录
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2647
wordpress_url: https://blog.ch-wind.com/?p=2647
date: '2019-08-08 23:46:42 +0000'
date_gmt: '2019-08-08 15:46:42 +0000'
tags:
- HTTPS
---
经过了几个月的观察，现在网站总算是完全平稳的运作在Https上了。


之所以要自己折腾Https证书这些事情，是因为最终网站迁移到Linode上了。


虽然现在的共享主机商都会提供Https签名服务，但是无奈一直都找不到靠谱的主机商。试来试去，发现还是Linode适合我这种规模小但对稳定性有要求的。虽然速度上偶尔会有非常卡的情况，但是现状来看实在无可奈何。因为本质上这边不产生收益，所以没有办法花费太多成本在上面。


记得以前Https证书很难搞定，只有Comodo的免费授权，要更新起来特别麻烦。而个人站点基本不可能去搞商业证书，完全意义不明~


好在现在有了[lets encrypt](https://letsencrypt.org/)，可以免费的进行Https证书的申请。


第一次弄的时候，由于没有什么时间，参照官方教程随便配置了下。


lets encrypte的签名有效时间比较短，需要自己隔一段时间重新签名一次。但是途中不小心忙忘了 ，导致证书失效。几个常见的浏览器，Firefox和Chrome，遇到这种情况是直接不让访问网站的，相当的尴尬。


于是就又开始折腾。折腾完了就有了下面的记录，方便下次需要配置的时候直接拷贝就可以了~


## Acme.sh


几经搜索，终于找到了这个自动签名工具。不但有中文的[说明文档](https://github.com/Neilpang/acme.sh/wiki/%E8%AF%B4%E6%98%8E)，功能上，也比官方的工具更直观一些。


操作上，为了方便下次自动签名，首先第一步是添加DNS API。具体可以参考[官方说明](https://github.com/Neilpang/acme.sh/wiki/dnsapi)。


之后按照文档进行证书申请，完成申请后就可以安装了。


对于Nginx，安装的主要的命令是这样：



```
acme.sh --install-cert -d *.ch-wind.com \
--cert-file      /etc/nginx/ssl/ch-wind.cer  \
--key-file       /etc/nginx/ssl/ch-wind.key  \
--ca-file       /etc/nginx/ssl/ca.cer  \
--fullchain-file /etc/nginx/ssl/fullchain.cer \
--reloadcmd     "service nginx force-reload"

```

一旦完成一次操作，之后就会每隔60天自动更新证书，观察了几个月，基本算是没什么问题。


需要注意的是，对于wild card的域名证书，是不可以使用给根域名的。虽然不知道为什么，但是如果有做根域名跳转的话，需要对根域名另外签一次名。


## IPV6


既然都加HTTPS了，自然不能忘了IPV6。


网站的IPV6迁移是最简单的了，不过现在纯IPV6的用户应当还是比较少。大多数都只是根据线路来优先选择更快的一个。


配置上，只要服务器提供商有给IPV6地址，那么在DNS提供商那边添加一个AAAA记录就OK了。


当然，Nginx这边还需要配置下端口监听方式，如果之前没有配过的话。


## Nginx配置


接下里就是Nginx配置，这个基本参考官方文档就可以了。但是每次去找也很麻烦，这里贴出现在在使用的版本。



```
server{
    server_name ch-wind.com;
    return 301 https://blog.$host$request_uri;

    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/nginx/ssl/raw_ch-wind.cer; # managed by Certbot 
    ssl_certificate_key /etc/nginx/ssl/raw_ch-wind.key; # managed by Certbot
}

server{
    if ($host = blog.ch-wind.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen [::]:80;
    listen 80;

    server_name blog.ch-wind.com;
    return 301 https://$server_name$request_uri;


}

server {
        ## Your website name goes here.
        server_name blog.ch-wind.com;
        ## Your only path reference.
        root /var/www/chwindblog;
        ## This should be in your http block and if it is, it's not needed here.
        index index.php;

        location = /favicon.ico {
                log_not_found off;
                access_log off;
        }

        location = /robots.txt {
                allow all;
                log_not_found off;
                access_log off;
        }

        location / {
                # This is cool because no php is touched for static content.
                # include the "?$args" part so non-default permalinks doesn't break when using query string
                try_files $uri $uri/ /index.php?$args;
        }

        location ~ \.php$ {
                #NOTE: You should have "cgi.fix_pathinfo = 0;" in php.ini
                include snippets/fastcgi-php.conf;
                fastcgi_intercept_errors on;
                fastcgi_pass unix:/var/run/php/php7.2-fpm.sock;
                fastcgi_buffers 16 16k;
                fastcgi_buffer_size 32k;
        }

        location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
                expires max;
                log_not_found off;
        }

    ## listen 80;

    listen [::]:443 ssl;
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/ch-wind.cer; # managed by Certbot 
    ssl_certificate_key /etc/nginx/ssl/ch-wind.key; # managed by Certbot
}

server{
    if ($host = ch-wind.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    server_name ch-wind.com;
    listen [::]:80;
    listen 80;
    return 404; # managed by Certbot


}

```

里面有被Certbot配置过的痕迹，不过CertBot的自动更新功能配置起来有些迷。


整个配置有点乱，也没时间整，真的是凑活着用了……


