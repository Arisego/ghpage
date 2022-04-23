---
layout: post
status: publish
published: true
title: Elasticsearch环境安装使用笔记
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 3517
wordpress_url: https://blog.ch-wind.com/?p=3517
date: '2021-05-31 14:37:33 +0000'
date_gmt: '2021-05-31 06:37:33 +0000'
tags: []
---
想要作一些简单的数据分析，看kibana界面似乎很好用的样子，于是尝试安装了一下。


实际操作环境：windows10和ubuntu20.04。


本次的目标是，通过ELK框架对在Mysql中的数据进行分析。


## ELK安装


基础的安装部分比较简单，可以参考网上的其他文章。Ubuntu系统上的安装可以参考DigitalOcean的[这篇](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-20-04)，基本上就是使用apt命令就可以了。windows上的就更加单纯一些，只要下载对应的bat文件然后解压就可以了。


不过由于很多工具都是linux上的，而且windows安装jdk的mysql包之类的会很麻烦，最后切换到ubuntu上了。


另外，如果是在云服务器上进行安装的话，需要注意主机的配置。实际测试，在腾讯云上这个配置：



> 1核 2GB 1Mbps
> 
> 
> 系统盘：高性能云硬盘
> 
> 


无法正常的运行，只要一启动logstash，就会导致Elasticsearch挂掉。


### 指令备忘


使用时注意开启服务：



```
sudo systemctl start elasticsearch
sudo systemctl start kibana
```

可以使用下面的指令检查elasticsearch是否成功开启



```
curl -X GET "localhost:9200"
```

kibana直接在本地访问就好：http://localhost:5601。如果是在服务器上可能需要额外的配置端口开放或者用nginx作反向代理，可以参考上面的digitalocean的文档进行。


如果需要服务常驻的话可以打开：



```
sudo systemctl enable elasticsearch
sudo systemctl enable kibana
```

## Logstash使用


ELK里面，其实Elasticsearch和Kibana一开始只需要安装好就可以了，主要的是Logstash配置好，将数据推送过去。


LogStash其实官方的这篇就很好用了：[Stashing Your First Event](https://www.elastic.co/guide/en/logstash/7.12/first-event.html)。


这边稍微记录下有用的内容，对于找不到LogStash的路径的话，可以使用指令



> whereis logstash
> 
> 


logstash最基本的功能测试，可以用于检查功能是否正常



```
cd logstash-7.12.1
bin/logstash -e 'input { stdin { } } output { stdout {} }'
```

官方有个[FileBeat教程](https://www.elastic.co/guide/en/logstash/7.12/advanced-pipeline.html)，使用logstash接入filebeat来分析apache的日志，基本照着做就可以了。


要测试一个配置文件是否正确：



> sudo bin/logstash --config.test_and_exit -f first.conf
> 
> 


### Mysql连接


Logstash使用mysql需要额外的安装Mysql连接用套件。windows版可以在这里下载[连接套件](https://dev.mysql.com/downloads/connector/j/)。



```
input {
  jdbc {
    jdbc_driver_library => "C://Program Files (x86)//MySQL//Connector J 8.0//mysql-connector-java-8.0.25.jar"
    jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
    jdbc_connection_string =>  "jdbc:mysql://localhost:3306/awesome_database"
    jdbc_user => "your_awesome_mysql_user"
    jdbc_password =>  "your_awesome_password"
    statement =>  "SELECT * from awseome_table_name"
  }
}

output{
  stdout { codec => rubydebug { metadata => true } }
}


```

jdbc_driver_library 这里需要指向安装目录中对应的连接套件的jar文件。其他的配置项都比较明了。


ubuntu下也需要对应的安装一些连接套件：



> wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.46.zip
> 
> 


然后解压



> unzip mysql-connector-java-5.1.46.zip
> 
> 


将解压后内部的jar路径填到logstash配置的input部分



```
input {
  jdbc {
    jdbc_driver_library => "usr/share/logstash/mysql-connector-java-5.1.46/mysql-connector-java-5.1.46.jar"
    jdbc_driver_class =>"com.mysql.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://localhost:3306/awesome_database_name"
    jdbc_user => "your_awesome_mysql_user"
    jdbc_password => "your_awesome_password"
    statement =>  "SELECT * from awseome_table_name"
  }
}

output{
  stdout { codec => rubydebug { metadata => true } }
}

```

### 输入到Elastic


需要将配置中的output改到对应的elastic



```
output{
  # stdout { codec => rubydebug { metadata => true } }
  elasticsearch {
        hosts => [ "localhost:9200" ]
        index => "kibana-index"
    }
   # stdout { codec => dots }
}

```

加入到index后，kibana中需要创建新的index parten才能正确看到。


如果是本地的话，使用这个网址就可以了：http://localhost:5601/app/management/kibana/indexPatterns/


Mysql推送数据多次推送的情况下，会出现很多重复的数据，可以通过在output这边添加配置解决：



```
output{
  #stdout { codec => rubydebug { metadata => true } }
  elasticsearch {
       hosts => [ "localhost:9200" ]
       index => "productinfo"
       document_id => "%{productid}"
  }
   # stdout { codec => dots }
}

```

其中，productid就是mysql这边的主键。


对于更加复杂的情况，可以在input这边处理，比较简单的处理方式是使用jdbc input提供的预定义配合时间戳来进行。详细的可以看[[官方文档](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-jdbc.html#_predefined_parameters)]。


比较简单的用法：



```
input {
  jdbc {
    statement => "SELECT id, mycolumn1, mycolumn2 FROM my_table WHERE id > :sql_last_value"
    use_column_value => true
    tracking_column => "id"
    # ... other configuration bits
  }
}
```

这边用的是id来避免input的时候重复，如果ID不是自增的，可以用timestamp来代替，其实默认sql_last_value就是时间戳形式的。更加复杂的情况需要结合last_run来进行，可以进一步参考文档。


一时半会没看到自动根据主键来避免重复的input配置方式。这边暂时在output那边控制下就可以了，不纠结了。


 


