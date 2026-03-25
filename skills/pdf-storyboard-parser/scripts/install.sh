#!/bin/bash
# 一键安装脚本

echo "🔧 PDF 分镜图提取工具 v8 - 安装脚本"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3，请先安装 pip"
    exit 1
fi

echo "✅ pip3 已安装"

# 安装依赖
echo ""
echo "📦 正在安装 Python 依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "📖 使用方法:"
    echo "  python3 extract_v8.py <PDF文件路径>"
    echo ""
    echo "📚 查看完整文档:"
    echo "  cat README.md"
else
    echo ""
    echo "❌ 安装失败，请检查错误信息"
    exit 1
fi
