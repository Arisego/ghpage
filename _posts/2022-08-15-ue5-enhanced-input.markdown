---
layout: post
title:  UE5 Enhanced input
tags:
- UE5
---

最近看Lyra的代码，发现有个新的Enhanced Input系统，稍微看了下。

当前使用的UE5版本为5.0.3。

这个系统目前还在实验性阶段，但是看起来官方似乎挺想推的。

[官方文档](https://docs.unrealengine.com/4.27/en-US/InteractiveExperiences/Input/EnhancedInput/)和社区的[使用教程](https://dev.epicgames.com/community/learning/tutorials/aqrD/unreal-engine-enhanced-input-binding-with-gameplay-tags-c)都有比较详尽的描述。

虽然看起来这个系统是为`GameAbilitySystem`而设计的，且教程那边也用到了`GamePlayTags`。但是实际上这个系统本身并不强制的使用这两个东西。

## 简单使用

基础的配置当然还是要按照官方的来，需要打开插件，然后将输入系统配置到Enhanced Input。

其实这个系统主要就是将原本只能在项目配置中定义的输入传递给资产化了，方便动态绑定。

原本在UE4的时候我们要实现动态绑定需要自己做一层中继，现在只是官方给出了可以方便进行动态绑定的部分而已。

核心的部分是`UInputAction`与`Input Mapping Contexts`，这两个的使用可以参照上面给出的第二个链接。

只不过`UInputAction`可以直接配置，不需要硬性使用GAS那一套东西。感觉最大的好处是方便项目之间迁移，之前迁移一些逻辑后会发现输入配置对不上。有的时候要到代码和蓝图里面找逻辑中原本绑定的输入到底是什么。输入的配置资产化之后就可以连输入部分一起迁移了。

当然，有一个官方的动态输入绑定方案自然会方便很多。

### 输入类型

这里面个人在测试的时候遗漏了一个地方，就是移动方向这些输入需要修改为Axis2D

1. IA_Fire - ValueType(bool), Triggers(Pressed), Modifiers(None)
2. IA_Jump - ValueType(bool), Triggers(Pressed ), Modifiers(None) 
3. IA_Move - ValueType(Axis2D), Triggers(None ), Modifiers(None ) 
4. IA_MouseLook - ValueType(Axis2D), Triggers(None), Modifiers(Negate - Y axis) 
5. IA_StickLook - ValueType(Axis2D ), Triggers(None), Modifiers(None)

如果这里漏掉的话，之后做输入转换的一些2维的操作其实是会失败的。

表现上会变成只能左右移动无法上下移动，由于原文只有这里没有截图，当时跳过去了。

## CommonUI问题

CommonUI这边有一个全局的Action绑定，但是配置好之后使用的过程中总是会报错。

> "Cannot
> bind widget [%s] to action [%s] - provided tag does not map to an existing UI
> input action. It can be added under Project Settings->UI Input.

排查了下原因，感觉是实验性阶段的BUG。主要的问题来源是：

`UCommonUIInputSettings`的加载时机要早于`FGlobalUITags`的标签加载时机

> UGameplayTagsManager::OnLastChanceToAddNativeTags

导致在配置加载的时候没有读取到Tag，最后绑定的时候就错了。

倒腾了下没发现好的直接修正的方式，只能通过自己定义Tag的方式来绕过。自己定义Tag可以选择直接在项目配置里面加。如果一时之间找不到配置的位置，在项目配置里面搜索`gameplay tags`即可。

或者在代码中快速定义：

> UE_DEFINE_GAMEPLAY_TAG_STATIC(Tag_CUSTOM_SETTINGS_INPUT_ACTION_Cancel, "UI.Action.Css.Cancel");

也可以通过.h与.cpp中分别定义来方便别的类能够取到

> UE_DECLARE_GAMEPLAY_TAG_EXTERN(Tag_CUSTOM_SETTINGS_INPUT_ACTION_Confrim);

> UE_DEFINE_GAMEPLAY_TAG(Tag_CUSTOM_SETTINGS_INPUT_ACTION_Confrim, "UI.Action.Css.Confirm")

## 总结

总体而言感觉新系统的意义不是很大，如果项目中已有完整的输入管理逻辑的话，没有必要迁移。可能对新项目可以考虑下……