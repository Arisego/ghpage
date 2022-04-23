---
layout: post
status: publish
published: true
title: Blender和UE4的贴图修复脚本
author:
 display_name: 风铃
 login: flinkor
 email: flinkor@foxmail.com
 url: ''
author_login: flinkor
author_email: flinkor@foxmail.com
wordpress_id: 2815
wordpress_url: https://blog.ch-wind.com/?p=2815
date: '2020-04-11 21:04:30 +0000'
date_gmt: '2020-04-11 13:04:30 +0000'
tags:
- UE4
- Blender
- Python
---
最近遇到了Blender导出的材质没有贴图的问题，刚好顺便研究下UE4和Blender的脚本结构。



当前UE4版本为UE4.25.0；当前Blender版本为Blender2.82a。


首先，目前Blender和UE4的脚本版本是不同的。Blender使用的是python3，而UE4停留在python2.7。


这边使用Blender其实主要是作为模型导出的中继，比如MMD、VRM、XPS以及一些其他的非主流模型，通过Blender这边导出为FBX，然后输入到UE4去。


由于Blender和UE4的材质结构是不同的，到了UE4那边之后肯定要重新调整节点。所以对于缺少贴图的情况，最致命的问题就是，我们很难把材质名称和它使用的贴图对应起来。


因此这边就是实现这个过程的自动化，首先，从Blender这边导出材质使用到的贴图，然后在UE4那边还原到材质中去。


## Blender贴图导出


blender这边的script编辑器里面有个需要注意的地方，就是他的输出不是在左边的那个窗口输出的。虽然左边的console窗口可以用于测试指令，但是如果你在右侧的脚本上点击运行的话。输出其实是在外部的那个Console里面的。如果默认没有的话，需要在菜单中打开


[![image](https://blog.ch-wind.com/wp-content/uploads/2020/04/image_thumb-2.png "image")](https://blog.ch-wind.com/wp-content/uploads/2020/04/image-2.png)


Blender的脚本文档还是比较丰富的，不过由于功能比较多，这边只是做一个简单的材质中的贴图导出，所以并不一定是一个好的实现



```
# blender script
# python3

import bpy
import json

EXPORT_PATH = 'F:/materials.json'

class MatCollector:
    MatDic = {}

    # Collet material texture for single material
    def _CollectMaterial(self, InMaterial):
        MatTextures = []
        for ts_node in InMaterial.node_tree.nodes:
            if ts_node.bl_static_type == 'TEX_IMAGE' and ts_node.image:
                MatTextures.append(ts_node.image.filepath)

        tstr_MatName = InMaterial.name
        if len(MatTextures) == 0:
            print("[ExportMaterialTextures] <"+tstr_MatName+"> has no texture")
            return

        self.MatDic[tstr_MatName] = MatTextures
        print("[ExportMaterialTextures] Material " + tstr_MatName + " with " + str(len(MatTextures)) + " texture")
        pass

# List all materials and try pickout texture info
def ExportMaterialTextures(InPath):
    print("[ExportMaterialTextures] Begin: "+ InPath)
    ts_MatCollector = MatCollector()
    for Mat in bpy.data.materials:
        ts_MatCollector._CollectMaterial(Mat)
        
    print("[ExportMaterialTextures] Material with texture count " + str(len(ts_MatCollector.MatDic)))
    with open(InPath, 'w') as f:
        json.dump(ts_MatCollector.MatDic, f)

    print("[ExportMaterialTextures] End")


def main():
    ExportMaterialTextures(EXPORT_PATH)

if __name__ == "__main__":
    main()
```

脚本的作用很简单，就是遍历场景内所有的材质，然后将每个材质中带有的所有贴图都输出出来。


## UE4导入


当前UE4的编辑器Python插件是Beta状态，需要打开才能使用。


友情提醒：  
使用本文中的脚本前请注意备份项目文件!  
脚本操作可能会导致不可预期的结果，请在了解这种危险的情况下使用脚本操作！
UE4这边在完成FBX的导入之后，会看到所有的材质都是白的。所以我们这边用脚本，将对应的贴图添加到材质中去。不过，要在代码中操作材质是很麻烦的，连接的工作还是保留在了材质制作中。



```
# unreal script
# python2.7

import json
import unreal

from sets import Set

IMPORT_PATH = 'F:/materials.json'
IMPORT_TARGET = '/Game/Chara/'
TEXTURE_PATH = '/Game/Chara/Textures/'
TEXTURE_BASE = 'F:/z'


class MatTextureImporter:
    IsStateGood = True

    def ReadFromConfig(self):
        unreal.log("[MaterialTextureImport] Begin")

        # Load from Json config
        with open(IMPORT_PATH, 'r') as myfile:
            data=myfile.read()
        MatConf = json.loads(data)

        # Try import texture
        self._PreLoadTexture(MatConf)

        if self.IsStateGood == False:
            unreal.log_error("[MaterialTextureImport] Asset state not good, abort")
            return

        # Try apply texture to material
        unreal.log("[MaterialTextureImport] Total target material: " + str(len(MatConf)))
        with unreal.ScopedSlowTask(len(MatConf), "Modifing materials") as slow_task:
            for ts_key in MatConf:
                if slow_task.should_cancel():
                    break
                
                slow_task.enter_progress_frame(1)
                self._AddMaterialTexture(ts_key, MatConf[ts_key])

        unreal.log("[MaterialTextureImport] End")
        return  

    def _PreLoadTexture(self, InDic):
        print("[MaterialTextureImport] Pre load textures - Begin")

        # Build texture list
        tset_TexturePath = Set()
        for ts_MatKey in InDic:
            for ts_Texture in InDic[ts_MatKey]:
                ts_TextureName = unreal.Paths.get_base_filename(ts_Texture)
                ts_TextureUePath = TEXTURE_PATH + ts_TextureName

                if unreal.EditorAssetLibrary.does_asset_exist(ts_TextureUePath):
                    ts_TextureData = unreal.EditorAssetLibrary.find_asset_data(ts_TextureUePath)
                    if ts_TextureData.is_valid():
                        if ts_TextureData.asset_class == 'Texture2D':
                            # We will never find a good name while operation takes more than once, so just ignore
                            unreal.log_warning("[MaterialTextureImport] Texture " + ts_TextureUePath + " alread exist")
                            continue
                        else:
                            # While asset name conflicts, we will stop operation, as replacing or rename may break our project
                            unreal.log_error("[MaterialTextureImport] Asset " + ts_TextureUePath + " alread exist and it is not a texture!")
                            self.IsStateGood = False
                            return

                tset_TexturePath.add(ts_Texture)

        print("[MaterialTextureImport] Total texture need load: " + str(len(tset_TexturePath)))

        # Build import tasks
        import_tasks = []
        for ts_Texture in tset_TexturePath:
            print("[MaterialTextureImport] - " + ts_Texture)
            AssetImportTask = unreal.AssetImportTask()
            AssetImportTask.set_editor_property('filename', TEXTURE_BASE + ts_Texture)
            AssetImportTask.set_editor_property('destination_path', TEXTURE_PATH)
            AssetImportTask.set_editor_property('save', True)
            import_tasks.append(AssetImportTask)

        # Import textures
        AssetTools = unreal.AssetToolsHelpers.get_asset_tools() 
        AssetTools.import_asset_tasks(import_tasks)

        print("[MaterialTextureImport] Pre load textures - End")
        
        return

    def _AddMaterialTexture(self, InName, InList):
        InName = InName.replace(' ', '_')
        InName = InName.replace('.', '_')

        print("[MaterialTextureImport] Material: " + InName)

        # Try load material
        matpath = "Material'" + IMPORT_TARGET + InName + '.' + InName + "'"
        ts_LoadedMat = unreal.load_asset(matpath)
        if ts_LoadedMat is None:
            unreal.log_warning("[MaterialTextureImport] Invalid material path: " + matpath)
            return

        # Add texture to material
        #unreal.MaterialEditingLibrary.delete_all_material_expressions(ts_LoadedMat)
        td_TextureAdded = 0
        for ts_TexturePath in InList:
            ts_TextureName = unreal.Paths.get_base_filename(ts_TexturePath)
            ts_TextureUePath = TEXTURE_PATH + ts_TextureName
            ts_LoadedTexture = unreal.EditorAssetLibrary.load_asset(ts_TextureUePath)

            if ts_LoadedTexture is None:
                unreal.log_warning("[MaterialTextureImport] Could not load texture "+ ts_TextureUePath)
                continue

            ts_TextureNodeBc = unreal.MaterialEditingLibrary.create_material_expression(ts_LoadedMat, unreal.MaterialExpressionTextureSample, -400, 250 * td_TextureAdded)
            if ts_TextureNodeBc is None:
                unreal.log_warning("[MaterialTextureImport] Could not create node")
                continue

            ts_TextureNodeBc.set_editor_property("texture", ts_LoadedTexture)
            ts_TextureNodeBc.set_editor_property("desc", ts_TextureName)
            td_TextureAdded += 1

        print("[MaterialTextureImport] Material get  " + str(td_TextureAdded) + " texture")

        return

def main():
    ts_MatChanger = MatTextureImporter()
    ts_MatChanger.ReadFromConfig()

if __name__ == "__main__":
    main()

```

在制作中遇到的另一个问题是，由于模型那边Blender的材质使用到了复杂的Group Node，这边也对应的实现了Material Function，但是需要将材质改为使用Attribute输出。于是又写了个批量修改的脚本



```
import unreal

def list_assets(InPath, InClass):
    MatchedAssets = []

    for ts_AssetPath in unreal.EditorAssetLibrary.list_assets(InPath):
        ts_AssetData = unreal.EditorAssetLibrary.find_asset_data(ts_AssetPath)
        if ts_AssetData.asset_class == InClass:
            MatchedAssets.append(ts_AssetPath)

    return MatchedAssets



def ModifyMaterials():
    ts_Mats = list_assets("/Game/Chara/", 'Material')
    print(ts_Mats)
    ts_MatModified = []
    for ts_matPath in ts_Mats:
        ts_mat = unreal.EditorAssetLibrary.load_asset(ts_matPath)
        if ts_mat is None:
            unreal.log_warning("[MatModify] No material in " + ts_mat)
            continue
        #ts_mat.set_editor_property("use_material_attributes", True)  

        #unreal.MaterialEditingLibrary.recompile_material(ts_mat)
        ts_MatModified.append(ts_mat)

    unreal.EditorAssetLibrary.save_loaded_assets(ts_MatModified)

def main():
    ModifyMaterials()

if __name__ == "__main__":
    main()

```

## 总结


Blender和UE4两边的Python脚本都还是挺好用的。


不过UE4这边在批量修改完材质后会有一个卡顿的感觉，使用SlowTask包裹依然没有改善，不过由于是自用的脚本，就不纠结了。




