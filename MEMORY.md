# MEMORY.md - 长期记忆

## 关于 Alice

- **名字：** Alice
- **QQ：** 1903354726
- **职业：** 互联网产品，关注最新前沿大模型
- **时区：** Asia/Shanghai (GMT+8)
- **Mac mini 用户**，OpenClaw 部署在本地

## 关于我（小马儿）

- **名字：** 小马儿
- **职责：** 帮 Alice 处理日常工作
- **人设原则：**
  1. 绝不骑墙，有自己强烈的观点，不说"看情况"含糊其辞
  2. 删掉一切像死板"职场规定"的话
  3. 拒绝废话开场，直接给答案；一句话能说明白就只给一句话
  4. 毒舌且迷人：如果 Alice 要做蠢事，直接指出来，不粉饰太平

## 重要记录

- **2026-03-22：** OpenClaw 更新模型版本后 workspace 被重置，之前的记忆全部丢失，重新认识
- 桌面 `~/Desktop/资产/` 里的 skill 包未受影响
- OpenClaw CLI 及内置 skills 均完好

## 项目信息：镖人2

- **项目路径：** ~/Desktop/镖人2项目/
- **资产路径：** ~/Desktop/资产/
- **有效资产数：** 122 个（已建立索引）
- **内容：** 历史武侠动画，隋朝背景

## 资产结构

```
资产/
├── 人设定稿/          # 角色人设（刀马、杨广、陈国武将等 89 个角色）
│   ├── 001刀马/       # 含 PNG/JPEG/PSD 多格式，含道具、表情、战马等
│   ├── 002竖/
│   ├── 003知世郎/
│   └── ...（共89个角色目录）
├── 氛围/              # 场景氛围图（18张）
│   └── 灭陈水战.jpg、竹林死斗修改.jpg 等
├── 道具/              # 道具图
│   └── 十三骁骑尉/    # 十三骁骑卫武器专属
├── 香盘表/            # Excel 香盘表（镜号+人物+场景配置）
│   ├── 20250904镖人2-01集香盘表.xlsx
│   └── 20250928镖人04集香盘表.xlsx
└── 01分镜/            # PDF 分镜稿

镖人2项目/
├── assets/            # 已整理的资产副本（供 AI 生成用）
│   ├── characters/    # 刀马_01集_色稿.jpg、陈国武将_色稿.png 等
│   ├── scenes/        # 灭陈水战.jpg 等
│   ├── moods/
│   └── props/
├── storyboard/        # 分镜图（shot_040/sketch.png 等）
├── output/            # 生成结果
└── shot_configs/      # 镜头配置（待生成）
```

## 5个 Skills

| Skill | 职责 | 输入 | 输出 |
|-------|------|------|------|
| asset-library-manager | 扫描资产、过滤PSD/线稿、建立索引 | 资产目录 | project_index.json |
| pdf-storyboard-parser | 解析 PDF 分镜，提取镜号+图+描述 | 分镜稿.pdf | storyboard/shot_XXX/ |
| shot-mapping-parser | 解析 Excel 香盘表 | shot_mapping.xlsx | shot_mapping.json |
| shot-config-builder | 关联资产+分镜+配置，构建生成 Prompt | shot_mapping.json + project_index | shot_configs/shot_XXX_config.json |
| ai-shot-generator | 调用 zencli 执行生成，版本管理 | shot_config.json | output/shot_XXX_vN.png |

## 完整工作流

```
准备资产 → 解析资产库 → 解析 PDF 分镜 → 解析香盘表 → 构建配置 → 生成镜头
```

## ZenStudio 工具

- **CLI：** `/usr/local/bin/zencli`（v1.2.2）
- **模型：** 贝宝pro（316）最常用，支持 8 张输入图片
- **命令：** `zencli generate image --prompt ... --model 316 --input-images url1,url2,... --poll`
- **上传：** `zencli upload <file>`

## 镖人2项目完整资产结构

### 筛选脚本（已建立）
- `~/Desktop/镖人2工作流/镖人2_筛选核心资产.command` — 智能精选核心资产（977→117张）
- `~/Desktop/镖人2工作流/镖人2_资产批量打标签.command` — 全量扫描脚本
- `~/Desktop/小马儿记忆备份.command` — 双击自动 commit 记忆

### 资产路径
- 人设定稿：`~/Desktop/资产/人设定稿/`（89个角色目录）
- 场景氛围：`~/Desktop/资产/氛围/氛围/`（18张）
- 道具：`~/Desktop/资产/道具/`
- 香盘表：`~/Desktop/资产/香盘表/`

### 关键区分（重要！）
- 青年刀马：`001刀马/BR2_青年刀马_人设设定清稿_rr2.jpg`
- 刀马17岁 ≠ 青年刀马
- 陈国武将 ≠ 陈国士兵
- 线稿标记：RR/sketch/线稿/draft/草图/轮廓 → ❌排除
- 定稿标记：清稿/色稿/上色/final/v2/v3/三视图 → ✅

### AI 生成（ZenStudio）
- 工具：zencli（v1.2.2）
- 模型：贝宝pro (316)
- 上传：`zencli upload <file>`
- 生成：`zencli generate image --prompt ... --model 316 --input-images url1,url2 --poll`

### 批量分析状态
- 2026-03-22：建立资产语义标签流程
- 117个核心资产批量分析中（子agent运行中）
- 输出：`~/.openclaw/workspace/temp_assets/project_index.json`

## 待补充

- Alice 常用的具体项目或场景
- 其他偏好和习惯
