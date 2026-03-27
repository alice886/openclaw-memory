# Shot Mapping Parser

**职责**：解析 Excel 香盘表（.xlsx/.xls）→ 标准化 JSON（shot_mapping.json）

**触发**：用户说"解析香盘表"、"导入 Excel 香盘表"、上传 .xlsx 文件

**不负责**：资产查找（asset-library-manager）/ AI 生成（ai-shot-generator）

---

## 字段映射

| Excel列名 | JSON字段 | 类型 |
|-----------|----------|------|
| 镜号 | shot_number | string（标准化，如c001→001） |
| 场景 | scene | string |
| 天气时间 | weather_time | string |
| 人物 | characters | array（顿号/逗号分隔） |
| 道具 | props | array |
| 机位/构图/动作/时长/备注 | camera/composition/action/duration/notes | string |
| 分镜图 | sketches | array |

---

## 核心规则

### 镜号标准化
```
c001→001, C002→002, 003→003, c1→001, shot12→012
→ 移除非数字字符 → 取第一个数字 → 补前导零至3位
```

### 多值字段拆分
支持分隔符：`、` `，` `,` `;` `；`
空值（"-" "无" "空"）→ 返回 []

### assets 字段自动生成
```json
"assets": {
  "characters": ["刀马", "小七"],
  "scenes": ["洞穴外面"],
  "props": ["刀"],
  "moods": ["火光"]
}
```

### 分镜图关联
优先读 Excel"分镜图"列指定路径；未指定则自动查找 `storyboard/shot_XXX/*.png`

---

## 输出示例

**输入**：`| c001 | 洞穴外面 | 火光 | 刀马、小七 | 刀 |`
**输出 JSON**：
```json
{
  "project_name": "shot_mapping",
  "total_shots": 1,
  "shots": [{
    "shot_number": "001",
    "scene": "洞穴外面",
    "weather_time": "火光",
    "characters": ["刀马", "小七"],
    "props": ["刀"],
    "assets": {
      "characters": ["刀马", "小七"],
      "scenes": ["洞穴外面"],
      "props": ["刀"],
      "moods": ["火光"]
    },
    "sketches": []
  }]
}
```

---

## 执行流程

1. 读取 Excel → 识别表头行
2. 逐行解析：标准化镜号 → 拆分多值字段 → 映射到标准格式
3. 输出 JSON 到同目录下 `shot_mapping.json`
4. 报告：总镜头数 + 警告（格式异常/字段缺失）

---

**版本**：2.0.0  
**依赖**：pandas, openpyxl  
**输出**：shot_mapping.json  
**协作者**：ai-shot-generator, asset-library-manager
