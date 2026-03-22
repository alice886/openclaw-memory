#!/usr/bin/env python3
"""
解析 PDF 分镜文件
用法: python parse_pdf_storyboard.py <pdf_file> [output_dir]
"""

import sys
import re
from pathlib import Path

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("❌ 缺少依赖库")
    print("请运行:")
    print("  pip install pdf2image pytesseract pillow")
    print("\n系统依赖:")
    print("  macOS: brew install poppler tesseract tesseract-lang")
    print("  Ubuntu: sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-chi-sim")
    sys.exit(1)

def extract_shot_number(text):
    """识别镜号的多种格式"""
    patterns = [
        (r'[cC](\d+)', 'prefix'),              # c001, C001
        (r'镜[号头][:：\s]*(\d+)', 'chinese'), # 镜号: 001
        (r'[Ss]hot\s*(\d+)', 'english'),       # Shot 001
        (r'第\s*(\d+)\s*镜', 'chinese_format'), # 第001镜
        (r'^(\d+)$', 'plain', re.MULTILINE)    # 纯数字
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
    print("⏳ 转换 PDF 页面为图片 (DPI=300)...")
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
        try:
            text = pytesseract.image_to_string(page_image, lang='chi_sim+eng')
        except Exception as e:
            print(f"   ⚠️  OCR 失败: {e}")
            text = ""
        
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
        
        # 提取描述（清理镜号）
        description = text
        for pattern in [r'[cC]\d+', r'镜[号头][:：\s]*\d+', r'[Ss]hot\s*\d+', r'第\s*\d+\s*镜']:
            description = re.sub(pattern, '', description)
        description = '\n'.join([line.strip() for line in description.split('\n') if line.strip()])
        
        if description:
            desc_path = shot_dir / "description.txt"
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(description)
            print(f"   📝 保存描述: {desc_path} ({len(description)} 字)")
        else:
            print(f"   ⚠️  未提取到描述文字")
        
        results.append({
            "page": page_num,
            "shot_number": shot_number,
            "sketch_path": str(sketch_path),
            "description_length": len(description)
        })
        
        print()
    
    # 报告
    print("="*60)
    print("✅ PDF 解析完成")
    print(f"   共提取 {len(results)} 个镜头")
    print(f"   📁 保存位置: {output_path.absolute()}")
    
    if warnings:
        print(f"\n⚠️  警告: {len(warnings)} 条")
        for warning in warnings[:10]:
            print(f"   - {warning}")
        if len(warnings) > 10:
            print(f"   ... 还有 {len(warnings)-10} 条警告")
    
    print("="*60)
    
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
    
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        sys.exit(1)
    
    parse_pdf_storyboard(pdf_file, output_dir)
