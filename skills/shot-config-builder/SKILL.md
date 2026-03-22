# Shot Config Builder

**描述**: 镜头配置构建器，读取香盘表配置，关联分镜图和资产，构建完整的 AI 生成执行配置。

**职责范围**:
- ✅ 读取 shot_mapping.json（来自 shot-mapping-parser）
- ✅ 查找分镜图路径（来自 pdf-storyboard-parser 或位图目录）
- ✅ 调用 asset-library-manager 查找资产
- ✅ 构建生成 Prompt
- ✅ 验证文件存在性
- ✅ 输出完整执行配置 (shot_config.json)

**不负责**:
- ❌ Excel/PDF 解析（由其他 parser 负责）
- ❌ 调用 zencli 生成（由 ai-shot-generator 负责）

**触发条件**: 
- 用户说"构建镜头配置"、"准备生成"
- 用户说"构建镜号 001 的配置"
- 其他 skill 调用：生成前准备

---

## 🔧 核心功能

### 1. 构建单镜头配置

**命令**:
```
构建镜头 001 的配置
准备生成镜号 c001
```

**执行流程**:

#### Step 1: 读取香盘表配置
```python
import json

with open("shot_mapping.json") as f:
    shot_mapping = json.load(f)

shot = next(s for s in shot_mapping["shots"] if s["shot_number"] == "001")

print(f"📋 镜号: {shot['shot_number']}")
print(f"   场景: {shot['scene']}")
print(f"   人物: {', '.join(shot['characters'])}")
```

#### Step 2: 查找分镜图
```python
from pathlib import Path

shot_number = shot["shot_number"]
storyboard_dir = Path(f"storyboard/shot_{shot_number}")

if storyboard_dir.exists():
    sketches = sorted(storyboard_dir.glob("*.png"))
    print(f"🎨 找到分镜图: {len(sketches)} 张")
else:
    print(f"⚠️  未找到分镜图目录")
    sketches = []
```

#### Step 3: 查找资产
```python
# 调用 asset-library-manager 的搜索功能

asset_paths = {
    "characters": [],
    "scenes": [],
    "props": [],
    "moods": []
}

# 查找角色
for char in shot["assets"]["characters"]:
    result = search_asset(char, "characters")
    
    if result["status"] == "found":
        asset_paths["characters"].append(result["path"])
        print(f"   ✅ 角色: {char} → {result['path']}")
    elif result["status"] == "multiple":
        print(f"   🟡 角色: {char} 有 {len(result['candidates'])} 个候选")
        # 触发二次确认
        choice = ask_user_confirm(result["candidates"])
        asset_paths["characters"].append(choice)
    else:
        print(f"   ❌ 未找到角色: {char}")

# 同样处理场景、道具、氛围
...
```

#### Step 4: 构建 Prompt
```python
def build_prompt(shot):
    """根据香盘表字段构建 Prompt"""
    
    # 基础模板
    template = "{scene_desc}{atmosphere}{characters_desc}{action}{reference}"
    
    # 场景描述
    scene_desc = f"在{shot['scene']}"
    
    # 氛围
    if shot.get("weather_time"):
        atmosphere = f"，{shot['weather_time']}氛围下"
    else:
        atmosphere = ""
    
    # 角色描述
    characters = "、".join(shot["characters"])
    props_desc = ""
    if shot.get("props"):
        props = "、".join(shot["props"])
        props_desc = f"手持{props}"
    
    characters_desc = f"，{characters}{props_desc}"
    
    # 动作（来自 description.txt 或 Excel）
    if shot.get("action"):
        action = f"，{shot['action']}"
    else:
        # 读取 PDF 提取的描述
        desc_file = Path(f"storyboard/shot_{shot['shot_number']}/description.txt")
        if desc_file.exists():
            action = f"，{desc_file.read_text(encoding='utf-8').strip()}"
        else:
            action = ""
    
    # 参考分镜图
    reference = "。参考分镜图构图，保持人物姿态和场景布局。"
    
    # 拼接
    prompt = template.format(
        scene_desc=scene_desc,
        atmosphere=atmosphere,
        characters_desc=characters_desc,
        action=action,
        reference=reference
    )
    
    return prompt

# 示例输出
prompt = build_prompt(shot)
print(f"\n📝 生成 Prompt:\n{prompt}")

# "在洞穴外面，火光氛围下，刀马、小七手持刀，
#  站在洞口，警惕地观察周围。
#  参考分镜图构图，保持人物姿态和场景布局。"
```

#### Step 5: 验证文件存在
```python
all_input_images = sketches + asset_paths["characters"] + asset_paths["scenes"] + asset_paths["props"] + asset_paths["moods"]

missing_files = []
for img in all_input_images:
    if not Path(img).exists():
        missing_files.append(img)

if missing_files:
    print(f"\n⚠️  缺失文件: {len(missing_files)} 个")
    for f in missing_files:
        print(f"   - {f}")
```

#### Step 6: 输出配置
```python
shot_config = {
    "shot_number": shot["shot_number"],
    "original_shot_id": shot.get("original_shot_id"),
    "input_images": [str(img) for img in all_input_images],
    "prompt": prompt,
    "generation_settings": {
        "model": shot.get("generation_settings", {}).get("model", "316"),
        "aspect_ratio": shot.get("generation_settings", {}).get("aspect_ratio", "16:9"),
        "resolution": shot.get("generation_settings", {}).get("resolution", "1K")
    },
    "metadata": {
        "scene": shot["scene"],
        "characters": shot["characters"],
        "props": shot.get("props", []),
        "weather_time": shot.get("weather_time"),
        "total_input_images": len(all_input_images),
        "has_sketches": len(sketches) > 0,
        "missing_files": missing_files
    }
}

# 保存
output_file = f"shot_configs/shot_{shot['shot_number']}_config.json"
Path("shot_configs").mkdir(exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(shot_config, f, ensure_ascii=False, indent=2)

print(f"\n✅ 配置已保存: {output_file}")
```

**输出示例 (shot_001_config.json)**:
```json
{
  "shot_number": "001",
  "original_shot_id": "c001",
  "input_images": [
    "storyboard/shot_001/sketch_from_pdf.png",
    "assets/characters/刀马_三视图.png",
    "assets/characters/小七_三视图.png",
    "assets/scenes/洞穴外面_远景.png",
    "assets/moods/火光_氛围.png"
  ],
  "prompt": "在洞穴外面，火光氛围下，刀马、小七手持刀，站在洞口，警惕地观察周围。参考分镜图构图，保持人物姿态和场景布局。",
  "generation_settings": {
    "model": "316",
    "aspect_ratio": "16:9",
    "resolution": "1K"
  },
  "metadata": {
    "scene": "洞穴外面",
    "characters": ["刀马", "小七"],
    "props": ["刀"],
    "weather_time": "火光",
    "total_input_images": 5,
    "has_sketches": true,
    "missing_files": []
  }
}
```

---

### 2. 批量构建配置

**命令**:
```
构建所有镜头配置
批量构建镜号 001-010
```

**执行流程**:
```python
def build_all_configs(shot_mapping_file, output_dir="shot_configs"):
    with open(shot_mapping_file) as f:
        shot_mapping = json.load(f)
    
    Path(output_dir).mkdir(exist_ok=True)
    
    total = len(shot_mapping["shots"])
    success = 0
    failed = []
    
    print(f"🚀 开始批量构建配置 (共 {total} 个镜头)\n")
    
    for idx, shot in enumerate(shot_mapping["shots"], start=1):
        shot_num = shot["shot_number"]
        print(f"[{idx}/{total}] 镜号: {shot_num}")
        
        try:
            config = build_shot_config(shot)
            output_file = Path(output_dir) / f"shot_{shot_num}_config.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            if config["metadata"]["missing_files"]:
                print(f"   ⚠️  缺失 {len(config['metadata']['missing_files'])} 个文件")
            else:
                print(f"   ✅ 完成")
            
            success += 1
        
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            failed.append(shot_num)
    
    print(f"\n{'='*60}")
    print(f"✅ 批量构建完成")
    print(f"   成功: {success} 个")
    print(f"   失败: {len(failed)} 个")
    
    if failed:
        print(f"\n失败镜号: {', '.join(failed)}")
    
    print(f"   📁 配置保存: {output_dir}/")
    print("="*60)
```

---

### 3. 验证配置完整性

**命令**:
```
验证镜头 001 的配置
检查配置完整性
```

**检查项**:
- ✅ 所有输入图片文件存在
- ✅ Prompt 不为空
- ✅ 分镜图存在
- ✅ 至少有 1 个角色资产
- ✅ 输入图片总数 ≤ 8（贝宝 pro 限制）

**输出示例**:
```
🔍 验证镜号 001

[文件存在性]
✅ 分镜图: storyboard/shot_001/sketch.png
✅ 角色 1: assets/characters/刀马.png
✅ 角色 2: assets/characters/小七.png
✅ 场景: assets/scenes/洞穴外面.png
✅ 氛围: assets/moods/火光.png

[内容完整性]
✅ Prompt 不为空 (98 字)
✅ 有分镜图
✅ 有角色资产 (2 个)

[生成参数]
✅ 模型: 316
✅ 比例: 16:9
✅ 输入图片: 5 张 (≤ 8)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 配置验证通过，可以生成
```

---

## 📚 辅助脚本

### scripts/build_shot_config.py

```python
#!/usr/bin/env python3
"""
构建镜头配置
用法: python build_shot_config.py <shot_mapping.json> [shot_number]
"""

import sys
import json
from pathlib import Path

def search_asset(name, category, project_path="."):
    """调用 asset-library-manager 查找资产"""
    index_file = Path(project_path) / "project_index.json"
    
    if not index_file.exists():
        return {"status": "not_found"}
    
    with open(index_file) as f:
        index = json.load(f)
    
    assets = index.get("assets", {}).get(category, {})
    
    # 精确匹配
    if name in assets:
        return {
            "status": "found",
            "path": assets[name]["path"]
        }
    
    # 模糊匹配
    candidates = []
    for asset_name, asset_info in assets.items():
        if name.lower() in asset_name.lower():
            candidates.append({
                "name": asset_name,
                "path": asset_info["path"]
            })
    
    if len(candidates) == 1:
        return {
            "status": "found",
            "path": candidates[0]["path"]
        }
    elif len(candidates) > 1:
        return {
            "status": "multiple",
            "candidates": candidates
        }
    
    return {"status": "not_found"}

def build_prompt(shot):
    """构建 Prompt"""
    scene_desc = f"在{shot['scene']}"
    
    atmosphere = ""
    if shot.get("weather_time"):
        atmosphere = f"，{shot['weather_time']}氛围下"
    
    characters = "、".join(shot["characters"])
    props_desc = ""
    if shot.get("props"):
        props = "、".join(shot["props"])
        props_desc = f"手持{props}"
    
    characters_desc = f"，{characters}{props_desc}"
    
    # 读取描述
    action = ""
    desc_file = Path(f"storyboard/shot_{shot['shot_number']}/description.txt")
    if desc_file.exists():
        action = f"，{desc_file.read_text(encoding='utf-8').strip()}"
    elif shot.get("action"):
        action = f"，{shot['action']}"
    
    reference = "。参考分镜图构图，保持人物姿态和场景布局。"
    
    prompt = f"{scene_desc}{atmosphere}{characters_desc}{action}{reference}"
    return prompt

def build_shot_config(shot, project_path="."):
    """构建单个镜头配置"""
    shot_number = shot["shot_number"]
    
    # 查找分镜图
    storyboard_dir = Path(project_path) / "storyboard" / f"shot_{shot_number}"
    sketches = []
    if storyboard_dir.exists():
        sketches = [str(p) for p in sorted(storyboard_dir.glob("*.png"))]
    
    # 查找资产
    asset_paths = []
    missing_assets = []
    
    for category in ["characters", "scenes", "props", "moods"]:
        for name in shot["assets"].get(category, []):
            result = search_asset(name, category, project_path)
            
            if result["status"] == "found":
                asset_paths.append(result["path"])
            else:
                missing_assets.append(f"{category}/{name}")
    
    # 构建 Prompt
    prompt = build_prompt(shot)
    
    # 收集所有输入图片
    all_input_images = sketches + asset_paths
    
    # 验证文件存在
    missing_files = []
    for img in all_input_images:
        if not Path(project_path, img).exists():
            missing_files.append(img)
    
    # 生成配置
    config = {
        "shot_number": shot_number,
        "original_shot_id": shot.get("original_shot_id"),
        "input_images": all_input_images,
        "prompt": prompt,
        "generation_settings": {
            "model": shot.get("generation_settings", {}).get("model", "316"),
            "aspect_ratio": shot.get("generation_settings", {}).get("aspect_ratio", "16:9"),
            "resolution": shot.get("generation_settings", {}).get("resolution", "1K")
        },
        "metadata": {
            "scene": shot.get("scene"),
            "characters": shot.get("characters", []),
            "props": shot.get("props", []),
            "weather_time": shot.get("weather_time"),
            "total_input_images": len(all_input_images),
            "has_sketches": len(sketches) > 0,
            "missing_files": missing_files,
            "missing_assets": missing_assets
        }
    }
    
    return config

def main():
    if len(sys.argv) < 2:
        print("用法: python build_shot_config.py <shot_mapping.json> [shot_number] [project_path]")
        print("\n示例:")
        print("  python build_shot_config.py shot_mapping.json")
        print("  python build_shot_config.py shot_mapping.json 001")
        print("  python build_shot_config.py shot_mapping.json 001 ~/MyFilm")
        sys.exit(1)
    
    mapping_file = sys.argv[1]
    target_shot = sys.argv[2] if len(sys.argv) > 2 else None
    project_path = sys.argv[3] if len(sys.argv) > 3 else "."
    
    # 读取香盘表
    with open(mapping_file) as f:
        shot_mapping = json.load(f)
    
    output_dir = Path(project_path) / "shot_configs"
    output_dir.mkdir(exist_ok=True)
    
    shots_to_build = shot_mapping["shots"]
    if target_shot:
        shots_to_build = [s for s in shots_to_build if s["shot_number"] == target_shot]
    
    if not shots_to_build:
        print(f"❌ 未找到镜号: {target_shot}")
        sys.exit(1)
    
    print(f"🚀 开始构建配置 (共 {len(shots_to_build)} 个镜头)\n")
    
    for idx, shot in enumerate(shots_to_build, start=1):
        shot_num = shot["shot_number"]
        print(f"[{idx}/{len(shots_to_build)}] 镜号: {shot_num}")
        
        config = build_shot_config(shot, project_path)
        
        output_file = output_dir / f"shot_{shot_num}_config.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        if config["metadata"]["missing_files"]:
            print(f"   ⚠️  缺失 {len(config['metadata']['missing_files'])} 个文件")
        else:
            print(f"   ✅ 完成")
    
    print(f"\n{'='*60}")
    print(f"✅ 配置构建完成")
    print(f"   📁 保存位置: {output_dir}/")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

## 🔗 协作 Skills

- **输入**: 
  - shot_mapping.json (from shot-mapping-parser)
  - storyboard/shot_XXX/ (from pdf-storyboard-parser)
  - project_index.json (from asset-library-manager)

- **输出**: 
  - shot_configs/shot_XXX_config.json

- **被依赖**: 
  - `ai-shot-generator` - 读取配置执行生成

---

**版本**: 1.0.0  
**依赖**: Python 3, pathlib, json  
**输出**: shot_configs/ 目录
