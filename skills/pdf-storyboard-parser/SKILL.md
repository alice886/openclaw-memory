# PDF Storyboard Parser

**描述**: PDF 分镜解析器，从 PDF 分镜文件中按镜号提取分镜图和描述文字，为 AI 生成提供构图参考。

**职责范围**:
- ✅ 解析 PDF 分镜文件
- ✅ 识别镜号（OCR / 页码映射 / AI 分析）
- ✅ 提取分镜图（高清图片）
- ✅ 提取描述文字
- ✅ 按镜号组织输出文件

**不负责**:
- ❌ 资产查找（由 `asset-library-manager` 负责）
- ❌ AI 生成（由 `ai-shot-generator` 负责）

**触发条件**: 
- 用户说"解析 PDF 分镜"、"导入分镜稿"
- 用户上传 .pdf 分镜文件
- 用户说"提取分镜图"

---

## 📄 PDF 分镜格式

### 典型 PDF 分镜页面

```
┌─────────────────────────────────┐
│         镜号: c001              │
│                                 │
│   ┌─────────────────────────┐   │
│   │                         │   │
│   │    [分镜草图图像]       │   │
│   │                         │   │
│   └─────────────────────────┘   │
│                                 │
│  描述：洞穴外面，火光照耀。     │
│  刀马和小七站在洞口，警惕地     │
│  观察周围...                    │
│                                 │
│  机位：中景                     │
│  构图：中心构图                 │
└─────────────────────────────────┘
```

---

## 🔧 核心功能

### 1. 解析 PDF 分镜

**命令**:
```
解析 PDF 分镜 ~/MyFilm/分镜稿.pdf
导入分镜稿 storyboard.pdf
```

**执行流程**:

#### Step 1: 加载 PDF
```python
from pdf2image import convert_from_path

images = convert_from_path(
    "分镜稿.pdf",
    dpi=300  # 高分辨率
)

print(f"📄 PDF 共 {len(images)} 页")
```

#### Step 2: 逐页识别镜号
```python
import pytesseract
import re

for page_num, page_image in enumerate(images, start=1):
    # OCR 识别文字
    text = pytesseract.image_to_string(page_image, lang='chi_sim+eng')
    
    # 提取镜号
    shot_number = extract_shot_number_from_text(text)
    
    if not shot_number:
        print(f"⚠️  第 {page_num} 页: 未识别到镜号")
        shot_number = f"{page_num:03d}"  # 降级为页码
    
    print(f"[第 {page_num} 页] 识别镜号: {shot_number}")
```

**镜号识别正则**:
```python
def extract_shot_number_from_text(text):
    """
    识别镜号的多种格式：
    - c001, C001
    - 镜号: 001, 镜头: 001
    - Shot 001, shot001
    - 第001镜
    """
    patterns = [
        r'[cC](\d+)',              # c001, C001
        r'镜[号头][:：\s]*(\d+)',  # 镜号: 001
        r'[Ss]hot\s*(\d+)',        # Shot 001
        r'第\s*(\d+)\s*镜',        # 第001镜
        r'^(\d+)$'                 # 纯数字（行首）
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            num = int(match.group(1))
            return f"{num:03d}"
    
    return None
```

#### Step 3: 保存分镜图
```python
output_dir = Path(f"storyboard/shot_{shot_number}")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存图片
sketch_path = output_dir / "sketch_from_pdf.png"
page_image.save(sketch_path, "PNG", quality=95)

print(f"   📸 保存分镜图: {sketch_path}")
```

#### Step 4: 提取描述文字
```python
# 清理文字（移除镜号）
description = text
for pattern in [r'[cC]\d+', r'镜[号头][:：\s]*\d+', r'[Ss]hot\s*\d+']:
    description = re.sub(pattern, '', description)

description = description.strip()

# 保存描述
desc_path = output_dir / "description.txt"
with open(desc_path, 'w', encoding='utf-8') as f:
    f.write(description)

print(f"   📝 保存描述: {desc_path}")
```

---

### 2. 页码映射模式（备用）

**场景**：PDF 中镜号无法识别或格式不统一

**命令**:
```
解析 PDF 分镜 storyboard.pdf --mapping page-to-shot
```

**交互流程**:
```
📄 PDF 共 25 页

❓ 未能自动识别镜号，使用页码映射模式？

请输入映射规则：
- 简单模式（第 N 页 = 镜号 N）: 输入 "auto"
- 手动指定: 输入 "manual"
- 跳过: 输入 "skip"

用户输入: auto

✅ 使用自动映射:
   第 1 页 → 镜号 001
   第 2 页 → 镜号 002
   ...
   第 25 页 → 镜号 025

继续解析？(Y/n)
```

**手动映射**:
```json
{
  "1": "c001",
  "2": "c002",
  "3": "c003",
  "5": "c005",  // 第 4 页为空页，跳过
  ...
}
```

---

### 3. 批量处理

**命令**:
```
批量解析分镜 PDF ~/MyFilm/storyboards/*.pdf
```

**示例**:
```
~/MyFilm/storyboards/
├── 第一集_分镜.pdf
├── 第二集_分镜.pdf
└── 第三集_分镜.pdf

解析后：
storyboard/
├── shot_001/ (from 第一集)
├── shot_002/
...
├── shot_026/ (from 第二集)
...
```

---

### 4. AI 辅助识别（未来扩展）

**使用 OpenClaw 的 pdf 工具**:
```python
from openclaw import pdf_tool

for page_num in range(1, total_pages + 1):
    result = pdf_tool.analyze_page(
        pdf_path="分镜稿.pdf",
        page=page_num,
        prompt="请提取这页分镜图的镜号（如 c001, 镜头002 等）"
    )
    
    shot_number = result.shot_number
    description = result.description
```

---

## 📚 辅助脚本

### scripts/parse_pdf_storyboard.py

```python
#!/usr/bin/env python3
"""
解析 PDF 分镜文件
用法: python parse_pdf_storyboard.py <pdf_file> [output_dir]
"""

import sys
import re
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

def extract_shot_number(text):
    """识别镜号"""
    patterns = [
        (r'[cC](\d+)', 'prefix'),
        (r'镜[号头][:：\s]*(\d+)', 'chinese'),
        (r'[Ss]hot\s*(\d+)', 'english'),
        (r'第\s*(\d+)\s*镜', 'chinese_format'),
        (r'^(\d+)$', 'plain', re.MULTILINE)
    ]
    
    for pattern_info in patterns:
        pattern = pattern_info[0]
        flags = pattern_info[2] if len(pattern_info) > 2 else 0
        
        match = re.search(pattern, text, flags)
        if match:
            num = int(match.group(1))
            return f"{num:03d}"
    
    return None

def parse_pdf_storyboard(pdf_file, output_dir="storyboard"):
    """解析 PDF 分镜"""
    print(f"📄 正在解析 PDF: {pdf_file}\n")
    
    # 转换 PDF 为图片
    print("⏳ 转换 PDF 页面...")
    try:
        images = convert_from_path(pdf_file, dpi=300)
    except Exception as e:
        print(f"❌ PDF 转换失败: {e}")
        sys.exit(1)
    
    print(f"✅ PDF 共 {len(images)} 页\n")
    
    # 逐页处理
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    warnings = []
    
    for page_num, page_image in enumerate(images, start=1):
        print(f"[第 {page_num}/{len(images)} 页]")
        
        # OCR 识别
        text = pytesseract.image_to_string(page_image, lang='chi_sim+eng')
        
        # 提取镜号
        shot_number = extract_shot_number(text)
        
        if not shot_number:
            warnings.append(f"第 {page_num} 页: 未识别到镜号，使用页码")
            shot_number = f"{page_num:03d}"
        
        print(f"   🔍 识别镜号: {shot_number}")
        
        # 创建输出目录
        shot_dir = output_path / f"shot_{shot_number}"
        shot_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存分镜图
        sketch_path = shot_dir / "sketch_from_pdf.png"
        page_image.save(sketch_path, "PNG", quality=95)
        print(f"   📸 保存分镜图: {sketch_path}")
        
        # 提取描述
        description = text
        for pattern in [r'[cC]\d+', r'镜[号头][:：\s]*\d+', r'[Ss]hot\s*\d+']:
            description = re.sub(pattern, '', description)
        description = description.strip()
        
        if description:
            desc_path = shot_dir / "description.txt"
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(description)
            print(f"   📝 保存描述: {desc_path} ({len(description)} 字)")
        
        results.append({
            "page": page_num,
            "shot_number": shot_number,
            "sketch_path": str(sketch_path),
            "description_length": len(description)
        })
        
        print()
    
    # 报告
    print("="*50)
    print("✅ PDF 解析完成")
    print(f"   共提取 {len(results)} 个镜头")
    print(f"   📁 保存位置: {output_path}")
    
    if warnings:
        print(f"\n⚠️  警告: {len(warnings)} 条")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("="*50)
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python parse_pdf_storyboard.py <pdf_file> [output_dir]")
        print("\n示例:")
        print("  python parse_pdf_storyboard.py 分镜稿.pdf")
        print("  python parse_pdf_storyboard.py storyboard.pdf ~/MyFilm/storyboard")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "storyboard"
    
    parse_pdf_storyboard(pdf_file, output_dir)
```

---

## 🎓 最佳实践

### 1. PDF 分镜制作建议

**推荐格式**:
```
每页一个镜头
页面顶部明确标注镜号（c001, c002...）
分镜图清晰，占页面主体
描述文字简洁，包含关键信息
```

**避免**:
```
❌ 一页多个镜头（难以自动分割）
❌ 镜号不明确或格式混乱
❌ 图片模糊或分辨率过低
❌ 过多装饰性元素干扰 OCR
```

### 2. 镜号命名规范

**推荐**:
- `c001`, `c002`, `c003` （带前缀，易识别）
- `镜号: 001`, `镜号: 002` （中文标注）

**可识别**:
- `Shot 001`, `shot 002` （英文）
- `第001镜`, `第002镜` （中文格式）

**避免**:
- `1a`, `2b`（字母后缀难处理）
- `镜头A`, `镜头B`（非数字）

### 3. 分镜图质量

**要求**:
- 分辨率 ≥ 1024px（短边）
- 清晰的人物轮廓和构图
- 避免过度草图（线稿）
- 最好有基本的明暗关系

---

## 🔌 对外接口（供其他 Skill 调用）

### 函数: 解析 PDF 分镜
```javascript
// 输入
{
  "pdf_file": "分镜稿.pdf",
  "output_dir": "storyboard",
  "ocr_lang": "chi_sim+eng"
}

// 输出
{
  "status": "success",
  "total_pages": 25,
  "extracted_shots": 25,
  "output_dir": "storyboard",
  "warnings": [
    "第 5 页: 未识别到镜号"
  ],
  "shots": [
    {
      "shot_number": "001",
      "sketch_path": "storyboard/shot_001/sketch_from_pdf.png",
      "description": "洞穴外面..."
    },
    ...
  ]
}
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install pdf2image pytesseract pillow

# macOS
brew install poppler tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-chi-sim
```

### 2. 准备 PDF 分镜文件
确保每页包含：
- 镜号标注
- 分镜草图
- 简要描述（可选）

### 3. 解析
```
对 Agent 说：解析 PDF 分镜 ~/MyFilm/分镜稿.pdf
```

### 4. 验证输出
```bash
ls storyboard/shot_001/
# sketch_from_pdf.png
# description.txt
```

---

## 🔗 协作 Skills

- **输入**: PDF 分镜文件
- **输出**: 按镜号组织的分镜图和描述文字
- **被依赖**: 
  - `ai-shot-generator` - 读取分镜图作为构图参考

---

**版本**: 1.0.0  
**依赖**: pdf2image, pytesseract, pillow  
**输出**: storyboard/shot_XXX/ 目录
