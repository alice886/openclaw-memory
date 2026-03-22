#!/bin/bash
# 资产智能搜索脚本
# 用法: ./search_asset.sh <资产类型> <搜索关键词> <项目路径>

ASSET_TYPE="$1"  # characters/scenes/props/moods
QUERY="$2"
PROJECT_PATH="$3"

ASSET_DIR="$PROJECT_PATH/assets/$ASSET_TYPE"

if [ ! -d "$ASSET_DIR" ]; then
  echo "❌ 资产目录不存在: $ASSET_DIR"
  exit 1
fi

# 过滤规则
exclude_pattern='\.psd$|\.psb$|\.ai$|\.sketch$|线稿|lineart|sketch|draft|outline|草图'

echo "🔍 搜索 \"$QUERY\" 在 $ASSET_TYPE..."

# 第 1 层：完全匹配
echo ""
echo "--- 第 1 层：完全匹配 ---"
exact_matches=$(find "$ASSET_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
  | grep -i "$QUERY" \
  | grep -Ev "$exclude_pattern")

if [ -n "$exact_matches" ]; then
  count=$(echo "$exact_matches" | wc -l)
  echo "✅ 找到 $count 个完全匹配:"
  echo "$exact_matches" | nl
  exit 0
fi

# 第 2 层：词序宽松匹配（所有关键词都存在）
echo ""
echo "--- 第 2 层：宽松匹配 ---"
words=$(echo "$QUERY" | tr ' ' '|')
loose_matches=$(find "$ASSET_DIR" -type f \( -name "*.png" -o -name "*.jpg" \) \
  | grep -Ev "$exclude_pattern" \
  | grep -Ei "$words")

if [ -n "$loose_matches" ]; then
  count=$(echo "$loose_matches" | wc -l)
  echo "🟡 找到 $count 个宽松匹配（需确认）:"
  echo "$loose_matches" | nl
  exit 0
fi

# 第 3 层：模糊匹配（部分关键词）
echo ""
echo "--- 第 3 层：模糊匹配 ---"
first_word=$(echo "$QUERY" | awk '{print $1}')
fuzzy_matches=$(find "$ASSET_DIR" -type f \( -name "*.png" -o -name "*.jpg" \) \
  | grep -i "$first_word" \
  | grep -Ev "$exclude_pattern")

if [ -n "$fuzzy_matches" ]; then
  count=$(echo "$fuzzy_matches" | wc -l)
  echo "🟡 找到 $count 个模糊匹配（可能不准确）:"
  echo "$fuzzy_matches" | nl
  exit 0
fi

# 未找到
echo ""
echo "❌ 未找到 \"$QUERY\""
echo ""
echo "💡 资产库中所有 $ASSET_TYPE:"
find "$ASSET_DIR" -type f \( -name "*.png" -o -name "*.jpg" \) \
  | grep -Ev "$exclude_pattern" \
  | xargs -n1 basename \
  | head -20
exit 1
