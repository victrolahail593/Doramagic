# Doramagic v2 重构方案 — "超级 Copy Cat"

> 日期: 2026-03-11
> 状态: 草案，待创始人审查
> 背景: 基于 PRODUCT_MANUAL v1.0 + 全部 60+ 份技术文档 + 3 轮第一性原理讨论

---

## 0. 一句话定义

**Doramagic 是 OpenClaw 生态的"超级抄作业引擎"——它理解用户的模糊需求，从开源项目和优秀 Skill 中发现知识、资源和模式，像拼乐高一样自动组装出开袋即食的个性化 AI 技能。**

对比 v1.0 的定义："开源项目灵魂提取系统"——这是一个引擎层描述，不是产品描述。

---

## 1. 为什么要重构

### v1.0 的根本问题

| 维度 | v1.0 现状 | 问题 |
|------|---------|------|
| **用户定义** | CTO/开发者/产品经理（三类散点用户） | 无统一获客渠道，无共同 Job-to-be-Done |
| **入口** | GitHub URL | 用户必须先知道要分析哪个项目 |
| **输出** | CLAUDE.md / .cursorrules / advisor-brief.md | 知识文档，不是可运行的能力 |
| **核心能力** | 知识提取（设计哲学、决策规则、社区经验） | 缺失"资源提取"——API、数据源、工具链 |
| **用户旅程** | 提供 URL → 等 40 分钟 → 得到文档 → 手动注入 AI | 从"得到文档"到"解决问题"还有巨大鸿沟 |

### 核心洞察

v1.0 提取了项目的"大脑"（知识），但完全忽略了"肌肉"（资源）。

一个股民不需要知道 akshare 的设计哲学。他需要的是：akshare 的 A 股行情 API 被正确调用、vnpy 的选股逻辑被正确复制、社区踩过的坑被提前规避——最终拼装成一个他说"帮我选股"就能跑的 Skill。

**知识让 AI 知道怎么想，资源让 AI 有能力行动，模式让 AI 知道怎么拼。三者缺一不可。**

---

## 2. 新架构：五阶段流水线

```
用户的一句话需求
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Phase 1: 需求理解 (Need Understanding)          │
│  苏格拉底对话 → 需求画像 + 搜索策略               │
│  用户交互：3-5 轮对话                             │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Phase 2: 源泉发现 (Source Discovery)            │
│  多维搜索：开源项目 + Skill 市场 + API 目录       │
│  输出：源泉地图 + 提取计划                        │
│  用户交互：展示发现，确认方向（1 轮）              │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Phase 3: 多源提取 (Multi-Source Extraction)      │
│  并行子代理提取：知识 + 资源 + 模式               │
│  ★ 新增：资源卡片 (Resource Card)                 │
│  用户交互：无（后台并行，实时展示进度）            │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Phase 4: 智能拼装 (Intelligent Assembly)         │
│  AI 架构师：选积木 → 设计蓝图 → 生成 Skill        │
│  输出：SKILL.md + stages/ + 默认配置              │
│  用户交互：无（后台执行，实时展示进度）            │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Phase 5: 交付与增强 (Delivery & Enhancement)     │
│  安装 → 冒烟测试 → 呈现能力 → 提示可选升级        │
│  用户交互：确认安装，了解能力边界                  │
└─────────────────────────────────────────────────┘
```

### 与 v1.0 的关系

| v1.0 组件 | v2 中的角色 |
|-----------|----------|
| Soul Extractor (8+2 stage) | Phase 3 的知识提取子引擎（保留核心，增加资源提取） |
| Skill Forge (5 stage) | 整体架构的骨架（Phase 1/2 直接复用，Phase 3-5 重构） |
| 知识卡片体系 (CC/WC/DR/CT/AC) | 保留，新增 Resource Card (RC) |
| 质量评判系统 (5 维评分) | 保留，增加"可用性"维度 |
| validate_extraction.py | 保留，扩展校验资源卡片 |
| repo_facts.json | 扩展为 repo_resources.json（含 API/数据源/工具链） |

---

## 3. 各阶段详细设计

### Phase 1: 需求理解 (Need Understanding)

**继承自**: Skill Forge STAGE-1-discovery.md
**强化点**: 增加环境感知（用户的 OpenClaw 配置、可用模型、已安装 Skill）

**AI 角色**: 产品顾问

**对话结构** (3-5 轮，每轮 1-2 个问题)：

| 轮次 | 目的 | 示例问题 |
|------|------|---------|
| R1 | 问题本质 | "你想让 AI 帮你做什么？最痛的一件事是什么？" |
| R2 | 场景与频率 | "这件事你多久做一次？花多长时间？现在怎么做的？" |
| R3 | 成功标准 | "做到什么程度你会觉得'这真好用'？" |
| R4 | 偏好与约束 | "你更想要简单快速的还是功能全面的？有没有什么数据源/工具你已经在用的？" |
| R5 | 确认 | "我理解你需要 X，核心是 Y，对吗？" |

**产出**: 需求画像文档

```yaml
# need-profile.yaml
core_problem: "A股选股+跟踪+研究，目前手动耗时且不系统"
user_persona: "个人投资者，非技术背景，价值投资偏好"
trigger: "用户说'帮我选股'、'看看这只股票'、'今天大盘怎么样'"
expected_output: "选股列表+个股分析报告+持仓变动提醒"
success_criteria: "每天5分钟了解持仓动态，每周收到选股建议"
anti_requirements: "不需要自动交易（但可选升级），不需要期货/期权"
complexity: "simple_first"  # 先简单跑起来，再逐步增强
search_keywords: ["A股数据", "量化选股", "股票分析", "行情API"]
user_environment:
  platform: openclaw
  available_models: [claude-sonnet, gemini-flash]
  installed_skills: [web-search, file-manager]
  memory_files: [MEMORY.md]
```

**Hard Gate**: 需求画像必须包含 core_problem + trigger + expected_output，否则继续对话。

---

### Phase 2: 源泉发现 (Source Discovery)

**继承自**: Skill Forge STAGE-2-search.md
**强化点**: 搜索范围从"开源项目"扩展到四类源泉

**AI 角色**: 开源生态专家 + Skill 市场分析师

**四类源泉**:

| 源泉类型 | 搜索方式 | 评估维度 | 示例 |
|---------|---------|---------|------|
| **开源项目** | GitHub 搜索、AI 知识库 | 相关性、设计质量、社区活跃度 | akshare, vnpy, qlib |
| **OpenClaw Skill** | Skill 市场搜索 | 功能匹配度、用户评分、可复用性 | stock-analysis, data-fetcher |
| **API/数据源** | API 目录、项目文档 | 免费性、易用性、数据质量 | tushare, 东方财富接口 |
| **社区经验** | GitHub Issues、SO、论坛 | 痛点密度、解决方案质量 | "akshare 踩坑"、"vnpy 部署" |

**输出**: 源泉地图 (source-map.md)

```markdown
## 源泉地图

### 主力源泉（深度提取）
1. **akshare** (GitHub ★4.2k) — A股数据获取的事实标准
   - 提取目标：API 端点清单、数据格式、调用模式、已知限制
   - 提取类型：知识 + 资源

2. **stock-analysis-skill** (OpenClaw, 1.2k 安装) — 现有最接近的 Skill
   - 提取目标：交互模式、阶段设计、提示词模板
   - 提取类型：模式

### 辅助源泉（轻量提取）
3. **vnpy** (GitHub ★21k) — 量化交易框架
   - 提取目标：选股策略模式、风险控制规则
   - 提取类型：知识

4. **tushare** — 金融数据 API
   - 提取目标：API 端点、认证方式、数据覆盖范围
   - 提取类型：资源

### 社区信号源
- GitHub Issues: akshare#top20, vnpy#top10
- Stack Overflow: [akshare] tag, [tushare] tag
```

**用户交互**: 展示源泉地图摘要，确认方向（"我找到这些，方向对吗？"），一轮确认。

**Hard Gate**: 至少 1 个主力源泉 + 1 个资源源泉。

---

### Phase 3: 多源提取 (Multi-Source Extraction)

**这是核心引擎层，也是 v1.0 Soul Extractor 被重新利用的地方。**

**AI 角色**: 提取工程师团队（并行子代理）

**三类提取并行执行**:

#### 3A. 知识提取 (Knowledge Extraction) — 继承 v1.0

对每个主力源泉执行精简版 Soul Extraction：
- Stage 1 (Essence): 7 问协议 → 设计哲学 + 心智模型
- Stage 2 (Concepts): 核心概念卡片 (CC-*)
- Stage 3 (Rules): 决策规则卡片 (DR-*)
- Stage 3.5 (Validation): 验证门控

**与 v1.0 的区别**: 不再生成 CLAUDE.md 作为最终产出，而是作为 Phase 4 的输入材料。

#### 3B. 资源提取 (Resource Extraction) — ★ 全新

**这是 v1.0 完全缺失的维度。**

对每个源泉提取可操作的资源信息，生成 **Resource Card (RC-)**：

```yaml
---
card_type: resource_card
card_id: RC-AKSHARE-001
source: akshare (GitHub)
title: "A股实时行情接口"
resource_type: api          # api | data_feed | tool | library | service
---

## 调用方式
​```python
import akshare as ak
# 获取 A 股实时行情
df = ak.stock_zh_a_spot_em()
# 获取个股历史数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily")
​```

## 认证要求
无需 API Key，免费开放

## 速率限制
无官方限制，建议 ≤ 1 req/sec（来源：Issue #892 社区经验）

## 数据格式
pandas DataFrame
- 实时行情: 代码, 名称, 最新价, 涨跌幅, 成交量, ...
- 历史数据: 日期, 开盘, 收盘, 最高, 最低, 成交量, ...

## 依赖安装
pip install akshare

## 可靠性
高 — 数据源为东方财富，社区活跃（周更新）

## 集成复杂度
低 — 一行代码调用，返回标准 DataFrame

## 已知陷阱
- 盘后数据可能延迟 15 分钟（DR-AKSHARE-003）
- 部分接口在非交易时间返回空 DataFrame（不是错误）
- 港股数据偶尔缺失（Issue #1234, 未修复）

## 适用场景
- [x] 实时行情获取
- [x] 批量股票筛选
- [x] 历史数据下载
- [ ] 分钟级高频数据（需 tushare 或 wind）
```

**资源提取的来源**:
1. **项目 README / 文档** — API 端点列表、安装方式、基础用法
2. **代码分析** — 函数签名、参数类型、返回值结构
3. **示例代码** — examples/ 目录、README 中的 code snippets
4. **社区经验** — Issues 中的调用模式、踩坑记录、性能数据
5. **repo_facts.json** — 扩展为 repo_resources.json，增加 API 端点、数据格式等确定性信息

**提取脚本扩展**: `extract_repo_resources.py`（扩展自 extract_repo_facts.py）
- 扫描 API 路由定义（Flask routes, FastAPI endpoints, Express routes）
- 扫描 HTTP 客户端调用（requests, axios, fetch）
- 扫描数据库连接字符串
- 扫描环境变量引用（.env.example, config.py）
- 扫描 SDK/客户端初始化代码
- 输出结构化 JSON

#### 3C. 模式提取 (Pattern Extraction) — 增强版

从 OpenClaw Skill 和优秀开源项目中提取"怎么拼"的模式：

```yaml
---
card_type: pattern_card
card_id: PT-STOCK-SKILL-001
source: stock-analysis-skill (OpenClaw)
title: "股票分析 Skill 的阶段设计模式"
---

## 模式描述
该 Skill 将股票分析拆分为 4 个阶段：
1. 意图识别 → 判断用户想要选股/分析/跟踪
2. 数据获取 → 调用行情 API 获取原始数据
3. 分析处理 → 应用策略逻辑生成结论
4. 结果呈现 → 格式化输出 + 可视化建议

## 可复用元素
- 意图识别的 trigger 设计
- 数据获取的错误处理模式
- 结果呈现的 Markdown 表格模板

## 适配建议
- 阶段 1 可直接复用
- 阶段 2 需替换为 akshare API（原 Skill 用的 yfinance）
- 阶段 3 需根据用户的价值投资偏好重写策略
- 阶段 4 可直接复用
```

**并行执行与进度透明**:

```
[Phase 3] 多源提取进行中...
  ├─ 子代理 A: akshare 知识提取 ✓ (3 概念卡 + 5 规则卡)
  ├─ 子代理 B: akshare 资源提取 ✓ (8 个 API 端点, 2 个数据格式)
  ├─ 子代理 C: vnpy 知识提取   ✓ (选股策略模式 + 3 条关键规则)
  ├─ 子代理 D: tushare 资源提取 ⟳ (API 端点扫描中...)
  ├─ 子代理 E: stock-skill 模式提取 ✓ (4 阶段设计模式)
  └─ 子代理 F: 社区信号收集    ✓ (12 条高价值信号)
```

**Hard Gate**: 至少产出 3 张知识卡 + 2 张资源卡 + 1 张模式卡。

---

### Phase 4: 智能拼装 (Intelligent Assembly)

**AI 角色**: Skill 架构师

**输入**: Phase 1 需求画像 + Phase 3 全部卡片（知识 + 资源 + 模式）

**拼装逻辑**:

```
Step 1: 蓝图设计
  ├─ 从需求画像提取：trigger 列表、阶段骨架、输出格式
  ├─ 从模式卡片提取：参考架构（如 4 阶段设计）
  └─ 从知识卡片提取：关键约束和规则（嵌入 Skill 的 stage 指令中）

Step 2: 资源绑定
  ├─ 选择最优资源卡片（优先：免费 + 低集成复杂度 + 高可靠性）
  ├─ 生成资源调用代码模板
  └─ 标记需要用户配置的资源（API Key 等）→ 分为"必需"和"可选升级"

Step 3: 规则注入
  ├─ 将 DR-* 卡片中 severity=CRITICAL 的规则写入 stage 指令
  ├─ 将社区踩坑经验写入 stage 的"注意事项"
  └─ 将资源卡片的"已知陷阱"写入相关 stage 的错误处理指令

Step 4: 生成 Skill 包
  ├─ SKILL.md（触发词 + 描述 + 阶段索引）
  ├─ stages/STAGE-1-*.md ... STAGE-N-*.md
  ├─ config.yaml（默认配置，开袋即食）
  └─ README.md（能力说明 + 可选升级指南）
```

**"开袋即食"原则**:
- 所有免费、无需认证的资源：默认启用
- 需要 API Key 的资源：标记为"可选升级"，不影响基础功能
- 需要用户数据的功能：提示用户"提供 X 可解锁 Y 能力"

**示例输出 (股票 Skill)**:

```yaml
# SKILL.md
---
name: my-stock-advisor
description: >
  个人 A 股投资助手 — 选股、分析、跟踪一站式服务。
  Triggers on: "帮我选股", "分析一下XXX", "今天大盘怎么样", "看看我的持仓"
version: 1.0.0
user-invocable: true
tags: [stock, finance, A-share, investment]
---

## 能力清单
- [x] A股实时行情查询（akshare, 免费）
- [x] 个股基本面分析
- [x] 基于价值投资的选股筛选
- [x] 持仓跟踪与变动提醒
- [ ] 历史数据回测（需提供 tushare token）
- [ ] 模拟/实盘交易（需提供券商 API）

## 阶段
1. [意图识别](stages/STAGE-1-intent.md) — 理解用户想做什么
2. [数据获取](stages/STAGE-2-data.md) — 获取行情和基本面数据
3. [智能分析](stages/STAGE-3-analysis.md) — 应用选股/分析逻辑
4. [结果呈现](stages/STAGE-4-present.md) — 格式化输出 + 投资建议
```

**进度透明**:

```
[Phase 4] 拼装中...
  ✓ 蓝图设计完成：4 阶段架构（意图→数据→分析→呈现）
  ✓ 资源绑定：akshare (免费) 作为主数据源
  ✓ 规则注入：7 条关键规则已嵌入
  ✓ 生成 SKILL.md + 4 个 stage 文件
  ✓ 默认配置：开袋即食，无需 API Key
```

---

### Phase 5: 交付与增强 (Delivery & Enhancement)

**AI 角色**: 交付工程师 + 产品顾问

**交付流程**:

```
Step 1: 安装
  └─ 将 Skill 包写入 OpenClaw skills/ 目录

Step 2: 冒烟测试
  └─ 自动执行一次简单调用（如"查一下贵州茅台今天行情"）
  └─ 验证数据获取和格式化输出正常

Step 3: 能力呈现
  ├─ "你的「我的A股助手」已安装完成。"
  ├─ "现在可以做：选股筛选、个股分析、持仓跟踪"
  ├─ "试试说：'帮我从沪深300中选出低估值的股票'"
  └─ 展示一个真实输出示例

Step 4: 可选升级提示
  ├─ "💡 提供 tushare token 可解锁：历史数据回测、更丰富的财务指标"
  ├─ "💡 告诉我你的持仓清单，我可以每天自动跟踪"
  └─ "💡 提供券商 API 可启用模拟交易（支持华泰、中信）"
```

**Hard Gate**: 冒烟测试通过才交付。失败则回到 Phase 4 修复。

---

## 4. 关键创新：Resource Card (资源卡片)

**这是 v2 相比 v1 最核心的新增。**

### 为什么 v1.0 缺失资源提取是致命的

v1.0 的知识卡片体系 (CC/WC/DR/CT/AC) 回答的是：
- 这个项目是什么？怎么设计的？为什么这样设计？会踩什么坑？

但它不回答：
- 这个项目提供了哪些**可直接调用的能力**？
- 调用这些能力需要什么**前置条件**？
- 调用时会遇到什么**实际限制**？

对于"理解一个项目"，知识卡片足够。
对于"用一个项目的能力拼装新东西"，**必须有资源卡片**。

### Resource Card 的六个维度

| 维度 | 说明 | 为什么重要 |
|------|------|---------|
| **调用方式** | 代码示例、SDK 用法、CLI 命令 | AI 需要知道怎么调用 |
| **认证要求** | 无/API Key/OAuth/付费 | 决定是否"开袋即食" |
| **速率限制** | QPS、日配额、并发数 | 影响 Skill 的可用性设计 |
| **数据格式** | 返回结构、字段说明 | AI 需要知道怎么解析结果 |
| **集成复杂度** | 依赖安装、环境要求 | 影响"开袋即食"的可行性 |
| **已知陷阱** | 社区踩过的坑、边界情况 | 防止生成的 Skill 踩同样的坑 |

### 资源提取来源优先级

```
优先级 1: 项目文档（README, API docs）
  → 最权威，但可能不完整

优先级 2: 代码分析（函数签名、示例代码）
  → 最准确，但需要代码理解能力

优先级 3: 社区经验（Issues、SO、博客）
  → 最实用（真实踩坑），但需要过滤噪音

优先级 4: 包管理器元数据（npm、PyPI）
  → 依赖信息、版本兼容性
```

### 扩展 extract_repo_facts.py → extract_repo_resources.py

在原有提取（CLI commands, skills, config keys, file paths）基础上新增：

```python
# 新增提取目标
resources = {
    "api_endpoints": [],     # Flask routes, FastAPI paths, Express routes
    "http_clients": [],      # requests.get/post, axios, fetch 调用
    "sdk_initializations": [],  # API client 初始化代码
    "env_variables": [],     # 环境变量引用（.env.example, config）
    "data_formats": [],      # 返回值类型、JSON schema
    "dependencies": [],      # 外部服务依赖（数据库、缓存、MQ）
    "auth_patterns": [],     # 认证方式（API Key, OAuth, token）
    "example_usages": [],    # examples/ 目录中的使用示例
}
```

---

## 5. 完整用户旅程示例：股民老王

### 背景
老王，45 岁，中国 A 股散户，非技术背景。用 OpenClaw 作为日常 AI 助手。
他想让 AI 帮他做股票研究，但现有 Skill 太通用。

### Phase 1: 需求理解

```
老王: 我想要一个帮我炒股的 AI 助手

Doramagic: 明白，我帮你打造一个。先聊几个问题——
你炒股最头疼的是什么？是选股难、跟踪累、还是分析不到位？

老王: 主要是选股，我不知道该买什么。还有就是买了之后不能及时跟踪。

Doramagic: 你平时选股有什么偏好吗？比如喜欢低估值的、高成长的、
还是看技术指标的？

老王: 我喜欢价值投资，找那种被低估的好公司。

Doramagic: 最后一个问题——你希望这个助手多快给你结果？
是简单快速先用起来，还是功能全面但需要多设置一些？

老王: 先简单好用的，后面再加功能。

Doramagic: 明白了！我理解你需要的是：
- 核心功能：基于价值投资的 A 股选股
- 附加功能：持仓跟踪提醒
- 风格：开袋即食，后续可扩展
我这就去找最好的"作业"来抄。
```

### Phase 2: 源泉发现

```
[Phase 2] 搜索中...
  ✓ 发现 akshare (★4.2k) — A股数据获取事实标准，免费无需API Key
  ✓ 发现 stock-analysis-skill (OpenClaw) — 可复用的交互模式
  ✓ 发现 vnpy (★21k) — 量化选股策略库，价值投资因子
  ✓ 发现 tushare — 金融数据API（可选升级，需注册）

Doramagic: 我找到了几个好的"作业"可以抄：
1. akshare — 免费的A股数据，不用注册就能用
2. 一个现有的股票分析 Skill — 我会借鉴它的交互设计
3. vnpy 的选股逻辑 — 里面有成熟的价值投资筛选策略

方向对吗？

老王: 对，就这些。
```

### Phase 3: 多源提取 (后台并行，实时展示)

```
[Phase 3] 正在从 4 个源泉提取知识和资源...
  ✓ akshare: 提取了 15 个数据接口 + 3 条使用陷阱
  ✓ vnpy: 提取了价值投资5因子模型 + 回测方法论
  ✓ stock-skill: 提取了 4 阶段交互模式
  ✓ 社区: 提取了 8 条最佳实践（含"akshare 非交易时间返回空数据"等）
```

### Phase 4: 智能拼装 (后台执行，实时展示)

```
[Phase 4] 正在拼装你的专属 Skill...
  ✓ 架构设计：4 阶段（意图识别→数据获取→价值分析→结果呈现）
  ✓ 数据源绑定：akshare（免费，开袋即食）
  ✓ 选股策略：PE<行业均值 + ROE>15% + 连续3年净利润增长
  ✓ 社区踩坑规则已注入（7 条）
  ✓ 生成完毕！
```

### Phase 5: 交付

```
Doramagic: 你的「老王的A股助手」已安装完成！

现在可以做：
  ✅ 说"帮我选股"→ 从沪深全市场筛选低估值好公司
  ✅ 说"分析一下贵州茅台"→ 出基本面分析报告
  ✅ 说"看看我的持仓"→ 跟踪你关注的股票变动

试试看？比如说"帮我从沪深300中选出低估值的好公司"。

💡 后续可升级：
  - 告诉我你的持仓清单 → 每天自动推送变动提醒
  - 注册 tushare（免费）→ 解锁 10 年历史数据回测
  - 提供券商 API → 启用模拟交易
```

---

## 6. 技术实现路径

### 需要新建的

| 组件 | 说明 | 优先级 |
|------|------|--------|
| Resource Card 定义 | 新卡片类型 + YAML schema | P0 |
| extract_repo_resources.py | 资源提取脚本（扩展自 extract_repo_facts.py） | P0 |
| Phase 2 源泉搜索引擎 | 多源搜索 + 评分排序 | P0 |
| Phase 4 拼装引擎 | Skill 生成逻辑（资源绑定 + 规则注入） | P0 |
| Phase 5 冒烟测试框架 | 自动验证生成的 Skill 可运行 | P1 |
| Pattern Card 定义 | 新卡片类型（从 Skill 中提取模式） | P1 |

### 可复用的 v1.0 资产

| 组件 | 复用方式 |
|------|---------|
| Soul Extractor Stage 1-3.5 | Phase 3A 知识提取子引擎 |
| Skill Forge Stage 1 | Phase 1 需求理解 |
| Skill Forge Stage 2 | Phase 2 源泉发现骨架 |
| validate_extraction.py | 扩展支持 Resource Card |
| community_signals 收集 | Phase 3 社区信号子代理 |
| 5 维质量评分 | 保留，增加"可用性"维度 |

### 需要修改的 v1.0 组件

| 组件 | 修改内容 |
|------|---------|
| repo_facts.json schema | 扩展为 repo_resources.json |
| Skill Forge Stage 5 | 重写为 Phase 4 拼装引擎（增加资源绑定逻辑） |
| assemble-output.sh | 重写为 assemble-skill.sh（输出 Skill 包而非 CLAUDE.md） |

---

## 7. 开放问题（需创始人决策）

### Q1: v2 是否完全取代 v1 的独立 Soul Extractor？
- 方案 A: Soul Extractor 作为 v2 的内部引擎，不再独立暴露
- 方案 B: 保留独立的 Soul Extractor（给开发者用），v2 面向终端用户
- **建议**: 方案 B，两个入口，一个引擎

### Q2: 源泉发现阶段如何获取 OpenClaw Skill 信息？
- 需要 OpenClaw Skill 市场的搜索 API 或本地索引
- 如果暂无 API，可以先从已安装 Skill 中提取模式

### Q3: 资源提取的准确性如何保证？
- 代码分析（确定性）+ LLM 补充（需验证）
- 建议：对资源卡片也增加证据级别标注（E1-E4）

### Q4: 冒烟测试的边界在哪？
- 数据类 Skill 可以直接测试（调 API 看有没有返回）
- 交互类 Skill 只能验证格式（无法验证内容质量）

### Q5: v2 的产品形态？
- 纯 OpenClaw Skill？
- 同时保留 CLI 版本？
- **建议**: OpenClaw Skill 优先，CLI 作为开发者工具保留

### Q6: 学习 Claude Code 的工程实践（创始人需求）
> **来源**: Q14 讨论中的关键洞察 (2026-03-11)
>
> Claude Code 的价值公式：**产品 = 模型 + 文件系统 + Git + 工具编排 + 项目上下文**
>
> Doramagic 应参考这个工程模式：不是简单包装 LLM，而是为 LLM 提供**操作化基础设施**——让 AI 能真正"做事"而不只是"说话"。
>
> 具体参考方向：
> - Claude Code 如何将模型能力与系统工具无缝集成
> - Claude Code 的权限模型、工具编排模式、上下文管理策略
> - 将"知识操作化"作为产品设计的核心原则
>
> **优先级**: 高——这是产品架构层面的参考，影响整体设计方向

### Q7: 自我学习与信任校准机制（创始人需求）
> **来源**: Q19 讨论中的关键需求 (2026-03-11)
>
> Doramagic 锻造的道具必须具备**自我学习能力**——越用越好用。
>
> 核心机制：
> - 定期 review：道具根据使用数据定期自检，发现自身短板
> - 回炉改造：用户可将道具带回 Doramagic 进行改进（已在 Q8 讨论中提出）
> - 信任校准：先建立信任，再通过互动逐步校准信任阈值（边际效应）
> - MEMORY.md 反馈循环：使用中的经验沉淀为持久记忆，提升后续表现
>
> 产品节奏：不在 Day 1 解决全部质量问题，而是通过演进式互动持续提升
>
> **优先级**: 高——这是产品核心体验的一部分，影响用户留存和口碑

---

## 8. 与 v1.0 的核心差异总结

| 维度 | v1.0 | v2.0 |
|------|------|------|
| **产品定义** | 开源项目灵魂提取系统 | OpenClaw 个性化 Skill 制造器 |
| **入口** | GitHub URL | 用户的一句话需求 |
| **出口** | CLAUDE.md（知识文档） | SKILL.md + stages/（可运行的 Skill） |
| **核心能力** | 知识提取 | 需求理解 + 多源发现 + 知识/资源/模式提取 + 智能拼装 |
| **缺失维度** | 资源（API/数据源/工具链） | ★ Resource Card 补齐 |
| **用户角色** | 主动型（用户要知道分析哪个项目） | 被动型（AI 帮用户找到该抄谁的作业） |
| **交付体验** | 等 40 分钟得到文档 | 实时进度 + 开袋即食的 Skill |
| **目标用户** | 开发者/CTO | OpenClaw 终端用户（含非技术用户） |
