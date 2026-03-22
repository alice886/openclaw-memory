# Shot Config Builder

**描述**: 将资产、分镜、香盘表关联起来，构建每个镜头的完整生成配置（Prompt + 资产路径 + 参数），输出到 `shot_configs/shot_XXX_config.json`，供 ai-shot-generator 执行。

**触发条件**: 
- 用户说"构建镜头配置"
- 用户说"准备生成 XXX"
- shot_mapping.json 已存在，需要生成具体镜头的配置

---

## 📐 标准化工作流

### 输入数据

1. **shot_mapping.json** — 由 shot-mapping-parser 从 Excel 香盘表解析得到
   - 包含：镜号、场景、人物、道具、讲戏 等字段

2. **project_index.json** — 由 asset-library-manager 扫描资产库得到
   - 包含：每个资产的文件路径、CDN URL、tags

3. **storyboard/shot_XXX/sketch.png** — 分镜图
   - 来源：`~/Desktop/镖人2项目/storyboard/shot_XXX/sketch.png`

### 输出数据

`shot_configs/shot_XXX_config.json`:
```json
{
  "shot_id": "c003",
  "episode": "EP01",
  "scene": "长江-隋军马船",
  "time": "夜晚",
  "character": "青年刀马",
  "props": "刀马腰间绑的4把刀",
  "storyboard_ref": "~/Desktop/镖人2项目/storyboard/shot_XXX/sketch.png",
  "prompt": {
    "image": "【二维动画风格】...\n构图严格参考分镜图。\n人物严格参考青年刀马人设图。\n场景氛围严格参考灭陈水战。",
    "video": "二维动画风格，长江夜晚水战，青年刀马在战船上..."
  },
  "assets": {
    "character": {
      "name": "青年刀马",
      "path": "~/Desktop/资产/人设定稿/001刀马/BR2_青年刀马_人设设定清稿_rr2.jpg",
      "cdn_url": "https://...",
      "type": "character"
    },
    "scene": {
      "name": "灭陈水战",
      "path": "~/Desktop/资产/氛围/氛围/灭陈水战.jpg",
      "cdn_url": "https://...",
      "type": "scene"
    },
    "storyboard": {
      "path": "~/Desktop/镖人2项目/storyboard/shot_XXX/sketch.png",
      "cdn_url": "https://...",
      "type": "storyboard"
    }
  },
  "generation": {
    "image_model": "316",
    "image_resolution": "2K",
    "video_model": "2",
    "video_duration": 5
  }
}
```

---

## 🔧 执行步骤

### Step 1: 读取 shot_mapping.json
找到目标镜号的记录，提取：
- 镜号
- 场景（匹配氛围图）
- 人物（匹配人设图）
- 道具
- 讲戏（Prompt 基础文本）

### Step 2: 匹配资产

**场景匹配规则**：
```
香盘表场景 → 资产库场景
"长江-隋军马船" → "灭陈水战.jpg"
"相州寺外" → "相州寺外冬近.jpg"
"竹林" → "竹林死斗修改.jpg"
```

**人设匹配规则**：
```
香盘表人物 → 人设定稿
"青年刀马" → "001刀马/BR2_青年刀马_人设设定清稿_rr2.jpg"
"大隋士兵" → "056大隋士兵/大隋士兵-全身-色稿.png"
```

**注意区分**：
- 青年刀马 ≠ 刀马17岁
- 陈国武将 ≠ 陈国士兵

### Step 3: 上传资产获取 CDN URL
对所有未上传的资产执行 `zencli upload`，获取 CDN URL。

### Step 4: 构建 Prompt
从「讲戏」字段提取基础描述，加上风格和参考说明：

```
【二维动画风格】
[从讲戏解析的场景描述]
构图严格参考分镜图（storyboard/sketch.png）。
人物严格参考[角色名]人设图。
场景氛围严格参考[场景图名称]。

确保：角色与人设图完全一致，场景与参考图一致，构图与分镜图一致，二维动画风格，清晰分层。
```

### Step 5: 写入 shot_configs/
```bash
mkdir -p ~/Desktop/镖人2项目/shot_configs/
# 写入 shot_c003_config.json
```

---

## 📋 香盘表字段说明

| 字段 | 说明 | 用途 |
|------|------|------|
| 镜号 | c001, c002 等 | 唯一标识 |
| 场景 | 长江-隋军马船 等 | 匹配场景氛围图 |
| 天气时间 | 夜晚、船上火光 等 | 加入 Prompt |
| 人物 | 青年刀马、大隋士兵 等 | 匹配人设图 |
| 道具 | 刀马腰间4把刀 等 | 加入 Prompt |
| 讲戏 | 36长江水战 等 | Prompt 基础文本 |

---

**版本**: 2.0.0（新增标准化工作流）  
**依赖**: shot-mapping-parser, asset-library-manager, ai-shot-generator