---
layout: post
status: publish
published: true
title: UE4属性反射小结
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2695
wordpress_url: https://blog.ch-wind.com/?p=2695
date: '2019-09-08 20:04:30 +0000'
date_gmt: '2019-09-08 12:04:30 +0000'
tags:
- UE4
---
UProperty是UE4自己建立的一个反射系统的一部分，这里稍微整理下接触到的东西。


平时使用时，如果声明使用了属性系统，就必须在头文件上包含`*.generated.h`


这样的话UE4就会“自动”的帮你完成反射部分的工作。这部分依赖于UBT和UHT，一般情况下不需要在意。


有的时候加完新的.h会提示这个文件不存在，一般情况下重新Generate一下项目就好了。


之所以动到这里是因为之前有个导出的需求，发现有个属性是Private的而有定义成UProperty。由于是制作插件所以不能修改引擎代码，所以只能从旁边绕路了。


## UProperty相关读取


对于指定Class里面的所有属性，可以直接使用帮助类来遍历：



```
for (TFieldIterator<UProperty> PropIt(GetClass()); PropIt; ++PropIt) 
{ 
  UProperty* Property = *PropIt; // Do something with the property 
}
```

在其之上就可以使用**ContainerPtrToValuePtr**或者**GetPropertyValue**来对属性进行读取了，在BlueprintNodeHelpers::CollectPropertyDescription中也能看到使用的实例。


或者也可以封装成函数：



```
bool GetFloatByName(UObject * Target, FName VarName, float &outFloat) 
{ 
  if (Target) //make sure Target was set in blueprints. 
  { 
    float FoundFloat; UFloatProperty* FloatProp = FindField<UFloatProperty>(Target->GetClass(), VarName);  // try to find float property in Target named VarName 
    if (FloatProp) //if we found variable 
    { 
      FoundFloat = FloatProp->GetPropertyValue_InContainer(Target);  // get the value from 
      FloatProp outFloat = FoundFloat;  // return float 
      return true; // we can return 
    } 
  } 
  return false; // we haven't found variable return false 
}
```

### 蓝图属性


关于蓝图的属性载入过程，可以参考AActor::Serialize：



```
if (const UBlueprintGeneratedClass* BPGC = Cast<UBlueprintGeneratedClass>(GetClass()))
{
  NativeConstructedComponentToPropertyMap.Reset();
  NativeConstructedComponentToPropertyMap.Reserve(OwnedComponents.Num());
  for(TFieldIterator<UObjectProperty> PropertyIt(BPGC, EFieldIteratorFlags::IncludeSuper); PropertyIt; ++PropertyIt)
  {
    UObjectProperty* ObjProp = *PropertyIt;
    // Ignore transient properties since they won't be serialized
    if(!ObjProp->HasAnyPropertyFlags(CPF_Transient))
    {
      UActorComponent* ActorComponent = Cast<UActorComponent>(ObjProp->GetObjectPropertyValue_InContainer(this));
      if(ActorComponent != nullptr && ActorComponent->CreationMethod == EComponentCreationMethod::Native)
      {
        NativeConstructedComponentToPropertyMap.Add(ActorComponent->GetFName(), ObjProp);
      }
    }
  }
}
```

## FGuid


这里要读取的是FGuid，当时做了两种尝试


### 通过ExportTextItem


这样做是因为FGuid有提供LexFromString方法，ExportTextItem本身封装在DescribeProperty中：



```
FString DescribeProperty(const UProperty* Prop, const uint8* PropertyAddr)
{
  FString ExportedStringValue;
  const UStructProperty* StructProp = Cast<const UStructProperty>(Prop);
  const UFloatProperty* FloatProp = Cast<const UFloatProperty>(Prop);
  if (StructProp && StructProp->GetCPPType(NULL, CPPF_None).Contains(GET_STRUCT_NAME_CHECKED(FBlackboardKeySelector)))
  {
    // special case for blackboard key selectors
    const FBlackboardKeySelector* PropertyValue = (const FBlackboardKeySelector*)PropertyAddr;
    ExportedStringValue = PropertyValue->SelectedKeyName.ToString();
  }
  else if (FloatProp)
  {
    // special case for floats to remove unnecessary zeros
    const float FloatValue = FloatProp->GetPropertyValue(PropertyAddr);
    ExportedStringValue = FString::SanitizeFloat(FloatValue);
  }
  else
  {
    Prop->ExportTextItem(ExportedStringValue, PropertyAddr, NULL, NULL, PPF_PropertyWindow, NULL);
  }
  const bool bIsBool = Prop->IsA(UBoolProperty::StaticClass());
  return FString::Printf(TEXT("%s: %s"), *FName::NameToDisplayString(Prop->GetName(), bIsBool), *ExportedStringValue);
}
```

实际使用的话是这样的：



```
UProperty* tp_FindedProp = FindField<UProperty>(tp_LandscapeHCC->GetClass(), TEXT("HeightfieldGuid"));
const uint8* PropData = tp_FindedProp->ContainerPtrToValuePtr<uint8>(tp_LandscapeHCC);
FString tstr_DProperty = DescribeProperty(tp_FindedProp, PropData);
FGuid ts_Guid;
LexFromString(ts_Guid, DProperty);
```

### 直接转换


其实也可以直接强制转换类型，不过会有一定的危险性



```
const FGuid* tp_GuidConvert = (FGuid*)PropData;
UE_LOG(LogTemp, Log, TEXT("Compare to see: %s || %s"), *tstr_DProperty, *LexToString(*tp_GuidConvert));
```

## UFUNCTION


这里的另一个需求是要求目标的Object实现一个事先约定好的接口，而插件这边则负责调用改接口来实现特定的额外导出。


其实FindFunctionByName是引擎内本来就有的 ，蓝图节点UK2Node_CallFunction中也能看到引擎是如何将功能暴露到蓝图的。在参考上UObject::CallFunctionByNameWithArguments和UObject::FindFunction也可以得到一些帮助，最后在实现上采用了这样的形式：



```
UE_LOG(LogWorldExport, Log, TEXT("Get target class"));
static FName ts_FuncName(TEXT("ExportOut"));
UFunction* tp_ExportFunc = tp_IterActor->FindFunction(ts_FuncName);
//tp_IterActor->ProcessEvent(tp_ExportFunc, nullptr);
if (tp_ExportFunc)
{
  FFrame Stack(tp_IterActor, tp_ExportFunc, nullptr);
  tp_ExportFunc->Invoke(tp_IterActor, Stack, nullptr);
}
else
{
  UE_LOG(LogWorldExport, Error, TEXT("Target class %s found but func %s is not fund"), *tstr_ActorName, *ts_FuncName.ToString());
}
```

如果需要返回值的话，可以这样：



```
const bool bHasReturnParam = Function->ReturnValueOffset != MAX_uint16;
uint8* ReturnValueAddress = bHasReturnParam ? ((uint8*)Parms + Function->ReturnValueOffset) : nullptr;
```

## 总结


其实在读取UStruct的时候，应当是可以使用**ContainerPtrToValuePtr**作Struct的转换的，不过不知道当时为什么没有这么做，这点只能留到下次有相关需求的时候再考证了。


另外，如果对UProperty的读写有兴趣的话，其实可以参考引擎的LoadConfig和SaveConfig，里面包含了所有类型的属性的读写。


