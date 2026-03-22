# PDF Storyboard Parser v2.0

**描述**: PDF 分镜解析器，从 PDF 分镜文件中按 C 镜头号提取分镜图和描述文字，解决页面顺序≠镜头号顺序的问题，支持多页镜头（1/2、2/2）。

**核心问题（v1.0 的缺陷）**:
- ❌ 用 pytesseract OCR 提取镜号 → 文字乱码，镜号识别全错
- ❌ 按页码顺序建文件夹 → shot_001 不等于 c001
- ❌ 多页镜头（1/2、2/2）没有合并处理

**v2.0 改进**:
- ✅ 用 AI（OpenClaw image 工具）逐页分析，正确识别 C 镜头号
- ✅ 按 C 镜头号建目录（shot_c310/shot_c311/）
- ✅ 多页镜头合并（1/2 + 2/2 → 同一目录多个文件）

---

## 📐 关键概念

### C 镜头号格式
```
c001, c002, c003...     （EP01 的镜头）
c310, c311, c312...     （EP03 的镜头，编号连续）
```

### 多页镜头
```
c311 页面 → 可能有 1/2 和 2/2 两张分镜图
c311_1_of_2.png           第1张
c311_2_of_2.png           第2张
```

### 目录结构变化

**旧（错误）**:
```
storyboard/
├── shot_001/      ← PDF第1页，不等于c001
├── shot_002/      ← PDF第2页，不等于c002
└── ...
```

**新（正确）**:
```
storyboard/
├── shot_c001/
│   ├── sketch.png
│   ├── description.txt
│   └── metadata.json
├── shot_c310/
│   ├── c310_1_of_2.png
│   ├── c310_2_of_2.png   ← 多页镜头
│   └── description.txt
└── ...
```

---

## 🔧 核心功能

### 1. 解析 PDF 分镜

**命令**:
```
解析 PDF 分镜 ~/Desktop/资产/01分镜/BR2-01RE-20250414.pdf
```

**执行流程**:

#### Step 1: PDF 转图片
用 pdf2image 将 PDF 每页转为高清图片（300 DPI）

#### Step 2: AI 逐页分析（关键改进）
对每一页图片，用 `image` 工具分析：

**分析 Prompt**:
```
分析这张分镜页面，输出 JSON：

{
  "shot_number": "c310",        ← 镜头号（c开头，如c001、c310）
  "page_label": "1/2",         ← 该镜头内的页码（1/2、2/3等，无则为1/1）
  "page_total": 2,              ← 该镜头共几页
  "description": "..."          ← 分镜描述文字（中文，动作、场景、对话等）
  "scene": "..."               ← 场景名称
  "time": "..."                ← 时间（白天/夜晚等）
  "characters": ["刀马", "小七"], ← 出现的人物
  "camera": "..."              ← 机位/运镜
  "confidence": 0.9             ← 识别置信度
}

注意：
- 如果页面没有镜头号，shot_number 填 null
- description 尽量完整提取页面上的文字描述
- page_label 只填数字，如 "1/2"，不是镜头号
```

#### Step 3: 按 C 镜头号组织目录
```python
# 识别结果示例
{
  "shot_number": "c310",
  "page_label": "1/2",
  "description": "刀马站在洞穴外，观察周围...",
  ...
}
```

**目录构建规则**:
```
shot_number + "_" + page_label  → 目录名/文件名
c310 + 1/2                     → shot_c310/c310_1_of_2.png
c310 + 2/2                     → shot_c310/c310_2_of_2.png
```

#### Step 4: 保存文件
```
storyboard/shot_c310/
├── c310_1_of_2.png           ← AI 重命名
├── c310_2_of_2.png           ← AI 重命名
├── description.txt            ← 所有描述合并
└── metadata.json              ← 原始 AI 分析结果
```

#### Step 5: 合并多页镜头描述
同一镜头的多页描述合并到一个 description.txt

---

## 📄 输出文件格式

### description.txt
```
【c310 - 1/2】
刀马站在洞穴外，观察周围，警惕地...

【c310 - 2/2】
小七从洞内走出，说：...
```

### metadata.json
```json
{
  "shot_number": "c310",
  "total_pages": 2,
  "pages": [
    {
      "page_label": "1/2",
      "description": "刀马站在洞穴外...",
      "scene": "洞穴外",
      "time": "白天",
      "characters": ["刀马"],
      "camera": "中景"
    },
    {
      "page_label": "2/2",
      "description": "小七从洞内走出...",
      "scene": "洞穴外",
      "time": "白天",
      "characters": ["刀马", "小七"],
      "camera": "中景"
    }
  ]
}
```

---

## 🔍 分镜图查找流程（重要）

**镜头号 ≠ 页面顺序**

```
用户要生成：c310
❌ 不能用 storyboard/shot_001/sketch.png
✅ 正确用 storyboard/shot_c310/c310_1_of_2.png
```

**查找规则**:
1. 扫描 storyboard/ 目录
2. 找 shot_c310 目录
3. 读 metadata.json 确认多页情况
4. 取 c310_1_of_2.png（默认第一张）

---

## 📝 快速开始

### 1. 解析
```
对 Agent 说：解析 PDF 分镜 ~/Desktop/资产/01分镜/BR2-01RE-20250414.pdf
```

### 2. 验证结果
```bash
ls storyboard/shot_c310/
# 应该看到 c310_1_of_2.png, c310_2_of_2.png, metadata.json
```

### 3. 生成时使用
```
shot_configs/shot_c310_config.json 里的 storyboard_ref 指向：
storyboard/shot_c310/c310_1_of_2.png
```

---

## ⚠️ 注意事项

1. **PDF 每页可能有多个镜头** — 一页包含多个分镜格，需要 AI 仔细识别
2. **镜号可能跨页** — c311 只有 1 张时会标 1/1，不是没有
3. **description.txt 可能有乱码** — 来自 PDF 本身的文字，不是 AI 识别问题
4. **PDF 分辨率要够高** — 300 DPI 以上，截图太低会影响 AI 识别

---

**版本**: 2.0.0（修复分镜图≠页面顺序问题，支持多页镜头）  
**依赖**: OpenClaw image 工具, pdf2image, Python 3.8+  
**协作 Skill**: ai-shot-generator, shot-config-builder