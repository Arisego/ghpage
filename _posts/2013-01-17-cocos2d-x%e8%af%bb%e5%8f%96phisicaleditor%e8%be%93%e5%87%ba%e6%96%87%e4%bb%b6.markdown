---
layout: post
status: publish
published: true
title: cocos2d-x读取PhisicalEditor输出文件
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 548
wordpress_url: http://blog.ch-wind.com/?p=548
date: '2013-01-17 23:36:38 +0000'
date_gmt: '2013-01-17 15:36:38 +0000'
tags:
- cocos2d-x
- PhisicalEditor
---
今天本来想找一个比较方便易用的动画编辑还载入方案，无意中翻到了PhisicalEditor这个软件。


这个软件和TexturePacker是一个作者出的，功能是用于快速生成用于box2d的碰撞图形。当时下载的时候没有注意过这个软件，因为大多数时候我们都不会用到需要精确到接近像素级的碰撞检测，通常而言采用适当的圆形或者矩形就可以很好的模拟游戏中的大部分碰撞行为了。在实际思考过之后，我发现这个软件还是可以很好的提高开发速度的。只要将它和texturepacker结合使用的话就可以很好的快速生成图形和碰撞了。而且它在需要进行真实物理模拟的游戏中还是很有作用的。


[![物理模拟](https://blog.ch-wind.com/wp-content/uploads/2013/01/unnamed-file-300x233.jpg)](https://blog.ch-wind.com/wp-content/uploads/2013/01/unnamed-file)


可是在实际开始进行测试的时候遇到了一个问题，cocos2d-x目前的版本号是2.1beta，前不久刚进行过一次大的版本迁移。所以很多能够找到的代码都不能用了，很不幸的是，phisicaleditor提供的cocos2d-x接口就不能用了。于是我便开始改造这个接口，一些大的引擎方面的变更就不提了。主要的还是在核心算法上有很大的变动，因为原本的代码使用的数据结构和目前代码提供的数据结构已经可以说是完全的不同了。虽然有想过使用tinyxml来替代，但是衡量了一下还是决定改用新的数据结构。



```
CCArray *fixtureList = (CCArray *)(bodyData->objectForKey("fixtures"));
        FixtureDef **nextFixtureDef = &(bodyDef->fixtures);
		//<ObjectDict *>
		int con = fixtureList->count();
		for (int i = 0; i<con; i++) {
            b2FixtureDef basicData;
            ObjectDict *fixtureData = (ObjectDict *) fixtureList->objectAtIndex(i);

            basicData.filter.categoryBits = static_cast<CCString *>(fixtureData->objectForKey("filter_categoryBits"))->intValue();
            basicData.filter.maskBits = static_cast<CCString *>(fixtureData->objectForKey("filter_maskBits"))->intValue();
            basicData.filter.groupIndex = static_cast<CCString *>(fixtureData->objectForKey("filter_groupIndex"))->intValue();
            basicData.friction = static_cast<CCString *>(fixtureData->objectForKey("friction"))->floatValue();
            basicData.density = static_cast<CCString *>(fixtureData->objectForKey("density"))->floatValue();
            basicData.restitution = static_cast<CCString *>(fixtureData->objectForKey("restitution"))->floatValue();
            basicData.isSensor = (bool)static_cast<CCString *>(fixtureData->objectForKey("isSensor"))->intValue();

			CCString *cb = static_cast<CCString *>(fixtureData->objectForKey("userdataCbValue"));

            int callbackData = 0;
```

这个解析函数是通过xml的解析来完成box2d相关属性的读入和初始化，所以其实一直都在重复着类似这样的改动。~~其中比较奇怪的一点是，新的cocos2d-x中的map并没有提供用于遍历的函数。而原来似乎是有着类似于iter的机制的。于是只能采用AllKey()方法获得key的ccarray然后遍历，这样的话效率就会有所下降。使用迭代器的话，遍历的复杂度是n。而这样的话就会变成n*log(n)了，不过一般情况下这个配置文件是不太可能有这么多的节点的，所以实际上影响不会很大。因为好奇所以看了下AllKey()方法的实现，发现是这样的：~~



```
~~CCArray* CCDictionary::allKeys()
{
 int iKeyCount = this->count();
 if (iKeyCount <= 0) return NULL;

 CCArray* pArray = CCArray::createWithCapacity(iKeyCount);

 CCDictElement *pElement, *tmp;
 if (m_eDictType == kCCDictStr)
 {
 HASH_ITER(hh, m_pElements, pElement, tmp) 
 {
 CCString* pOneKey = new CCString(pElement->m_szKey);
 pOneKey->autorelease();
 pArray->addObject(pOneKey);
 }
 }
 else if (m_eDictType == kCCDictInt)
 {
 HASH_ITER(hh, m_pElements, pElement, tmp) 
 {
 CCInteger* pOneKey = new CCInteger(pElement->m_iKey);
 pOneKey->autorelease();
 pArray->addObject(pOneKey);
 }
 }

 return pArray;
}~~
```

~~显然的内部还是有迭代机制的，但是似乎不对外开放了。~~


更正：当时没仔细研究，ccdic是有遍历的接口的。一般情况下使用类似下面的宏就可以了：



```
CCDictElement* cde = NULL;
CCDICT_FOREACH(m_itemlist,cde){
}
```

做完上面的改动之后，运行时会报错，错在ccsprite的gldrawarray上。这时候才能理解到opengl是一个状态机这句话，似乎两个版本之间对opengl状态的修改有所不同，于是在重载了的ondraw中把所有的修改gl的代码一一注释掉了。另外有一个奇怪的地方是，用于b2world调试输出gles-render似乎被从引擎核心里移除了？于是只能从官方的例子中把这个文件给拷了过来。


总体来看的话其实改动的地方并不多，只是折腾来折腾去的却也花了不少时间。于是把修改后的代码直接传上来，方便有用到的同学就不用再改了。鉴于以前下载别人代码的经验，把整个工程文件打上来了。


http://pan.baidu.com/share/link?shareid=201320&uk=1913549955


