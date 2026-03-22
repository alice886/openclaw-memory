# Asset Library Manager

**描述**: 智能资产库管理系统，负责影视项目资产的扫描、过滤、索引、搜索和验证。支持 PSD 过滤、线稿识别、精准匹配和二次确认机制。

**职责范围**:
- ✅ 资产文件扫描与过滤
- ✅ 智能搜索与精准匹配
- ✅ 资产索引生成与维护
- ✅ 项目完整性检查
- ✅ 上传资产到 ZenStudio 媒资库

**不负责**:
- ❌ AI 生成任务执行（由 `storyboard-generator` 负责）
- ❌ 分镜脚本解析（由 `storyboard-generator` 负责）

**触发条件**: 
- 用户提到"扫描资产"、"查找资产"、"初始化资产库"
- 用户搜索角色/场景/道具（如"找青年刀马"）
- 用户要求"检查项目完整性"
- 用户需要"上传资产到云端"

---

## 📁 文件结构规范

资产库应按以下结构组织：

```
<项目路径>/
├── assets/                    # 资产库根目录
│   ├── characters/           # 人设图
│   │   ├── 青年刀马_三视图.png     ✅ 上色完成
│   │   ├── 青年刀马_线稿.png       ❌ 线稿（会被过滤）
│   │   ├── 老年刀马_三视图.png     ✅（不同角色）
│   │   └── 角色A.psd              ❌ PSD（会被过滤）
│   ├── scenes/               # 场景图
│   ├── props/                # 道具图
│   └── moods/                # 氛围图
└── project_index.json        # 资产索引（本 skill 生成）
```

---

## 🔧 核心功能

### 1. 初始化资产库
**命令**: 
```
初始化资产库 <项目路径>
扫描资产 <项目路径>
```

**执行流程**:
1. 读取 `asset_rules`（如果存在 `shot_mapping.json`）
2. 扫描 `assets/` 各子目录
3. 应用过滤规则（PSD、线稿等）
4. 可选：使用 `image` 工具验证图片是否上色
5. 生成 `project_index.json`
6. 输出统计报告

**输出示例**:
```
✅ 资产库初始化完成
📊 共扫描 150 个文件
✅ 有效资产: 45 个
❌ 已过滤: 105 个
   - PSD 文件: 60 个
   - 线稿: 30 个
   - 其他: 15 个

📋 资产统计:
   🎭 角色: 12 个
   🏞️ 场景: 18 个
   🎨 道具: 10 个
   🌅 氛围图: 5 个
```

---

### 2. 智能资产搜索
**命令**:
```
查找资产 <关键词> [类型]
搜索角色 青年刀马
找场景 竹林
```

**匹配策略（三层）**:

#### 第 1 层：完全匹配（最高优先级）
```bash
文件名必须包含完整关键词
示例：
✅ "青年刀马_三视图.png" ← 输入"青年刀马"
❌ "老年刀马.png"        ← 不匹配
❌ "刀马青年版.png"      ← 词序不同，进入下一层
```

#### 第 2 层：词序宽松匹配（需确认）
```bash
包含所有关键字但顺序不同
示例：
🟡 "刀马_青年版.png"     ← 包含"刀马"和"青年"
```

#### 第 3 层：模糊匹配（最低优先级，必须确认）
```bash
部分关键词匹配
示例：
🟡 "老年刀马.png"        ← 仅匹配"刀马"
```

**匹配流程图**:
```
用户输入：青年刀马
    ↓
第 1 层完全匹配 → 找到？
    ├─ 是 → 只有 1 个？
    │        ├─ 是 → 直接返回 ✅
    │        └─ 否 → 触发二次确认 🟡
    └─ 否 → 第 2 层宽松匹配 → 找到？
             ├─ 是 → 触发二次确认 🟡
             └─ 否 → 第 3 层模糊匹配 → 找到？
                      ├─ 是 → 触发二次确认 🟡
                      └─ 否 → 提供相似建议 💡
```

---

### 3. 二次确认机制
当匹配结果不唯一或不确定时，展示候选项供用户选择。

**确认消息格式**:
```
🔍 找到 3 个可能的"青年刀马"资产：

1️⃣ 青年刀马_三视图.png
   路径: assets/characters/青年刀马_三视图.png
   类型: 三视图 | 已上色 ✅
   [缩略图]

2️⃣ 刀马_青年版.png
   路径: assets/characters/刀马_青年版.png
   类型: 半身像 | 已上色 ✅
   [缩略图]

3️⃣ 青年时期_刀马.png
   路径: assets/characters/青年时期_刀马.png
   类型: 未知 | 已上色 ✅
   [缩略图]

💡 推荐使用 1️⃣（三视图更适合 AI 生成）

请回复数字选择，或输入"取消"
```

**Agent 行为**:
1. 使用 `message` 工具发送候选图片（`--media` 参数）
2. 等待用户回复
3. 解析用户选择（数字 1-N 或"取消"）
4. 返回选中的资产路径

---

### 4. 资产完整性检查
**命令**:
```
检查项目完整性
验证资产库
```

**检查项目**:
1. 读取 `shot_mapping.json`（如果存在）
2. 列出所有被引用的资产名称
3. 在 `project_index.json` 中查找
4. 标记：✅ 找到 | 🟡 多个候选 | ❌ 缺失

**输出报告**:
```
📋 项目完整性检查报告

✅ 完全匹配: 38/45 个资产
🟡 需要确认: 5 个资产（存在多个候选）
   - "青年刀马": 3 个候选
   - "竹林": 2 个候选
❌ 缺失资产: 2 个
   - "魔法书"（shot_005 需要）
   - "城堡内景"（shot_012 需要）

💡 建议：
1. 为"青年刀马"添加明确标记（如重命名）
2. 补充缺失的道具和场景图
3. 运行"重新扫描资产库"更新索引
```

---

### 5. 上传到 ZenStudio
**命令**:
```
上传资产到云端
同步资产库
```

**执行流程**:
1. 读取 `project_index.json`
2. 遍历所有有效资产
3. 调用 `zencli upload <文件>` 上传到 COS
4. 调用 `zencli asset create` 入库媒资
5. 更新 `project_index.json` 记录 CDN URL 和 asset_id
6. 输出上传报告

**输出示例**:
```
📤 开始上传资产...

[1/12] 青年刀马_三视图.png
   ✅ 已上传: https://zenvideo-pro.gtimg.com/.../xxx.png
   ✅ 已入库: asset_id = abc123

[2/12] 老年刀马_三视图.png
   ✅ 已上传
   ✅ 已入库: asset_id = def456

...

✅ 上传完成: 12/12 成功
📁 已更新 project_index.json
```

---

## 🔍 智能过滤规则

### 1. 文件格式过滤
**排除规则**:
```bash
- *.psd              # Photoshop 源文件
- *.psb              # 大型 PSD
- *.ai               # Illustrator
- *.sketch           # Sketch 设计稿
- *.blend            # Blender 工程文件
```

### 2. 线稿识别

**方法 1：文件名关键词过滤**（快速，优先）
```bash
排除包含以下关键词的文件：
- 线稿 / lineart / line-art
- 草图 / sketch / draft
- 轮廓 / outline
- 未上色 / uncolored / bw (black-white)
```

**方法 2：图像内容分析**（备用，慢但准确）

仅在以下情况触发：
- 用户明确要求："严格过滤线稿"
- 文件名不明确（无上述关键词）
- 初始化时设置 `strict_lineart_check: true`

实现方式：
```javascript
// 使用 OpenClaw 的 image 工具
const result = await image({
  image: "assets/characters/可疑文件.png",
  prompt: `判断这张图片：
    1. 是否为线稿（只有黑白线条，无色彩填充）？
    2. 是否已上色（有颜色、阴影、质感）？
    
    回答格式：
    线稿: 是/否
    已上色: 是/否
    置信度: 0-100`
});

if (result.includes("线稿: 是") || result.includes("已上色: 否")) {
  // 排除此文件
}
```

**识别特征**:
- ❌ 线稿：纯黑白、只有线条、无色彩填充、无阴影
- ✅ 完成稿：有颜色、有阴影、有材质质感、有光影

### 3. 三视图优先
**优先级排序**:
1. 文件名包含"三视图" / "turnaround" / "character_sheet"
2. 文件名包含"正侧背" / "front_side_back"
3. 图像分析确认（可选）

**标记方式**:
在 `project_index.json` 中标记：
```json
{
  "assets": {
    "characters": {
      "青年刀马": {
        "path": "assets/characters/青年刀马_三视图.png",
        "type": "turnaround",  // ← 三视图标记
        "colored": true,
        "verified": true,
        "priority": 1          // ← 最高优先级
      }
    }
  }
}
```

---

## 📄 输出格式：project_index.json

```json
{
  "project_name": "奇幻冒险短剧",
  "project_path": "/Users/alice/MyFilm",
  "scan_time": "2026-03-21T21:30:00+08:00",
  "total_files_scanned": 150,
  "valid_assets": 45,
  "filtered_files": 105,
  "assets": {
    "characters": {
      "青年刀马": {
        "path": "assets/characters/青年刀马_三视图.png",
        "filename": "青年刀马_三视图.png",
        "type": "turnaround",
        "colored": true,
        "verified": true,
        "file_size": 2048576,
        "resolution": "2048x2048",
        "uploaded": true,
        "cdn_url": "https://zenvideo-pro.gtimg.com/.../xxx.png",
        "asset_id": "abc123",
        "priority": 1
      },
      "老年刀马": {
        "path": "assets/characters/老年刀马_三视图.png",
        "filename": "老年刀马_三视图.png",
        "type": "turnaround",
        "colored": true,
        "verified": true,
        "uploaded": false,
        "priority": 1
      }
    },
    "scenes": {
      "竹林": {
        "path": "assets/scenes/竹林_远景.png",
        "filename": "竹林_远景.png",
        "type": "scene",
        "colored": true,
        "verified": true,
        "uploaded": false,
        "priority": 2
      }
    },
    "props": {},
    "moods": {}
  },
  "filter_stats": {
    "psd_files": 60,
    "lineart_files": 30,
    "other_excluded": 15
  }
}
```

---

## 🛠️ 实现要点

### Agent 行为规范

1. **首次使用必须初始化**
   ```
   用户: "查找青年刀马"
   Agent: 检测到 project_index.json 不存在
          → "需要先初始化资产库，请提供项目路径"
   ```

2. **文件路径解析**
   - 支持相对路径：`assets/characters/青年刀马.png`
   - 支持绝对路径：`/Users/alice/MyFilm/assets/characters/青年刀马.png`
   - 自动展开 `~`：`~/projects/MyFilm/`

3. **缓存策略**
   - `project_index.json` 作为缓存，避免重复扫描
   - 用户可手动刷新：`重新扫描资产库`
   - 检测文件变更（可选）：对比修改时间

4. **错误处理**
   - 目录不存在 → 提示用户确认路径
   - 无有效资产 → 提示检查文件格式和命名
   - 搜索无结果 → 提供相似建议（Levenshtein 距离）

5. **性能优化**
   - 扫描阶段：仅文件名过滤（快）
   - 初始化完成后：可选深度验证（慢）
   - 图像分析：仅在必要时使用

---

## 🔌 对外接口（供其他 Skill 调用）

### 函数 1：搜索资产
```javascript
// 输入
{
  "query": "青年刀马",
  "type": "characters",  // 可选
  "strict": false        // 是否要求完全匹配
}

// 输出
{
  "status": "found" | "multiple" | "not_found",
  "results": [
    {
      "name": "青年刀马",
      "path": "assets/characters/青年刀马_三视图.png",
      "cdn_url": "https://...",
      "asset_id": "abc123",
      "confidence": 100  // 匹配置信度
    }
  ]
}
```

### 函数 2：获取资产详情
```javascript
// 输入
{
  "name": "青年刀马",
  "type": "characters"
}

// 输出
{
  "path": "assets/characters/青年刀马_三视图.png",
  "cdn_url": "https://...",
  "asset_id": "abc123",
  "type": "turnaround",
  "colored": true
}
```

### 函数 3：批量获取资产
```javascript
// 输入
{
  "names": ["青年刀马", "竹林", "宝剑"],
  "types": ["characters", "scenes", "props"]
}

// 输出
{
  "found": [
    { "name": "青年刀马", "path": "...", ... },
    { "name": "竹林", "path": "...", ... }
  ],
  "missing": ["宝剑"]
}
```

---

## 📚 辅助脚本

### scripts/scan_assets.sh
```bash
#!/bin/bash
# 扫描资产目录并生成索引
# 用法: ./scan_assets.sh <项目路径>

PROJECT_PATH="$1"
ASSET_DIR="$PROJECT_PATH/assets"
OUTPUT="$PROJECT_PATH/project_index.json"

# 过滤规则
EXCLUDE_EXT='\.psd$|\.psb$|\.ai$|\.sketch$'
EXCLUDE_KW='线稿|lineart|sketch|draft|outline|草图'

echo "🔍 扫描资产库: $ASSET_DIR"

# 扫描各类资产
for category in characters scenes props moods; do
  echo "📁 扫描 $category..."
  find "$ASSET_DIR/$category" -type f \
    \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
    | grep -Ev "$EXCLUDE_EXT" \
    | grep -Ev "$EXCLUDE_KW"
done

# 生成 JSON（简化版，实际由 Agent 生成完整版）
```

### scripts/search_asset.sh
（已创建，见前面的代码）

### scripts/upload_assets.sh
```bash
#!/bin/bash
# 批量上传资产到 ZenStudio
# 用法: ./upload_assets.sh <project_index.json>

INDEX_FILE="$1"

# 读取资产列表并上传
jq -r '.assets[][] | .path' "$INDEX_FILE" | while read -r asset_path; do
  echo "📤 上传: $asset_path"
  
  # 1. 上传到 COS
  cdn_url=$(zencli upload "$asset_path" -o json | jq -r '.cdn_url')
  
  # 2. 入库媒资
  asset_id=$(zencli asset create --url "$cdn_url" --project-id <id> -o json | jq -r '.asset_id')
  
  echo "✅ CDN URL: $cdn_url"
  echo "✅ Asset ID: $asset_id"
done
```

---

## 🎓 最佳实践

### 1. 文件命名规范
```
推荐格式：<名称>_<类型>_<版本>.png

✅ 青年刀马_三视图_v2.png
✅ 老年刀马_半身像_final.png
✅ 竹林_远景_日间.png
✅ 宝剑_特写_上色.png

❌ IMG_20240315.png
❌ 新建文件夹/角色1.png
❌ 刀马(1)(2)最终版v3真的最终版.png
```

### 2. 目录结构
```
assets/
├── characters/          # 所有角色放这里
│   ├── 青年刀马_三视图.png
│   └── 老年刀马_三视图.png
├── scenes/              # 所有场景放这里
│   ├── 竹林_远景.png
│   └── 城堡_内景.png
├── props/               # 所有道具放这里
└── moods/               # 所有氛围图放这里

不要：
❌ assets/角色/人物/主角/青年/刀马.png  （嵌套太深）
❌ assets/characters/青年刀马/三视图/final/v2.png  （过度分类）
```

### 3. 版本管理
```
同一资产的多个版本：
青年刀马_三视图_v1.png
青年刀马_三视图_v2.png
青年刀马_三视图_final.png  ← 推荐使用

优先级：
1. 标记为 "final" 或 "official"
2. 版本号最高（v3 > v2 > v1）
3. 修改时间最新
```

### 4. 定期维护
```
建议每周执行：
1. 重新扫描资产库（刷新索引）
2. 检查项目完整性
3. 清理未使用的资产
4. 备份 project_index.json
```

---

## 📌 常见问题

### Q1: 为什么找不到某个资产？
**可能原因**:
1. 文件名包含"线稿"等关键词被过滤
2. 文件格式是 PSD
3. 文件在错误的目录（如放在 `scenes/` 但应该在 `characters/`）
4. `project_index.json` 过期，需重新扫描

**解决方法**:
```
1. 检查文件名和格式
2. 运行"重新扫描资产库"
3. 使用"列出所有资产"查看完整列表
```

### Q2: 如何区分"青年刀马"和"老年刀马"？
**关键**：文件名必须包含完整的区分信息
```
✅ 青年刀马_三视图.png
✅ 老年刀马_三视图.png

❌ 刀马_v1.png  （无法区分）
❌ 刀马(青年).png  （括号内的信息可能被忽略）
```

### Q3: 图像分析很慢怎么办？
**优化方案**:
1. 使用规范的文件命名，避免触发图像分析
2. 在 `asset_rules` 中设置 `strict_lineart_check: false`
3. 仅在初始化时执行一次深度验证

---

## 🚀 快速开始

### 1. 准备项目目录
```bash
mkdir -p ~/MyFilm/assets/{characters,scenes,props,moods}
```

### 2. 复制资产文件
```bash
# 将你的图片文件复制到对应目录
cp 角色图/*.png ~/MyFilm/assets/characters/
cp 场景图/*.png ~/MyFilm/assets/scenes/
```

### 3. 初始化资产库
```
对 Agent 说：初始化资产库 ~/MyFilm
```

### 4. 搜索资产
```
对 Agent 说：查找青年刀马
```

### 5. 上传到云端（可选）
```
对 Agent 说：上传资产到云端
```

---

## 📦 输出产物

本 Skill 生成以下文件：

1. **project_index.json** - 资产索引（主要输出）
2. **asset_scan_report.txt** - 扫描报告（可选）
3. **missing_assets.txt** - 缺失资产列表（如果有）

这些文件会被 `storyboard-generator` skill 读取使用。

---

**版本**: 1.0.0  
**依赖**: zencli, jq, grep, find  
**协作 Skill**: storyboard-generator
