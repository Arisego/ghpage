---
layout: post
status: publish
published: true
title: cocos2d-x中Mask的实现及优化
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 584
wordpress_url: http://blog.ch-wind.com/?p=584
date: '2013-04-19 10:36:10 +0000'
date_gmt: '2013-04-19 02:36:10 +0000'
tags:
- cocos2d-x
---
关于cocos2d-x内的Mask来做类似光点或者视野控制等功能的思路，最早是在一篇外文上看到的。


拿来用过之后发现效果还是不错，于是直接放进了程序里。可是在实际运用时发现其运行效率不是那么理想，尤其是以pc平台为目标时由于配置不同造成的帧率下降比较明显。对代码进行分析之后发现，Mask的功能使用的是CCRenderTexture动态生成纹理并覆盖在目标层上的。在每一次绘制中，这个纹理都会重新生成一次，这就造成了极大的效率上的浪费。同时CCRenderTexture貌似使用了FBO，在某些旧的显卡上会引发极大的帧率丢失。


于是着手对其进行改造，事实上之所以要每次循环都重新生成纹理是因为mask本身的位置会不断更新。而如果打算单独使用sprite+glblencfunc来解决的话，由于绘制顺序的关系很难找到一个好的动态mask解决方案。当然准备一个大概四倍视口的mask图片是可以的，但是这样的话效率也比较低下，只能留作备选方案。


最终选择的解决方案是使用clippingnode，clippingnode是使用模板测试来实现的，这是gl的基础功能，不会对硬件有太大的需求。以一个CCColorlayer为Clipping的content，首先进行模板测试，然后再叠加作为遮罩的sprite就好了。



```
		csb_st = CCSpriteBatchNode::create("Images/circle.png");

		cp_board = CCClippingNode::create();
		cp_board->setContentSize(visibleSize);
		cp_board->setPosition(CCPointZero);
		cp_board->setAnchorPoint(CCPointZero);
		cp_board->setStencil(csb_st);
		cp_board->setInverted(true);

		//////////////////////////////////////////////////////////////////////////

		CCLayerColor* clc = CCLayerColor::create(ccc4BFromccc4F(m_renderColor),visibleSize.width,visibleSize.height);
		clc->setAnchorPoint(CCPointZero);
		clc->setPosition(CCPointZero);
		cp_board->addChild(clc);			//content
		cn_borad->addChild(cp_board,m_iLaDep+1);

		CC_BREAK_IF(!f_refresh_circles());
```

sprite的话使用传说中的经典地图遮罩blend就好了：



```
		ccBlendFunc cbf = {GL_DST_COLOR, GL_ZERO};

		cns_blocks = CCSpriteBatchNode::create("Images/circle.png");
		cns_blocks->setBlendFunc(cbf);
		cp_board->addChild(cns_blocks);

		////////////////////////////////////////////////////////////////////////////
		m_AkaruCircle = CCSprite::create("Images/circle.png");
		m_AkaruCircle->setBlendFunc(cbf);
		m_AkaruCircle->setPosition(ccp(200,200));
		m_AkaruCircle->setScale(4);
		m_Board->addChild(m_AkaruCircle,m_iLaDep);
```

当然，这样的话由于GLZERO的blend结果是(0,0,0,0)，如果不是做纯黑的不透明遮罩，即便精心的准备遮罩图片，多少还是会有一些违和感存在，如果出现这种情况而无法从其他方面进行修正的话，还是必须使用rendertexture。由于rendertexture的效率因素，我们必须尽量减少其负担，只是对sprite进行处理，除非需要动态改变遮罩的背景色，我们都不会对sprite进行重新生成。



```
	ccBlendFunc cbf = {GL_ZERO, GL_ONE_MINUS_SRC_ALPHA};

	CCSprite* t_sp = CCSprite::create("Images/circle.png");
	t_sp->setPosition(CCPointZero);
	t_sp->setAnchorPoint(CCPointZero);
	t_sp->setBlendFunc(cbf);

	CCSize vs = t_sp->getContentSize();
	CCRenderTexture* t_crt = CCRenderTexture::create(vs.width, vs.height);
	t_crt->beginWithClear(m_renderColor.r, m_renderColor.g, m_renderColor.b, m_renderColor.a);

	t_sp->visit();

	t_crt->end();

	m_AkaruCircle = CCSprite::createWithTexture(t_crt->getSprite()->getTexture());
	//m_AkaruCircle->autorelease();
	m_AkaruCircle->setScale(4);
	m_Board->addChild(m_AkaruCircle,m_iLaDep);
```

这样一来Mask的总体效率就是一次模板测试加上两次spritebachnode的绘制，可以作为频繁使用CCRenderTexture的替代方案使用了。代码如下，由于目前的代码结构的关系，要测试的话spotlight类需要被继承，然后在适当的地方调用f_init才行。



```
http://pan.baidu.com/share/link?shareid=418465&uk=1913549955
```

