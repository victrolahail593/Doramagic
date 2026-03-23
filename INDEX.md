# Doramagic 项目索引

> **定位**：OpenClaw 生态中的哆啦A梦——不教用户做事，给他工具
> **品牌触发**：`/dora`
> **核心护城河**：灵魂提取引擎（WHY + UNSAID 智慧层提取），行业空白
> **当前状态**：心脏已建（单项目提取引擎），身体待建（Phase A/B/E/F/G/H）

---

## 产品设计之魂

> 哆啦A梦从不教大雄怎么做事，而是从口袋里掏出道具让大雄自己解决问题。
> Doramagic 是**知识魔法**（武装用户），而非方法论魔法（约束用户）。

**核心定位**：抄作业高手（非从零构建），有立场的专家（非信息搬运工）
**架构原则**：代码说事实，AI 说故事（确定性提取为骨架，LLM 仅做解读）
**硬性约束**：必须吃透 OpenClaw 规则，Doramagic 适应平台而非反过来

---

## 代码规模（截至 2026-03-21）

| 分类 | 数量 |
|------|------|
| 产品代码（Python） | ~17,033 行 |
| 测试代码 | ~7,613 行 |
| 合计 | ~24,646 行 |
| Pydantic 模型 | 76 个 |
| Python 源文件 | 50 个 |
| 测试文件 | 18 个 |
| 灵魂积木 | 89 块（12 JSONL 文件） |

---

## 目录结构

```
Doramagic/
│
├── skills/                                # ★ Skill 实现（交付物）
│   ├── doramagic/                         # ★★ 正式版 Doramagic Skill (v1.1)
│   │   ├── SKILL.md                       # Skill 定义（/dora 触发，必读）
│   │   ├── cards/                         # 知识卡片输出
│   │   └── scripts/                       # 脚本工具
│   ├── soul-extractor/                    # 历史版：Soul Extractor v0.9 + P0补丁
│   ├── skill-forge/                       # 元技能：Skill 开发框架
│   ├── doramagic-s1/s2/s3/s4/            # 赛马选手版本（归档）
│   ├── released/                          # 已发布 Skill（归档）
│   └── templates/                         # Skill 模板
│
├── packages/                              # ★ Python 核心包（~17K 行）
│   ├── extraction/                        # 提取引擎（Stage 0/1/1.5）
│   ├── contracts/                         # 数据契约（Pydantic 模型）
│   ├── cross_project/                     # 跨项目分析（discovery/compare/synthesis）
│   ├── skill_compiler/                    # Knowledge Compiler
│   ├── platform_openclaw/                 # OpenClaw 平台集成（validator）
│   ├── orchestration/                     # Phase Runner（全管线编排）
│   ├── community/                         # 社区信号采集（DSD）
│   ├── domain_graph/                      # 快照构建器
│   ├── shared_utils/                      # 共享工具
│   ├── racekit/                           # 赛马基础设施
│   ├── evals/                             # 评估框架
│   ├── preextract_api/                    # 预提取 API
│   └── doramagic_product/                 # 产品级 pipeline（实验）
│
├── bricks/                                # ★ 灵魂积木（89 块，12 框架）
│   ├── BRICK_INVENTORY.md                 # 积木清单（L1/L2 共 89 块）
│   ├── python_general.jsonl               # Python 通用积木
│   ├── django.jsonl                       # Django 框架积木
│   ├── fastapi_flask.jsonl
│   ├── react.jsonl
│   ├── go_general.jsonl
│   ├── domain_finance.jsonl               # 广义财务领域
│   ├── domain_health.jsonl                # 健康数据领域
│   ├── domain_pkm.jsonl                   # PKM 领域
│   ├── domain_private_cloud.jsonl         # 私有云领域
│   ├── domain_info_ingestion.jsonl        # 信息摄取领域
│   └── home_assistant.jsonl
│
├── races/                                 # 赛马成果（R05/R06）
│   ├── r05/                               # Round 0-5：模块赛马（259 测试通过）
│   └── r06/                               # ★ Round 6：全面落地赛马（120/120）
│       ├── agentic/                       # Race A: Agentic 提取
│       ├── bricks/                        # Race B: 积木制作
│       ├── compiler/                      # Race C: Knowledge Compiler
│       ├── confidence/                    # Race D: 置信度+DSD
│       ├── injection/                     # Race E: 积木注入
│       └── runner/                        # Race G: Phase Runner
│
├── runs/                                  # ★ 实际运行记录
│   ├── 20260320-*/                        # 本机测试运行
│   ├── run-20260320-*/                    # 端到端测试（python-dotenv）
│   └── openclaw/                          # Mac mini OpenClaw 真实跑单
│       ├── family-recipe-manager/         # TandoorRecipes 提取（验证案例）
│       └── wifi-password-202603201657/    # wifi 工具 Skill
│
├── apps/                                  # 应用层
│   ├── terminal/                          # Terminal M3 v1（CLI 工具）
│   └── preextract-api/                    # 预提取 REST API
│
├── data/                                  # 数据与 Fixtures
│   ├── fixtures/                          # 测试 Fixtures（sim2/sim3 系列）
│   └── snapshots/                         # 快照数据（calorie-tracking 等）
│
├── experiments/                           # 实验迭代记录（exp01-exp08）
│   ├── exp01-v04-minimax/                 # MiniMax 初版（42%）
│   ├── exp05-v08-superpowers/             # v0.8 最佳实践
│   ├── exp07-v09-superpowers-usertest/    # wger 适应性测试（Traceability 100%）
│   └── exp08-v09patch-superpowers/        # ★ P0补丁后（96%）
│
├── research/                              # 研究文档（28 个主题）
│   ├── product-review-2026-03-11/         # ★ v2 产品定义（决策溯源）
│   ├── product-definition-v3/             # v3 产品定义
│   ├── soul-lego-bricks/                  # 积木粒度研究
│   ├── confidence-system/                 # 置信度体系研究
│   ├── cross-project-intelligence/        # ★ 跨项目智能（第二飞轮）
│   ├── pre-extraction-domains/            # 6个首批预提取领域研究
│   ├── agentic-extraction/                # Agentic 提取研究
│   ├── agentic-validation/                # 验证体系研究
│   ├── ai-knowledge-consumption/          # AI 知识消费格式研究
│   ├── soul-decomposition/                # 知识分层研究
│   ├── soul-extractor-review/             # Soul Extractor 评审
│   ├── glm5/                              # GLM-5 优秀实践
│   ├── sim2-calorie/                      # Sim2 热量追踪模拟
│   ├── sim3-flight/                       # Sim3 航班模拟
│   └── papers/                            # 学术论文
│
├── docs/                                  # 开发文档
│   ├── doramagic-dev-manual-v5.3.md       # ★ 开发手册 v5.3（必读）
│   ├── dev-context-briefing.md            # 开发上下文简报
│   ├── dev-plan-codex-module-specs.md     # 模块规格说明
│   ├── PRODUCT_MANUAL.md                  # 产品手册
│   ├── brainstorm/                        # 头脑风暴记录（早期）
│   └── plans/                             # 实现计划
│
├── reports/                               # 报告汇总
│   ├── races/                             # 赛马评审报告（r01-r06）
│   └── evals/                             # 评估报告
│
├── tests/                                 # 测试
│   ├── integration/                       # 集成测试
│   └── smoke/                             # 冒烟测试
│
├── scripts/                               # 工具脚本
│   ├── dev/                               # 开发辅助脚本
│   └── release/                           # 发布脚本
│
├── _deprecated_variants/                  # 已归档变体（Gemini/GLM5 版本）
├── doramagic.py                           # ★ 主入口（Skill 形态）
├── doramagic_sonnet.py                    # Sonnet 变体（97分，WHY最深）
├── doramagic_gemini.py                    # Gemini 变体（精简版）
├── models.json                            # 模型无关架构配置
├── platform_rules.json                    # OpenClaw 平台规则
├── pyproject.toml                         # Python 项目配置
└── Makefile                               # 常用命令
```

---

## 核心能力：产品管线

### 已建成（Phase C — 单项目灵魂提取）

| Stage | 名称 | 产出 |
|-------|------|------|
| 0.5 | 积木查询 | 框架公共知识锚定 |
| 1 | 鹰眼扫描 | repo_profile + soul（WHY/UNSAID） |
| 1.5 | Agentic 提取 | 动态代码探索（two-call pattern） |
| 2 | 概念+工作流卡 | CC/WF 卡片 |
| 3 | 规则+社区陷阱 | DC/TC 卡片 |
| 3.5 | 置信度+DSD | 证据链标注+确定性8项检查 |
| 4 | Knowledge Compiler | 按类型路由编译（事实→结构/哲学→叙事/踩坑→警告） |
| 4.5 | 专家叙事合成 | 因果链+踩坑故事 |
| M | 模块地图 | 架构分工图 |
| C | 社区智慧 | 结构性痛点根因 |
| F | 组装输出 | CLAUDE.md + .cursorrules + advisor-brief.md |

### 待建（身体部分）

| Phase | 名称 | 状态 |
|-------|------|------|
| A | 需求理解（自然语言 → need_profile） | ❌ 未建 |
| B | 作业发现（自动 GitHub 搜索） | ❌ 未建 |
| E | 跨项目综合 | ⚠️ 代码已有（cross_project 包），未接入 |
| F+G+H | Skill 编译+门控+交付 | ⚠️ 代码已有（skill_compiler+orchestration），未接入 |
| System B | 预提取 API | ⚠️ stub 已有 |

---

## 灵魂积木系统

- **总量**：89 块（15 个 L1 框架级 + 74 个 L2 模式级）
- **覆盖**：Python 通用、Django、FastAPI/Flask、React、Go、6 个垂直领域
- **Failure Bricks**：17 块（占比 19.1%，防踩坑用）
- **文件**：`bricks/*.jsonl`，格式：JSONL（每行一块积木）

---

## 技术架构亮点

| 特性 | 说明 |
|------|------|
| 模型无关 | capability_router.py + llm_adapter.py + models.json |
| 证据绑定 | EvidenceTag + file:line 来源追踪 |
| 置信度四级 | SUPPORTED / CONTESTED / WEAK / REJECTED |
| DSD 检测 | 8 项确定性暗雷指标，WARNING 不 BLOCKING |
| 赛马机制 | namespace 隔离，PM 评审，120/120 测试通过 |

---

## 实验迭代历史

| 版本 | 目录 | 关键成果 |
|------|------|---------|
| v0.4 | exp01-v04-minimax | Baseline（42%） |
| v0.5-0.6 | exp02/03 | 社区信号 + 规则卡 |
| v0.7 | exp04 | 验证闭环基础设施 |
| v0.8 | exp05 | WHY 层叙事合成 |
| v0.9 | exp06/07 | 三路分离 + wger 适应性（100% traceability） |
| v0.9+P0 | exp08 | **5个P0补丁（42%→96%）** |

---

## 赛马战绩（R06 全面落地）

| 选手 | 特长 | 核心贡献 |
|------|------|---------|
| S1-Sonnet | WHY 最深，连续最强 | 全部赛道胜出（agentic/compiler/confidence/injection/runner） |
| S2-Codex | 框架最健壮 | assemble_output.py、extract_facts.py 进入正式版 |
| S3-Gemini | 最精简 | 部分竞争 |
| S4-GLM5 | 知识卡片多 | bricks 制作（89块） |

---

## 重要文档快速导航

| 文档 | 路径 | 用途 |
|------|------|------|
| 开发手册 v5.3 | `docs/doramagic-dev-manual-v5.3.md` | ★ Session 启动必读 |
| v2 产品定义 | `research/product-review-2026-03-11/doramagic-v2-product-definition.md` | 产品哲学溯源 |
| Skill 定义 | `skills/doramagic/SKILL.md` | /dora 触发流程 |
| 积木清单 | `bricks/BRICK_INVENTORY.md` | 积木全量索引 |
| 产品手册 | `docs/PRODUCT_MANUAL.md` | 用户使用指南 |
| R06 工作日志 | `races/r06/R06_WorkLog.md` | 赛马决策记录 |

---

## 同步说明

- **本机路径**：`~/Documents/vibecoding/Doramagic/`
- **Mac mini 路径**：`~/Doramagic-racer/`（内容完全同步）
- **OpenClaw 已部署**：`~/.openclaw/skills/soul-extractor/` + symlink `dora`
- **最后同步**：2026-03-21
- **同步命令**：`rsync -avzu --exclude='.venv' --exclude='__pycache__' --exclude='.claude/' tangsir@192.168.1.104:~/Doramagic-racer/ ~/Documents/vibecoding/Doramagic/`
