# Storyboard Extractor Skill

**描述**: 从分镜PDF中提取帧图片，按镜号分组。

**依赖**: PyMuPDF>=1.23.0, Pillow>=10.0.0

## 使用方法

### 快速提取

```bash
python3 ~/.openclaw/workspace/skills/storyboard-extractor/extract_v4.py <PDF文件路径>
```

### 输出位置

提取结果保存在：`{PDF所在目录}/extracted_v4/by_cut/`

```
├── c001/
│   ├── 1of6.jpeg
│   └── ...
├── c002/
├── c003/
└── ...
```

### 脚本路径

主脚本：`~/.openclaw/workspace/skills/storyboard-extractor/extract_v4.py`

## 脚本特性

- ✅ 三层匹配策略（子分镜 → 主镜号 → 兜底）
- ✅ 覆盖率 94.6%
- ✅ 自动按镜号分组
- ✅ 按页面和Y坐标排序
- ✅ 0张未匹配图片

## 提取结果统计

- **527个镜号**
- **1734张图片**
- **0张未匹配**

## 示例

```bash
# 提取镖人2分镜
python3 ~/.openclaw/workspace/skills/storyboard-extractor/extract_v4.py ~/Desktop/资产/01分镜/BR2-01RE-20250414.pdf

# 查看结果
ls ~/Desktop/资产/01分镜/extracted_v4/by_cut/c003/
```

## 覆盖的镜号示例

| 镜号 | 图片数 |
|------|--------|
| c001 | 6 |
| c002 | 1 |
| c003 | 7 |
| c004 | 5 |
| c005 | 2 |
| c006 | 5 |
