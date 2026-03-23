# Doramagic 开发方案参考稿

日期：2026-03-18  
作者角色：Codex 架构参考方案  
适用范围：Doramagic 双系统开发、4 路 AI 协作、赛马式模块实现

## 0. 执行摘要

结论先行：

1. **仓库形态建议采用 Monorepo**，但不是“大一统单应用”，而是“**两个独立可部署应用 + 一组共享 packages/contracts**”。
2. **System A（终端 / OpenClaw Skill）是 v1 关键路径**，必须在没有云端 API 的情况下独立跑通 Stage 0-5 和 Phase A-H。
3. **System B（预提取知识 API）不是 v1 阻塞项**，应设计成静态快照服务，复用同一套 contracts 和 graph snapshot 格式。
4. **赛马机制只用于高歧义、高杠杆模块**，不要把 schema、fixtures、平台规则、目录骨架也拿去赛马。
5. **主实现语言建议 Python**。现有 TS 9k+ 原型应视为“设计素材库”和“CLI/Prompt 参考”，不宜直接作为正式基线。

首个可用版本建议定义为：

- 输入一个用户需求
- 自动完成候选项目发现、多项目提取、综合、Skill 编译、静态校验
- 输出 `SKILL.md + README.md + PROVENANCE.md + LIMITATIONS.md`
- 全流程在本地终端可运行

在这个定义下，API、领域图谱增强、知识健康检查、供应链、错误共识都应作为 **v1.5+ 增强能力**，而不是阻塞首个可用版本的前置条件。

## 1. 仓库结构设计

### 1.1 Monorepo vs 多 Repo 取舍

| 维度 | Monorepo | 多 Repo |
| --- | --- | --- |
| 双系统共享 schema | 原子变更，最优 | 容易漂移 |
| 赛马隔离 | 用 worktree 即可 | 物理隔离更强，但管理更重 |
| 独立部署 | 可通过 `apps/` 分离实现 | 天然支持 |
| 测试夹具复用 | 最方便 | 重复维护 |
| 共享 graph / snapshot 格式 | 最稳定 | 版本协商成本高 |
| 研发启动速度 | 更快 | 初期更慢 |
| 长期边界约束 | 需要 discipline | 天然更硬 |

**推荐：Monorepo。**

原因：

- Doramagic 当前最大的耦合点不是运行时，而是 **artifact contract**。例如 `project_fingerprint.json`、`community_knowledge.json`、`validation_report.json`、`platform_rules.json` 这些结构一旦分仓，很快就会出现契约漂移。
- 赛马模式下会持续产生多个分支、多个 worktree、多个临时实现。Monorepo 更适合用统一 fixtures、统一回归测试、统一评审模板来控复杂度。
- System A 和 System B 虽然独立部署，但它们消费的是同一套知识对象，不应该演化出两套 schema。

多 Repo 只在一个条件下值得考虑：当 API 团队和终端团队变成长期独立组织，且 contracts 已稳定半年以上。当前阶段不满足这个前提。

### 1.2 推荐目录结构

建议目录精确到二级如下：

```text
Doramagic/
├── apps/
│   ├── terminal/
│   └── preextract-api/
├── packages/
│   ├── contracts/
│   ├── orchestration/
│   ├── extraction/
│   ├── cross-project/
│   ├── domain-graph/
│   ├── community/
│   ├── skill-compiler/
│   ├── platform-openclaw/
│   ├── evals/
│   ├── racekit/
│   └── shared-utils/
├── data/
│   ├── fixtures/
│   └── snapshots/
├── skills/
│   ├── templates/
│   └── released/
├── scripts/
│   ├── dev/
│   └── release/
├── tests/
│   ├── integration/
│   └── smoke/
├── reports/
│   ├── races/
│   └── evals/
├── docs/
│   ├── architecture/
│   └── runbooks/
├── research/
│   ├── inputs/
│   └── archived/
└── experiments/
    ├── spikes/
    └── archived/
```

### 1.3 共享模块划分

必须共享，不允许双份实现的内容：

- `packages/contracts`
  - 所有 JSON/MD artifact 的 Pydantic model / JSON Schema
  - schema versioning
  - 序列化、反序列化、兼容层
- `packages/shared-utils`
  - repo I/O、路径工具、日志、budget 计数、token/cost 记录
- `packages/evals`
  - golden fixtures、模块验收器、回归测试装载器
- `packages/platform-openclaw`
  - `platform_rules.json` 解释器
  - `skill_check.py`
  - OpenClaw 兼容性静态检查
- `packages/racekit`
  - 赛马分支创建、worktree 初始化、提交清单、评审模板生成

建议共享但允许延后抽象的内容：

- `packages/orchestration`
- `packages/extraction`
- `packages/cross-project`

不建议共享成基础库的内容：

- `apps/terminal` 的 CLI 展示层
- `apps/preextract-api` 的 HTTP handler / auth / deployment 配置

## 2. 模块划分与依赖图

### 2.1 模块总表

| 模块 | 主要职责 | 输入 | 输出 | 依赖 | 估算行数 | 赛马建议 |
| --- | --- | --- | --- | --- | ---: | --- |
| contracts.artifacts | 定义所有 artifact schema | 产品文档、现有 JSON/MD 约定 | Pydantic models / JSON Schema | 无 | 400-600 | 不赛马 |
| shared-utils.runtime | 日志、budget、路径、缓存、重试 | 配置、运行时上下文 | 通用 helper | contracts | 300-500 | 不赛马 |
| evals.fixtures | 固定 repo fixture、gold set、回归输入 | 既有实验资产 | 可复用测试数据 | contracts | 300-500 | 不赛马 |
| racekit.workspace | worktree、branch、评审模板自动化 | 模块 brief、分支名 | race workspace | shared-utils | 250-400 | 不赛马 |
| extraction.stage0_facts | 基础 repo facts 提取 | 仓库路径 | `repo_facts.json` | contracts, shared-utils | 300-500 | 可单人实现 |
| extraction.stage1_scan | 广泛代码扫描 | 仓库路径、facts | `repo_facts_v2.json` | stage0 | 500-700 | 赛马 |
| extraction.stage15_agentic | Agent Loop 深挖、证据索引 | repo、tool budget、stage1 输出 | hypothesis/evidence/optimized facts | stage1, evals | 900-1400 | 重点赛马 |
| extraction.stage3_cards | Soul Card/Insight Card 构建 | validated facts | `repo_soul.json` | stage15 | 500-700 | 可赛马 |
| extraction.stage35_validate | 社区/代码交叉验证 | repo soul、community refs | `repo_soul_validated.json` | stage3, community | 400-700 | 赛马 |
| community.harvest | GitHub/社区信号抓取归一化 | repo list、query plan | `community_knowledge.json` | contracts | 300-500 | 可赛马 |
| cross-project.discovery | Phase A/B 候选项目发现与筛选 | `need_profile.json` | `discovery_result.json` | community, shared-utils | 400-700 | 赛马 |
| cross-project.fingerprint | 生成 `project_fingerprint.json` | single-project extraction package | fingerprint | stage35 | 400-700 | 不建议赛马 |
| cross-project.compare | 项目比较、ALIGNED/MISSING/DRIFTED | 多个 fingerprint | comparison set / diff matrix | fingerprint | 700-1000 | 重点赛马 |
| cross-project.synthesis | StitchCraft/综合报告生成 | diff matrix、community knowledge | `synthesis_report.md` | compare, community | 600-900 | 重点赛马 |
| skill-compiler.openclaw | 生成 `SKILL.md` 与配套说明 | synthesis report、platform rules | `SKILL.md`, `README.md` | synthesis, platform | 500-800 | 重点赛马 |
| platform-openclaw.validator | Skill 静态校验、错误信息规范化 | skill bundle | `validation_report.json` | contracts, platform rules | 600-900 | 赛马 |
| orchestration.phase_runner | 运行 Phase A-H 与 Stage 0-5 | need profile、repo list | 全流程交付包 | 上述绝大多数模块 | 700-1100 | 重点赛马 |
| apps.terminal.cli | 用户命令入口、日志、产物管理 | CLI args | 交付目录、状态输出 | orchestration | 400-700 | 可单人实现 |
| domain-graph.snapshot_builder | Atom cluster、共识层快照构建 | fingerprints、validated souls | graph snapshot | compare, synthesis | 900-1400 | 后置赛马 |
| apps.preextract-api.read | 快照读取 API | snapshot | query/read API | domain-graph, contracts | 400-700 | 赛马 |
| apps.preextract-api.ingest | 快照入库、刷新、版本切换 | snapshot bundle | served snapshot | domain-graph | 400-700 | 可单人实现 |

### 2.2 ASCII 依赖关系图

```text
[contracts] ----> [shared-utils] ----> [racekit]
     |
     +----> [evals.fixtures]
     |
     +----> [platform-openclaw.validator]

[extraction.stage0_facts]
        |
        v
[extraction.stage1_scan]
        |
        v
[extraction.stage15_agentic] <---- [evals.fixtures]
        |
        v
[extraction.stage3_cards] ----> [extraction.stage35_validate] <---- [community.harvest]
        |                                   |
        +------------------------------+    |
                                           v
                              [cross-project.fingerprint]
                                           |
                                           v
[cross-project.discovery] ----------> [cross-project.compare]
                                           |
                                           v
                              [cross-project.synthesis]
                                           |
                      +--------------------+-------------------+
                      v                                        v
          [skill-compiler.openclaw]              [domain-graph.snapshot_builder]
                      |                                        |
                      v                                        v
          [platform-openclaw.validator]          [apps.preextract-api.ingest]
                      |                                        |
                      v                                        v
             [orchestration.phase_runner] -----> [apps.preextract-api.read]
                      |
                      v
               [apps.terminal.cli]
```

### 2.3 关键路径

**终端 v1 关键路径：**

1. `contracts.artifacts`
2. `evals.fixtures`
3. `extraction.stage15_agentic`
4. `cross-project.fingerprint`
5. `cross-project.compare`
6. `cross-project.synthesis`
7. `skill-compiler.openclaw`
8. `platform-openclaw.validator`
9. `orchestration.phase_runner`
10. `apps.terminal.cli`

**不阻塞终端 v1 的模块：**

- `domain-graph.snapshot_builder`
- `apps.preextract-api.read`
- `apps.preextract-api.ingest`
- 高级健康检查、供应链、错误共识

### 2.4 哪些模块适合赛马

适合赛马的模块特征：

- 算法或 orchestrator 路径不唯一
- prompt/agent flow 有明显设计空间
- 集成成本高，但优秀方案能显著降低后续返工

优先赛马：

- `extraction.stage1_scan`
- `extraction.stage15_agentic`
- `cross-project.compare`
- `cross-project.synthesis`
- `skill-compiler.openclaw`
- `platform-openclaw.validator`
- `orchestration.phase_runner`
- `apps.preextract-api.read`

不适合赛马：

- `contracts.artifacts`
- `evals.fixtures`
- `racekit.workspace`
- `cross-project.fingerprint`
- `platform_rules.json` 维护
- 目录骨架和基础 CI

理由很简单：这些模块更像“规则源”和“共享基础设施”，需要的是统一性，不是多样性。

## 3. 赛马机制详细方案

### 3.1 总原则

赛马不是默认开发模式，而是 **高价值模块的设计竞争机制**。建议采用：

- 1 名固定架构师/评审者：Claude + Sonnet 4.6（本地）
- 3 名轮换选手：
  - Codex + GPT-5.4（本地）
  - Gemini + Gemini 3 Pro（本地）
  - Claude + GLM5（Mac mini）

每个模块由 **2 个选手独立实现**。第 3 个选手不空转，负责：

- 非关键路径模块
- 测试夹具补齐
- Spike / deployment parity 验证
- 下一轮 brief 准备

### 3.2 赛道规划

#### a) 哪些模块放在同一轮赛马

建议按依赖分 6 轮：

**Round 0：非赛马启动轮**

- `contracts.artifacts`
- `evals.fixtures`
- `racekit.workspace`
- 基础 repo bootstrap

**Round 1：单项目提取核心轮**

- `extraction.stage1_scan`
- `extraction.stage15_agentic`

**Round 2：多项目比较核心轮**

- `cross-project.compare`
- `cross-project.discovery`

**Round 3：综合与编译轮**

- `cross-project.synthesis`
- `skill-compiler.openclaw`

**Round 4：校验与总编排轮**

- `platform-openclaw.validator`
- `orchestration.phase_runner`

**Round 5：双系统分叉轮**

- `domain-graph.snapshot_builder`
- `apps.preextract-api.read`

如 Round 1-4 全部顺利，Round 4 结束即可得到首个可用终端版本；Round 5 产出 API 参考实现。

#### b) 选手如何配对

推荐采用 **轮换配对**，不要固定双人组。

| 轮次 | 模块 | 选手 A | 选手 B | 第三人职责 |
| --- | --- | --- | --- | --- |
| Round 1 | `stage1_scan` / `stage15_agentic` | Codex | Gemini | GLM5 做 smoke fixture 与部署脚本 |
| Round 2 | `compare` / `discovery` | Codex | GLM5 | Gemini 做 CLI skeleton |
| Round 3 | `synthesis` / `skill-compiler` | Gemini | GLM5 | Codex 做 sample output diff 与回归夹具 |
| Round 4 | `validator` / `phase_runner` | Codex | Gemini | GLM5 做 Mac mini 兼容验证 |
| Round 5 | `snapshot_builder` / `api.read` | Codex | GLM5 | Gemini 做 ingest admin 和 API smoke |

配对原则：

- **探索型模块**：优先 `Codex vs Gemini`，因为两者思路差异大，能拉开方案空间。
- **平台/部署相关模块**：优先 `GLM5` 参与，因为它运行在未来部署环境上。
- **稳定性/校验模块**：优先让写法更严谨的两方正面对比，不追求“创意差异”，追求“错误收敛”。

#### c) 是否允许重新配对

允许，而且应该允许。

规则：

- 每轮评审后更新模块评分卡
- 若某选手在某类模块上持续获胜，下一轮可让其转去更难模块
- 同一模块若重赛，优先换配对，不要原样重打

#### d) 总共需要几轮赛马

建议：

- **到终端首个可用版本：4 个正式赛马轮 + 1 个非赛马启动轮**
- **到双系统参考版本：5 个正式赛马轮 + 1 个非赛马启动轮**

### 3.3 赛马规则

#### a) 交付物标准

每位选手每次交付必须包含：

1. 模块代码
2. 单元测试
3. 最少 1 个基于 fixture 的集成测试
4. 模块 `README.md`
5. `DECISIONS.md`，写明关键设计选择、已知缺陷、未覆盖项

如果是用户可见模块，还必须附：

- 样例输入
- 样例输出
- 失败场景说明

#### b) 时间限制

建议时间盒：

- 中小模块：6-8 小时
- 核心模块：10-14 小时
- 超过 14 小时未形成可评审交付，视为本轮失败，不继续延长

原因：赛马要比较的是方案质量，不是无限堆时间后的局部修补能力。

#### c) 选手是否能看到对方代码

建议 **完全隔离直到评审结束**。

选手可以看到：

- 同一份模块 brief
- 同一份 contracts
- 同一份 fixtures
- 同一份验收标准

选手不可以看到：

- 对手 branch
- 对手中间实现
- 对手评审草稿

这样才能真正比较方案，而不是比较“谁改别人代码更快”。

#### d) 如果两个选手都做得不好

不要硬选。

处理顺序：

1. 架构师写失败复盘，明确失败属于“spec 不清”还是“实现不佳”
2. 缩小模块边界，拆成更小赛道
3. 冻结新的验收 fixture
4. 更换配对，开启重赛
5. 必要时由架构师先下发骨架 contract，再进入下一轮

### 3.4 评审标准

建议总分 100，按以下维度打分：

| 维度 | 权重 | 说明 |
| --- | ---: | --- |
| Contract 正确性 | 25 | 是否严格满足输入输出 schema |
| 可验证性 | 20 | 是否易测、是否保留 trace/provenance |
| 集成适配度 | 20 | 是否便于接入后续模块 |
| 代码清晰度 | 15 | 结构、命名、错误处理是否稳 |
| 性能与成本 | 10 | token、I/O、运行时成本是否合理 |
| 运维稳定性 | 10 | 重试、超时、幂等、日志是否完整 |

评审结果只有 4 种：

1. 选 A
2. 选 B
3. 合并 A+B
4. 都不要，重做

#### 评审报告模板

```text
# Race Review: <round>/<module>

## Result
- Winner: A | B | Merge | Reject

## Score
- Contract correctness:
- Verifiability:
- Integration fit:
- Code clarity:
- Performance/cost:
- Operational stability:

## Strengths
- A:
- B:

## Weaknesses
- A:
- B:

## Merge decision
- Keep from A:
- Keep from B:
- Drop:

## Required follow-up
- [ ] ...
- [ ] ...
```

### 3.5 合并策略

#### a) 选中方案后如何集成

建议流程：

1. 选手代码保留在各自 `race/` 分支
2. 架构师从获胜分支 `cherry-pick` 或 `merge --squash` 到 `integration/<phase>`
3. 若是 A+B 合并，由架构师在独立 `merge/<round>/<module>` 分支完成
4. 合并完成后立即跑模块回归 + 一条上游/下游 smoke

不建议直接把 racer 分支 merge 到 `main`。应始终先进入 `integration`，再按 phase 进入 `main`。

#### b) 落选方案如何归档

建议保留三样东西：

1. 原分支
2. 评审报告
3. 如有价值的片段清单

归档位置：

- git 分支：`archive/rXX/<module>/<agent>`
- 文档：`reports/races/rXX-<module>-review.md`

#### c) 合并后的回归测试

每次合并后至少跑 4 层：

1. schema / static validation
2. 模块 unit tests
3. fixture-based integration test
4. 端到端 smoke：从 `need_profile.json` 到 skill bundle

### 3.6 分支与工作空间

#### a) 本地工作空间隔离

建议用 git worktree，而不是多个临时 clone。

目录规范：

```text
.worktrees/
├── r01-stage15-codex/
├── r01-stage15-gemini/
├── r02-compare-codex/
├── r02-compare-glm5/
└── merge-r02-compare/
```

理由：

- 切换快
- 与主仓共享对象库
- 更容易统一清理

#### b) 分支命名规范

```text
main
integration/phase-1
integration/phase-2
race/r01/stage15/codex
race/r01/stage15/gemini
merge/r01/stage15
archive/r01/stage15/codex
```

#### c) Mac mini 的管理方式

Mac mini 上的 Claude + GLM5 既是选手又是未来部署目标，因此要 **逻辑隔离**：

- 开发 clone：`Doramagic-racer`
- 部署 clone：`Doramagic-deploy`
- 快照数据目录与运行日志目录独立
- 赛马窗口内不做 API 发布
- 发布窗口内不跑重型 benchmark

核心规则：**不要把“正在参赛的代码”和“正在提供服务的代码”放在同一个 worktree。**

### 3.7 赛马日历

建议日历如下：

| 阶段 | 内容 | 建议时长 |
| --- | --- | --- |
| Round 0 | bootstrap、contracts、fixtures | 2-3 天 |
| Round 1 | stage1/stage1.5 | 2-3 天 |
| Review 1 | 评审、合并、回归 | 0.5-1 天 |
| Round 2 | discovery/compare | 2-3 天 |
| Review 2 | 评审、合并、回归 | 0.5-1 天 |
| Round 3 | synthesis/compiler | 2-3 天 |
| Review 3 | 评审、合并、回归 | 0.5-1 天 |
| Round 4 | validator/phase runner | 2-3 天 |
| Review 4 | 评审、回归、出首个终端版本 | 1 天 |
| Round 5 | snapshot/API | 2-3 天 |
| Review 5 | API 集成与双系统 smoke | 0.5-1 天 |

整体预估：

- **终端首个可用版本**：12-16 个工作日
- **双系统参考版本**：18-24 个工作日

前提：

- 不新增范围
- 现有实验资产可直接转为 fixture
- 架构师持续做强约束评审，不让模块无限返工

## 4. 技术选型建议

### 4.1 编程语言

推荐：

- **主语言：Python 3.12+**
- 辅助：Bash 仅用于 repo prep / wrapper
- 暂不建议把 TypeScript 继续作为主实现语言

原因：

1. 既有工程计划和 Session 30 已明确 Python 更适合当前生态。
2. 多数核心问题是数据处理、artifact 编排、schema 校验、agent orchestration，不是前端体验。
3. 现有 TS 原型是 valuable reference，但不再匹配“双系统 + 共享 contracts + 静态知识 API”的新边界。

对旧原型的建议：

- `doramagic-codex`：提炼 CLI 交互、日志格式、提示词经验，不直接继承代码结构
- `doramagic-claude`：提炼早期流程设计和 sample prompt
- `doramagic-python`：可放弃，仅保留脚手架价值

### 4.2 云端 API 框架

推荐：

- **FastAPI + Pydantic + Uvicorn**

原因：

- API 很轻，主要是读取静态快照和少量管理接口
- 与 contracts 层天然一致
- 测试和 schema 文档生成成本低

不建议：

- Django，过重
- Flask，schema 与校验纪律不够强

### 4.3 包管理、任务与环境

推荐：

- `uv` 管理 Python 依赖与虚拟环境
- `pytest` 作为主测试框架
- `ruff` 做 lint + format
- `mypy` 做关键包静态检查
- `just` 或 `make` 组织常用任务

### 4.4 测试框架与 CI 策略

测试分 4 层：

1. unit tests
2. fixture integration tests
3. end-to-end smoke
4. golden regression tests

CI 建议：

- `pull_request` 跑 unit + contract + targeted integration
- `integration/*` 分支额外跑 e2e smoke
- `main` 分支跑 release-grade full regression

### 4.5 OpenClaw Skill 工具链

建议形成统一命令面：

```text
uv run doramagic extract-single
uv run doramagic compile-skill
uv run doramagic validate-skill
uv run doramagic run-phase
uv run doramagic build-snapshot
uv run doramagic serve-api
```

OpenClaw 相关必须具备：

- `platform_rules.json` 作为唯一平台规则源
- `skill_check.py` 作为静态规则检查器
- 固定的 sample skill fixture
- 至少一条 OpenClaw smoke case，覆盖工具名映射与 frontmatter 合法性

## 5. 里程碑与验收

### 5.1 Phase 划分

#### Phase 0：基础设施冻结

目标：

- repo 结构落地
- contracts 初版冻结
- fixture 与 racekit 建好

交付物：

- `packages/contracts`
- `packages/evals`
- `packages/racekit`

验收标准：

- 主要 artifact schema 都可被序列化/校验
- 能一键创建赛马 worktree
- 至少 3 个 fixture repo 可跑 smoke

对应赛马：

- Round 0 之前或 Round 0 内完成，不赛马

#### Phase 1：单项目提取可用

目标：

- 跑通 Stage 0 / 1 / 1.5 / 3 / 3.5

交付物：

- 提取 CLI
- evidence / hypothesis / claim ledger
- validated repo soul

验收标准：

- 在固定 repo 上稳定输出
- Stage 1.5 的中间文件齐全
- 至少 1 个 gold case 达到可接受质量

对应赛马：

- Round 1

#### Phase 2：多项目比较可用

目标：

- 跑通 Phase A/B/C/D/E 的主要数据流

交付物：

- discovery result
- fingerprint
- compare diff
- synthesis report

验收标准：

- 3-5 个项目可生成有意义 diff
- `ALIGNED/MISSING/ORIGINAL/DRIFTED` 可复现

对应赛马：

- Round 2 + Round 3

#### Phase 3：Skill 编译与终端交付

目标：

- 输出完整 skill bundle

交付物：

- `SKILL.md`
- `README.md`
- `PROVENANCE.md`
- `LIMITATIONS.md`
- `validation_report.json`

验收标准：

- 能通过 OpenClaw 静态校验
- 至少 1 个真实需求可从头到尾跑通

对应赛马：

- Round 3 + Round 4

#### Phase 4：预提取图谱与 API

目标：

- 生成 graph snapshot
- 提供静态 read API

交付物：

- snapshot bundle
- query/read API
- ingest/refresh script

验收标准：

- API 可按 domain/version 返回 snapshot 内容
- terminal 可选接入 API，但断开 API 仍可独立工作

对应赛马：

- Round 5

### 5.2 关键阻塞点

最容易卡住整个计划的不是模型能力，而是以下 5 点：

1. artifact schema 没有冻结
2. Stage 1.5 中间文件和 evidence binding 不稳定
3. `project_fingerprint.json` 定义过松，导致 compare 漂移
4. OpenClaw 平台规则没有形成唯一真源
5. 赛马评审没有统一模板，导致“合并”变成随意拼接

## 6. 风险与缓解

### 6.1 赛马成本 vs 质量收益

赛马的收益高于成本，只在这三类模块成立：

- 路径选择明显影响后续 3 个以上模块
- prompt / agent loop 设计空间大
- 直接影响平台适配与最终交付质量

控制成本的方法：

- 只赛马 6-8 个核心模块
- 每轮必须时间盒
- 失败就重拆模块，不要继续加时间

### 6.2 4 路集成风险

风险来源：

- 3 个选手 + 1 个架构师的代码风格、抽象层级、错误处理方式不同
- 不同模块若同时修改 contracts，极易冲突

缓解：

- contracts 只允许在非赛马基础分支改动
- 每轮开始前冻结本轮 contract
- 每轮结束只由架构师执行合并
- 所有模块都必须通过 fixture-based contract test

### 6.3 早期 TS 原型复用 vs 重写

建议：**以重写为主，以抽取经验为辅。**

可复用：

- CLI 命令设计
- 输出目录组织
- prompt 与日志形式
- 某些验证器逻辑

不建议直接复用：

- 核心 orchestrator
- 内部数据结构
- 模块边界

原因：当前架构已经从“单系统实验原型”升级为“双系统 + 共享 contract + 赛马协作开发”，旧 TS 代码的边界假设已经过时。

### 6.4 Mac mini 资源冲突

风险：

- 既做 GLM5 racer，又做 API 部署，会争抢 CPU、磁盘、端口与日志目录

缓解：

- 赛马与部署分 clone
- benchmark、snapshot build、API serve 分时段执行
- 用固定端口和固定日志路径
- 每轮评审前暂停 Mac mini 上所有非必要长跑任务

## 7. 推荐落地顺序

建议严格按以下顺序启动：

1. 建 Monorepo 骨架
2. 冻结 contracts、fixtures、racekit
3. 用 Round 1 打通单项目提取核心
4. 用 Round 2/3 打通 compare -> synthesis -> compiler
5. 用 Round 4 把 terminal 端到端跑通
6. 最后再做 snapshot 与 API

如果顺序反过来，例如先做 API、先做领域图谱、先做健康检查，结果通常会是：系统看起来更完整，但首个真正可用的交付更晚。

## 8. 最终建议

最稳的开发策略不是“把所有研究成果一次性工程化”，而是：

- 先把 **System A 的核心链路** 做成可交付、可回归、可赛马
- 再把 **System B** 做成共享 contracts 之上的静态加速层

这会保住 Doramagic 当前最重要的两件事：

1. 终端产品始终独立成立
2. 预提取 API 始终只是加速器，而不是单点依赖

在这个前提下，赛马机制才能成为质量放大器，而不是复杂度放大器。
