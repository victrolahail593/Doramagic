# Doramagic 产品定义与开发手册 v5.3

> **版本**: v5.3（开发冻结版）
> **日期**: 2026-03-18
> **状态**: **完成**（Part 1-4 全部完成，可进入 Round 0）
> **演进链**: v5.2（产品定义全书）→ v5.3（开发冻结版，收敛为可执行的开发手册）
>
> **本手册的定位**：所有 AI 开发环境的唯一共同依据。拿到这份手册就能独立开发。

---

# 第一部分：产品定义（冻结）

## 1.1 一句话定义

Doramagic 是运行在 OpenClaw 上的哆啦A梦——用户说出模糊烦恼，Doramagic 从开源世界找最好作业，提取智慧，锻造开袋即食的 AI 道具。

## 1.2 产品灵魂（不可修改）

> **不教用户做事，给他工具。**
> **代码说事实，AI 说故事。**
> **能力升级，本质不变。**

哆啦A梦从不教大雄怎么做事，而是从口袋里掏出道具让大雄自己解决问题。

## 1.3 核心用户

**主用户**：开发者（抄作业的人）。
**扩展用户**：项目作者、技术选型者、创业者、投资人、PM/CTO——这些是"无意中的扩展"，不为他们改变产品哲学。

## 1.4 核心交付物

| 输出 | 消费者 | 优先级 |
|------|--------|--------|
| **SKILL.md** | 开发者（核心） | 最高 |
| **PROVENANCE.md** | 开发者 | 最高（伴随 SKILL.md） |
| **LIMITATIONS.md** | 开发者 | 最高（伴随 SKILL.md） |
| 热力图（知识差距可视化） | 开发者 / 选型者 | 高 |
| DOMAIN_TRUTH.md | 领域学习者 / 选型者 | 衍生 |
| HEALTH_CHECK.md | 项目作者 / 评估者 | 衍生 |
| SOUL_DIFF.md | 选型者 / 技术决策者 | 衍生 |
| STITCH_MAP | 高级开发者 | 衍生 |

## 1.5 非目标清单

- 不做通用问答产品
- 不做通用代码生成助手
- 不做项目托管平台
- 不做面向所有角色的统一 BI 产品
- 不给总分、不开处方、不教用户做事
- 不为扩展用户改变核心体验

## 1.6 护城河

| 层级 | 护城河 | 时间尺度 |
|------|--------|---------|
| 短期 | WHY + UNSAID 提取能力（行业空白） | 现在 |
| 中期 | 跨项目知识关系引擎（公约数 + 打架 + 缝合） | 6-12 月 |
| 长期 | 处理不完整知识的能力 + 知识供应链溯源 | 12+ 月 |

## 1.7 首批预提取领域（6 个）

| # | 领域 | 范围 |
|---|------|------|
| 1 | **广义个人财务** | 记账/预算 + 投资理财 + 房产投资 + 财务知识 |
| 2 | **笔记/PKM** | 块编辑/文档树 + 双向链接 + local-first + 知识回流 |
| 3 | **私有云与自托管基础设施** | 容器编排 + 反代/网络 + 认证/SSO + 监控 + 备份 |
| 4 | **健康数据（综合角度）** | 健身追踪 + 异构设备数据对齐 + 协议逆向 + 去噪 |
| 5 | **信息摄取与内容管理** | RSS/过滤 + Anti-AI 去噪 + OCR/Paperless + 网页存档 |
| 6 | **智能家居与生活自动化** | 家居自动化规则 + 设备集成 + 能源监控 + 场景联动 |

每个领域预提取 5-7 个精选项目，成本 $10-40/领域。

选择原则：**知识独特性 > 供需缺口 > 平台适配**。

## 1.8 硬性约束清单

1. **不教用户做事**：所有输出是工具/信息，不是建议/指令
2. **代码说事实**：确定性提取为骨架，LLM 仅做解读
3. **能力升级本质不变**：新能力叠加，不替代
4. **吃透 OpenClaw 规则**：Doramagic 适应平台，不是反过来
5. **偏向漏报不偏向误报**：所有不确定场景
6. **NEVER 硬判定唯一源头**：知识溯源只标注，不下结论
7. **不给总分**：所有评估类输出，给维度不给分数
8. **冲突是高价值知识**：标注冲突，不消解冲突
9. **管线通用，知识领域特定**：Phase A-H 流程不随领域变化

---

# 第二部分：系统架构

## 2.1 两个独立系统

Doramagic 由两个**可独立运行**的系统组成：

```
┌──────────────────────────────────────────────────────────┐
│                    用户（OpenClaw）                        │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────┐         │
│  │         系统 A：Doramagic 终端               │         │
│  │     （完整独立的知识提取与锻造软件）          │         │
│  │                                              │         │
│  │  Phase A→B→C→D→E→F→G→H                      │         │
│  │  （包含完整的 Stage 0-5 提取管线）           │         │
│  │                                              │         │
│  │  ┌──────────┐                                │         │
│  │  │ 可选连接  │←── 有则加成，无则独立工作      │         │
│  │  └────┬─────┘                                │         │
│  └───────┼──────────────────────────────────────┘         │
│          │                                                │
│          │ API 调用（查询/提交）                           │
│          ▼                                                │
│  ┌─────────────────────────────────────────────┐         │
│  │       系统 B：预提取云端 API                  │         │
│  │     （静态知识仓库，可选增强服务）            │         │
│  │                                              │         │
│  │  查询接口：拉取领域知识（图谱/原子/积木）    │         │
│  │  提交接口：推送预提取数据（管理员使用）      │         │
│  │                                              │         │
│  │  存储：SQLite + Parquet + JSONL              │         │
│  │  运行在：Mac mini (192.168.1.104)            │         │
│  └─────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────┘
```

### 关键原则

1. **Doramagic 终端必须独立可运行**——API 不在时，终端照样能完成从需求理解到 Skill 交付的全部流程
2. **API 是加成不是依赖**——连接 API 时获得 Brick 效应（+20% 提取质量）、秒出领域概览、更强的假公约数防护
3. **API 不做实时计算**——只存储和提供预计算好的知识，等 Doramagic 发来请求才响应
4. **两个系统独立开发、独立部署、独立运行**

### 类比

- Doramagic 终端 = 考古学家（独立工作，挖掘分析全靠自己）
- 预提取 API = 图书馆（有它工作更好，没它也能干活）

## 2.2 系统 A：Doramagic 终端

### 定位

运行在 OpenClaw 平台上的完整知识提取与 Skill 锻造软件。是 Doramagic 的核心产品。

### 内部架构

```
Doramagic 终端
├── 单项目管线（Soul Extractor）
│   ├── Stage 0: 确定性提取（prepare-repo.sh + repomix + repo_facts.json）
│   ├── Stage 1: 广度扫描（Q1-Q7 + Q8 假说生成）
│   ├── Stage 1.5: Agent Exploration Loop（假说驱动深挖，可选）
│   ├── Stage 2: 概念提取（concept_cards + workflow_cards）
│   ├── Stage 3: 规则提取（decision_rule_cards）
│   ├── Stage 3.5: 验证硬阻断（fact-checking + claim traceability）
│   ├── Stage 3.7: 知识健康检查注入（如有匹配领域图谱，可选）
│   ├── Stage 4: 专家叙事合成（可选）
│   └── Stage 5: 输出组装（CLAUDE.md）
│
├── 多项目管线（Phase A-H）
│   ├── Phase A: 需求理解 → need_profile.json
│   ├── Phase B: 作业发现 → discovery_result.json
│   ├── Phase C: 并行灵魂提取（调用单项目管线 x N）
│   ├── Phase D: 社区知识采集 → community_knowledge.json
│   ├── Phase E: 知识综合 → synthesis_report.md
│   ├── Phase F: Skill 组装 + 平台适配
│   ├── Phase G: 质量门控（7 项检查）
│   └── Phase H: 交付（SKILL.md + README + PROVENANCE + LIMITATIONS）
│
├── 确定性编排层
│   ├── 子代理分派（Stage→模型映射）
│   ├── 中间产物管理（Filesystem-as-Memory）
│   ├── 降级策略（子代理失败→单代理串行）
│   └── 平台适配（platform_rules.json）
│
├── 质量保证体系
│   ├── Tier 1: 静态验证（skill_check.py, <5s）
│   ├── Tier 2: Benchmark（A/B 对照, ~10min）
│   ├── Tier 3: LLM-as-judge（Sonnet 评分, ~30s）
│   ├── 幻觉三层防护
│   ├── 暗雷扫描（Top 10 + Tier-0 错误共识）
│   └── 模板防腐系统（.tmpl + skill_gen.py）
│
└── API 客户端（可选）
    ├── 查询领域图谱（增强 Stage 0/1 注入）
    └── 查询积木/废弃事件（增强 Stage 3.5/3.7）
```

### 子代理架构

| Stage | 执行者 | 理由 |
|-------|--------|------|
| Stage 0 / 框架检测 / repo_facts | 确定性脚本，无模型 | 零幻觉 |
| Stage 1 (WHY) / Stage 4 (叙事) | Opus 子代理 | 需要深度推理 |
| Stage 2/3 (概念/规则) | Sonnet 子代理 + 积木锚点 | 结构化提取 |
| Stage 1.5 (Agent Loop) | Sonnet/Opus（视项目规模） | 工具调用密集 |
| Phase E (知识综合) | Opus 子代理 | 需要跨源权衡 |
| Phase F (Skill 组装) | Sonnet + 确定性模板 | 格式编译为主 |

### 降级策略

| 场景 | 降级方案 |
|------|---------|
| 子代理失败 | 自动降级为单代理串行模式（v1.0 管线作 fallback） |
| Agent Loop 失败 | 回退到纯 Stage 1 输出 |
| 弱模型 (MiniMax) | 增强版 Stage 0（Haiku 辅助），跳过 Agent Loop |
| 找不到候选项目 | 飞轮入口：从零创建，新 skill 回流 |
| 质量门控连续失败 | 最多 3 轮 REVISE，仍失败则终止并说明原因 |

### OpenClaw 平台约束

| 约束 | 影响 |
|------|------|
| 子代理最多 5 并发 | Phase C 并行提取的并发上限 |
| allowed-tools: exec/read/write | 不能用 Claude Code 工具名 |
| 存储路径: ~/clawd/ | 所有 Skill 数据存储在此 |
| SOUL.md 加载不可靠 | 关键指令写 AGENTS.md 或显式传入 |
| 默认模型 MiniMax | 子代理模型路由更关键 |
| cron 不在 SKILL.md 中 | 通过平台其他机制设置 |

## 2.3 系统 B：预提取云端 API

### 定位

静态知识仓库服务。离线预计算，在线只做查询和提交。

### 两个 API 接口

**接口 1：查询接口**（供 Doramagic 终端调用）

| 端点 | 描述 | 返回 |
|------|------|------|
| `GET /domains` | 列出已预提取的领域 | 领域列表 + 项目数 + 最后更新时间 |
| `GET /domains/{id}/bricks` | 获取领域积木 | DOMAIN_BRICKS.json（注入 Stage 0/1） |
| `GET /domains/{id}/truth` | 获取领域真相 | DOMAIN_TRUTH.md |
| `GET /domains/{id}/atoms` | 查询知识原子 | Atom Cluster 列表（按相关度排序） |
| `GET /domains/{id}/deprecations` | 获取废弃事件 | deprecation_events.jsonl 子集 |
| `GET /domains/{id}/health/{project}` | 项目体检 | HEALTH_CHECK.md（如有） |

**接口 2：提交接口**（供管理员使用，初期内部）

| 端点 | 描述 | 输入 |
|------|------|------|
| `POST /domains/{id}/projects` | 新增预提取项目 | 提取包（Stage 0-5 输出） |
| `PUT /domains/{id}/rebuild` | 触发图谱重建 | 无（使用已提交的项目数据） |
| `POST /deprecations` | 新增废弃事件 | deprecation_event 对象 |

### 存储架构

| 存储 | 用途 | 格式 |
|------|------|------|
| SQLite | 元数据 + 索引 + 事务 | domain_map.sqlite |
| Parquet | 知识原子 + 嵌入向量（批处理分析） | atoms.parquet |
| JSONL | 废弃事件 + 增量日志（append-only） | deprecation_events.jsonl |

### 离线批量管线

预提取不是实时的。管理员手动触发或定期运行：

```
discover（选定领域+项目）
  → clone（克隆项目代码）
  → batch_extract（对每个项目运行 Stage 0-5）
  → build_fingerprints（生成 project_fingerprint.json）
  → compare（三层匹配 + 假公约数防护）
  → build_domain_map（构建领域图谱）
  → compile_outputs（编译 DOMAIN_BRICKS / DOMAIN_TRUTH / 积木）
```

成本：7 项目 ≈ $10-40，1-2 小时（并行提取）。

### 增量更新

新项目加入时，atom 级增量融合：
- 新 atom 找已有 cluster → 命中则更新 stats → 未命中则建新 cluster
- 只重编译受影响的 bricks
- 全量重算仅在 schema migration 时

## 2.4 终端与 API 的交互流程

```
用户："我想做一个智能记账 skill"
  │
  ▼
Doramagic 终端
  │
  ├─ Phase A: 理解需求 → need_profile.json
  │
  ├─ [可选] 查询 API: GET /domains → 发现"广义个人财务"领域已预提取
  │     │
  │     └─ GET /domains/finance/bricks → 获取领域积木
  │        GET /domains/finance/atoms?keywords=budget,expense → 获取相关知识原子
  │        GET /domains/finance/deprecations → 获取废弃知识
  │
  ├─ Phase B: 作业发现（GitHub 搜索 + 如有 API 则用领域知识辅助筛选）
  │
  ├─ Phase C: 并行提取（Stage 0 注入领域积木 → Brick 效应 +20%）
  │
  ├─ Phase D-H: 后续管线（正常执行）
  │
  └─ 输出: SKILL.md + README + PROVENANCE + LIMITATIONS

如果 API 不可用：
  → 跳过所有 API 调用，Phase B 纯 GitHub 搜索，Stage 0 无积木注入
  → 一切正常工作，只是质量没有加成
```

## 2.5 关键数据结构

详见 v5.2 附录 C。以下是开发时最常用的结构：

| 结构 | 系统 | 用途 |
|------|------|------|
| `need_profile.json` | 终端 | Phase A 输出，驱动整个管线 |
| `discovery_result.json` | 终端 | Phase B 输出，候选项目列表 |
| `repo_facts.json` | 终端 | Stage 0 确定性事实 |
| `exploration_log.jsonl` | 终端 | Stage 1.5 Agent 工具调用记录 |
| `claim_ledger.jsonl` | 终端 | Stage 1.5 知识声明账本 |
| `synthesis_report.md` | 终端 | Phase E 知识综合报告 |
| `validation_report.json` | 终端 | Phase G 门控结果 |
| `platform_rules.json` | 终端 | OpenClaw 适配规则配置 |
| `domain_map.sqlite` | API | 领域共识图谱 |
| `DOMAIN_BRICKS.json` | API | 领域积木（注入终端 Stage 0/1） |
| `deprecation_events.jsonl` | API | 废弃事件数据库 |
| `project_fingerprint.json` | 共享 | 机器可比较的项目知识指纹 |
| Atom Cluster | 共享 | 图谱基本操作单位 |

---

# 第三部分：开发计划

## 3.1 开发角色

| 角色 | 环境 | 职责 |
|------|------|------|
| **PM（项目经理）** | Claude Code + Opus 4.6（本机主对话） | 架构设计、contracts 定义、任务分配、赛马评审、代码合并、质量决策 |
| **选手 S1** | Claude Code + Sonnet 4.6 子代理（本机） | 赛马开发 |
| **选手 S2** | Codex + GPT 5.4（本机） | 赛马开发 |
| **选手 S3** | Gemini + Gemini 3 Pro（本机） | 赛马开发 |
| **选手 S4** | Claude + GLM5（Mac mini 192.168.1.104） | 赛马开发 + 目标服务器 |

**核心模型：1 PM + 4 选手 = 每轮 2 条并行赛道（2×2）**

## 3.2 技术选型

| 维度 | 选型 | 理由 |
|------|------|------|
| **主语言** | Python 3.12+ | 数据处理/schema 校验/agent 编排最适合；现有实验脚本均为 Python |
| **辅助语言** | Bash（仅 repo prep/wrapper） | 保持 stage0-v2.sh 等已验证脚本 |
| **API 框架** | FastAPI + Pydantic + Uvicorn | 轻量、与 contracts 天然一致、schema 文档自动生成 |
| **包管理** | uv | 快速、确定性依赖解析 |
| **测试** | pytest | 主流、插件生态丰富 |
| **Lint/Format** | ruff | 快、统一 |
| **类型检查** | mypy（关键包） | contracts 层必须类型安全 |
| **任务运行** | Makefile 或 just | 统一命令面 |
| **TS 原型处置** | 作设计参考，不继承代码 | 架构已从单系统升级为双系统+共享 contracts，旧边界假设过时 |

## 3.3 仓库结构

**Monorepo**，两个独立可部署应用 + 共享 packages：

```
Doramagic/
├── apps/
│   ├── terminal/           # 系统 A：Doramagic 终端（OpenClaw Skill）
│   └── preextract-api/     # 系统 B：预提取云端 API
├── packages/
│   ├── contracts/          # 所有 artifact 的 Pydantic model / JSON Schema（地基）
│   ├── extraction/         # Stage 0-5 提取管线
│   ├── cross-project/      # Phase B/E 发现+比较+综合
│   ├── community/          # Phase D 社区知识采集
│   ├── skill-compiler/     # Phase F Skill 编译
│   ├── platform-openclaw/  # 平台适配（rules + validator + skill_check）
│   ├── domain-graph/       # 领域图谱构建+快照
│   ├── orchestration/      # Phase A-H + Stage 0-5 编排层
│   ├── evals/              # fixtures + 回归测试 + golden cases
│   ├── racekit/            # 赛马工具（worktree + branch + 评审模板）
│   └── shared-utils/       # 日志/budget/路径/重试/token 计数
├── data/
│   ├── fixtures/           # 固定测试数据（repo snapshots）
│   └── snapshots/          # 领域图谱快照
├── skills/
│   ├── templates/          # SKILL.md 模板（.tmpl）
│   └── released/           # 已发布的 skills
├── scripts/
│   ├── dev/                # 开发脚本
│   └── release/            # 发布脚本
├── tests/
│   ├── integration/        # 集成测试
│   └── smoke/              # 冒烟测试
├── reports/
│   ├── races/              # 赛马评审报告
│   └── evals/              # 评估报告
├── docs/                   # 文档（含本手册）
├── research/               # 研究资产（已有）
└── experiments/            # 实验（已有）
```

### 共享规则

| 类型 | 规则 |
|------|------|
| **必须共享** | contracts（所有 schema）、evals（fixtures）、platform-openclaw（规则）、shared-utils |
| **建议共享** | extraction、cross-project、orchestration |
| **不共享** | terminal CLI 展示层、API HTTP handler/auth/部署配置 |
| **contracts 修改权** | 仅 PM，赛马选手不能修改 contracts |

## 3.4 模块划分

### 18 个模块总表

| # | 模块 | 职责 | 赛马？ | 预估行数 |
|---|------|------|--------|---------|
| 1 | contracts.artifacts | 所有 artifact schema 定义 | 不赛马（PM 定义） | 400-600 |
| 2 | shared-utils | 日志/budget/路径/重试 | 不赛马 | 300-500 |
| 3 | evals.fixtures | 固定 repo fixture + golden cases | 不赛马 | 300-500 |
| 4 | racekit | 赛马工具自动化 | 不赛马 | 250-400 |
| 5 | extraction.stage0 | 确定性 repo facts 提取 | 单人 | 300-500 |
| 6 | **extraction.stage1_scan** | 广度扫描 Q1-Q8 | **赛马** | 500-700 |
| 7 | **extraction.stage15_agentic** | Agent Loop 深挖 | **重点赛马** | 900-1400 |
| 8 | extraction.stage3_cards | 概念/规则卡片构建 | 可赛马 | 500-700 |
| 9 | **extraction.stage35_validate** | 交叉验证 + claim traceability | **赛马** | 400-700 |
| 10 | community.harvest | 社区信号采集 | 可赛马 | 300-500 |
| 11 | **cross-project.discovery** | Phase A/B 需求理解+作业发现 | **赛马** | 400-700 |
| 12 | cross-project.fingerprint | 项目指纹生成 | 不赛马 | 400-700 |
| 13 | **cross-project.compare** | 三层匹配 + ALIGNED/MISSING 等 | **重点赛马** | 700-1000 |
| 14 | **cross-project.synthesis** | StitchCraft + 综合报告 | **重点赛马** | 600-900 |
| 15 | **skill-compiler.openclaw** | SKILL.md 编译 + 平台适配 | **重点赛马** | 500-800 |
| 16 | **platform-openclaw.validator** | 静态校验 + 错误规范化 | **赛马** | 600-900 |
| 17 | **orchestration.phase_runner** | Phase A-H + Stage 0-5 编排 | **重点赛马** | 700-1100 |
| 18 | domain-graph.snapshot_builder | Atom Cluster + 图谱快照 | 后置赛马 | 900-1400 |
| — | apps.terminal.cli | 终端 CLI 入口 | 单人 | 400-700 |
| — | apps.preextract-api.read | API 查询接口 | 赛马 | 400-700 |
| — | apps.preextract-api.ingest | API 提交接口 | 单人 | 400-700 |

**赛马模块 8 个**，非赛马模块 10 个。总预估 ~12,000-18,000 行。

### 依赖关系图

```
[contracts] ──→ [shared-utils] ──→ [racekit]
     │
     ├──→ [evals.fixtures]
     │
     ├──→ [extraction.stage0]
     │         │
     │         ▼
     │    [extraction.stage1_scan]          ← 赛马 Round 1A
     │         │
     │         ▼
     │    [extraction.stage15_agentic]      ← 赛马 Round 1B
     │         │
     │         ▼
     │    [extraction.stage3_cards]
     │         │
     │         ▼
     │    [extraction.stage35_validate] ←── [community.harvest]
     │         │
     │         ▼
     │    [cross-project.fingerprint]
     │         │
     │         ▼
     │    [cross-project.discovery]         ← 赛马 Round 2A
     │         │
     │         ▼
     │    [cross-project.compare]           ← 赛马 Round 2B
     │         │
     │         ▼
     │    [cross-project.synthesis]         ← 赛马 Round 3A
     │         │
     │         ▼
     │    [skill-compiler.openclaw]         ← 赛马 Round 3B
     │         │
     │         ▼
     │    [platform-openclaw.validator]     ← 赛马 Round 4A
     │         │
     │         ▼
     │    [orchestration.phase_runner]      ← 赛马 Round 4B
     │         │
     │         ▼
     │    [apps.terminal.cli]
     │
     └──→ [domain-graph.snapshot_builder]   ← 赛马 Round 5
              │
              ▼
         [apps.preextract-api]
```

## 3.5 赛马机制

### 总原则

- 赛马是**高价值模块的设计竞争机制**，不是所有模块的默认模式
- 4 个选手 = 每轮 **2 条并行赛道**
- 完全隔离：选手看不到对方代码，只看到相同的 brief + contracts + fixtures
- PM 是唯一的评审者和合并者

### 赛马日历（4 选手版）

| 阶段 | 赛道 A | 赛道 B | 时长 |
|------|--------|--------|------|
| **Round 0** | PM 统一实现：contracts + fixtures + racekit + repo 骨架 | — | 2-3 天 |
| **Round 1** | `stage1_scan`（S1 vs S2） | `stage15_agentic`（S3 vs S4） | 2-3 天 |
| **Review 1** | PM 评审 + 合并 + 回归 | | 0.5-1 天 |
| **Round 2** | `discovery`（S1 vs S3） | `compare`（S2 vs S4） | 2-3 天 |
| **Review 2** | PM 评审 + 合并 + 回归 | | 0.5-1 天 |
| **Round 3** | `synthesis`（S2 vs S3） | `skill-compiler`（S1 vs S4） | 2-3 天 |
| **Review 3** | PM 评审 + 合并 + 回归 | | 0.5-1 天 |
| **Round 4** | `validator`（S1 vs S2） | `phase_runner`（S3 vs S4） | 2-3 天 |
| **Review 4** | PM 评审 + 合并 + 回归 → **终端 v1** | | 1 天 |
| **Round 5** | `snapshot_builder`（S2 vs S4） | `api.read`（S1 vs S3） | 2-3 天 |
| **Review 5** | PM 评审 → **双系统 v1** | | 0.5-1 天 |

### 配对原则

| 原则 | 说明 |
|------|------|
| **轮换配对** | 每轮重新配对，避免固定组合的思维趋同 |
| **能力互补** | 探索型模块让思路差异大的选手对碰（如 S2 Codex vs S3 Gemini） |
| **平台相关** | 部署/平台相关模块让 S4 (GLM5/Mac mini) 参与 |
| **错误收敛** | 校验类模块让写法严谨的选手正面对比 |

### 赛马规则

**交付物标准**（每个选手每次必须提交）：

1. 模块代码（符合 contracts）
2. 单元测试（≥80% 行覆盖）
3. 至少 1 个 fixture-based 集成测试
4. `README.md`（用法说明）
5. `DECISIONS.md`（关键设计选择、已知缺陷、未覆盖项）
6. 样例输入/输出（用 fixtures 目录中的数据）

**时间限制**：

| 模块类型 | 时间盒 |
|---------|--------|
| 中小模块（500-700 行） | 6-8 小时 |
| 核心模块（800+ 行） | 10-14 小时 |
| 超时未交付 | 本轮失败，不延长 |

**隔离规则**：

| 可见 | 不可见 |
|------|--------|
| 模块 brief（PM 撰写） | 对手分支 |
| contracts 包 | 对手中间实现 |
| fixtures 数据 | 对手评审草稿 |
| 验收标准 | |

**双方都不好时的处理**：

1. PM 写失败复盘（spec 不清 or 实现不佳？）
2. 缩小模块边界，拆成更小赛道
3. 冻结新的验收 fixture
4. 更换配对，重赛
5. 必要时 PM 先下发骨架代码

### 评审标准

| 维度 | 权重 | 说明 |
|------|------|------|
| Contract 正确性 | 25% | 输入输出是否严格满足 schema |
| 可验证性 | 20% | 是否易测、是否保留 trace/provenance |
| 集成适配度 | 20% | 是否便于接入后续模块 |
| 代码清晰度 | 15% | 结构、命名、错误处理 |
| 性能与成本 | 10% | token、I/O、运行时成本 |
| 运维稳定性 | 10% | 重试、超时、幂等、日志 |

**评审结果**：选 A / 选 B / 合并 A+B / 都不要重做

### 合并策略

1. 获胜方案 `merge --squash` 到 `integration/<phase>` 分支
2. A+B 合并时，PM 在 `merge/<round>/<module>` 分支完成
3. 合并后跑：schema 校验 → 模块 unit → fixture 集成 → 端到端 smoke
4. 通过后才进入 `main`
5. 落选方案归档到 `archive/` 分支 + 评审报告

### 分支规范

```
main                              # 稳定主分支
integration/phase-1               # Phase 1 集成分支
integration/phase-2               # Phase 2 集成分支
race/r01/stage15/s1-sonnet        # Round 1 选手 S1
race/r01/stage15/s3-gemini        # Round 1 选手 S3
merge/r01/stage15                 # Round 1 合并分支
archive/r01/stage15/s3-gemini     # Round 1 落选归档
```

### Mac mini 管理

| 用途 | 路径 | 规则 |
|------|------|------|
| S4 赛马开发 | `~/Doramagic-racer/` | 赛马期间使用 |
| API 部署 | `~/Doramagic-deploy/` | 发布期间使用 |
| 图谱数据 | `~/Doramagic-data/` | 独立目录 |

**核心规则**：参赛代码和服务代码永远不在同一个 worktree。

## 3.6 里程碑

| 里程碑 | 内容 | 对应赛马 | 验收标准 | 预估 |
|--------|------|---------|---------|------|
| **M0：基础冻结** | contracts + fixtures + 骨架 | Round 0 | schema 可序列化/校验；3 个 fixture repo 可跑 smoke | 2-3 天 |
| **M1：单项目提取可用** | Stage 0/1/1.5/3/3.5 跑通 | Round 1 | 固定 repo 稳定输出；中间文件齐全；1 个 gold case 通过 | 3-4 天 |
| **M2：多项目比较可用** | Phase A/B + fingerprint + compare + synthesis | Round 2+3 | 3-5 项目可生成有意义 diff；ALIGNED/MISSING 可复现 | 5-7 天 |
| **M3：终端 v1** | Skill 编译 + 门控 + 端到端 | Round 4 | OpenClaw 静态校验通过；1 个真实需求从头到尾跑通 | 3-4 天 |
| **M4：双系统 v1** | 领域图谱 + API | Round 5 | API 可按 domain 返回快照；终端断开 API 仍独立工作 | 3-4 天 |

**总预估**：
- **终端 v1**：~14-18 工作日（Round 0-4）
- **双系统 v1**：~18-24 工作日（Round 0-5）

## 3.7 关键路径

```
contracts → extraction.stage0 → stage1 → stage15 → stage3 → stage35
  → fingerprint → compare → synthesis → skill-compiler → validator
  → phase_runner → terminal.cli
```

**不在关键路径上**（可并行或后置）：
- community.harvest（Phase D，可与 Round 1 并行）
- domain-graph（Round 5，不阻塞终端 v1）
- preextract-api（Round 5）

## 3.8 风险管理

| 风险 | 严重度 | 缓解 |
|------|--------|------|
| contracts 定义不准，导致赛马产出无法合并 | **最高** | PM 亲自定义 contracts + 每轮开始前冻结 |
| 赛马选手代码风格差异大 | 高 | ruff 统一格式 + contracts 强约束 + PM 合并时统一 |
| Stage 1.5 Agent Loop 实现复杂度超预期 | 高 | 降级路径已有（回退到 Stage 1）；时间盒 14 小时 |
| Mac mini 开发/部署冲突 | 中 | 分 clone + 分时段 |
| 某轮赛马两方都失败 | 中 | 拆小模块 + 换配对 + PM 下发骨架 |

---

# 第四部分：各模块开发规格

详细的 8 个赛马模块接口规格见独立文档：

**`docs/dev-plan-codex-module-specs.md`**（2000+ 行，含完整 Pydantic models）

以下是摘要索引。

## 4.1 全局约束（所有模块必须遵守）

### 统一返回 Envelope

所有赛马模块返回 `ModuleResultEnvelope[T]`：
- `status`: ok / degraded / blocked / error
- `data`: 模块特定输出
- `metrics`: wall_time_ms / llm_calls / prompt_tokens / completion_tokens / estimated_cost_usd / retries

### 统一错误码

| 错误码 | 含义 |
|--------|------|
| `E_INPUT_INVALID` | 输入字段缺失或类型不合法 |
| `E_UPSTREAM_MISSING` | 上游 artifact 不存在 |
| `E_SCHEMA_MISMATCH` | 输入 schema version 不兼容 |
| `E_TIMEOUT` | 运行超时 |
| `E_RETRY_EXHAUSTED` | 重试后仍失败 |
| `E_BUDGET_EXCEEDED` | token/调用/时间预算超标 |
| `E_NO_CANDIDATES` | discovery 找不到候选 |
| `E_NO_HYPOTHESES` | stage1.5 没有可验证假说 |
| `E_PLATFORM_VIOLATION` | skill 不符合 OpenClaw 规则 |
| `E_UNRESOLVED_CONFLICT` | synthesis/compiler 遇到未解决冲突 |
| `E_VALIDATION_BLOCKED` | validation 给出 BLOCKED |

### 统一文件名（不允许选手修改）

`need_profile.json` / `discovery_result.json` / `hypothesis_list.json` / `hypotheses.jsonl` / `exploration_log.jsonl` / `claim_ledger.jsonl` / `evidence_index.json` / `context_digest.md` / `comparison_result.json` / `synthesis_report.json` / `synthesis_report.md` / `SKILL.md` / `PROVENANCE.md` / `LIMITATIONS.md` / `validation_report.json` / `run_manifest.json`

### 冻结前提

在任何赛马轮开始前，以下必须冻结：artifact schema 版本号、文件命名、共享错误码、`project_fingerprint.json` schema、`platform_rules.json` 语义、fixture 数据集。

## 4.2 赛马模块规格索引

| # | 模块 | 一句话职责 | 关键输入 | 关键输出 | 性能预期 |
|---|------|---------|---------|---------|---------|
| 1 | `extraction.stage1_scan` | 广度扫描 Q1-Q8 + 假说生成 | RepoFacts | findings + hypotheses | <3min, <$0.08/repo |
| 2 | `extraction.stage15_agentic` | 假说驱动深挖 + file:line 证据绑定 | Stage1Output + Budget | claims + exploration_log | <10min, <$0.35/repo |
| 3 | `cross-project.compare` | 三层匹配 + ALIGNED/MISSING/ORIGINAL 标注 | fingerprints[] | CompareSignal[] | <90s, <$0.10 |
| 4 | `cross-project.discovery` | 需求→候选项目 + 搜索覆盖 | NeedProfile | DiscoveryCandidate[] | <5min, <$0.15 |
| 5 | `cross-project.synthesis` | 多源知识综合→选择/排除/冲突 | 提取包+比较+社区 | SynthesisReport | <5min, <$0.20 |
| 6 | `skill-compiler.openclaw` | synthesis→SKILL.md 编译 | SynthesisReport + PlatformRules | SKILL.md + PROVENANCE + LIMITATIONS | <3min, <$0.10 |
| 7 | `platform-openclaw.validator` | 7 项静态校验→PASS/REVISE/BLOCKED | SkillBundle + PlatformRules | ValidationReport | <60s, <$0.03 |
| 8 | `orchestration.phase_runner` | 串起 Phase A-H，支持降级和 REVISE 循环 | raw_input 或 NeedProfile | DeliveryBundle + RunManifest | <30min, <$2.50/run |

## 4.3 共享基础模型（PM 在 Round 0 冻结）

以下 Pydantic models 定义在 `packages/contracts/` 中，所有模块共用：

- `RepoRef` — 仓库引用（repo_id/full_name/url/commit_sha/local_path）
- `EvidenceRef` — 证据引用（file_line/artifact_ref/community_ref）
- `NeedProfile` — 用户需求结构化（raw_input/keywords/intent/search_directions/constraints）
- `KnowledgeAtom` — 知识原子（subject/predicate/object/scope/normative_force/confidence/evidence）
- `ProjectFingerprint` — 项目指纹（code_fingerprint/knowledge_atoms/soul_graph/community_signals）
- `DiscoveryCandidate` — 候选项目（name/url/type/relevance/quick_score/quality_signals）
- `CommunityKnowledge` — 社区知识（skills/tutorials/use_cases）

完整 Pydantic 定义见 `dev-plan-codex-module-specs.md` Section 1.4。

## 4.4 赛马选手必读

每个赛马选手在开始开发前必须阅读：

1. **本手册 Part 1-3**（产品定义 + 架构 + 开发计划）
2. **`dev-plan-codex-module-specs.md`** 中自己负责模块的完整规格
3. **`packages/contracts/`** 中已冻结的 Pydantic models
4. **`data/fixtures/`** 中的测试数据
5. **PM 下发的模块 Brief**（包含本轮特定要求）

不需要阅读：
- 其他选手的代码
- 研究文档（除非 Brief 中特别引用）
- v5.2 产品定义全书（已被本手册取代）

---

# 附录

## A. 已验证的实验结论索引

| 实验 | 结论 | 可复用资产 |
|------|------|-----------|
| WHY 提取 v1-v3 | 输入质量是天花板；两杠杆独立可叠加 | stage0-v2.sh, why-extraction-prompt-v2.md |
| Soul Extractor v0.9 | 42%→96% 有效；跨领域适应性好 | 完整 Stage 0-5 管线 + 5 个 P0 补丁 |
| 跨项目智能 | 公约数/打架/独创可识别 | fingerprint schema, compare 设计 |
| Sim1-3 模拟验证 | 多项目管线 Phase A-H 跑通 | 管线设计 + 交付包模板 |
| Agentic A/B | Stage 1+1.5 互补验证通过 | 5 工具定义 + 假说模板 |
| Knowledge Compiler | 降级为工程任务（1天） | 编译格式规范 |
| 领域图谱三方 | 架构已定（SQLite+Parquet+JSONL） | 存储方案 + 增量更新算法 |

## B. 已有代码资产

| 资产 | 位置 | 行数 | 语言 | 状态 |
|------|------|------|------|------|
| doramagic-claude | Mac mini (原型) | 2,272 | TypeScript | 早期探索，需评估复用 |
| doramagic-codex | Mac mini (原型) | 7,018 | TypeScript | 早期探索，32/32 测试通过 |
| doramagic-python | Mac mini (原型) | ~131 | Python | 脚手架 |
| stage0-v2.sh | 研究脚本 | — | Bash | 已验证，可复用 |
| collect-community-signals.py | 研究脚本 | 310 | Python | 已验证，可复用 |
| extract_repo_facts.py | 研究脚本 | — | Python | 已验证，可复用 |
| validate_extraction.py | 研究脚本 | — | Python | 已验证，可复用 |
| WHY 提取 Prompt v2 | 研究资产 | — | Markdown | 已验证，可复用 |
| 4 维度 Rubric | 研究资产 | — | — | 已验证，可复用 |

## C. 产品哲学术语规范

| 禁止用词 | 推荐用词 |
|---------|---------|
| 错误 | 观测到差异 |
| 漏掉 | 未覆盖 |
| 落后 | 非主流路径 |
| 错误共识 | 高风险共识 |
| 诊断 | 知识位置定位 |
| 健康/不健康 | （不使用，给维度数据） |
| 应该/必须（面向用户） | （不使用，给工具不给建议） |

## D. 参考文档索引

| 文档 | 位置 | 用途 |
|------|------|------|
| V5.2 产品定义全书 | `docs/research/20260315_doramagic_v5_product_definition.md` | 完整产品设计（1140行） |
| 开发上下文简报 | `docs/dev-context-briefing.md` | v5.2 之后的新决策汇总 |
| 多项目管线设计 | `docs/multi-project-pipeline.md` | Phase A-H 详细定义 |
| 领域图谱三方研究 | `research/cross-project-intelligence/domain-map-synthesis.md` | 图谱架构与存储方案 |
| 预提取领域调研 | `research/pre-extraction-domains/` | 6 个领域的选择依据 |
| 工程计划 v1 | `docs/engineering-plan-v1.md` | 原始工程计划（部分已更新） |
