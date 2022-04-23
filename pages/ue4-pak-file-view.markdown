---
layout: page
status: publish
published: true
exclude: true
title: UE4文件查看插件
author:
  display_name: chaoshikari
  login: chaoshikari
  email: chaoshikari@gmail.com
  url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 2141
wordpress_url: http://blog.ch-wind.com/?page_id=2141
date: '2017-12-10 19:46:07 +0000'
date_gmt: '2017-12-10 11:46:07 +0000'
tags: []
---
<p>这个插件是从测试工程中分离出来的，虽然之前的文章中有提到文件浏览器的制作，但是无奈那时的代码已经丢失，所以这里提供的是比较简单的功能。<!--more--></p>
<h2>安装</h2>
<p>和一般的插件是一样的，直接扔到Plugins里面就可以了。</p>
<p>然后在启用插件后，在原有的GameMode中指定HUD为Hud_FileView即可。如果有进一步的需求的话，可以直接使用Wid_FileView。</p>
<h2>使用</h2>
<p>和普通的文件浏览器功能差不多，但是双击umap文件的话会直接触发加载那个地图。</p>
<p><a href="https://blog.ch-wind.com/ue4-pak-file-view/snap/" rel="attachment wp-att-2145"><img class="aligncenter size-full wp-image-2145" src="https://blog.ch-wind.com/wp-content/uploads/2017/12/Snap.jpg" alt="" width="565" height="156" /></a></p>
<p>注意，如果一路上行虽然会看到系统文件路径，但是实际上是在使用UFS进行查看，也就是说在目录中看到的是实际Mount之后的虚拟文件状态。</p>
<p>主要的功能之一就是查看实际Mount到UE4之后，UFS是如何对文件进行放置的。可以用于快速的排查打包策略制定时的问题。</p>
<h2>下载</h2>
<p>请移步Github，<a href="https://github.com/Arisego/FileViewer">https://github.com/Arisego/FileViewer</a>。</p>
