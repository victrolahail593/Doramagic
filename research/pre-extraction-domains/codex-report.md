# Doramagic 首批预提取领域选择报告

**Date:** 2026-03-18  
**Owner:** Codex  
**Status:** Draft  
**Brief:** `/Users/tang/Documents/vibecoding/Doramagic/research/pre-extraction-domains/research-brief.md`

---

## 0. 执行摘要

这次调研的核心结论是：

> **如果目标是用 5 个“出厂领域”启动 Doramagic 的预提取飞轮，最优组合不是单纯押注 OpenClaw 上已经很热的 Productivity 类，而是优先选择“GitHub 有足够作业供给、ClawHub 现有 skill 又明显偏浅”的领域。**

我最终推荐的 **Top 5 首批预提取领域** 是：

1. **个人财务追踪**
2. **笔记 / 知识管理**
3. **食谱 / 膳食规划**
4. **文档 / OCR / Paperless 工作流**
5. **健康 / 健身追踪**

### 为什么不是直接照抄 Grok 的 6 个候选

Grok 抓住了 **OpenClaw 平台适配** 这个维度，但对另外三个维度相对低估：

- **GitHub 作业供给密度**
- **ClawHub 现有 skill 的“深度不足”**
- **5-7 个项目能否覆盖 60%+ 核心知识**

在这三个维度上，**`notes/knowledge`** 和 **`document/OCR`** 明显被低估；而 **`travel planning`** 虽然用户需求直觉强，但开源项目池分散、冷启动覆盖度差，不适合首批预提取。

### 一个反直觉发现

> **最值得认真考虑的 sleeper 领域不是旅行，也不是日历，而是 `document/OCR/paperless`。**

原因很简单：

- GitHub 上有足够成熟的大项目与配套生态
- ClawHub 的 `Documents & Presentations` 类只有 **11** 个 skill，明显偏薄
- 这个领域天然适合 OpenClaw 的 `~/clawd/` 文件 I/O、`exec`、定时归档、通知复查
- WHY / UNSAID 很丰富：OCR 可靠性、命名约定、入库规则、分类策略、人工复核阈值、去重与审计链

---

## 1. 方法论

### 1.1 数据来源

- 调研 Brief：`/Users/tang/Documents/vibecoding/Doramagic/research/pre-extraction-domains/research-brief.md`
- GitHub Search API：按领域短语查询 `repo count / stars / forks / updated_at`
- GitHub Repo API：拉取 Top 领域金项目的精确仓库指标
- `awesome-openclaw-skills` README：统计各分类 skill 数量  
  Repo: <https://github.com/sundial-org/awesome-openclaw-skills>
- ClawHub 官方文档：<https://openclawdoc.com/docs/skills/clawhub/>
- 社区补充信号：
  - r/selfhosted 上 RSS dashboard 替代需求：<https://www.reddit.com/r/selfhosted/comments/1k0hic7/>
  - r/selfhosted 上 Obsidian-like self-hosted notes 需求：<https://www.reddit.com/r/selfhosted/comments/1prcor5/selfhost_notewebapp_like_obsidian/>

### 1.2 口径说明

- 所有 GitHub 数字均为 **2026-03-18** 当天实时查询结果
- `repo count` 是 **查询短语对应的 GitHub Search API `total_count`**，是可复现的“查询口径计数”，不是全领域绝对 census
- 对少数容易被搜索词低估的领域，我改用了更贴近 GitHub 命名习惯的代理短语  
  例如：
  - `notes/knowledge` 用 `note taking self-hosted`
  - `task/calendar` 用 `kanban self-hosted` 作为结构化任务管理代理
  - `document/OCR` 用 `ocr self-hosted`，并额外查看 `paperless-ngx` 生态

### 1.3 ROI 成本模型

沿用 Brief 中已有的三方研究成本模型：

- **窄领域 / 5 个项目**：约 **350k-550k packed tokens**，**$10-18**，**1.0-1.3 小时**
- **中领域 / 6 个项目**：约 **500k-800k packed tokens**，**$18-30**，**1.2-1.7 小时**
- **宽领域 / 7 个项目**：约 **700k-1.1M packed tokens**，**$28-40**，**1.5-2.0 小时**

评分不是只看供给，而是综合：

- GitHub 作业供给
- ClawHub 白地程度
- OpenClaw 平台适配度
- WHY / UNSAID 提取价值
- 冷启动可行性

---

## 2. ClawHub 生态快照

基于 `awesome-openclaw-skills` README 统计到的分类 skill 数量：

| 类别 | skill 数 |
|---|---:|
| Developer Tools | 178 |
| Utilities | 150 |
| Web & Search | 134 |
| Productivity & Tasks | 126 |
| Agent Core & Memory | 83 |
| Finance & Trading | 29 |
| Video & YouTube | 28 |
| Audio & Speech | 25 |
| Content & Writing | 24 |
| Communication & Email | 22 |
| Image Generation | 18 |
| Security | 17 |
| Health & Wellness | 15 |
| Smart Home & Devices | 14 |
| Documents & Presentations | 11 |
| Social Media | 11 |
| Lifestyle & Fun | 10 |
| Notes & Knowledge | 10 |
| Cloud & Infrastructure | 7 |
| Research & Education | 1 |

### 2.1 关键观察

- **最拥挤的不是生活类，而是 agent/dev 工具类。** `Developer Tools`、`Utilities`、`Web & Search`、`Productivity & Tasks` 四大类合计已经 588 个 skill。
- **Finance 看起来不空，但大多是交易/行情/交易所接入。** 个人财务管理明显不足。
- **Notes & Knowledge 只有 10 个，且以 Obsidian/Notion/密码库连接器为主。** 真正的“知识工作流 intelligence”很少。
- **Health & Wellness 只有 15 个，且多是 wearable API 包装。** 缺少面向“行为改变 / 训练管理 / 数据解释”的深层 skill。
- **Documents & Presentations 只有 11 个，是明显白地。**
- **Research & Education 只有 1 个，是最薄的类目，但用户需求是否足够强还不确定。**

### 2.2 Doramagic 的机会位

对 Doramagic 来说，最好的切入口不是“技能最多的地方”，而是：

> **用户意图强，但现有 skill 主要是 API wrapper、CLI wrapper、单点提醒器，而不是跨项目抽取后的深层知识工具。**

---

## 3. 16 个候选领域量化评分表

| 领域 | GitHub 查询口径 | Repo 数 | 相关 ClawHub 类别 | 类别 skill 数 | 冷启动 5-7 项目是否可到 60%+ | 预提取成本 | 总分 / 10 | 结论 |
|---|---|---:|---|---:|---|---|---:|---|
| 个人财务追踪 | `"expense tracker" self-hosted` | 45 | Finance & Trading | 29 | 是 | 中 | **9.2** | 推荐 |
| 笔记 / 知识管理 | `note taking self-hosted` | 141 | Notes & Knowledge | 10 | 是 | 宽 | **9.1** | 推荐 |
| 食谱 / 膳食规划 | `"recipe manager" self-hosted` | 37 | Lifestyle & Fun / scattered | 10 | 是 | 中 | **8.8** | 推荐 |
| 文档 / OCR / Paperless | `ocr self-hosted` | 94 | Documents & Presentations | 11 | 是 | 中-宽 | **8.7** | 推荐 |
| 健康 / 健身追踪 | `"fitness tracker" self-hosted` | 15 | Health & Wellness | 15 | 是 | 中 | **8.2** | 推荐 |
| 提醒 / 习惯追踪 | `"habit tracker" self-hosted` | 25 | Productivity & Tasks | 126 | 勉强可以 | 中 | **8.1** | Near-miss |
| RSS / 新闻聚合 | `"rss reader" self-hosted` | 85 | Web & Search | 134 | 是 | 中 | **8.0** | Near-miss |
| 书签 / Read-later | `"bookmark manager" self-hosted` | 74 | Web & Search | 134 | 是 | 中 | **7.9** | Near-miss |
| 任务 / 看板 / 日历 | `kanban self-hosted` | 110 | Productivity & Tasks | 126 | 是 | 宽 | **7.6** | 供给强，但红海 |
| 家庭库存 / Pantry | `"home inventory" self-hosted` | 18 | Lifestyle & Fun / scattered | 10 | 勉强可以 | 窄-中 | **7.5** | 观察名单 |
| 语言学习 / Flashcards | `flashcards self-hosted` | 33 | Research & Education | 1 | 勉强可以 | 中 | **7.4** | 观察名单 |
| 智能家居 / Home Automation | `home automation self-hosted` | 136 | Smart Home & Devices | 14 | 可以 | 宽 | **7.4** | 供给强，但系统边界大 |
| 个人 CRM | `personal crm self-hosted` | 13 | Communication & Email / scattered | 22 | 勉强可以 | 窄-中 | **7.1** | 观察名单 |
| 活动 / Event Planning | `event management self-hosted` | 30 | Lifestyle & Fun / scattered | 10 | 勉强可以 | 中 | **7.0** | 观察名单 |
| 旅行规划 | `"travel planner" open source` | 14 | Lifestyle & Fun / scattered | 10 | 否 | 中 | **6.6** | 不建议首批 |
| 邮件 / Inbox 管理 | `"mail client" self-hosted` | 1 | Communication & Email | 22 | 否 | 窄 | **6.0** | 不建议首批 |

### 3.1 表格解读

- **Top 5 的共同点**：都满足“供给足够 + ClawHub 现有 skill 不深 + 5-7 个项目可以形成稳定 Alpha 图谱”
- **Travel 被我明确降级**：用户需求真实，但开源作业池太散，5-7 个项目很难覆盖核心知识
- **Task/Calendar 被我降到 near-miss / 红海**：供给强，但 ClawHub 已经很挤，Doramagic 很难在首发阶段直接打出明显差异
- **Habits 不差，但仓库池没有 Grok 结论那么厚**：更适合作为第 6 个或第 7 个领域

---

## 4. Top 5 推荐领域

## 4.1 No.1 个人财务追踪

**为什么排第一**

- GitHub 有稳定的高质量项目池
- ClawHub 的 `Finance & Trading` 类目虽然有 29 个 skill，但多数是交易、行情、钱包、交易所接入，不是个人财务系统
- WHY / UNSAID 丰富：账户建模、复式与非复式账本、分类体系、对账、预算滚动、隐私边界、家庭共享
- OpenClaw 适配好：cron 对账提醒、月报、通知、CSV/账单文件导入、exec 数据处理都天然适配

**建议首批金项目**

| Repo | Stars | Forks | Updated | Link |
|---|---:|---:|---|---|
| maybe-finance/maybe | 54,044 | 5,450 | 2026-03-18 | <https://github.com/maybe-finance/maybe> |
| actualbudget/actual | 25,532 | 2,240 | 2026-03-18 | <https://github.com/actualbudget/actual> |
| firefly-iii/firefly-iii | 22,683 | 2,090 | 2026-03-18 | <https://github.com/firefly-iii/firefly-iii> |
| ellite/Wallos | 7,559 | 343 | 2026-03-18 | <https://github.com/ellite/Wallos> |
| Tanq16/ExpenseOwl | 1,394 | 126 | 2026-03-17 | <https://github.com/Tanq16/ExpenseOwl> |

**预提取 ROI**

- 预估规模：**7 项目 / 宽领域**
- 预估成本：**$28-40，1.5-2.0 小时**
- 预期收益：高覆盖、高复用、强用户价值

**WHY / UNSAID 亮点**

- 预算系统为什么总要和真实 cashflow 分离
- 为什么自动分类永远要保留人工修正口
- 多账户同步为什么经常毁于“语义一致性”而不是技术接 API
- 家庭共享账本的权限和心理边界

**冷启动判断**

> **是。** 5-7 个项目足以覆盖账户、交易、预算、报表、导入、共享、隐私这条主链。

---

## 4.2 No.2 笔记 / 知识管理

**为什么排第二**

- GitHub 供给是所有非 dev-tool 候选里最厚的一档
- ClawHub `Notes & Knowledge` 只有 **10** 个 skill，且多数是连接器，不是知识工作流 intelligence
- WHY / UNSAID 极丰富：块结构 vs 文档结构、同步模型、本地优先、引用/反链、知识检索、写作工作流

**建议首批金项目**

| Repo | Stars | Forks | Updated | Link |
|---|---:|---:|---|---|
| AppFlowy-IO/AppFlowy | 68,636 | 4,959 | 2026-03-18 | <https://github.com/AppFlowy-IO/AppFlowy> |
| toeverything/AFFiNE | 66,169 | 4,619 | 2026-03-18 | <https://github.com/toeverything/AFFiNE> |
| usememos/memos | 57,996 | 4,209 | 2026-03-18 | <https://github.com/usememos/memos> |
| outline/outline | 37,670 | 3,146 | 2026-03-18 | <https://github.com/outline/outline> |
| TriliumNext/Trilium | 35,095 | 2,333 | 2026-03-18 | <https://github.com/TriliumNext/Trilium> |

**预提取 ROI**

- 预估规模：**7 项目 / 宽领域**
- 预估成本：**$28-40，1.5-2.0 小时**
- 预期收益：极高，且可以自然扩展到 read-later、research、writing

**WHY / UNSAID 亮点**

- 为什么“块编辑器”和“文档树”会把整个产品哲学带偏
- 本地优先、离线优先、多人协作之间的真正张力
- 搜索不是功能点，而是知识系统的底层承诺
- 为什么很多笔记工具最后卡在“知识捕获”而不是“知识回流”

**冷启动判断**

> **是。** 5-7 个项目足以覆盖 block-based、document-based、wiki、PKM、collab、local-first 这些核心路线。

---

## 4.3 No.3 食谱 / 膳食规划

**为什么排第三**

- GitHub 上有足够多的成熟开源项目，且结构相对聚焦
- ClawHub 没有一个强势、成体系的食谱 / 膳食类目，只是零散 skill
- 该领域极适合 OpenClaw：食谱整理、购物清单、库存联动、餐次计划、周期提醒
- WHY / UNSAID 很多来自“家庭真实工作流”，这正是代码外知识密度高的地方

**建议首批金项目**

| Repo | Stars | Forks | Updated | Link |
|---|---:|---:|---|---|
| mealie-recipes/mealie | 11,732 | 1,174 | 2026-03-18 | <https://github.com/mealie-recipes/mealie> |
| grocy/grocy | 8,840 | 746 | 2026-03-17 | <https://github.com/grocy/grocy> |
| TandoorRecipes/recipes | 8,094 | 783 | 2026-03-18 | <https://github.com/TandoorRecipes/recipes> |
| nextcloud/cookbook | 614 | 104 | 2026-03-18 | <https://github.com/nextcloud/cookbook> |

**预提取 ROI**

- 预估规模：**5-6 项目 / 中领域**
- 预估成本：**$16-28，1.0-1.5 小时**
- 预期收益：高，且容易给用户“立刻有用”的感知

**WHY / UNSAID 亮点**

- 食谱数据结构为什么总绕不开“单位换算”和“家庭规模”
- 膳食规划为什么天然需要和库存、购物、过期提醒联动
- 为什么“菜谱保存”不难，“真的按它做并重复执行”才难

**冷启动判断**

> **是。** 5-6 个项目足够覆盖食谱管理、购物清单、库存联动、餐次安排这条主链。

---

## 4.4 No.4 文档 / OCR / Paperless 工作流

**为什么排第四**

- `Documents & Presentations` 在 ClawHub 只有 **11** 个 skill，是明显白地
- GitHub 真实供给不差；`paperless-ngx` 单生态查询就有 **561** 个相关结果，说明扩展链很长
- 非常适合 OpenClaw 的文件工作流、定时处理、审查提醒和归档通知
- WHY / UNSAID 极强：OCR 精度阈值、归档规则、命名策略、人工复核、搜索与合规

**建议首批金项目**

| Repo | Stars | Forks | Updated | Link |
|---|---:|---:|---|---|
| Stirling-Tools/Stirling-PDF | 75,476 | 6,423 | 2026-03-18 | <https://github.com/Stirling-Tools/Stirling-PDF> |
| paperless-ngx/paperless-ngx | 37,450 | 2,390 | 2026-03-18 | <https://github.com/paperless-ngx/paperless-ngx> |
| sismics/docs | 2,535 | 624 | 2026-03-18 | <https://github.com/sismics/docs> |
| eikek/docspell | 2,193 | 170 | 2026-03-13 | <https://github.com/eikek/docspell> |
| papermerge/papermerge-core | 447 | 97 | 2026-03-17 | <https://github.com/papermerge/papermerge-core> |

**预提取 ROI**

- 预估规模：**6 项目 / 中-宽领域**
- 预估成本：**$24-38，1.4-1.9 小时**
- 预期收益：很高，属于“用户一用就知道值不值”的领域

**WHY / UNSAID 亮点**

- 为什么“自动归档”必须允许人工回看和纠错
- OCR 不准时该如何设定复核阈值和降级路径
- 入库命名、标签、来源、版本链为什么比 OCR 模型本身更影响长期可用性

**冷启动判断**

> **是。** 5-6 个项目可以覆盖 OCR、归档、搜索、PDF 处理、规则引擎、人工复核这条主链。

---

## 4.5 No.5 健康 / 健身追踪

**为什么排第五**

- GitHub 项目池不算极厚，但已足够冷启动
- ClawHub `Health & Wellness` 只有 **15** 个 skill，且多是 wearable / API wrapper，不是整合型工作流
- 该领域的 WHY / UNSAID 来自“坚持”和“解释”，不是 CRUD
- 与 Doramagic 哲学兼容：不是教练，而是锻造用户可持续使用的工具

**建议首批金项目**

| Repo | Stars | Forks | Updated | Link |
|---|---:|---:|---|---|
| wger-project/wger | 5,815 | 842 | 2026-03-18 | <https://github.com/wger-project/wger> |
| endurain-project/endurain | 1,832 | 111 | 2026-03-18 | <https://github.com/endurain-project/endurain> |
| SamR1/FitTrackee | 1,083 | 70 | 2026-03-17 | <https://github.com/SamR1/FitTrackee> |

**预提取 ROI**

- 预估规模：**5-6 项目 / 中领域**
- 预估成本：**$14-24，1.0-1.4 小时**
- 预期收益：中高，尤其适合做 habit / health 交叉扩展

**WHY / UNSAID 亮点**

- 记录不难，长期坚持难，为什么健康工具的核心其实是反馈循环
- 为什么训练日志、恢复、睡眠、体重数据很容易形成“伪精确”
- 如何把“每天看数据”变成“每周形成行动”

**冷启动判断**

> **是。** 5-6 个项目足以覆盖 workout logging、metrics、progress、recovery、habit loop 这条主链。

---

## 5. 为什么这些领域没进 Top 5

### 5.1 提醒 / 习惯追踪

它不是差，而是：

- ClawHub `Productivity & Tasks` 已经很拥挤
- GitHub 项目池比我预期更薄
- 如果只做 5 个首发领域，我更愿意把它放在第 6 位

结论：**强候补，不是首批必选。**

### 5.2 任务 / 日历管理

- GitHub 供给很强
- 但 OpenClaw 现有 skill 已经有大量 Todoist / TickTick / Linear / Calendar wrapper
- 白地不够大，首发差异化没有 `finance / notes / docs` 明显

结论：**适合第 2 批，不适合第 1 批。**

### 5.3 RSS / 书签 / Read-later

- 供给比预期强，且社区需求真实
- 但 WHY / UNSAID 密度略低，更多是产品整合和信息流编排问题

结论：**适合作为 notes/research 的邻域扩展。**

### 5.4 旅行规划

- 需求很强
- 但 OSS 项目池太散：行程、地图、预算、票务、地点推荐、地理数据都分裂
- 5-7 个项目很难覆盖 60%+ 核心知识

结论：**不建议首批预提取。**

---

## 6. Grok 分析里被低估或遗漏的方向

### 被低估 1：笔记 / 知识管理

这是我认为 Grok 最明显低估的领域。

- GitHub 项目池极厚
- ClawHub 类目极薄
- WHY / UNSAID 极多
- 能向 read-later、research、writing 形成自然飞轮

### 被低估 2：文档 / OCR / Paperless

这是本次调研最强的 sleeper。

- ClawHub 白地明显
- 用户价值直接
- OpenClaw 运行时能力天然适配
- 社区经验密度高

### 被低估 3：RSS / 书签 / 信息摄取

不是最该首发，但比旅行更适合冷启动。

原因是：

- 项目池更厚
- 工作流更聚焦
- 和 notes / research 的相邻性更强

---

## 7. 建议的首批预提取顺序

如果只做一个迭代周期，我建议按下面顺序执行：

1. **个人财务追踪**
2. **笔记 / 知识管理**
3. **食谱 / 膳食规划**
4. **文档 / OCR / Paperless**
5. **健康 / 健身追踪**

### 为什么这个顺序最优

- 前两个领域最容易验证 Doramagic 的“WHY / UNSAID 提取价值”
- 第三个领域最容易形成“用户一上手就觉得值”的体验
- 第四个领域最有机会成为反直觉爆款
- 第五个领域天然能向 habit / reminder 扩展

---

## 8. 最终结论

**如果 Doramagic 只允许带 5 个“出厂知识库”上线，我的建议不是从最热的 skill 类别里选，而是从“白地最大、供给足够、冷启动可控”的领域里选。**

最终推荐：

1. 个人财务追踪
2. 笔记 / 知识管理
3. 食谱 / 膳食规划
4. 文档 / OCR / Paperless
5. 健康 / 健身追踪

**第 6 位候补**：提醒 / 习惯追踪  
**第 7 位候补**：RSS / 新闻聚合  
**第 8 位候补**：任务 / 看板 / 日历

如果下一步要把这个结果转成工程动作，我建议立刻做两件事：

1. 为 Top 5 每个领域冻结 **5-7 个首批预提取仓库清单**
2. 先从 **个人财务** 和 **笔记 / 知识管理** 两个领域跑一次 Alpha 图谱，验证 60%+ 覆盖判断

