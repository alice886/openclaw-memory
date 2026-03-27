# Asset Library Manager v3.0

**职责**：资产扫描 + 三重过滤 + 语义标签 + 自然语言搜索

**触发**：初始化资产库 / 搜索资产 / 检查完整性 / 上传 ZenStudio

**不负责**：AI 生成（ai-shot-generator）/ 分镜解析（pdf-storyboard-parser）

---

## 三重过滤规则

### Step 1：文件格式过滤
排除：`.psd .psb .ai .sketch .blend`

### Step 2：文件名关键词过滤
**排除**：`RR` `线稿` `lineart` `sketch` `draft` `rough` `草图` `轮廓` `outline` `未上色` `uncolored` `bw`
**通过**：`清稿` `色稿` `上色` `final` `v2` `v3` `三视图` `turnaround`

### Step 3：图片内容分析（`image` 工具）
- ❌ 线稿：大量清晰线条 + 无阴影 + 无质感
- ✅ 上色稿：有颜色 + 有阴影/质感/立体感
- ⚠️ 赛璐璐风格（有颜色但几乎无阴影）易误判，关键看有无阴影/立体感

---

## 语义标签生成（初始化时）

对每个通过过滤的资产，用 `image` 工具分析：

```
分析这张图片，输出 JSON：
{
  "description": "一句话描述",
  "tags": ["关键词1", "关键词2"...],
  "scene": "场景类型",
  "has_people": true/false,
  "has_character": "角色名或null",
  "mood": "紧张/温馨/激烈...",
  "time_of_day": "白天/夜晚/黄昏..."
}
```

---

## 语义搜索（自然语言）

**示例**：
```
"沙漠黄昏不带人" → {scene:"沙漠", time_of_day:"黄昏", has_people:false}
"竹林激烈打斗" → {tags包含:["竹林","打斗"], mood:"激烈"}
"找夜晚有刀马的场景" → {has_character:"刀马", time_of_day:"夜晚"}
```

**匹配优先级**：
1. 精确属性（has_people / has_character / time_of_day）
2. Tags 关键词匹配（命中越多越优先）
3. scene 模糊匹配

**关键词搜索**（保留）：含具体资产名 → 精确匹配文件名

---

## 输出格式：project_index.json

```json
{
  "project_name": "镖人2",
  "total_files_scanned": 200,
  "valid_assets": 150,
  "assets": {
    "characters": {
      "青年刀马": {
        "path": "assets/characters/青年刀马_三视图.png",
        "colored": true, "priority": 1,
        "tags": ["刀马", "青年", "武士", "铠甲", "三视图"],
        "has_character": "刀马", "has_people": true
      }
    },
    "scenes": {
      "长江水战": {
        "path": "assets/scenes/灭陈水战.jpg",
        "tags": ["长江", "水战", "夜晚", "火光"],
        "scene": "长江", "mood": "紧张", "time_of_day": "夜晚"
      }
    }
  }
}
```

---

## 快速开始

```
初始化资产库 ~/Desktop/镖人2项目
找一张沙漠黄昏不带人的图片
查找角色 青年刀马
检查项目完整性
```

---

**版本**：3.0.0（语义标签 + 自然语言搜索）  
**依赖**：zencli, jq, find, OpenClaw image 工具  
**协作**：ai-shot-generator, shot-config-builder
