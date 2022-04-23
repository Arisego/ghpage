---
layout: post
status: publish
published: true
title: Android简单的将Activity改为Fragment
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 526
wordpress_url: http://blog.ch-wind.com/?p=526
date: '2012-12-16 11:20:01 +0000'
date_gmt: '2012-12-16 03:20:01 +0000'
tags:
- Android
- Fragment
---
开发android有时会遇到这样的问题，那就是需要将Activity改造成Fragment。


本来Fragment是新的android版本上的东西，不过既然google这么亲切的提供了向下兼容的包。那么总会有这样的需要的时候，好在Activity到Fragment的转化并不复杂，因为本来就是相似的东西。最近就遇到了这的问题，于是来总结一下经验。


从Activity到Fragment最大的变动在于，在Fragment里面的onCreate()函数内，是没有办法使用findViewById、setContentView这些函数的。因为Fragment本身并没有提供这些方法。于是我们只能通过onCreateView和onViewCreated来实现对显示的控制。



```
@Override

public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
  return inflater.inflate(R.layout.about_detail, container, false);
}

@Override

public void onViewCreated(View view, Bundle savedInstanceState) {
  super.onViewCreated(view, savedInstanceState);
  version = (TextView) view.findViewById(R.id.version);
  loginfo = (TextView) view.findViewById(R.id.loginfo);
}
```

而一些Fragment没有提供的属于Activity的函数我们可以通过getActivity()得到作为parent的Activity来调用，因为Fragment只是作为片段提供给Activity使用的，所以很多功能的实现都被留在了Activity里面。不过无论如何，只要利用Eclipse自带的查错功能可以非常快速的完成这些操作。这种改动一般不会很复杂，只要把Fragment要做的事情交给作为parent的Activity处理就可以了。比如像Intent的处理就可以这样：



```
Intent i = new Intent();
i.setClass(getActivity().getApplicationContext(), NewActivity.class);
startActivity(i);
getActivity().finish();
```

 


