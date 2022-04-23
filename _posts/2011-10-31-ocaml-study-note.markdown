---
layout: post
status: publish
published: true
title: OCaml学习札记
author:
 display_name: chaoshikari
 login: chaoshikari
 email: chaoshikari@gmail.com
 url: http://blog.ch-wind.com
author_login: chaoshikari
author_email: chaoshikari@gmail.com
author_url: http://blog.ch-wind.com
wordpress_id: 94
wordpress_url: http://www.ch-wind.com/?p=94
date: '2011-10-31 22:29:19 +0000'
date_gmt: '2011-10-31 14:29:19 +0000'
tags: []
---
时间过得真快，一转眼2011就要结束了。~~而我却还是一事无成呢，在心里认为自己很伟大以及在现实面前很平庸这样的矛盾真是让人痛苦啊（笑）。~~最近也是，不知道为什么就是什么也没干的过来了。最后发现只有正在学习的这门课程能够拿出来证明我真的活过了这几个月……


好吧，上面的都是闲话，这里直接切入正题。接触到ocaml是因为正在学函数式程序设计，英文好像叫 function programing 来着，记不清了。这里主要写一些自己学到的东西吧，当然不敢说是教程了。


ocaml是object caml的简称，而caml是ml的一种方言。它最主要的特点就是是一种函数式语言，据说这种语言可以减少代码量。而且设计上也更加适用于并行运算，因为它在设计上没有变量。没有变量就没有内存共享，这样就可以方便的进行并行运算了。


当然这都是被宣称的，真实情况就不是很清楚了。个人感觉，至少现在还不怎么流行就是了。主要这种语言要用的话原来的编程思路似乎得转变一下，然后它只提高了编程效率，对于运行效率却不太可能有什么提升。而且并行运算似乎也不是非它不可。现在编程的都是实用主义的，自然用的人就少了。在我看，这门语言目前比较适合对编程有些兴趣，想要挑战自己智商的人，因为它在具体的算法的设计和实现上确实比较精妙。不过F#是以ocaml为基础的，由于ocaml内部没有对应的图形库，所以F#必须搭配.net的其他语言才可以编出可视化的程序。


我想,学习一门新的语言对于程序员而言基本上是家常便饭了，所以基本上没有什么难的。


基本类型没有什么变化int、float、char、string、list都有,不过使用的时候不用事先声明习惯了c风格的童鞋可能会有点不习惯。


ocaml里最大的特点就是所谓的函数式程序的特性，也就说可以将函数定义好作为算子来使用。要说明的话太过于麻烦，而且要学语言最快的还是看代码。于是来看这段代码吧：



```
let nextx a x = (a/.x +. x) /. 2.0;;
let rec findroot a x acc =
  if abs_float (x -. nextx a x) < acc *. x then
    nextx a x
  else
    findroot a (nextx a x) acc  ;;
let sqroot a = findroot a 1.0 0.000001
```

这段代码是对牛顿逼近算法求平方根的一个实现，算法方面就不做解释了。可以看到nextx是用来求下一个逼近值的函数，而findroot则是主函数。在定义时需要递归的函数前必须加rec来声明，否则无法编译。这就是一段简单的ocaml程序，其实ocaml最主要的就是将函数编写成为通式来使用。这点和面向对象的一些思路很像，不过函数式语言最终的目的是将函数作为单体([monad](http://en.wikipedia.org/wiki/Monad_%28functional_programming%29))的运算子,以实现良好的有序操作或者控制流。


下面再给一段较为复杂的代码：



```
type ´a tree = Leaf ¦ Node of ´a * ´a tree * ´a tree;;

let rec fold_tree f e t =
  	match t with
  		Leaf -> e ¦
  		Node (a,b,c) -> f (a, fold_tree f e b , fold_tree f e c) ;;
let height t = fold_tree (fun (a,b,c) -> (max b c) + 1 ) 0 t;;
let t1 =
  Node ( "a" ,
    Node (  "b" ,
      Node ( "c" ,
        Node ( "d" , Leaf , Leaf) , Leaf ) ,Leaf) ,Node ( "e" ,Leaf,Leaf));;
let balance t = ( fold_tree (fun (a,b,c) -> if (b = -1 ¦¦ c == -1 ) then (-1)
				else
				  let ab =  abs (b-c) in
				  if ab <= 1 then (max b c)+1
				  else (-1)
				) 0 t ) <> (-1);;

balance (Node ( "a" , Leaf ,Leaf));;
balance t1;;
```

这是一段用于检验二叉树是否平衡的代码。上面的代码首先定义了一个类型tree用来表示二叉树，使用的定义方式类似于离散数学中的归纳定义。也就是Leaf是二叉树，而一个节点下有两个子树也是二叉树。而fold_tree则是ocaml中比较常见的一种通式的写法，通过match匹配，对整棵树进行遍历。而fold_tree的参数f则是一个可以自定义的函数。下面的函数balance就是对fold_tree的一种应用。


据说很好的利用通式可以简化编程的代码量和降低算法的设计复杂度，在实际写过一段时间之后发现确实如此，函数式语言还是有些优点的。不过我还没有系统的对ocaml进行过学习当然也没有继续深入研究的打算，如果要深入研究的话我推荐一下语言参考，解释的还是非常详细的。同时也把我这段作为习作写的代码也上传了吧，里面有关单体的运用的那块不是我一个人写的，总之希望对正在学习的人有所帮助吧。



>  下载地址：<http://3721up.com/4cve>
> 
> 


