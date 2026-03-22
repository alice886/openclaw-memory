# AI Shot Generator

**描述**: AI 镜头生成器，读取完整的镜头配置，调用 zencli 执行图片/视频生成任务，支持批量生成和版本管理。

**职责范围**:
- ✅ 读取 shot_config.json（来自 shot-config-builder）
- ✅ 调用 zencli 生成图片/视频
- ✅ 单镜头生成
- ✅ 批量生成（带进度、间隔、错误重试）
- ✅ 版本管理（v1, v2, ...）
- ✅ 生成历史日志（generation_log.json）
- ✅ 结果下载与保存

**不负责**:
- ❌ 资产查找（由 shot-config-builder 负责）
- ❌ Prompt 构建（由 shot-config-builder 负责）
- ❌ 配置文件生成（由其他 parser 负责）

**触发条件**: 
- 用户说"生成镜头 001"、"生成镜号 c001"
- 用户说"批量生成镜头 001-010"
- 用户说"重新生成镜头 005"

---

## 🎬 核心功能

### 1. 单镜头生成

**命令**:
```
生成镜头 001
生成镜号 c001
```

**执行流程**:

#### Step 1: 读取配置
```python
import json
from pathlib import Path

config_file = "shot_configs/shot_001_config.json"

with open(config_file) as f:
    config = json.load(f)

print(f"🎬 生成镜头 {config['shot_number']}")
print(f"   输入图片: {config['metadata']['total_input_images']} 张")
print(f"   模型: {config['generation_settings']['model']}")
```

#### Step 2: 验证文件
```python
missing = config["metadata"]["missing_files"]
if missing:
    print(f"❌ 缺失文件: {len(missing)} 个")
    for f in missing:
        print(f"   - {f}")
    sys.exit(1)

print("✅ 所有输入文件存在")
```

#### Step 3: 调用 zencli
```bash
zencli generate image \
  --prompt "在洞穴外面，火光氛围下..." \
  --model 316 \
  --aspect-ratio 16:9 \
  --input-images "sketch.png,刀马.png,小七.png,洞穴.png,火光.png" \
  --poll \
  -o json
```

```python
import subprocess

# 构建命令
input_images = ",".join(config["input_images"])

cmd = [
    "zencli", "generate", "image",
    "--prompt", config["prompt"],
    "--model", config["generation_settings"]["model"],
    "--aspect-ratio", config["generation_settings"]["aspect_ratio"],
    "--input-images", input_images,
    "--poll",
    "-o", "json"
]

print("🎨 开始生成...")
print(f"   Prompt: {config['prompt'][:80]}...")

# 执行
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ 生成失败: {result.stderr}")
    sys.exit(1)

# 解析结果
output = json.loads(result.stdout)
task_id = output["task_id"]
cdn_url = output["output_url"]

print(f"✅ 生成完成")
print(f"   Task ID: {task_id}")
print(f"   CDN URL: {cdn_url}")
```

#### Step 4: 下载结果
```python
import requests

shot_num = config["shot_number"]

# 确定版本号
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

existing_versions = list(output_dir.glob(f"shot_{shot_num}_v*.png"))
version = len(existing_versions) + 1

output_file = output_dir / f"shot_{shot_num}_v{version}.png"

# 下载
response = requests.get(cdn_url)
with open(output_file, "wb") as f:
    f.write(response.content)

print(f"📁 保存位置: {output_file}")
```

#### Step 5: 记录历史
```python
from datetime import datetime

log_file = "generation_log.json"

if Path(log_file).exists():
    with open(log_file) as f:
        log = json.load(f)
else:
    log = {"shots": {}}

if shot_num not in log["shots"]:
    log["shots"][shot_num] = {"versions": []}

log["shots"][shot_num]["versions"].append({
    "version": version,
    "timestamp": datetime.now().isoformat(),
    "output_path": str(output_file),
    "task_id": task_id,
    "cdn_url": cdn_url,
    "used_images": config["input_images"],
    "prompt": config["prompt"],
    "model": config["generation_settings"]["model"],
    "aspect_ratio": config["generation_settings"]["aspect_ratio"]
})

with open(log_file, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print(f"📝 已记录到生成日志")
```

**完整输出示例**:
```
🎬 生成镜头 001
   输入图片: 5 张
   模型: 316 (贝宝pro)

✅ 所有输入文件存在

🎨 开始生成...
   Prompt: 在洞穴外面，火光氛围下，刀马、小七手持刀...
   
   ⏳ 生成中... (预计 30s)
   
✅ 生成完成
   Task ID: d6v9gcbtivgcveuecifg
   CDN URL: https://zenvideo-pro.gtimg.com/.../xxx.png

📁 保存位置: output/shot_001_v1.png
📝 已记录到生成日志

🔗 ZenStudio 查看:
   https://ai.tvi.v.qq.com/zenstudio/...
```

---

### 2. 批量生成

**命令**:
```
批量生成镜头 001-010
生成所有镜头
批量生成前 5 个镜头
```

**执行流程**:

```python
def batch_generate(shot_range, interval=5):
    """批量生成镜头
    
    Args:
        shot_range: 镜号范围，如 "001-010" 或 ["001", "002", ...]
        interval: 每个镜头间隔秒数（避免 API 限流）
    """
    import time
    
    # 解析范围
    if isinstance(shot_range, str):
        if shot_range == "all":
            configs = list(Path("shot_configs").glob("shot_*_config.json"))
        elif "-" in shot_range:
            start, end = shot_range.split("-")
            start_num = int(start)
            end_num = int(end)
            configs = [
                Path(f"shot_configs/shot_{i:03d}_config.json")
                for i in range(start_num, end_num + 1)
            ]
        else:
            configs = [Path(f"shot_configs/shot_{shot_range}_config.json")]
    else:
        configs = [Path(f"shot_configs/shot_{s}_config.json") for s in shot_range]
    
    total = len(configs)
    success = 0
    failed = []
    skipped = []
    
    print(f"🚀 开始批量生成: {total} 个镜头\n")
    
    for idx, config_file in enumerate(configs, start=1):
        if not config_file.exists():
            shot_num = config_file.stem.replace("shot_", "").replace("_config", "")
            print(f"[{idx}/{total}] 镜号: {shot_num}")
            print(f"   ⏭️  跳过（配置不存在）\n")
            skipped.append(shot_num)
            continue
        
        with open(config_file) as f:
            config = json.load(f)
        
        shot_num = config["shot_number"]
        print(f"[{idx}/{total}] 镜号: {shot_num}")
        
        # 检查缺失文件
        if config["metadata"]["missing_files"]:
            print(f"   ⏭️  跳过（缺失 {len(config['metadata']['missing_files'])} 个文件）\n")
            skipped.append(shot_num)
            continue
        
        # 生成
        try:
            generate_shot(config)
            success += 1
            print(f"   ✅ 完成\n")
        except Exception as e:
            print(f"   ❌ 失败: {e}\n")
            failed.append(shot_num)
        
        # 间隔
        if idx < total:
            print(f"   ⏸️  等待 {interval}s...\n")
            time.sleep(interval)
    
    # 报告
    print("="*60)
    print("📊 批量生成完成")
    print(f"   ✅ 成功: {success} 个")
    print(f"   ⏭️  跳过: {len(skipped)} 个")
    print(f"   ❌ 失败: {len(failed)} 个")
    
    if skipped:
        print(f"\n跳过镜号: {', '.join(skipped)}")
    
    if failed:
        print(f"\n失败镜号: {', '.join(failed)}")
        print(f"💡 建议: 检查日志后重新生成失败的镜头")
    
    print(f"\n📁 生成文件: output/")
    print("="*60)
```

**进度报告示例**:
```
🚀 开始批量生成: 10 个镜头

[1/10] 镜号: 001
   🎨 生成中... ⏳
   ✅ 完成
   ⏸️  等待 5s...

[2/10] 镜号: 002
   🎨 生成中... ⏳
   ✅ 完成
   ⏸️  等待 5s...

[3/10] 镜号: 003
   ⏭️  跳过（缺失 1 个文件）

[4/10] 镜号: 004
   🎨 生成中... ⏳
   ❌ 失败: API 限流，请稍后重试

[5/10] 镜号: 005
   🎨 生成中... ⏳
   ✅ 完成
   ⏸️  等待 5s...

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 批量生成完成
   ✅ 成功: 7 个
   ⏭️  跳过: 2 个（缺少资产）
   ❌ 失败: 1 个（API 错误）

跳过镜号: 003, 008
失败镜号: 004

💡 建议: 检查日志后重新生成失败的镜头

📁 生成文件: output/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3. 重新生成（版本管理）

**命令**:
```
重新生成镜头 001
生成镜头 001 的新版本
```

**版本递增逻辑**:
```python
# 检查已有版本
existing = list(Path("output").glob(f"shot_{shot_num}_v*.png"))

# 版本号 = 已有版本数 + 1
version = len(existing) + 1

# 新文件名
output_file = f"output/shot_{shot_num}_v{version}.png"
```

**示例**:
```
output/
├── shot_001_v1.png  (第 1 次生成)
├── shot_001_v2.png  (重新生成)
├── shot_001_v3.png  (再次重新生成)
```

---

### 4. 错误重试

**自动重试策略**:
```python
def generate_with_retry(config, max_retries=3, retry_interval=10):
    """带重试的生成"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"   尝试 {attempt}/{max_retries}...")
            result = generate_shot(config)
            return result
        
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            
            if attempt < max_retries:
                print(f"   ⏳ {retry_interval}s 后重试...")
                time.sleep(retry_interval)
            else:
                print(f"   ❌ 达到最大重试次数")
                raise
```

---

### 5. 视频生成支持

**命令**:
```
生成镜头 001 视频
```

**调用 zencli（视频模式）**:
```bash
zencli generate video \
  --mode Text \
  --prompt "..." \
  --model <video_model_id> \
  --single-image-url "first_frame.png" \
  --duration 5 \
  --enable-sound \
  --poll
```

**配置标记**:
```json
{
  "shot_number": "001",
  "output_type": "video",  // ← 标记为视频
  "generation_settings": {
    "model": "video_model_id",
    "duration": 5,
    "enable_sound": true
  }
}
```

---

## 📚 辅助脚本

### scripts/generate_shot.sh

```bash
#!/bin/bash
# 生成单个镜头
# 用法: ./generate_shot.sh <shot_number> [project_path]

SHOT_NUM="$1"
PROJECT_PATH="${2:-.}"

CONFIG_FILE="$PROJECT_PATH/shot_configs/shot_${SHOT_NUM}_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 配置不存在: $CONFIG_FILE"
  exit 1
fi

echo "🎬 生成镜头 $SHOT_NUM"

# 读取配置
PROMPT=$(jq -r '.prompt' "$CONFIG_FILE")
MODEL=$(jq -r '.generation_settings.model' "$CONFIG_FILE")
ASPECT_RATIO=$(jq -r '.generation_settings.aspect_ratio' "$CONFIG_FILE")

# 构建输入图片列表
INPUT_IMAGES=$(jq -r '.input_images | join(",")' "$CONFIG_FILE")

echo "   模型: $MODEL"
echo "   输入图片: $(echo "$INPUT_IMAGES" | tr ',' '\n' | wc -l) 张"
echo ""

# 调用 zencli
zencli generate image \
  --prompt "$PROMPT" \
  --model "$MODEL" \
  --aspect-ratio "$ASPECT_RATIO" \
  --input-images "$INPUT_IMAGES" \
  --poll \
  -o json

if [ $? -eq 0 ]; then
  echo "✅ 生成完成"
else
  echo "❌ 生成失败"
  exit 1
fi
```

---

## 📊 生成历史日志 (generation_log.json)

```json
{
  "project_name": "奇幻冒险短剧",
  "last_updated": "2026-03-22T00:10:00+08:00",
  "total_shots": 25,
  "generated_shots": 15,
  "shots": {
    "001": {
      "status": "completed",
      "latest_version": 2,
      "versions": [
        {
          "version": 1,
          "timestamp": "2026-03-21T23:00:00+08:00",
          "output_path": "output/shot_001_v1.png",
          "task_id": "d6v9gcbtivgcveuecifg",
          "cdn_url": "https://zenvideo-pro.gtimg.com/.../xxx.png",
          "used_images": [
            "storyboard/shot_001/sketch.png",
            "assets/characters/刀马.png",
            "assets/characters/小七.png",
            "assets/scenes/洞穴外面.png",
            "assets/moods/火光.png"
          ],
          "prompt": "在洞穴外面，火光氛围下...",
          "model": "316",
          "aspect_ratio": "16:9"
        },
        {
          "version": 2,
          "timestamp": "2026-03-22T00:05:00+08:00",
          "output_path": "output/shot_001_v2.png",
          "task_id": "d6v9hhhhtivgcveueddd1",
          "cdn_url": "https://zenvideo-pro.gtimg.com/.../yyy.png",
          "used_images": [...],
          "prompt": "...",
          "model": "316",
          "aspect_ratio": "16:9"
        }
      ]
    },
    "002": {
      "status": "completed",
      "latest_version": 1,
      "versions": [...]
    },
    "003": {
      "status": "failed",
      "error": "缺少资产: 魔法书",
      "attempts": 1
    }
  }
}
```

---

## 🎓 最佳实践

### 1. API 限流处理
```python
# 批量生成时设置间隔
batch_generate("001-025", interval=5)  # 每个镜头间隔 5 秒

# 遇到 429 错误时指数退避
retry_intervals = [10, 30, 60, 120]  # 10s, 30s, 1min, 2min
```

### 2. 质量检查
```python
# 生成后人工确认
generate_shot("001")
print("请检查 output/shot_001_v1.png")
confirm = input("满意吗？(y/n): ")

if confirm.lower() != 'y':
    print("重新生成...")
    generate_shot("001")  # 生成 v2
```

### 3. 成本控制
```python
# 先生成测试镜头
test_shots = ["001", "005", "010"]
for shot in test_shots:
    generate_shot(shot)

# 检查效果后再批量生成
input("测试镜头生成完毕，按回车继续批量生成...")
batch_generate("001-025")
```

---

## 🚀 快速开始

### 1. 确保配置存在
```bash
ls shot_configs/shot_001_config.json
```

### 2. 生成单个镜头
```
对 Agent 说：生成镜头 001
```

### 3. 批量生成
```
对 Agent 说：批量生成镜头 001-010
```

### 4. 查看结果
```bash
ls output/
# shot_001_v1.png
# shot_002_v1.png
# ...
```

---

## 🔗 协作 Skills

- **输入**: shot_configs/shot_XXX_config.json (from shot-config-builder)
- **输出**: 
  - output/shot_XXX_v1.png (生成的图片)
  - generation_log.json (生成历史)
- **依赖**: zencli

---

**版本**: 1.0.0  
**依赖**: zencli, Python 3, requests  
**输出**: output/ 目录 + generation_log.json
