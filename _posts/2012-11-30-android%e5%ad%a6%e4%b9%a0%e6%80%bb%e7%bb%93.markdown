---
layout: post
status: publish
published: true
title: Android学习总结
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 518
wordpress_url: http://blog.ch-wind.com/?p=518
date: '2012-11-30 12:38:18 +0000'
date_gmt: '2012-11-30 04:38:18 +0000'
tags:
- Android
---
历经近一个多月的时间，终于完成了自己的第一个android应用。途中虽然遇到不少纠结和dt的问题，可是现在回头看来却都没有留下什么深刻的印象。  

所以趁着还没有彻底忘记之前把还记得的几处记录一下。


## 自定义textview的ondraw不触发


对textview进行定制之后ondraw就没有办法触发了，虽然查了资料据说要调用setWillNotDraw(false)才行。可是就算执行了还是不绘制，最后才发现问题所在。是因为排版的问题导致了textview的高度是0，由于原本设计时是想靠ondraw绘制来占高度的，结果ondraw却没有办法调用。似乎android在高度为0时为了节省资源就不调用绘制函数了。


## textview的settextsize和gettextsize问题


这个问题纠结了很久，调试了半天才发现bug所在。textview在对字体进行设置时调用settextsize有好几个不同的传入值类型，目的是为了适应类似retina的功能。就好像px、dp之类的单位，之前一直没有在意过这些。所以就遇到了这个问题，具体的原因是这样的：



> **public void setTextSize (float size)**
> 
> 
> Set the default text size to the given value, interpreted as "scaled pixel" units. This size is adjusted based on the current density and user font size preference.
> 
> 
> **public void setTextSize (int unit, float size)**
> 
> 
> Set the default text size to a given unit and value. See TypedValue for the possible dimension units.
> 
> 
> **public float getTextSize ()**
> 
> 
> Returns the size (in pixels) of the default text size in this TextView.
> 
> 


settextsize在设置之后gettextsize的值就会不同，因为gettextsize的unit是pixels，而settextsize的是scaled pixel……


## canvas的清空问题


由于是使用的多层绘制，所以canvas在使用时每次都必须清空。找了好久才找到一个不错的方法：



```
Paint paint = new Paint();
paint.setXfermode(new PorterDuffXfermode(Mode.CLEAR));
canvas.drawPaint(paint);
paint.setXfermode(new PorterDuffXfermode(Mode.SRC));
```

 


