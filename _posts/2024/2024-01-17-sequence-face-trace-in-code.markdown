---
layout: post
title:  如何在代码中控制Sequence设置的FadeTrack
tags:
- ue5
---

有时出于表现需求，会在Sequence中添加FadeTrack用于遮蔽场景且选择KeepState，我们需要保证代码接管逻辑时其状态被清除掉。

当前使用的UE版本为UE5.3.2。

如果只是简单的使用FadeTrack是不会有问题的，但是当动态使用Sequence太多的时候，就很难控制最后一个执行的Sequence不是会保持状态的Fade。因此，干脆在代码中加一个保险。

通过名字判断，首先会找到，FadeTrack本身的定义是在`UMovieSceneFadeTrack`中的。经过一串查找，最后可以找到`FFadeUtil::ApplyFade`。而这其中我们的目标是这个：

```C++
    // Set runtime fade
    UObject* Context = Player.GetPlaybackContext();
    UWorld* World = Context ? Context->GetWorld() : nullptr;
    if( World && ( World->WorldType == EWorldType::Game || World->WorldType == EWorldType::PIE ) )
    {
        APlayerController* PlayerController = World->GetGameInstance()->GetFirstLocalPlayerController();
        if( PlayerController != nullptr && IsValid(PlayerController->PlayerCameraManager) )
        {
            PlayerController->PlayerCameraManager->SetManualCameraFade( FadeValue, FadeColor, bFadeAudio );
        }
    }
```

也就是说，实际调用`SetManualCameraFade`就可以调整FadeTrack了。

于是，在场景播放的动态Sequence系统结束时，调用下

```C++
SetManualCameraFade(0.0f, FLinearColor(0.0f, 0.0f, 0.0f, 0.0f), false);
```

就可以达到预期的效果了。