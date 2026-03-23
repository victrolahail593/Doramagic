# Doramagic 产品开发需求文档

> 日期：2026-03-20
> 版本：v1.0
> 目标：指导产品级赛马开发，产出端到端可用的 Doramagic 产品

---

## 1. 产品定位

**一句话**：Doramagic 是运行在 OpenClaw 上的哆啦A梦——用户说一句模糊的烦恼，Doramagic 从开源世界找到最好的作业，提取智慧，锻造一个开袋即食的 AI 道具。

**核心价值**：不教用户做事，给他工具。

**护城河**：WHY + UNSAID 智慧层提取能力（行业空白，永远是第一优先级）。

---

## 2. 用户旅程（端到端）

```
用户输入: "我想做一个记录食物卡路里的 skill"
                    │
                    ▼
           ┌─────────────────┐
           │  Phase A: 需求理解  │  → need_profile.json
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase B: 作业发现  │  → 找到 3-5 个真实开源项目
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase C: 灵魂提取  │  → 每个项目跑 Stage 0-5，提取知识
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase D: 社区采集  │  → 社区踩坑、最佳实践
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase E: 知识综合  │  → 跨项目比较 + 综合决策
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase F: Skill 锻造 │  → 组装 SKILL.md
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase G: 质量门控  │  → 7 项检查，不过则回 Phase F
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Phase H: 交付     │  → SKILL.md + PROVENANCE.md + LIMITATIONS.md
           └─────────────────┘
                    │
                    ▼
用户输出: 一个可以在 OpenClaw 上直接使用的 Skill
```

---

## 3. 产品验收体系

### 3.1 核心验收标准

Doramagic 必须能处理**任意用户需求**。用户随便说一句话，Doramagic 都能跑完全流程交付 Skill。

**验收通过条件**：以下 3 个随机需求全部端到端跑通，输出 SKILL.md + PROVENANCE.md + LIMITATIONS.md。

| # | 输入需求（随机抽取，不可提前准备） | 验证重点 |
|---|--------------------------------|---------|
| 1 | 一个常见领域需求（如个人记账、笔记管理） | 基本流程完整性 |
| 2 | 一个冷门领域需求（如 Ham Radio 日志管理） | 候选项目少时的优雅降级 |
| 3 | 一个模糊需求（如"帮我管理家里的东西"） | 需求理解 + 搜索方向推断能力 |

### 3.2 输出质量验收（每个 Skill 必须满足）

| 维度 | 标准 | 判定方法 |
|------|------|---------|
| **WHY 密度** | SKILL.md 不只有 WHAT（做什么），必须包含 WHY（为什么这样做）和 UNSAID（社区踩坑） | PM 审阅 |
| **溯源完整** | PROVENANCE.md 每条知识可追溯到具体项目的具体文件 | 抽查 3 条验证 |
| **边界诚实** | LIMITATIONS.md 诚实标明不能做什么，不编造能力 | PM 审阅 |
| **平台合规** | SKILL.md 符合 OpenClaw 规则，validator 7 项检查全过 | 自动验证 |
| **部分覆盖诚实** | 只找到 1-2 个项目时，输出明确标注覆盖范围而非假装全面 | PM 审阅 |

### 3.3 系统能力验收

| 能力 | 标准 |
|------|------|
| **独立运行** | 断开预提取 API 时，系统 A 照样完成全流程 |
| **API 加速** | 连接 API 且领域命中时，Phase B 跳过搜索直接获取 bricks，速度明显提升 |
| **暗雷防护** | 遇到"看起来好但实际误导"的项目时，Stage 3.5 能标记警告 |
| **冲突处理** | 多个项目知识矛盾时，标注冲突而非静默忽略 |

### 3.4 不验收的（v1 延后）

- 苏格拉底多轮对话（v1 用一句话输入）
- 回炉改造（v1 不做迭代）
- 热力图可视化
- 多语言支持

---

## 4. 系统架构

### 4.1 双系统

| 系统 | 角色 | 运行位置 | 依赖关系 |
|------|------|---------|---------|
| 系统 A：Doramagic 终端 | 完整独立的知识提取与 Skill 锻造 | OpenClaw 平台 | 不依赖系统 B |
| 系统 B：预提取 API | 静态知识仓库，只读查询 | Mac mini (192.168.1.104) | 独立部署运行 |

**关键原则**：API 是加成不是依赖。断开 API 时系统 A 照常工作。

### 4.2 Phase A-H 管线（系统 A 核心）

| Phase | 功能 | 输入 | 输出 |
|-------|------|------|------|
| A | 需求理解 | 用户原始文本 | need_profile.json |
| B | 作业发现 | need_profile + (可选)API domain bricks | discovery_result.json |
| C | 灵魂提取 | 候选项目列表 | 每个项目的知识卡片 |
| D | 社区采集 | 候选项目的社区信号 | community_knowledge.json |
| E | 知识综合 | 所有项目的知识 + 比较信号 | synthesis_report |
| F | Skill 锻造 | 综合报告 + 平台规则 | SKILL.md + README + PROVENANCE + LIMITATIONS |
| G | 质量门控 | Skill bundle | PASS / REVISE / BLOCKED |
| H | 交付 | 通过验证的 bundle | 最终交付物 |

### 4.3 Stage 0-5 单项目提取管线（被 Phase C 调用）

| Stage | 功能 | 技术 | LLM? |
|-------|------|------|------|
| 0 | 确定性提取 | git clone + repomix + repo_facts.json | 否 |
| 1 | 广度扫描 Q1-Q7 | 规则驱动 + 假说生成 | 否 |
| 1.5 | Agent 深潜 | ReAct 循环，假说驱动读代码 | **是** |
| 2 | 概念/工作流提取 | LLM 提取概念卡+工作流卡 | **是** |
| 3 | 规则提取 | LLM 提取决策规则卡 | **是** |
| 3.5 | 硬验证 | 事实检查 + 追踪性验证 | 否 |
| 4 | 专家叙事合成（可选） | LLM 合成叙事 | **是** |
| 5 | 输出组装 | assemble-output.sh | 否 |

### 4.4 预提取 API 端点（系统 B）

| 端点 | 功能 |
|------|------|
| GET /domains | 列出已预提取领域 |
| GET /domains/{id}/bricks | 领域积木（注入 Stage 0/1 加速） |
| GET /domains/{id}/truth | 领域真相 markdown |
| GET /domains/{id}/atoms | 知识原子查询 |
| GET /domains/{id}/deprecations | 废弃事件 |
| GET /domains/{id}/health/{project} | 项目体检 |

---

## 5. 已有资产（必须复用）

### 5.1 Soul Extractor（已验证，核心资产）

位置：`skills/soul-extractor/`

| 文件 | 功能 | 状态 |
|------|------|------|
| scripts/prepare-repo.sh | git clone + repomix + 社区信号 + repo_facts | **生产就绪** |
| scripts/extract.py | Phase 0-4 LLM 驱动提取 | **已验证（exp07/exp08）** |
| scripts/assemble-output.sh | 最终输出组装 + 验证 | **生产就绪** |
| scripts/extract_repo_facts.py | 确定性事实提取 | **生产就绪** |
| scripts/collect-community-signals.py | GitHub Issue/PR/CHANGELOG 采集 | **生产就绪** |
| scripts/validate_extraction.py | Stage 3.5 硬验证 | **生产就绪** |
| scripts/validate_output.py | 最终输出验证 | **生产就绪** |
| stages/STAGE-*.md | 各阶段 LLM 指令 | **已验证** |

**关键数据**：Soul Extractor 提取质量 42%→96%（benchmark），跨领域适应性好（superpowers + wger）。

### 5.2 赛马模块成果（骨架资产）

位置：`packages/`

| 模块 | 行数 | 测试 | 真实就绪度 | 复用方式 |
|------|------|------|-----------|---------|
| contracts | ~600 | — | 100% | **直接用**，按需扩展 |
| stage0 | 350 | 28 | 90% | **直接用**，补子目录扫描 |
| stage1_scan | 1100 | 46 | 70% | **直接用**，输出质量随 stage0 提升 |
| stage15_agentic | 560 | 6 | 10% | **重写**，接入 LLM + 真实文件读取 |
| discovery | 800 | 13 | 10% | **重写**，接入 GitHub API |
| compare | 440 | 7 | 80% | **直接用**，等上游喂真实 atoms |
| synthesis | 760 | 16 | 70% | **直接用**，补 LLM 语义决策 |
| skill_compiler | 400 | 7 | 60% | **改造**，对接 assemble-output.sh |
| validator | 550 | 11 | 90% | **直接用** |
| phase_runner | 845 | 7 | 20% | **改造**，替换所有 mock 为真实调用 |
| snapshot_builder | 985 | 4 | 70% | **直接用**，泛化领域关键词 |
| api.read | 405 | 9 | 95% | **直接用** |

**总计**：259 个测试全部通过，Pydantic 契约定义完整。

### 5.3 研究结论（设计指导）

| 结论 | 来源 | 应用 |
|------|------|------|
| 证据绑定优先于一切功能扩展 | exp07 (-11分) | Stage 3.5 必须 file:line 锚定 |
| Stage 0 改进比 Prompt 优化 ROI 更高 | WHY 实验 | 优先加强 stage0 |
| Agentic 提取是下一个量级的关键 | WHY 实验 | Stage 1.5 必须接 LLM |
| Knowledge Compiler 按知识类型路由格式 | 5大难点 | 事实→结构化，哲学→叙事 |
| CONTESTED/DIVERGENT 不消解，标注冲突 | 跨项目研究 | 冲突是高价值知识 |
| 部分覆盖是默认模式 | 飞轮研究 | 70%覆盖=完整交付+30%地图 |
| 暗雷检测权重高于正面指标 | 暗雷研究 | 一个暗雷命中可否决高分项目 |
| Sonnet 适合设计，Codex 适合执行 | 赛马数据 | 子代理分工依据 |

---

## 6. 硬性约束（不可违反）

1. **不教用户做事** — 所有输出是工具/信息，不是建议/指令
2. **代码说事实，AI 说故事** — 确定性提取为骨架，LLM 仅做解读
3. **偏向漏报不偏向误报** — 所有不确定场景
4. **冲突是高价值知识** — 标注冲突，不消解冲突
5. **API 是加成不是依赖** — 断开 API 时系统 A 照常工作
6. **吃透 OpenClaw 规则** — Doramagic 适应平台而非反过来
7. **Python 3.9 兼容** — 开发环境约束
8. **无 LLM 的阶段绝不调用 LLM** — Stage 0/1/3.5/5/validator 是确定性的

---

## 7. 产品级赛马规则

### 7.1 与模块赛马的区别

| 维度 | 模块赛马（Round 1-5） | 产品赛马 |
|------|---------------------|---------|
| 交付物 | 单个模块 + 测试 | 端到端可运行的 Doramagic |
| 验收 | 单元测试通过 | 验收场景 1-3 全部跑通 |
| Mock | 允许 mock 上下游 | 不允许 mock，必须真实数据 |
| 范围 | 单一职责 | 全管线集成 |

### 7.2 赛马组织

- **PM**：Claude Opus 4.6（评审 + 编排）
- **选手**：2-3 个 AI 选手，每个独立构建完整产品
- **验收**：PM 用验收场景 1-3 评分
- **合并**：选最优方案，从其他方案挑亮点合入

### 7.3 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 端到端完整性 | 30% | 验收场景能否跑通 |
| 输出质量 | 25% | SKILL.md 的知识密度和准确性 |
| 已有资产复用 | 15% | 是否充分利用赛马成果和 Soul Extractor |
| 代码质量 | 15% | 可维护性、测试覆盖 |
| 性能与成本 | 15% | LLM 调用次数、耗时、token 成本 |

### 7.4 赛马节奏

| 阶段 | 内容 | 预期耗时 |
|------|------|---------|
| Phase 1 | 单项目提取跑通（Stage 0-5 端到端） | 2-3 天 |
| Phase 2 | 多项目管线跑通（Phase A-H 端到端） | 3-4 天 |
| Phase 3 | 预提取 API 集成 + 验收场景全部通过 | 2-3 天 |

---

## 8. 技术选型

| 类别 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.9+ | 兼容开发环境 |
| 包管理 | uv | 快速依赖解析 |
| 测试 | pytest | 已有 259 测试 |
| Lint | ruff | 已配置 |
| API 框架 | FastAPI + Uvicorn | 系统 B 已实现 |
| LLM | Claude API (Opus/Sonnet) + 可选 MiniMax | 按任务复杂度选模型 |
| 代码打包 | repomix | Soul Extractor 已验证 |
| 社区采集 | GitHub API | collect-community-signals.py 已实现 |

---

## 9. 首批预提取领域（系统 B）

| 领域 | 预计项目数 | 预估成本 |
|------|-----------|---------|
| 广义个人财务 | 5-7 | $10-40 |
| 笔记/PKM | 5-7 | $10-40 |
| 私有云基础设施 | 5-7 | $10-40 |
| 健康数据 | 5-7 | $10-40 |
| 信息摄取与内容管理 | 5-7 | $10-40 |
| 智能家居 | 5-7 | $10-40 |

---

## 附录：关键文件索引

```
Doramagic/
├── skills/soul-extractor/          ← 已验证的提取引擎（核心资产）
│   ├── SKILL.md
│   ├── scripts/                    ← prepare-repo.sh, extract.py, assemble-output.sh
│   └── stages/                     ← STAGE-*.md LLM 指令
├── packages/                       ← 赛马模块成果（骨架资产）
│   ├── contracts/                  ← Pydantic 契约定义
│   ├── extraction/                 ← stage0, stage1_scan, stage15_agentic
│   ├── cross_project/              ← discovery, compare, synthesis
│   ├── skill_compiler/             ← compiler
│   ├── platform_openclaw/          ← validator
│   ├── orchestration/              ← phase_runner
│   ├── domain_graph/               ← snapshot_builder
│   └── preextract_api/             ← api.read (FastAPI)
├── data/fixtures/                  ← 测试 fixture 数据
├── research/                       ← 产品研究文档
└── docs/                           ← 开发手册 + 模块规格
```
