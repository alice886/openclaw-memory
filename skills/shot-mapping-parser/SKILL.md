# Shot Mapping Parser (Excel Edition)

**描述**: Excel 香盘表解析器，读取影视项目的 Excel 香盘表，解析镜头配置并转换为标准化 JSON 格式。

**职责范围**:
- ✅ 解析 Excel 文件（.xlsx / .xls）
- ✅ 标准化镜号格式（c001 → 001）
- ✅ 拆分多值字段（"刀马、小七" → ["刀马", "小七"]）
- ✅ 字段映射与验证
- ✅ 输出标准化 JSON 配置

**不负责**:
- ❌ 资产查找（由 `asset-library-manager` 负责）
- ❌ AI 生成（由 `ai-shot-generator` 负责）

**触发条件**: 
- 用户说"解析香盘表"、"导入 Excel 香盘表"
- 用户上传 .xlsx / .xls 文件
- 用户说"读取 shot_mapping.xlsx"

---

## 📋 Excel 表格格式

### 标准字段（列名）

| 列名 | 必需 | 说明 | 示例 |
|------|------|------|------|
| 镜号 | ✅ | 镜头编号（可带前缀） | c001, C002, 003 |
| 场景 | ✅ | 场景名称 | 洞穴外面, 竹林 |
| 天气时间 | 可选 | 氛围描述 | 火光, 清晨, 夜晚 |
| 人物 | ✅ | 角色名称（多个用顿号分隔） | 刀马、小七 |
| 道具 | 可选 | 道具名称（多个用顿号分隔） | 刀, 宝剑 |

### 可选扩展字段

| 列名 | 说明 | 示例 |
|------|------|------|
| 机位 | 镜头角度 | 低角度仰拍, 特写 |
| 构图 | 构图方式 | 中心构图, 三分法 |
| 动作 | 角色动作描述 | 缓步前进, 拔剑 |
| 时长 | 镜头时长 | 5s, 3s |
| 备注 | 其他说明 | 需要强调光影 |
| 分镜图 | 分镜草图路径 | storyboard/shot_001/sketch_01.png |

---

## 📊 示例 Excel

**输入 Excel (shot_mapping.xlsx)**:

| 镜号 | 场景 | 天气时间 | 人物 | 道具 | 机位 | 时长 |
|------|------|----------|------|------|------|------|
| c001 | 洞穴外面 | 火光 | 刀马、小七 | 刀 | 低角度仰拍 | 5s |
| C002 | 竹林 | 清晨 | 刀马 | 宝剑 | 中景 | 3s |
| 003  | 城堡大厅 | 夜晚 | 埃文、莉娜 | - | 特写 | 4s |

**输出 JSON (shot_mapping.json)**:

```json
{
  "project_name": "项目名称（从文件名推断或用户指定）",
  "source_file": "shot_mapping.xlsx",
  "parsed_at": "2026-03-21T23:54:00+08:00",
  "total_shots": 3,
  "shots": [
    {
      "shot_number": "001",
      "original_shot_id": "c001",
      "scene": "洞穴外面",
      "weather_time": "火光",
      "characters": ["刀马", "小七"],
      "props": ["刀"],
      "camera": "低角度仰拍",
      "duration": "5s",
      "assets": {
        "characters": ["刀马", "小七"],
        "scenes": ["洞穴外面"],
        "props": ["刀"],
        "moods": ["火光"]
      },
      "sketches": []
    },
    {
      "shot_number": "002",
      "original_shot_id": "C002",
      "scene": "竹林",
      "weather_time": "清晨",
      "characters": ["刀马"],
      "props": ["宝剑"],
      "camera": "中景",
      "duration": "3s",
      "assets": {
        "characters": ["刀马"],
        "scenes": ["竹林"],
        "props": ["宝剑"],
        "moods": ["清晨"]
      },
      "sketches": []
    },
    {
      "shot_number": "003",
      "original_shot_id": "003",
      "scene": "城堡大厅",
      "weather_time": "夜晚",
      "characters": ["埃文", "莉娜"],
      "props": [],
      "camera": "特写",
      "duration": "4s",
      "assets": {
        "characters": ["埃文", "莉娜"],
        "scenes": ["城堡大厅"],
        "props": [],
        "moods": ["夜晚"]
      },
      "sketches": []
    }
  ]
}
```

---

## 🔧 核心功能

### 1. 解析 Excel 文件

**命令**:
```
解析香盘表 shot_mapping.xlsx
导入 Excel 香盘表 ~/MyFilm/shot_mapping.xlsx
```

**执行流程**:
1. 读取 Excel 文件（支持 .xlsx / .xls）
2. 识别表头行（第 1 行）
3. 逐行解析数据（从第 2 行开始）
4. 标准化镜号
5. 拆分多值字段
6. 映射字段到标准格式
7. 输出 JSON 文件

**输出示例**:
```
📄 正在解析 Excel: shot_mapping.xlsx

✅ 识别到表头:
   - 镜号
   - 场景
   - 天气时间
   - 人物
   - 道具
   - 机位
   - 时长

📊 解析数据行...
   [1/25] 镜号: c001 → 001
   [2/25] 镜号: C002 → 002
   [3/25] 镜号: 003  → 003
   ...

✅ 解析完成
   共 25 个镜头
   📁 已保存: shot_mapping.json

⚠️  警告: 2 条
   - 行 5: 镜号格式异常 "shot5" → 自动修正为 "005"
   - 行 12: "人物" 字段为空

💡 建议:
   - 统一镜号格式（推荐：001, 002, 003）
   - 补充缺失的人物信息
```

---

### 2. 镜号标准化

**处理各种格式**:

```javascript
// 输入 → 输出
"c001"    → "001"
"C001"    → "001"
"001"     → "001"
"c1"      → "001"
"C1"      → "001"
"shot001" → "001"
"Shot1"   → "001"
"s01"     → "001"
"S-001"   → "001"

// 提取逻辑：
1. 移除所有非数字字符
2. 补齐前导零（统一为 3 位数）
```

**实现**:
```python
import re

def normalize_shot_number(raw_shot_id):
    # 提取数字
    numbers = re.findall(r'\d+', raw_shot_id)
    if not numbers:
        return None
    
    # 取第一个数字
    shot_num = int(numbers[0])
    
    # 补齐前导零
    return f"{shot_num:03d}"

# 测试
normalize_shot_number("c001")    # → "001"
normalize_shot_number("C1")      # → "001"
normalize_shot_number("shot12")  # → "012"
```

---

### 3. 多值字段拆分

**支持的分隔符**:
- 顿号：`、`
- 中文逗号：`，`
- 英文逗号：`,`
- 空格
- 分号：`;` / `；`

**示例**:
```python
def split_multi_value(text):
    if not text or text.strip() in ["-", "无", "空", ""]:
        return []
    
    # 替换所有分隔符为统一符号
    text = text.replace("、", ",")
    text = text.replace("，", ",")
    text = text.replace(";", ",")
    text = text.replace("；", ",")
    
    # 拆分并清理
    values = [v.strip() for v in text.split(",") if v.strip()]
    return values

# 测试
split_multi_value("刀马、小七")         # → ["刀马", "小七"]
split_multi_value("刀马，小七，老王")   # → ["刀马", "小七", "老王"]
split_multi_value("刀马 小七")          # → ["刀马", "小七"]
split_multi_value("-")                  # → []
```

---

### 4. 字段映射

**Excel 列名 → JSON 字段**:

| Excel 列名 | JSON 字段 | 类型 | 备注 |
|------------|-----------|------|------|
| 镜号 | shot_number | string | 标准化后 |
| 场景 | scene | string | 单值 |
| 天气时间 | weather_time | string | 映射到 moods |
| 人物 | characters | array | 拆分多值 |
| 道具 | props | array | 拆分多值 |
| 机位 | camera | string | 可选 |
| 构图 | composition | string | 可选 |
| 动作 | action | string | 可选 |
| 时长 | duration | string | 可选 |
| 备注 | notes | string | 可选 |

**assets 字段自动生成**:
```json
"assets": {
  "characters": ["刀马", "小七"],        // 来自"人物"列
  "scenes": ["洞穴外面"],                // 来自"场景"列
  "props": ["刀"],                       // 来自"道具"列
  "moods": ["火光"]                      // 来自"天气时间"列
}
```

---

### 5. 分镜图关联

**策略 1: 自动推断**（默认）
```
镜号: 001
自动查找: storyboard/shot_001/*.png

找到：
- storyboard/shot_001/sketch_01.png
- storyboard/shot_001/sketch_02.png

添加到 sketches: [
  "storyboard/shot_001/sketch_01.png",
  "storyboard/shot_001/sketch_02.png"
]
```

**策略 2: Excel 中指定**
如果 Excel 有"分镜图"列：
```
| 镜号 | ... | 分镜图 |
|------|-----|--------|
| c001 | ... | storyboard/shot_001/sketch_01.png |
```
直接使用该路径。

---

## 📚 辅助脚本

### scripts/parse_excel.py

```python
#!/usr/bin/env python3
"""
解析 Excel 香盘表
用法: python parse_excel.py <excel_file> [output_json]
"""

import sys
import json
import re
from pathlib import Path
import pandas as pd
from datetime import datetime

def normalize_shot_number(raw_shot_id):
    """标准化镜号"""
    if not raw_shot_id:
        return None
    
    # 转为字符串并清理
    raw_shot_id = str(raw_shot_id).strip()
    
    # 提取数字
    numbers = re.findall(r'\d+', raw_shot_id)
    if not numbers:
        return None
    
    # 取第一个数字并补齐前导零
    shot_num = int(numbers[0])
    return f"{shot_num:03d}"

def split_multi_value(text):
    """拆分多值字段"""
    if pd.isna(text) or str(text).strip() in ["-", "无", "空", ""]:
        return []
    
    text = str(text)
    # 统一分隔符
    for sep in ["、", "，", ";", "；"]:
        text = text.replace(sep, ",")
    
    # 拆分并清理
    values = [v.strip() for v in text.split(",") if v.strip()]
    return values

def parse_excel_shot_mapping(excel_file, output_json=None):
    """解析 Excel 香盘表"""
    print(f"📄 正在解析 Excel: {excel_file}")
    
    # 读取 Excel
    df = pd.read_excel(excel_file)
    
    # 识别表头
    print("\n✅ 识别到表头:")
    for col in df.columns:
        print(f"   - {col}")
    
    # 定义字段映射
    field_mapping = {
        "镜号": "shot_number",
        "场景": "scene",
        "天气时间": "weather_time",
        "人物": "characters",
        "道具": "props",
        "机位": "camera",
        "构图": "composition",
        "动作": "action",
        "时长": "duration",
        "备注": "notes",
        "分镜图": "sketches"
    }
    
    # 解析数据
    shots = []
    warnings = []
    
    print(f"\n📊 解析数据行...")
    for idx, row in df.iterrows():
        # 获取原始镜号
        raw_shot_id = row.get("镜号", row.get("镜头号", None))
        if pd.isna(raw_shot_id):
            warnings.append(f"行 {idx+2}: 缺少镜号")
            continue
        
        # 标准化镜号
        shot_number = normalize_shot_number(raw_shot_id)
        if not shot_number:
            warnings.append(f"行 {idx+2}: 镜号格式无效 '{raw_shot_id}'")
            continue
        
        print(f"   [{idx+1}/{len(df)}] 镜号: {raw_shot_id} → {shot_number}")
        
        # 构建镜头配置
        shot = {
            "shot_number": shot_number,
            "original_shot_id": str(raw_shot_id),
        }
        
        # 单值字段
        for excel_col in ["场景", "天气时间", "机位", "构图", "动作", "时长", "备注"]:
            if excel_col in df.columns and not pd.isna(row[excel_col]):
                json_field = field_mapping.get(excel_col, excel_col)
                shot[json_field] = str(row[excel_col]).strip()
        
        # 多值字段
        characters = split_multi_value(row.get("人物"))
        props = split_multi_value(row.get("道具"))
        
        shot["characters"] = characters
        shot["props"] = props
        
        # 构建 assets 字段
        shot["assets"] = {
            "characters": characters,
            "scenes": [shot.get("scene")] if shot.get("scene") else [],
            "props": props,
            "moods": [shot.get("weather_time")] if shot.get("weather_time") else []
        }
        
        # 分镜图
        if "分镜图" in df.columns and not pd.isna(row["分镜图"]):
            sketches = split_multi_value(row["分镜图"])
        else:
            # 自动查找
            storyboard_dir = Path(f"storyboard/shot_{shot_number}")
            if storyboard_dir.exists():
                sketches = [str(p) for p in sorted(storyboard_dir.glob("*.png"))]
            else:
                sketches = []
        
        shot["sketches"] = sketches
        
        # 验证
        if not characters:
            warnings.append(f"镜头 {shot_number}: 缺少人物信息")
        
        shots.append(shot)
    
    # 生成输出 JSON
    result = {
        "project_name": Path(excel_file).stem,
        "source_file": str(excel_file),
        "parsed_at": datetime.now().isoformat(),
        "total_shots": len(shots),
        "shots": shots
    }
    
    # 保存
    if not output_json:
        output_json = str(Path(excel_file).with_suffix(".json"))
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 报告
    print(f"\n✅ 解析完成")
    print(f"   共 {len(shots)} 个镜头")
    print(f"   📁 已保存: {output_json}")
    
    if warnings:
        print(f"\n⚠️  警告: {len(warnings)} 条")
        for warning in warnings[:5]:  # 只显示前 5 条
            print(f"   - {warning}")
        if len(warnings) > 5:
            print(f"   ... 还有 {len(warnings)-5} 条警告")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python parse_excel.py <excel_file> [output_json]")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    parse_excel_shot_mapping(excel_file, output_json)
```

---

## 🔌 对外接口（供其他 Skill 调用）

### 函数 1: 解析 Excel
```javascript
// 输入
{
  "excel_file": "shot_mapping.xlsx",
  "project_path": "~/MyFilm/"
}

// 输出
{
  "status": "success",
  "output_json": "shot_mapping.json",
  "total_shots": 25,
  "warnings": [...]
}
```

### 函数 2: 获取镜头配置
```javascript
// 调用 parse_excel.py 后，读取生成的 JSON
// 与之前的 JSON 版本兼容
```

---

## 🎓 最佳实践

### 1. Excel 表格规范
```
✅ 推荐：
- 第 1 行：表头（镜号、场景、天气时间、人物、道具）
- 从第 2 行开始：数据
- 镜号格式统一（如 c001, c002, ...）
- 人物字段用顿号分隔（刀马、小七）

❌ 避免：
- 表头行合并单元格
- 数据中有空行
- 镜号格式不统一（c001 混 shot2）
```

### 2. 分镜图命名
```
推荐目录结构：
storyboard/
  shot_001/
    sketch_01.png
    sketch_02.png
  shot_002/
    sketch_01.png
```

### 3. 资产名称一致性
```
Excel 中的名称必须与资产文件名一致：
- Excel: "刀马" → 文件: 刀马_三视图.png
- Excel: "竹林" → 文件: 竹林_远景.png

不一致示例（会找不到）：
- Excel: "刀马" ≠ 文件: 青年刀马_三视图.png
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install pandas openpyxl
```

### 2. 准备 Excel 香盘表
创建 `shot_mapping.xlsx`，包含列：
- 镜号
- 场景
- 天气时间
- 人物
- 道具

### 3. 解析
```
对 Agent 说：解析香盘表 ~/MyFilm/shot_mapping.xlsx
```

或直接运行脚本：
```bash
python scripts/parse_excel.py shot_mapping.xlsx
```

### 4. 查看结果
```bash
cat shot_mapping.json
```

---

## 🔗 协作 Skills

- **输入**: Excel 文件 (.xlsx / .xls)
- **输出**: 标准化 JSON (`shot_mapping.json`)
- **被依赖**: 
  - `ai-shot-generator` - 读取 JSON 配置
  - `asset-library-manager` - 使用资产名称查找文件

---

**版本**: 2.0.0 (Excel Edition)  
**依赖**: pandas, openpyxl, jq  
**输出**: shot_mapping.json
