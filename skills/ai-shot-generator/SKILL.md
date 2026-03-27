# AI Shot Generator

**职责**：调用 ZenStudio zencli 执行镜头生图+生视频

**触发**：用户说"生成镜头 XXX"、执行生成、shot_configs/ 下已有配置

**不负责**：Prompt 构建（shot-config-builder 负责）

---

## 标准化工作流

### Step 1：解析香盘表 → 获取讲戏字段
```
镜号 c003 → 讲戏字段 → "36长江水战"
```

### Step 2：准备三类资产

| 类型 | 来源 | 规则 |
|------|------|------|
| 人设图 | `~/Desktop/资产/人设定稿/<角色>/` | 清稿/色稿/final，排除RR/线稿；三视图>全身>半身>特写 |
| 场景氛围图 | `~/Desktop/资产/氛围/氛围/` | 从香盘表"场景"字段匹配（如"长江-隋军马船"→"灭陈水战.jpg"） |
| 分镜图 | `storyboard/shot_cXXX/cXXX_1_of_N.png` | 目录名是 `shot_c310` 不是 `shot_310` |

### Step 3：构建 Prompt
```
【二维动画风格】
[从讲戏字段解析的场景描述]
构图严格参考分镜图。
人物严格参考[角色名]人设图。
场景氛围严格参考[场景图名称]。
确保：角色形象与人设图完全一致，场景与参考图一致，构图与分镜图一致，二维动画风格，清晰分层。
```

### Step 4：执行生图
```bash
zencli generate image \
  --prompt "[完整Prompt]" \
  --model "316" \
  --resolution "1" \
  --aspect-ratio "16:9" \
  --count "1" \
  --input-images "[场景CDN],[人设CDN],[分镜CDN]" \
  --poll
```
默认值：模型=316贝宝pro，分辨率=2K(--resolution "1")，比例=16:9

### Step 5：执行生视频
```bash
zencli generate video \
  --prompt "[二维动画动态描述]" \
  --model "2" \
  --mode "Text" \
  --duration "5" \
  --count "1" \
  --single-image-url "[生成图CDN]" \
  --poll
```
默认值：模型=2 Zen-01-1.5pro，时长=5s

---

## 输出目录

```
output/EP<集数>_<镜号>/
├── input/              # AI 参考图
├── output.png          # 生成图
├── video_v2/output.mp4 # zen-03 视频
└── README.md            # 生成配置记录
```

---

## ⚠️ 常见错误

1. **选错角色版本**：青年刀马 ≠ 刀马17岁；陈国武将 ≠ 陈国士兵；排除 RR/线稿/sketch
2. **Prompt 过于模糊**：必须包含具体人物+场景+动作，必须加"严格参考[资产]"
3. **分辨率用错**：必须 `--resolution "1"`（2K），不能用默认值

---

**版本**：2.0.0  
**依赖**：zencli, shot-config-builder  
**协作**：asset-library-manager, shot-mapping-parser
