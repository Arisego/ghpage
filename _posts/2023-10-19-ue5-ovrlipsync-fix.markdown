---
layout: post
title:  UE5.2中OvrLipSync无法使用的问题
tags:
- ue5
---

OvrLipSync插件之前在UE4中使用还是比较正常的，但是在UE5.2上引入的时候发现生成的数据始终无法驱动动画。

当前使用的UE版本为UE5.2.0。

先直接上结论，输入指令：

> au.editor.ForceAudioNonStreaming 1

后再转化就可以了。

## 原因排查

这个插件之前用的时候是直接可以用的，所以没有怎么关注过细节。

这次稍微看了下实现，发现其原理还是比较简单的。尤其是针对离线数据使用的情况，其实就是针对语音文件生成了一个Visemes的数组。之后在语音播放时，根据当前播放的时间取到对应需要的MorphTarget值，然后设置到动画上。

由于这个过程在调试的时候不是很好判定，所以直接修改了插件的代码来观察生成的数据：

```C++
USTRUCT()
struct OVRLIPSYNC_API FOVRLipSyncFrame
{
	GENERATED_BODY()

	UPROPERTY(EditDefaultsOnly)
	TArray<float> VisemeScores;

	UPROPERTY(EditDefaultsOnly)
	float LaughterScore;

	FOVRLipSyncFrame(const TArray<float> &visemes = {}, float laughterScore = 0.0f)
		: VisemeScores(visemes), LaughterScore(laughterScore)
	{
	}
};
```

这样就可以在资产文件中观察生成的数据了，可以看到生成的数据全部都是0。

于是转到生成逻辑，发现在`DecompressSoundWave`内部调用`InitAudioResource`时，在检查`IsStreaming`的地方没通过，导致实际没有返回插件预期的数据。

虽然要比较正式的修改的话需要进一步的跟进流程来确定怎么调整，但是这部分代码是`OvrLipSync`官方维护的，要动起来也得花时间去看它的结构。发现有一个开关可以在编辑器内关闭这个行为后就没有跟进了。

这样可能只能在编辑器内起作用，但是由于实际使用的时候是直接调用生成的离线数据的。打包后离线数据的使用没有影响。

由于没有使用实时数据动态生成的需求，就没有继续跟进了。
