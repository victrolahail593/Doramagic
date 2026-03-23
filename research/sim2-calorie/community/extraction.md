# 社区知识采集报告

采集日期：2026-03-17
来源：GitHub openclaw/skills 仓库 + 任务预置的 LobsterLair 架构信息

---

## Skill 1: calorie-counter

**来源**
- 作者：cnqso
- ClawHub 链接：https://clawhub.com（slug: calorie-counter）
- GitHub：https://github.com/openclaw/skills/tree/main/skills/cnqso/calorie-counter
- 版本：1.0.0（单版本，无历史）

**核心功能**
1. 手动录入食物条目（名称 + 卡路里 + 蛋白质），支持立即反馈剩余配额
2. 设置每日卡路里目标、查询 7/30 天历史趋势
3. 体重追踪（磅，支持小数精度）

**存储模式**
- 类型：本地 SQLite 数据库
- 路径：`workspace/calorie-counter/calorie_data.db`
- 表结构：
  - `entries`：食物日志（id, 名称, 卡路里, 蛋白质, 日期, 时间戳）
  - `daily_goal`：每日目标卡路里
  - `weight_log`：体重记录（磅）
- 日期格式：YYYY-MM-DD，使用本地时区

**触发方式**
- 用户直接调用 Python 脚本子命令：
  - `python3 workspace/calorie-counter/scripts/calorie_tracker.py add`
  - `python3 ... summary`、`goal`、`weight`、`history`、`delete`
- 无自然语言触发器描述（命令行风格）

**可复用知识**
- 蛋白质估算规则（当用户未指定时）：瘦肉（鸡/火鸡）≈ 0.30g/kcal；鱼类、豆类、谷物各有不同系数 — 可直接复用为我们 skill 的默认估算逻辑
- SQLite 无需外部依赖（Python 标准库）— 低摩擦存储方案
- 局限：无宏量营养素（碳水、脂肪），只追踪卡路里+蛋白质 — 这是明显缺口

---

## Skill 2: opencal

**来源**
- 作者：neikfu
- ClawHub 链接：https://clawhub.com（slug: opencal）
- GitHub：https://github.com/openclaw/skills/tree/main/skills/neikfu/opencal
- 版本：1.0.0（单版本，无历史）

**核心功能**
1. 通过 OpenCal API 搜索食物数据库并按实际份量缩放后记录
2. 查询每日卡路里/蛋白质/碳水/脂肪进度（对比目标）
3. 支持修改每日目标、删除错误条目、补录历史条目

**存储模式**
- 类型：外部 SaaS API（非本地存储）
- 环境变量：`OPENCAL_API_KEY`（从 OpenCal App Profile 生成）
- API Base：`https://api.opencal.ai`
- 关键端点：
  - 搜索：`GET /api/v1/food/search?q=...&limit=5`
  - 记录：`POST /api/v1/food/log`（字段：name, amount, unit, calories, protein, carbs, fat, mealType）
  - 进度：`GET /api/v1/food/log?date=YYYY-MM-DD`
  - 目标：`GET/PUT /api/v1/goals`
- 速率限制：100 req/min

**触发方式**
- 自然语言触发（用户说出食物时自动流程）：
  1. 搜索食物数据库
  2. 将 per-100g 结果按实际份量缩放：`营养值 × (实际克数 / 100)`
  3. POST 记录，确认给用户
- 支持补录历史：在 payload 中加 `loggedAt: ISO-8601`

**可复用知识**
- **缩放公式**是核心细节：搜索结果全部基于 100g，必须 × (amount/100) 再写入 — 如果我们调用任何标准食物数据库 API（如 USDA、FatSecret）都适用同样规则
- mealType 分类：breakfast / lunch / dinner / snack — 标准四分类可直接采用
- 需要 API Key 注册意味着有外部依赖，对纯本地 skill 不适用
- 局限：依赖第三方付费服务，用户需要额外注册账号

---

## Skill 3: diet-tracker

**来源**
- 作者：yonghaozhao722
- ClawHub 链接：https://clawhub.com（slug: diet-tracker）
- GitHub：https://github.com/openclaw/skills/tree/main/skills/yonghaozhao722/diet-tracker
- 版本：1.2.0（最活跃，共 4 个版本：1.0.0 → 1.1.0 → 1.1.1 → 1.2.0）

**核心功能**
1. 自然语言食物描述触发自动营养查询（通过 `scripts/get_food_nutrition.py`）
2. 全宏量营养素追踪：卡路里 + 蛋白质 + 碳水 + 脂肪（严格禁止只记卡路里不记宏量）
3. cron 定时提醒：12:30 午餐、18:00 晚餐（若当餐未记录则推送）

**存储模式**
- 类型：Markdown 日记文件（本地）
- 路径：`memory/YYYY-MM-DD.md`
- 格式：
  ```
  Food Name - XX kcal (P: XXg, C: XXg, F: XXg)

  Daily Total: [已消耗] / [目标] kcal
  - Protein: [X] / [target]g
  - Carbs: [X] / [target]g
  - Fat: [X] / [target]g
  ```
- 用户档案：`USER.md`（每日目标卡路里默认 1650 kcal，含身高/体重/年龄/性别/活动水平用于 TDEE 计算）
- 食物数据库：`references/food_database.json`（兜底查询）

**触发方式**
- 自然语言：「我午饭吃了披萨」/ 「我的剩余卡路里配额是多少」
- 定时 cron：12:30 / 18:00 主动检查并提醒
- 用户档案驱动：USER.md 中的目标影响所有计算

**可复用知识**
- **USER.md 用户档案模式**是最可复用的架构决策：将个人参数（TDEE、目标、体测数据）从 skill 代码中分离到配置文件，skill 只读取 — 我们的 sim2 应采用同样模式
- **Markdown 日记文件格式**（memory/YYYY-MM-DD.md）：可读性好，且与 OpenClaw 的文件系统存储惯例完全一致
- cron 提醒机制：主动推送比等用户询问更有效 — 可考虑作为可选功能
- 体重变化预测输出：结合 TDEE 和卡路里赤字/盈余计算预期体重变化 — 有 WHY 层价值
- 局限：无视觉识别（纯文字描述），无图表/趋势可视化

---

## Skill 4: health-summary

**来源**
- 作者：yusaku-0426
- ClawHub 链接：https://clawhub.com（slug: health-summary）
- GitHub：https://github.com/openclaw/skills/tree/main/skills/yusaku-0426/health-summary
- 版本：1.0.0（单版本，日文界面）

**核心功能**
1. 生成日/周/月三种粒度的健康摘要（JSON 输出 + 格式化文本）
2. 全面宏微量营养素追踪：卡路里、P/C/F、膳食纤维、糖、钠、饱和脂肪、水分、运动时长
3. 对比个人目标（`config/health_targets.json`）并计算 delta 差值

**存储模式**
- 配置：`config/health_targets.json`（目标值，lean_mass_gain 默认：2200 kcal / P 165g / C 275g / F 55g）
- 输出：JSON 结构体（totals / targets / deltas / latest_weight / latest_sleep）
- 原始数据来源：SKILL.md 未明确说明（可能依赖外部追踪系统或数据库输入）
- 运行时：Node.js（`scripts/health_summary.js`）

**触发方式**
- 命令行调用：
  - `node scripts/health_summary.js today [--date=YYYY-MM-DD]`
  - `node scripts/health_summary.js week`
  - `node scripts/health_summary.js month`
- 用户层面：询问「今天怎么样」/ 「本周总结」即可触发

**可复用知识**
- **delta 差值计算**模式：不只报告「吃了多少」，而是「离目标还差多少」— 这是更有用的信息帧，我们应该标配
- 微量营养素追踪字段设计（纤维/糖/钠/饱和脂肪）：大多数社区 skill 只追踪宏量，这是差异化
- `lean_mass_gain` 命名的目标模式：暗示可支持多种目标模式（减脂/增肌/维持）— 配置驱动而非硬编码
- 时间聚合三级：today / week / month — 标准时间粒度设计
- 局限：数据来源不透明（SKILL.md 未说明 health_summary.js 从哪读数据），与其他 skill 的互操作性不清晰

---

## LobsterLair AI Health Coach 架构

**来源**：任务预置信息（URL 访问受限，以下为已知架构知识）

**5 个组件及分工**

| 组件 | 职责 |
|------|------|
| 食物识别（视觉模型） | 照片 → 食物名称 + 份量估算 |
| Apple Health 集成 | 步数、消耗热量、睡眠等被动数据输入 |
| 膳食计划 | 目标设定、每日/每周计划生成 |
| 人格层 | 驱动 AI 的语气和风格（SOUL.md 配置） |
| 仪表板 | 汇总展示，今日/历史可视化 |

**数据流**
```
用户拍照 → 视觉模型识别食物 → 宏量营养素计算 → 写入日志文件
Apple Health → 被动数据同步 → 合并进日志
SOUL.md → 配置 AI 人格 → 影响所有输出语气
```

**日志格式**
- 路径：`health/meals/YYYY-MM-DD.md`
- 注：与 diet-tracker 的 `memory/YYYY-MM-DD.md` 模式相同，日期命名是社区共识

**准确率**
- 视觉识别食物：80-90%（份量估算是主要误差来源）

**可复用知识**
- **SOUL.md 人格配置**：与 OpenClaw 的 SOUL.md 惯例完全一致，人格可热替换 — 这是 Doramagic 的标配架构
- 视觉识别 80-90% 准确率：意味着必须有用户确认步骤，不能自动写入 — 这是设计约束
- Apple Health 被动数据源：用户无需主动输入消耗数据，减少摩擦 — 高价值数据接入
- 仪表板作为独立组件：可视化是展示层，与数据层解耦

---

## 社区共识（公约数）

跨 4 个 skill + LobsterLair 的共同模式：

### 1. 日期命名文件存储
- diet-tracker：`memory/YYYY-MM-DD.md`
- health-summary：按日/周/月查询
- LobsterLair：`health/meals/YYYY-MM-DD.md`
- **结论**：YYYY-MM-DD 日期命名是 OpenClaw 社区存储惯例，我们必须遵从

### 2. 四大宏量营养素标配
- 全部 skill 都追踪卡路里 + 蛋白质
- diet-tracker 和 health-summary 强制追踪 P/C/F 三元组
- calorie-counter 仅追踪卡路里+蛋白质（最简化）
- **结论**：最低标准是卡路里+蛋白质；完整标准是 P/C/F 三元组

### 3. 用户档案配置文件分离
- diet-tracker：`USER.md`
- health-summary：`config/health_targets.json`
- **结论**：个人参数（目标、TDEE、偏好）从 skill 代码分离到配置文件是标准做法

### 4. 进度 = 实际值 + 目标值 + 剩余量
- 所有 skill 都报告「已消耗 / 目标 / 剩余」三元组
- health-summary 额外计算 delta
- **结论**：三元组是最低输出标准，delta 是增值

### 5. 宏量营养素估算（LLM 承担）
- calorie-counter：内置蛋白质估算规则
- diet-tracker：`get_food_nutrition.py` + `food_database.json` 兜底
- opencal：依赖 API 数据库
- **结论**：食物营养数据获取是所有 skill 的共同痛点，各有不同解法

---

## 社区空白（差异化机会）

社区 4 个 skill 共同缺失的能力：

### 1. WHY 层解读（最大空白）
- 社区全部停留在「记录 + 报告」层：吃了什么、离目标差多少
- 无一个 skill 解释「为什么这样」：这顿饭的营养搭配合理吗？连续三天蛋白质不足说明什么？
- **机会**：Doramagic 的核心差异化 — 从数据事实到饮食洞察

### 2. 视觉输入（仅 LobsterLair 有）
- 4 个社区 skill 全部依赖文字描述食物
- 拍照识别是最低摩擦的录入方式
- **机会**：视觉模型集成（但需要确认步骤，80-90% 准确率不足以自动写入）

### 3. 跨日趋势分析
- calorie-counter 有 7/30 天历史查询，但无趋势解读
- health-summary 有周/月聚合，但无异常检测
- **机会**：「你本周蛋白质摄入持续低于目标，可能影响恢复」类洞察

### 4. 饮食质量评分（非卡路里计数）
- 所有 skill 以「卡路里达标」为成功标准
- 无一涉及食物多样性、加工程度、营养密度
- **机会**：「同样 2000 kcal，今天的食物质量比昨天高 X 分」

### 5. 主动建议（非被动查询）
- diet-tracker 的 cron 提醒是最接近主动的设计，但只是提醒「去记录」
- 无 skill 会说「午餐建议补充蛋白质，因为早餐只有 10g」
- **机会**：基于当天已录数据的实时饮食建议

### 6. 与运动数据的联动
- 仅 LobsterLair 提到 Apple Health（运动消耗）
- 4 个社区 skill 都不考虑运动消耗对净卡路里的影响
- **机会**：「今天跑步消耗 400 kcal，实际可用配额 = 目标 + 400」

---

*采集完成。4 个 skill 的 SKILL.md 内容均从 GitHub raw 地址直接读取，数据可信。LobsterLair 架构为任务预置信息（URL 访问受限）。*
