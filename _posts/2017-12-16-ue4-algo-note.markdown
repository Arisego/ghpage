---
layout: post
status: publish
published: true
title: UE4算法帮助类笔记
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2158
wordpress_url: http://blog.ch-wind.com/?p=2158
date: '2017-12-16 16:35:14 +0000'
date_gmt: '2017-12-16 08:35:14 +0000'
tags:
- UE4
- Algo
- Sort
---
UE4有提供一套算法帮助类，命名空间为Algo，对于需要快速使用的情况可以参考。


当前使用的UE4版本为4.18.2。


整个Algo的定义分散在各个文件中，按照功能区分进行分布。


在定义上全部都是模板函数，通用性比较强。


## 数据整理


这一块是对内存数据块进行整理的通用模板。


### Copy


这是一个系列的拷贝模板函数，主要的工作就是对数据进行拷贝。


有一个CopyIf的变体，只会把符合条件的数据拷贝到目标中去。


通常需要拷贝的容器是Arrat，Map之类的，对于这个模板，只要保证源容器实现了range for和目标容器实现了Add函数就可以了。


当然，数据的类型必须至少是可转换的类型。



```
TArray<int> TestArray;
TArray<int> TestData;
Algo::Copy(TestData, TestArray);
```

### Transform


对数据进行某种操作，并填充到目标。


也有这Transfor_If的变体，要求传入的Transform操作必须返回要填充到目标的类型。



```
Algo::Transform(TestData, TestArray, [](int i) { return FMath::DegreesToRadians(i); });
check(TestArray.Num() == NUM_TEST_OBJECTS);
for (int i = 0; i < TestArray.Num(); ++i)
{
   check(TestArray[i] == FMath::DegreesToRadians(TestData[i]));
}
```

这里由于源与目标的数据类型可以是不一致的，再加上有If变体，其实是一个非常好用的数据批量处理模板。


这里传入的if条件和转置条件即可以是成员的指针也可以是成员的函数，在使用的时候可以灵活的采用。


## 二分搜索


内部封装的二分搜索算法，不用每次想要进行搜索的时候临时到Google或者代码库中去翻找搜索算法的代码了。


提供一下三个基本的函数



> BinarySearch
> 
> 
> LowerBound
> 
> 
> UpperBound
> 
> 


功能就如同函数名称一样，是搜索，最小值和最大值的查找。


## 排序


封装了几个排序算法，不过由于排序算法早就还给课本了，在这里就不比较性能了。


毕竟一直使用std的sort也没怎么关心过其内部实现，虽然TArray也是有封装sort操作的，这里也就不去看其实现了。


整体的排序上，有一个Algo::IsSorted()函数可以用于检查数据是否已经经过了排序。


同时排序算法都有提供SortBy的变体以方便进行更加精致的排序。


### Heap


严格的来说也提供了不是排序的部分。这里引用一下Wiki



> a heap is a specialized tree-based data structure
> 
> 


给和我一样一下子想不起来Heap到底是什么的筒子。


可以Algo::Heapify(TestArray)来将一个数组转换为Heap，同时提供了IsHeap函数来检查一个数组是否是以Heap的形式保存的。


然后Algo::HeapSort()才是进行堆排序的，其结果满足Algo::IsHeap以及Algo::IsSorted。


另外，根据资料显示，[[HeapSort并不是一个stable的排序算法](https://stackoverflow.com/questions/19336881/why-isnt-heapsort-stable)]，记得TArray是有提供StableSort的，果然其内部应该是有别的排序实现的。


### IntroSort


这个可以明确的记得当初并没有学过呢，再次引用Wiki



> Introsort or introspective sort is a hybrid sorting algorithm that provides both fast average performance and (asymptotically) optimal worst-case performance.
> 
> 


似乎是叫内省排序总之是相当优秀的排序算法，只是不是Stable的。


### Sort


直接调用Sort就可以了，Unstable，并没有解释到底用的是什么算法。也没有去关注它的实现……


