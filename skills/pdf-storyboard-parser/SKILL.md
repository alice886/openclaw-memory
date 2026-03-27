# PDF Storyboard Parser v2.0

**职责**：从 PDF 分镜文件按 C 镜头号提取分镜图+描述文字，解决"页面顺序≠镜头号顺序"问题，支持多页镜头

**触发**：用户说"解析 PDF 分镜 [路径]"

**核心改进**：v1 用 pytesseract OCR 镜号识别全错；v2 用 AI(image 工具)逐页分析，正确识别 C 镜头号

---

## 关键概念

**C 镜头号格式**：`c001, c310...`（EP 间编号连续）

**多页镜头**：`c310` 可能有多张分镜图 `c310_1_of_2.png` `c310_2_of_2.png`，合并到同一目录

**目录结构**（v2 正确 vs v1 错误）：
```
storyboard/
├── shot_c001/          ← 按C镜头号（正确）
├── shot_c310/          ← 含多页分镜图
│   ├── c310_1_of_2.png
│   ├── c310_2_of_2.png
│   ├── description.txt
│   └── metadata.json
```

---

## 执行流程

1. **PDF → 图片**：pdf2image 转 300 DPI 高清图
2. **AI 逐页分析**：用 `image` 工具识别 C 镜头号 + 描述文字 + 场景 + 人物 + 机位 + 页码标注
3. **按镜头号建目录**：shot_cXXX/，多页镜头合并
4. **保存**：图片重命名 + description.txt + metadata.json

---

## AI 分析 Prompt

```
分析这张分镜页面，输出 JSON：
{
  "shot_number": "c310",
  "page_label": "1/2",
  "page_total": 2,
  "description": "分镜描述文字（动作/场景/对话）",
  "scene": "场景名称",
  "time": "白天/夜晚",
  "characters": ["刀马", "小七"],
  "camera": "机位/运镜",
  "confidence": 0.9
}
注意：page_label 填数字如 "1/2"，非镜头号
```

---

## 输出文件

**description.txt**：
```
【c310 - 1/2】
刀马站在洞穴外，观察周围...
【c310 - 2/2】
小七从洞内走出，说：...
```

**metadata.json**：
```json
{
  "shot_number": "c310",
  "total_pages": 2,
  "pages": [{
    "page_label": "1/2",
    "description": "刀马站在洞穴外...",
    "scene": "洞穴外", "time": "白天",
    "characters": ["刀马"], "camera": "中景"
  }]
}
```

---

## ⚠️ 注意

- PDF 每页可能有多个镜头（多个分镜格）→ AI 仔细识别
- 镜号跨页时：只有1张也标 1/1
- description.txt 有乱码 → 来自 PDF 本身文字，非 AI 识别问题
- PDF 分辨率要 300 DPI 以上，太低影响识别

---

**版本**：2.0.0（修复页面顺序≠镜头号问题，支持多页镜头）  
**依赖**：OpenClaw image 工具, pdf2image, Python 3.8+  
**协作**：ai-shot-generator, shot-config-builder
