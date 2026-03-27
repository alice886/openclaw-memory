# Shot Config Builder

**职责**：整合资产+分镜+香盘表 → 构建镜头完整配置 → 输出到 `shot_configs/shot_XXX_config.json`

**触发**：用户说"构建镜头配置"、"准备生成 XXX"、shot_mapping.json 已存在

**不负责**：AI 生成执行（ai-shot-generator 负责）

---

## 输入数据

| 来源 | 内容 |
|------|------|
| shot_mapping.json（shot-mapping-parser） | 镜号/场景/人物/道具/讲戏 |
| project_index.json（asset-library-manager） | 资产路径/CDN URL/tags |
| storyboard/shot_XXX/sketch.png | 分镜图 |

---

## 执行步骤

1. 读 shot_mapping.json → 提取目标镜号的字段
2. **匹配资产**：
   - 场景：`"长江-隋军马船"` → `"灭陈水战.jpg"`
   - 人设：`"青年刀马"` → `"001刀马/BR2_青年刀马_人设设定清稿_rr2.jpg"`
   - ⚠️ 区分：青年刀马 ≠ 刀马17岁；陈国武将 ≠ 陈国士兵
3. 上传未上传资产 → 获取 CDN URL
4. 构建 Prompt + 写入 `shot_configs/shot_cXXX_config.json`

---

## 输出格式

```json
{
  "shot_id": "c003",
  "scene": "长江-隋军马船",
  "character": "青年刀马",
  "prompt": {
    "image": "【二维动画风格】长江流域夜晚水战...\n构图严格参考分镜图...\n人物严格参考青年刀马人设图...",
    "video": "二维动画风格，长江夜晚水战..."
  },
  "assets": {
    "character": { "path": "...", "cdn_url": "https://..." },
    "scene": { "path": "...", "cdn_url": "https://..." },
    "storyboard": { "path": "...", "cdn_url": "https://..." }
  },
  "generation": {
    "image_model": "316", "image_resolution": "2K",
    "video_model": "2", "video_duration": 5
  }
}
```

---

## Prompt 模板

```
【二维动画风格】
[从讲戏解析的场景描述]
构图严格参考分镜图（storyboard/sketch.png）。
人物严格参考[角色名]人设图。
场景氛围严格参考[场景图名称]。
确保：角色与人设图完全一致，场景与参考图一致，构图与分镜图一致，二维动画风格，清晰分层。
```

---

**版本**：2.0.0  
**依赖**：shot-mapping-parser, asset-library-manager, ai-shot-generator
