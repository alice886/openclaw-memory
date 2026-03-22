#!/bin/bash
# 扫描资产目录并应用过滤规则
# 用法: ./scan_assets.sh <项目路径>

PROJECT_PATH="$1"
ASSET_DIR="$PROJECT_PATH/assets"

if [ ! -d "$ASSET_DIR" ]; then
  echo "❌ 资产目录不存在: $ASSET_DIR"
  exit 1
fi

# 过滤规则
EXCLUDE_EXT='\.psd$|\.psb$|\.ai$|\.sketch$|\.blend$'
EXCLUDE_KW='线稿|lineart|sketch|draft|outline|草图|未上色|uncolored'

echo "🔍 扫描资产库: $ASSET_DIR"
echo ""

total_scanned=0
total_valid=0
total_filtered=0

# 扫描各类资产
for category in characters scenes props moods; do
  if [ ! -d "$ASSET_DIR/$category" ]; then
    echo "⚠️  跳过不存在的目录: $category"
    continue
  fi
  
  echo "📁 扫描 $category..."
  
  # 统计所有文件
  all_files=$(find "$ASSET_DIR/$category" -type f | wc -l)
  total_scanned=$((total_scanned + all_files))
  
  # 应用过滤规则
  valid_files=$(find "$ASSET_DIR/$category" -type f \
    \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
    | grep -Ev "$EXCLUDE_EXT" \
    | grep -Ev "$EXCLUDE_KW")
  
  valid_count=$(echo "$valid_files" | grep -c .)
  filtered_count=$((all_files - valid_count))
  
  total_valid=$((total_valid + valid_count))
  total_filtered=$((total_filtered + filtered_count))
  
  echo "   ✅ 有效: $valid_count 个"
  echo "   ❌ 过滤: $filtered_count 个"
  echo ""
  
  # 列出有效文件（前 5 个）
  if [ $valid_count -gt 0 ]; then
    echo "   示例文件:"
    echo "$valid_files" | head -5 | while read -r file; do
      basename "$file"
    done | sed 's/^/      - /'
    echo ""
  fi
done

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 扫描完成"
echo "   共扫描: $total_scanned 个文件"
echo "   ✅ 有效资产: $total_valid 个"
echo "   ❌ 已过滤: $total_filtered 个"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
