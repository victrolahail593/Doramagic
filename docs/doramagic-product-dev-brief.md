# Doramagic 产品开发 Brief

> **用途**：本文档是产品级赛马的完整 Brief。选手只需读此文档即可理解产品并完成开发。
> 日期：2026-03-20
> PM：Claude Opus 4.6

---

## 第一部分：理解产品

### 1.1 Doramagic 是什么

Doramagic 是运行在 OpenClaw 平台上的 AI 道具锻造师。

**类比**：哆啦A梦。大雄遇到烦恼，哆啦A梦从口袋里掏出道具。Doramagic 就是那个口袋——用户说出模糊需求，Doramagic 从开源世界找到最好的"作业"，提取其中的智慧，锻造出一个开袋即食的 AI 道具（OpenClaw Skill）。

**核心哲学**：**不教用户做事，给他工具。** Doramagic 不输出建议、教程、方法论，它输出可以直接使用的工具。

### 1.2 用户是谁

OpenClaw 平台的开发者。他们需要一个 Skill（AI 道具），但不想从零开始——世界上已经有人做过类似的事，Doramagic 帮他们找到这些"前辈的作业"，提取精华，锻造成适合 OpenClaw 平台的道具。

### 1.3 用户旅程

```
用户: "我想做一个管理家庭菜谱的 skill"
           │
           ▼
   Doramagic 理解需求
           │
           ▼
   去 GitHub 搜索相关开源项目
   （找到 recipe-manager, meal-planner, kitchen-helper 等 3-5 个项目）
           │
           ▼
   逐个提取知识（clone → 扫描代码 → LLM 深度分析）
   提取的不只是 WHAT（这个项目做了什么），
   更重要的是 WHY（为什么这样设计）和 UNSAID（社区踩过的坑）
           │
           ▼
   跨项目比较和综合
   （3 个项目都用了 JSON 存储 → 共识；
    1 个用了 SQLite 另外 2 个用 JSON → 标注冲突，不替用户决策）
           │
           ▼
   锻造 Skill（组装 SKILL.md，适配 OpenClaw 平台规则）
           │
           ▼
   质量门控（7 项检查：一致性、完整性、追溯性、平台合规、冲突解决、许可证、暗雷扫描）
           │
           ▼
用户得到:
  - SKILL.md     （可直接在 OpenClaw 使用的道具）
  - PROVENANCE.md（每条知识来自哪个项目的哪个文件）
  - LIMITATIONS.md（诚实标明能力边界）
```

### 1.4 Doramagic 的核心价值——WHY 和 UNSAID

普通的代码分析工具能告诉你一个项目"做了什么"（WHAT）。Doramagic 的独特价值在于提取两层更深的知识：

- **WHY（为什么这样设计）**：比如"为什么用 JSON 而不是数据库存储菜谱？"——因为单机 Skill 不需要并发访问，JSON 够用且零依赖。这种设计理由藏在代码注释、PR 讨论、commit message 里，不读代码根本不知道。

- **UNSAID（没人明说但用过才知道的坑）**：比如"菜谱名不要用中文做文件名，macOS 和 Linux 的文件系统编码不一致会出 bug"——这种经验藏在 Issue 讨论和社区帖子里。

这两层知识是 Doramagic 的护城河。如果只输出 WHAT，那跟 GitHub 搜索没区别。

### 1.5 九条硬性约束

开发过程中不可违反：

1. **不教用户做事** — 所有输出是工具/信息，不是建议/指令
2. **代码说事实，AI 说故事** — 确定性提取（代码扫描、文件解析）为骨架，LLM 仅做解读和综合
3. **偏向漏报不偏向误报** — 宁可少说，不可说错
4. **冲突是高价值知识** — 多项目知识矛盾时，标注冲突，不替用户消解
5. **API 是加成不是依赖** — 预提取 API 断开时，Doramagic 照样完成全流程
6. **吃透 OpenClaw 规则** — Doramagic 适应平台，不是反过来
7. **无 LLM 的阶段绝不调用 LLM** — Stage 0/1/3.5/5/validator 是确定性的
8. **部分覆盖是诚实的** — 只找到 1-2 个项目时，诚实标注覆盖范围，不编造全面性
9. **管线通用，知识领域特定** — Phase A-H 流程不随领域变化，只有提取出的知识内容随领域变化

---

## 第二部分：系统架构

### 2.1 双系统架构

```
┌─────────────────────────────────────────────────┐
│              系统 A：Doramagic 终端               │
│        （完整独立的知识提取与 Skill 锻造）         │
│                                                  │
│  用户需求 → Phase A→B→C→D→E→F→G→H → Skill 交付  │
│                                                  │
│  ┌──────────┐                                    │
│  │ 可选连接  │←── 有则加成（+20% 质量），无则独立  │
│  └────┬─────┘                                    │
└───────┼──────────────────────────────────────────┘
        │ API 查询
        ▼
┌─────────────────────────────────────────────────┐
│           系统 B：预提取云端 API                  │
│         （静态知识仓库，只读查询）                 │
│                                                  │
│  存储已预提取的领域知识（bricks/atoms/truth）     │
│  运行在 Mac mini (192.168.1.104)                 │
│  6 个端点：/domains, /bricks, /truth, /atoms...  │
└─────────────────────────────────────────────────┘
```

**本次开发重点是系统 A。** 系统 B 的 api.read 已在赛马中完成，可直接部署。

### 2.2 Phase A-H 主管线

| Phase | 名称 | 做什么 | 需要 LLM? | 输出 |
|-------|------|--------|----------|------|
| A | 需求理解 | 解析用户一句话为结构化需求 | 是 | need_profile.json |
| B | 作业发现 | 搜索 GitHub 找相关开源项目 | 否（API调用） | discovery_result.json |
| C | 灵魂提取 | 对每个项目跑 Stage 0→5 提取管线 | 是（Stage 1.5-4） | 知识卡片集 |
| D | 社区采集 | 收集 GitHub Issue/PR/CHANGELOG 中的社区经验 | 否（脚本） | community_knowledge.json |
| E | 知识综合 | 跨项目比较 + 综合决策报告 | 部分（决策理由） | synthesis_report |
| F | Skill 锻造 | 按平台规则组装 SKILL.md | 是（叙事合成） | SKILL.md 等 |
| G | 质量门控 | 7 项自动检查 | 否 | PASS/REVISE/BLOCKED |
| H | 交付 | 打包最终输出 | 否 | delivery bundle |

### 2.3 Stage 0-5 单项目提取管线（Phase C 内部）

每个候选项目都跑一遍这个管线：

| Stage | 名称 | 做什么 | 技术 |
|-------|------|--------|------|
| 0 | 准备 | git clone → repomix 打包 → 确定性事实提取 | shell + python 脚本 |
| 1 | 广度扫描 | 回答 7 个核心问题（Q1-Q7）+ 生成假说 | 规则驱动（无 LLM） |
| 1.5 | Agent 深潜 | 基于假说用 LLM 读代码验证 | **LLM + ReAct** |
| 2 | 概念提取 | 提取概念卡 + 工作流卡 | **LLM** |
| 3 | 规则提取 | 提取决策规则卡（含 UNSAID） | **LLM** |
| 3.5 | 硬验证 | 事实检查 + 追溯性验证 | 规则驱动（无 LLM） |
| 4 | 叙事合成 | 合成专家级知识传递文档（可选） | **LLM** |
| 5 | 输出组装 | 生成 CLAUDE.md / SKILL.md | shell 脚本 |

---

## 第三部分：已有资产（必须复用）

### 3.1 Soul Extractor — 核心提取引擎（已验证）

位置：`skills/soul-extractor/`

这是 Doramagic 最核心的资产。它已经在真实项目上验证过（benchmark 42%→96%），能从开源项目中提取 WHY + UNSAID 知识。

**关键脚本和用法：**

| 脚本 | 功能 | 用法 |
|------|------|------|
| `scripts/prepare-repo.sh` | Stage 0：clone + repomix + 社区信号 + repo_facts | `bash prepare-repo.sh <repo_url> <output_dir>` |
| `scripts/extract.py` | Stage 1.5-4：LLM 驱动的知识提取 | `python extract.py <repo_dir>` |
| `scripts/collect-community-signals.py` | Stage D：GitHub 社区信号采集 | `python collect-community-signals.py <repo_url> <output_file>` |
| `scripts/extract_repo_facts.py` | Stage 0：确定性事实提取 | `python extract_repo_facts.py <repo_dir> <output_json>` |
| `scripts/assemble-output.sh` | Stage 5：组装最终输出 | `bash assemble-output.sh <soul_dir> <output_dir>` |
| `scripts/validate_extraction.py` | Stage 3.5：硬验证 | `python validate_extraction.py <cards_dir>` |
| `scripts/validate_output.py` | 最终输出验证 | `python validate_output.py <output_dir>` |

**LLM 提取指令（Prompt）：**

| 文件 | 用于 Stage | 内容 |
|------|-----------|------|
| `stages/STAGE-1-essence.md` | 1 | 7 问灵魂发现（Q1-Q5 基础层 WHAT，Q6-Q7 灵魂层 WHY） |
| `stages/STAGE-2-concepts.md` | 2 | 概念卡 + 工作流卡提取指令 |
| `stages/STAGE-3-rules.md` | 3 | 规则卡提取指令（含 UNSAID） |
| `stages/STAGE-3.5-review.md` | 3.5 | 硬验证检查清单 |
| `stages/STAGE-4-synthesis.md` | 4 | 专家叙事合成指令 |
| `stages/STAGE-M-modules.md` | M | 模块地图指令 |
| `stages/STAGE-C-community.md` | C | 社区智慧合成指令 |

**产品开发中的使用方式：**
- Phase C（灵魂提取）直接调用 Soul Extractor 的脚本和 prompt
- 不要重写提取逻辑——Soul Extractor 已经验证过
- 需要做的是：用 Python 把这些脚本编排起来，集成到 Phase A-H 管线中

### 3.2 赛马模块成果 — 骨架资产（259 测试）

位置：`packages/`

赛马产出了 10 个模块，提供了 Pydantic 契约定义和骨架实现。

**直接可用的模块（填入真实数据即可工作）：**

| 模块 | 文件 | 功能 | 说明 |
|------|------|------|------|
| contracts | `packages/contracts/` | 所有数据结构定义 | **地基，直接用** |
| validator | `packages/platform_openclaw/.../validator.py` | 7 项质量检查 | **生产就绪**，读真实文件做检查 |
| api.read | `packages/preextract_api/.../app.py` | FastAPI 只读 API | **生产就绪**，部署即可用 |
| compare | `packages/cross_project/.../compare.py` | 跨项目比较（Jaccard+聚类） | **算法就绪**，等上游喂真实数据 |
| synthesis | `packages/cross_project/.../synthesis.py` | 知识综合决策 | **基本就绪**，需补 LLM 语义决策 |
| snapshot_builder | `packages/domain_graph/.../snapshot_builder.py` | 领域快照构建 | **基本就绪** |

**需要改造/重写的模块：**

| 模块 | 文件 | 问题 | 改造方向 |
|------|------|------|---------|
| stage0 | `packages/extraction/.../stage0.py` | 只扫顶层目录 | 改用 Soul Extractor 的 prepare-repo.sh |
| stage1_scan | `packages/extraction/.../stage1_scan.py` | 规则简单 | 结合 Soul Extractor 的 STAGE-1-essence.md |
| stage15_agentic | `packages/extraction/.../stage15_agentic.py` | 全 mock | 接入 LLM，用 Soul Extractor 的 extract.py |
| discovery | `packages/cross_project/.../discovery.py` | 硬编码项目库 | 接入 GitHub Search API |
| phase_runner | `packages/orchestration/.../phase_runner.py` | 全 mock 编排 | 替换为真实调用 |
| skill_compiler | `packages/skill_compiler/.../compiler.py` | 模板简单 | 对接 Soul Extractor 的 assemble-output.sh |

### 3.3 研究结论 — 设计决策依据

以下结论经过实验验证，开发中必须遵守：

| # | 结论 | 来源 | 影响 |
|---|------|------|------|
| 1 | 证据绑定优先于一切 — 无证据锚定的知识注入后得分反降 11 分 | exp07 | Stage 3.5 必须 file:line 锚定 |
| 2 | Stage 0 改进比 Prompt 优化 ROI 更高（+0.7 vs +0.5） | WHY实验 | 优先加强 Stage 0 |
| 3 | Agentic 提取（LLM 读代码）是下一个量级的突破 | WHY实验 | Stage 1.5 必须实现 |
| 4 | Knowledge Compiler 按知识类型路由格式 | 5大难点 | 事实→结构化，哲学→叙事 |
| 5 | 好作业 = 增量价值（Marginal Gain），不是绝对质量 | 好作业研究 | Discovery 排序依据 |
| 6 | 最危险的 source 是"看起来好但误导"的 | 暗雷研究 | 暗雷检测权重 > 正面指标 |
| 7 | 部分覆盖是默认模式 — 70% 覆盖 = 完整交付 + 30% 地图 | 飞轮研究 | 输出不假装全面 |
| 8 | Sonnet > Gemini（7.79 vs 6.63）但高分 WHY 不重叠 | WHY实验 | 多模型融合有价值 |

---

## 第四部分：开发步骤

### 步骤 0：环境准备

```bash
cd ~/Documents/vibecoding/Doramagic

# 项目结构已存在，259 测试应全部通过
python3 -m pytest  # 预期 259 passed

# 确认 Soul Extractor 脚本可执行
ls skills/soul-extractor/scripts/

# 确认 contracts 可导入
python3 -c "import sys; sys.path.insert(0,'packages/contracts'); from doramagic_contracts import *; print('OK')"
```

### 步骤 1：构建 CLI 入口 + Phase A

创建 `doramagic.py`（或 `packages/cli/doramagic_cli/main.py`），作为产品入口。

```
输入：python3 doramagic.py "我想做一个管理家庭菜谱的 skill"
输出：runs/<run_id>/delivery/ 目录下的 SKILL.md + PROVENANCE.md + LIMITATIONS.md
```

Phase A 将用户原始文本解析为 NeedProfile：
- 调用 LLM 提取 keywords、intent、search_directions、constraints
- 输出 need_profile.json
- 使用 contracts 中的 `NeedProfile` 模型

### 步骤 2：Phase B — 作业发现（接入 GitHub API）

基于 NeedProfile 的 keywords 和 search_directions：
- 调用 GitHub Search API（`https://api.github.com/search/repositories`）搜索相关项目
- 按 stars、更新时间、相关度排序
- 选出 top 3-5 个候选项目
- 输出 discovery_result.json

**注意**：本机 git clone 需通过 GitHub API 下载（zip/tarball），不支持直接 `git clone`。提供 helper：
```python
# 下载仓库代码
import urllib.request
url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
urllib.request.urlretrieve(url, f"{output_dir}/repo.zip")
```

### 步骤 3：Phase C — 灵魂提取（核心，调用 Soul Extractor）

对每个候选项目：

1. **Stage 0**：调用 `skills/soul-extractor/scripts/prepare-repo.sh`
   - 输入：repo URL + 工作目录
   - 输出：packed_compressed.xml, packed_full.xml, repo_facts.json, community_signals.md

2. **Stage 1**：结合 `stages/STAGE-1-essence.md` 的 7 问 + `stage1_scan.py` 的规则
   - 可以先用 stage1_scan.py 做规则扫描，再用 LLM 补充 Q6-Q7（WHY 层）

3. **Stage 1.5-4**：调用 `skills/soul-extractor/scripts/extract.py`
   - 这个脚本包含 Eagle Eye → Deep Dive → Community Soul → Project Soul 四个 Phase
   - 需要配置 LLM API（见步骤 6）

4. **Stage 3.5**：调用 `validate_extraction.py` 做硬验证

5. **Stage 5**：调用 `assemble-output.sh` 组装输出

### 步骤 4：Phase D — 社区采集

调用 `skills/soul-extractor/scripts/collect-community-signals.py`
- 已实现 GitHub Issue/PR/CHANGELOG 采集
- 输出 community_knowledge.json

### 步骤 5：Phase E — 知识综合

使用赛马模块：
1. `compare.py`：跨项目比较，输出 CompareSignal（ALIGNED/DIVERGENT/CONTESTED...）
2. `synthesis.py`：综合决策，输出 SynthesisReport（include/exclude/option 决策）

需要将 Stage 0-5 的产出转换为 `ProjectFingerprint`（contracts 中的模型）喂入 compare。

### 步骤 6：Phase F-G-H — 锻造 + 验证 + 交付

1. **Phase F**：使用 `skill_compiler.py` 或 `assemble-output.sh` 生成 SKILL.md
2. **Phase G**：使用 `validator.py` 做 7 项检查
3. **Phase H**：打包交付物到 `runs/<run_id>/delivery/`

### 步骤 7：端到端测试

用 3 个不同需求测试：
```bash
python3 doramagic.py "我想做一个管理家庭菜谱的 skill"
python3 doramagic.py "帮我做一个 Ham Radio 日志记录工具"
python3 doramagic.py "帮我管理家里的东西"
```

每次运行后检查：
- `runs/<run_id>/delivery/SKILL.md` 是否存在且包含 WHY
- `runs/<run_id>/delivery/PROVENANCE.md` 是否可追溯
- `runs/<run_id>/delivery/LIMITATIONS.md` 是否诚实
- validator 是否 PASS

---

## 第五部分：LLM 集成

### 5.1 哪些 Stage 需要 LLM

| Stage/Phase | LLM 用途 | 推荐模型 | 原因 |
|-------------|---------|---------|------|
| Phase A（需求理解） | 解析用户意图 | Sonnet | 简单任务 |
| Stage 1.5（Agent 深潜） | 读代码验证假说 | Opus | 需要深度推理 |
| Stage 2（概念提取） | 提取概念卡+工作流卡 | Sonnet | 结构化提取 |
| Stage 3（规则提取） | 提取决策规则卡 | Sonnet | 结构化提取 |
| Stage 4（叙事合成） | 专家级知识合成 | Opus | 需要深度综合 |
| Phase E（综合决策理由） | 解释为什么 include/exclude | Sonnet | 辅助决策 |
| Phase F（Skill 锻造叙事） | 组装 SKILL.md 的叙事部分 | Sonnet | 文本生成 |

### 5.2 LLM 调用方式

使用 Anthropic Python SDK：

```python
import anthropic
client = anthropic.Anthropic()  # 从 ANTHROPIC_API_KEY 环境变量读取

response = client.messages.create(
    model="claude-sonnet-4-6",  # 或 "claude-opus-4-6"
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)
```

环境变量配置：
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export DORAMAGIC_DEFAULT_MODEL="claude-sonnet-4-6"
export DORAMAGIC_DEEP_MODEL="claude-opus-4-6"
```

### 5.3 Prompt 来源

**不要自己写 prompt。** Soul Extractor 的 `stages/STAGE-*.md` 已经验证过，直接用。
- 读取 `stages/STAGE-1-essence.md` 的内容作为 System Prompt
- 把 repomix 压缩后的代码作为 User Message 传入
- 解析 LLM 输出为知识卡片

---

## 第六部分：技术环境

### 6.1 依赖

```
Python >= 3.9
anthropic        # LLM 调用
fastapi          # 系统 B（已实现）
uvicorn          # 系统 B（已实现）
httpx            # GitHub API 调用
pydantic >= 2.0  # 数据模型（已有）
pytest >= 8.0    # 测试
```

### 6.2 GitHub 访问

本机无法直接 `git clone`，使用 GitHub API 下载：

```python
def download_repo(owner: str, repo: str, branch: str, output_dir: str):
    """通过 GitHub API 下载仓库代码。"""
    import zipfile, io
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    resp = httpx.get(url, follow_redirects=True)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(output_dir)
```

GitHub Search API（无需认证，60次/小时）：
```
GET https://api.github.com/search/repositories?q={keywords}+language:python&sort=stars&per_page=5
```

### 6.3 文件结构

```
Doramagic/
├── doramagic.py                     ← 【新建】CLI 入口
├── skills/soul-extractor/           ← 【已有】核心提取引擎
├── packages/
│   ├── contracts/                   ← 【已有】数据模型
│   ├── extraction/                  ← 【改造】对接 Soul Extractor
│   ├── cross_project/               ← 【已有】compare + synthesis
│   ├── skill_compiler/              ← 【改造】对接 assemble-output.sh
│   ├── platform_openclaw/           ← 【已有】validator
│   ├── orchestration/               ← 【改造】phase_runner 接真实调用
│   ├── domain_graph/                ← 【已有】snapshot_builder
│   └── preextract_api/              ← 【已有】api.read
├── data/fixtures/                   ← 【已有】测试数据
├── runs/                            ← 【新建】运行时输出目录
└── docs/                            ← 【已有】文档
```

---

## 第七部分：验收标准

### 7.1 核心验收

Doramagic 必须能处理**任意用户需求**。验收时用 3 个随机需求（不可提前准备）测试端到端。

**每个需求必须产出：**
- SKILL.md — 符合 OpenClaw 平台规则，包含 WHY 和 UNSAID
- PROVENANCE.md — 每条知识可追溯到具体项目的具体文件
- LIMITATIONS.md — 诚实标明能力边界

### 7.2 输出质量

| 维度 | 标准 |
|------|------|
| WHY 密度 | SKILL.md 不只有 WHAT，必须包含 WHY 和 UNSAID |
| 溯源完整 | PROVENANCE.md 抽查 3 条可追溯 |
| 边界诚实 | LIMITATIONS.md 不编造能力 |
| 平台合规 | validator 7 项检查全过 |
| 部分覆盖诚实 | 项目少时标注覆盖范围 |

### 7.3 系统能力

| 能力 | 标准 |
|------|------|
| 独立运行 | 断开 API 时全流程完成 |
| API 加速 | 连接 API 且领域命中时速度提升 |
| 冲突处理 | 多项目矛盾时标注冲突 |

---

## 第八部分：评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 端到端完整性 | 30% | 3 个随机需求能否全部跑通 |
| 输出质量 | 25% | SKILL.md 的 WHY 密度和知识准确性 |
| 已有资产复用 | 15% | 是否充分利用 Soul Extractor + 赛马模块 |
| 代码质量 | 15% | 可维护性、测试覆盖、契约遵守 |
| 性能与成本 | 15% | LLM 调用次数、耗时、token 成本 |
