---
layout: post
status: publish
published: true
title: cocos2d-x中shader的使用
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 731
wordpress_url: http://blog.ch-wind.com/?p=731
date: '2013-09-30 21:33:13 +0000'
date_gmt: '2013-09-30 13:33:13 +0000'
tags:
- cocos2d-x
- shader
---
其实最近各种事情都比较乱本来不该研究这个的，但是个人习惯上一旦有什么事挂在那就会心烦，于是最终还是把整个事情搞到自己满意为止了。


shader这个东西貌似很高端，其实本质上和其他的语言没有什么差别，而且还是c风格的。所以主要的时间都花在了怎么让它跑起来上面了。


cocos2d-x使用shader上有一个麻烦的地方，就是shader里面有什么错的地方的话程序就直接报错退出，就算在debug模式下跟踪运行也不会输出任何错误信息。所以要让网上找到的shader代码正常运行起来花了我不少精神，好在sample里面有不少现成的shader，可以参照着进行修改。


首先还是来稍微了解下什么是shader吧，由于在程序方面我多少是个野狐禅，所以就从实用性的角度来解释吧。shader分为vertex顶点部分和Fragment像素部分两个部分，总体而言就是显卡上所提供的可编程部分。相当于可以交托给显卡运行的脚本的感觉，shader的一个好处就是可以跑出很多比较酷的效果而不用加载额外的资源。至于vertex和fagment的分法，其实是因为显卡在绘制的时候是先画点再涂颜色的。


不过就像是我们不必知道操作系统和硬件的详细机制一样，shader这个东西其实只要跑起来就可以了。因为是c风格的，所以算是非常的浅显易懂。废话那么多其实也没什么意义，目前找到两个比较好的在线的shader的预览站：


<https://www.shadertoy.com/>


<http://glsl.heroku.com/>


两个网站都是用webgl演示的，webgl本身是用的gles2.0的api，所以本质上和cocos2d-x是一样的。因此上面的shader只要稍微做一下修改就可以直接搬动到游戏里面使用，当然如果想自己实现牛逼的效果的话，自然需要自己研究下语法，这么多sample可以参考的话理论上也不会花多少时间的。


以结果而言，cocos2d-x的node里面是有自己的shaderprogram机制的。也就是说只要定义好了shader的话，是可以直接调用setshaderprogram来切换shader的，因此对于一些简单的shader特效，完全没有必要新定义一个类来做。言归正传，要让别人写好的shader跑起来，最主要的就是要注意uniform的定义。


在shader的语法中，uniform是从外界传入的参数。只要解决掉这个问题，就可以让shader正常的跑起来了。对于shadertoy上的shader，只要这样添加下面的代码进fsh里面就基本没有问题了：



```
uniform vec2 center;
uniform vec2 resolution;
uniform vec4 iMouse; 

float iGlobalTime = CC_Time[1];
vec2 iResolution = resolution;
```

如果要想让cocos2d-下能够将鼠标的移动传入shader中，以让大部分要读取鼠标位置的shader能够运行，需要做的改造如下：


首先定义一下作为uniform的中继的变量用来保存GLuint的id，这里面和gl差不多，因为是在显卡里的缘故，所以都会用一个uint的标记来做变量的索引。



```
GLuint     m_uniformMouse;
```

然后按照标准的做法在适当的地方初始化一下，之后重要的是要获得准确的uniform的值：



```
m_uniformMouse = glGetUniformLocation(shader->getProgram(), "iMouse");
```

然后在ondraw的地方，将新的鼠标位置通过这个id传递给shader



```
getShaderProgram()->setUniformLocationWith4f(m_uniformMouse, x, y, z, 0);
```

这个根据shader里面的定义会有不同，这里这样传递鼠标是因为shadertoy上的shader是这样统一定义的：



```
uniform vec4 iMouse;
```

这样的话鼠标的传递大体上就完成了，监听cctouch系列事件对x,y,z的值进行修改即可。


如果要传递texture的话，可以自己定义一个cctexure2d，然后通过getname获得它的id传递给shader即可。如果是基于ccsprite的子类的话就不用操这个心，具体可以参照下BYGraySprite的写法，代码在打包里。


有一个需要注意的问题是，cocos2d-x默认传递的参数CC_Time[1]其实是一个数组，可以选择0,1,2,3档的感觉，档越高速度越快。一般情况下随意调整即可，因为没有哪一个和shadertoy的iTime契合的很好……


代码里的2.1.4是自己测试用的，2.1.0是功能比较全的版本，里面的灰色的sprite的那个类有参照某前辈的博文，不过一时找不到出处了，好在代码里本身是有版权信息的。总之大概跑出来的效果是这样的：


[![截图](https://blog.ch-wind.com/wp-content/uploads/2013/09/aa-300x216.jpg)](https://blog.ch-wind.com/wp-content/uploads/2013/09/aa.jpg)


代码附上：


http://pan.baidu.com/s/1cKbPu


