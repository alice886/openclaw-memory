#!/usr/bin/env python3
"""
解析 Excel 香盘表
用法: python parse_excel.py <excel_file> [output_json]
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    print("❌ 缺少依赖：pandas")
    print("请运行: pip install pandas openpyxl")
    sys.exit(1)

def normalize_shot_number(raw_shot_id):
    """标准化镜号：c001 → 001"""
    if not raw_shot_id:
        return None
    
    raw_shot_id = str(raw_shot_id).strip()
    numbers = re.findall(r'\d+', raw_shot_id)
    
    if not numbers:
        return None
    
    shot_num = int(numbers[0])
    return f"{shot_num:03d}"

def split_multi_value(text):
    """拆分多值字段：刀马、小七 → ["刀马", "小七"]"""
    if pd.isna(text) or str(text).strip() in ["-", "无", "空", ""]:
        return []
    
    text = str(text)
    for sep in ["、", "，", ";", "；"]:
        text = text.replace(sep, ",")
    
    values = [v.strip() for v in text.split(",") if v.strip()]
    return values

def parse_excel_shot_mapping(excel_file, output_json=None, project_path="."):
    """解析 Excel 香盘表"""
    print(f"📄 正在解析 Excel: {excel_file}\n")
    
    # 读取 Excel
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"❌ 读取 Excel 失败: {e}")
        sys.exit(1)
    
    # 识别表头
    print("✅ 识别到表头:")
    for col in df.columns:
        print(f"   - {col}")
    
    # 解析数据
    shots = []
    warnings = []
    
    print(f"\n📊 解析数据行 ({len(df)} 行)...")
    
    for idx, row in df.iterrows():
        # 获取镜号
        raw_shot_id = None
        for col_name in ["镜号", "镜头号", "Shot", "shot"]:
            if col_name in df.columns:
                raw_shot_id = row.get(col_name)
                break
        
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
        
        # 单值字段映射
        single_fields = {
            "场景": "scene",
            "天气时间": "weather_time",
            "机位": "camera",
            "构图": "composition",
            "动作": "action",
            "时长": "duration",
            "备注": "notes"
        }
        
        for excel_col, json_field in single_fields.items():
            if excel_col in df.columns and not pd.isna(row[excel_col]):
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
        
        # 分镜图处理
        if "分镜图" in df.columns and not pd.isna(row["分镜图"]):
            sketches = split_multi_value(row["分镜图"])
        else:
            # 自动查找 storyboard/shot_XXX/ 目录
            storyboard_dir = Path(project_path) / "storyboard" / f"shot_{shot_number}"
            if storyboard_dir.exists():
                sketches = [str(p.relative_to(project_path)) for p in sorted(storyboard_dir.glob("*.png"))]
            else:
                sketches = []
        
        shot["sketches"] = sketches
        
        # 验证
        if not characters:
            warnings.append(f"镜头 {shot_number}: 缺少人物信息")
        if not shot.get("scene"):
            warnings.append(f"镜头 {shot_number}: 缺少场景信息")
        
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
    print(f"\n{'='*50}")
    print("✅ 解析完成")
    print(f"   共 {len(shots)} 个镜头")
    print(f"   📁 已保存: {output_json}")
    
    if warnings:
        print(f"\n⚠️  警告: {len(warnings)} 条")
        for warning in warnings[:10]:
            print(f"   - {warning}")
        if len(warnings) > 10:
            print(f"   ... 还有 {len(warnings)-10} 条警告")
    
    print("="*50)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python parse_excel.py <excel_file> [output_json] [project_path]")
        print("\n示例:")
        print("  python parse_excel.py shot_mapping.xlsx")
        print("  python parse_excel.py shot_mapping.xlsx output.json ~/MyFilm")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    project_path = sys.argv[3] if len(sys.argv) > 3 else "."
    
    parse_excel_shot_mapping(excel_file, output_json, project_path)
