# Soul Extractor 三个进化方向的技术可行性报告（Codex）

> 日期：2026-03-09  
> 任务文件：`20260309_codex_evolution_directions_task.md`

## 执行摘要

### 结论先行

我**同意“验证闭环优先”**，但**不同意后两项的排序**。  
我的推荐排序是：

> **P0 验证闭环 > P1 拆解 / 定向注入 > P2 WHY 层提取**

### 为什么这样排

1. **验证闭环必须先做**
   - 现在 Soul Extractor 已能稳定产出 WHAT / HOW / IF，但缺少“硬校验 + 软审查”。
   - 如果先扩能力、后补验证，只会更快地产出更多不可验证的内容。

2. **拆解 / 定向注入的工程 ROI 高于 WHY 层**
   - 它能直接提升 AI 燃料的“相关性 × 密度”，而且大部分能力可以复用现有卡片，在组装层实现。
   - 它不要求模型具备更强的隐含意图推理能力，落地风险更低。

3. **WHY 层很有战略价值，但不是下一步最稳的产品化路径**
   - WHY 是 Soul Extractor 从“文档级认知”走向“专家级认知”的关键。
   - 但 WHY 的来源更分散、验证更难、对弱模型更不友好，且显著依赖额外信号与更强审查机制。

### 推荐路线图

- **第 1 步**：加 `Stage 3.5 Validate`，建立 hard gate
- **第 2 步**：生成 `domain_map.yaml`，先做“提取后定向组装”
- **第 3 步**：新增 `design_rationale_card (DRC)`，先提取“显式 WHY”，再探索“隐式 WHY”

---

## 一、研究范围与证据

本报告回答三条进化方向：

1. 验证闭环
2. WHY 层提取
3. 拆解 / 定向注入

并额外回答：
- 是否同意既定优先级
- 每个方向的 MVP 工作量
- 每个方向的主要风险

### 证据来源

#### 本地来源

- `[L1]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_evolution_directions_task.md`
- `[L2]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_v06_plan.md`
- `[L3]` `Documents/vibecoding/allinone/skills/soul-extractor/stages/STAGE-3-rules.md`
- `[L4]` `Documents/vibecoding/allinone/skills/soul-extractor/scripts/collect-community-signals.py`
- `[L5]` `Documents/vibecoding/allinone/skills/soul-extractor/scripts/assemble-output.sh`
- `[L6]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_community_signals_report.md`
- `[L7]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_skill_engineering_report.md`

#### 外部来源

- `[S1]` OpenAI Structured Outputs — https://platform.openai.com/docs/guides/structured-outputs/supported-schemas
- `[S2]` OpenAI Evals Guide — https://platform.openai.com/docs/guides/evals
- `[S3]` OpenAI Graders Guide — https://platform.openai.com/docs/guides/graders/
- `[S4]` ADR / MADR Guidance — https://adr.github.io/ 、https://adr.github.io/madr/

### 本报告的基本判断

1. **当前 v0.6 已经足够进入“质量工程”阶段**，而不只是继续 prompt engineering。  
   来源：`[L1][L2][L3][L6][L7]`；置信度：**高**

2. **弱模型不适合同时承担“生成 + 审查 + 汇总”三重职责**。最稳做法是：
   - 脚本负责硬性验证
   - 模型负责软性审查
   - 审查与生成分阶段、分输入进行  
   来源：`[S1][S2][S3]` + 本地实验推理；置信度：**中高**

3. **WHY 层本质上接近“设计决策与 rationale 抽取”问题**，更像 ADR，而不是普通规则卡扩展。  
   来源：`[S4][L1]`；置信度：**高**

---

## 二、当前 v0.6 状态：适合怎么演进？

基于任务文件与现有技能目录，我认为 v0.6 的状态可以概括为：

### 已经做对了什么

- 已把提取流程拆成 Stage
- 已有社区信号输入面
- 已能稳定产出 WHAT / HOW / IF
- 已能组装 `.cursorrules` / `CLAUDE.md` / `project_soul.md`

### 现在最缺的是什么

- **缺验证**：没有 hard gate，就无法知道哪些卡能信
- **缺裁剪**：全量注入降低 AI 燃料密度
- **缺 WHY**：战略性知识无法沉淀

### 三个方向的依赖关系

```text
验证闭环
  -> 让现有产物可测、可挡、可比较
  -> 为 WHY 和定向注入提供可信基础

拆解 / 定向注入
  -> 复用已有 WHAT / HOW / IF，最快拉升实际使用价值
  -> 还能反过来暴露“某个问题域缺少 WHY/规则”的空洞

WHY 层提取
  -> 提升专家级认知与差异化
  -> 但依赖更好的来源、更细的审查、更强的模型或更严格的置信约束
```

所以工程主线应是：

> **先让当前产物可信，再让当前产物可裁剪，最后再让产物更聪明。**

---

## 三、方向 1：验证闭环（推荐 P0）

## 3.1 我是否建议增加验证 Stage？

**建议，而且应该明确插在 Stage 3 之后、Stage 4 之前。**

推荐新增：

> **Stage 3.5 — Validate & Review**

### 为什么位置要放这里

- Stage 3 已经产出完整 cards
- Stage 4 才负责组装注入文件
- 在两者之间拦截，最适合做：
  - 格式校验
  - 引用真实性校验
  - 社区信号关联校验
  - 内容质量抽样审查

### 推荐产物

新增两个文件：

- `soul/validation_report.json`
- `soul/validation_summary.md`

### 推荐门禁策略

- **hard fail**：阻止进入 Stage 4
- **soft fail**：允许进入 Stage 4，但在 summary 中标红

### hard fail 适用场景

- YAML frontmatter 缺字段
- `severity` 不在枚举中
- `sources` 中的 `file:line` 无法解析
- 社区陷阱引用的 issue / signal 根本不存在

### soft fail 适用场景

- 场景不够具体
- 影响范围太泛
- 规则太像 README 摘要而不像决策规则

来源：`[L1][L3][S1][S2][S3]`；置信度：**高**

---

## 3.2 验证应该由模型做还是脚本做？

### 结论

**脚本做硬校验，模型做软审查。不要二选一。**

### 脚本负责什么

这些都是确定性问题，应该脚本化：

1. 文件是否存在
2. frontmatter 是否能解析
3. 必填字段是否齐全
4. 枚举是否合法
5. `sources` 中的 `file:line` 是否存在
6. `DR-100~` 的 issue / advisory / changelog 引用是否在输入信号中出现过
7. 卡片数量是否达标
8. 卡片 ID 是否唯一、编号是否连续

### 模型负责什么

这些属于语义质量问题，适合二次审查：

1. 规则是否具体而非泛泛而谈
2. “真实场景”是否足够真实
3. `severity` 是否与描述相匹配
4. 规则是否真的回答了“何时会踩坑、怎么避免”
5. WHY 卡是否真的解释“为什么这样设计”，而不是改写 README

### 为什么不能只靠模型

- 弱模型容易“看起来认真审查，实则遗漏结构错误”
- 同一模型刚生成完再立刻自查，容易产生自我偏置
- 格式问题脚本更快、更稳定、可回归

### 为什么不能只靠脚本

- 脚本能知道 `file:line` 是否存在，但不知道“这个场景是不是编的”
- 脚本能知道有 `severity` 字段，但不知道严重度是否合理

来源：`[S1][S2][S3][L3]`；置信度：**高**

---

## 3.3 推荐的 Two-Stage Review 设计

### Round 1：Spec Review（脚本）

目标：保证“格式与可追溯性”

推荐新增文件：
- `skills/soul-extractor/scripts/validate_extraction.py`

#### 检查项

```python
REQUIRED_CARD_FIELDS = {
    "decision_rule_card": [
        "card_type", "card_id", "repo", "type", "title", "severity",
        "rule", "do", "dont", "confidence", "sources"
    ],
    "concept_card": [...],
    "workflow_card": [...],
    "design_rationale_card": [...],
}
```

#### 伪代码

```python
def validate_cards(output_dir):
    cards = load_all_cards(output_dir)
    repo_files = index_repo_files(f"{output_dir}/artifacts/_repo")
    community = load_community_index(f"{output_dir}/artifacts/community_signals.json")

    report = []
    for card in cards:
        errors = []
        warnings = []

        meta, body = parse_frontmatter(card)
        check_required_fields(meta, errors)
        check_enum(meta.get("severity"), ["CRITICAL", "HIGH", "MEDIUM", "LOW"], errors)
        check_card_id_unique(meta["card_id"], errors)
        check_rule_sections(body, warnings)

        for src in meta.get("sources", []):
            if is_file_line_source(src):
                ok = verify_file_line(src, repo_files)
                if not ok:
                    errors.append(f"invalid code source: {src}")
            elif is_community_source(src):
                ok = verify_community_ref(src, community)
                if not ok:
                    errors.append(f"invalid community source: {src}")

        report.append({
            "card_id": meta.get("card_id"),
            "errors": errors,
            "warnings": warnings,
            "pass": len(errors) == 0,
        })

    write_json(report, "validation_report.json")
    write_summary_md(report, "validation_summary.md")
    return exit_code_from_report(report)
```

### Round 2：Quality Review（模型）

目标：保证“内容不是空壳”

推荐新增文件：
- `skills/soul-extractor/stages/STAGE-3.5-review.md`
- 或 `scripts/review_cards.py`（如果以后走 API / structured output）

#### 审查策略

- **不要把全部 cards 一次性塞给弱模型审查**
- 按卡片逐张或按 3 张一组审查
- 输出严格结构化 JSON / YAML
- 每张卡只给 reviewer 它本身 + 对应证据摘录 + 审查 rubric

#### 审查 schema 示例

```yaml
card_id: DR-101
overall: pass
scores:
  specificity: 0.9
  realism: 0.7
  actionability: 0.8
  evidence_alignment: 0.9
findings:
  - kind: warning
    message: "Scenario is plausible but still generic; missing deployment context."
  - kind: pass
    message: "Severity aligns with community evidence."
recommended_fix:
  - "Add a concrete execution environment, e.g. CI/CD, Docker, multi-stage config."
```

### 弱模型能否同时生成和审查？

**不建议在同一轮里做。**

更稳的做法：
- 生成：Stage 3
- 审查：Stage 3.5
- 输入完全变化
- 目标完全变化
- 最好把 reviewer prompt 缩小到“单卡审查”

如果只能用 MiniMax-M2.5：
- 仍然可以做 reviewer
- 但必须：
  - 分卡审查
  - 固定 rubric
  - 结构化输出
  - 用脚本先过硬校验，减少模型负担

如果有强模型可用：
- 让强模型做 reviewer 更合理
- 但不是 MVP 必需项

来源：`[S1][S2][S3]` + 工程推理；置信度：**中高**

---

## 3.4 验证指标设计

### 我建议的指标体系

#### A. 结构合规类

1. **格式合规率**

```text
format_compliance_rate = pass_hard_validation_cards / total_cards
```

2. **字段完整率**

```text
required_field_coverage = present_required_fields / total_required_fields
```

3. **编号完整率**

```text
id_integrity = valid_unique_ids / expected_ids
```

#### B. 证据可追溯类

4. **证据可追溯率**

```text
traceability_rate = valid_source_refs / total_source_refs
```

5. **代码引用真实性**

```text
code_source_validity = valid_file_line_refs / total_file_line_refs
```

6. **社区引用真实性**

```text
community_source_validity = valid_issue_or_signal_refs / total_issue_or_signal_refs
```

#### C. 内容利用类

7. **社区信号利用率**

```text
community_utilization = unique_community_signals_used / eligible_ranked_signals
```

8. **高价值信号覆盖率**

```text
tier1_coverage = tier1_signals_referenced / tier1_signals_available
```

9. **证据融合率**

```text
cross_source_rule_rate = rules_using_code_and_community / total_rules
```

#### D. 质量判断类

10. **规则具体性均分**（模型审查）
11. **真实场景真实性均分**（模型审查）
12. **可执行性均分**（模型审查）
13. **严重度匹配度**（模型审查 + 规则 heuristics）

### 推荐 hard gate 阈值（MVP）

- `format_compliance_rate >= 0.95`
- `traceability_rate == 1.00`
- `community_source_validity == 1.00`
- `community_utilization >= 0.30`
- 至少 `3` 张 `DR-100~`

### 推荐 soft target（MVP）

- `specificity_avg >= 0.75`
- `realism_avg >= 0.70`
- `actionability_avg >= 0.80`

来源：`[L1][L3][S2][S3]`；置信度：**高**

---

## 3.5 验证方向的最小可行实现（MVP）

### 目标

在不换模型、不重写整条链路的前提下，让现有 v0.6 产物先“可挡、可量化、可回归”。

### 我会改的文件

1. **新增** `skills/soul-extractor/scripts/validate_extraction.py`
2. **新增** `skills/soul-extractor/stages/STAGE-3.5-review.md`
3. **修改** `skills/soul-extractor/stages/STAGE-3-rules.md`
4. **修改** `skills/soul-extractor/scripts/assemble-output.sh`
5. **可选修改** `skills/soul-extractor/SKILL.md`

### 工作量评估

- **1–2 天**
- **4–5 个文件**
- **主要风险低**

### 风险

1. `community_signals.md` 如果没有 machine-readable 索引，校验代码会写得很脆
2. reviewer 如果一次看太多卡，弱模型质量会掉
3. 若 hard gate 设太高，初期会频繁拦截，需要逐步调阈值

### 额外建议

为验证阶段引入一个 canonical machine file：

- `artifacts/community_signals.json`
- `soul/index.json`

Markdown 继续保留给人读，JSON 给脚本验证。  
这会让 Stage 3.5 的实现明显更稳。

---

## 四、方向 2：WHY 层提取（我建议排在 P2，作为能力增强）

## 4.1 WHAT/HOW/IF 为什么不够？

### 结论

你们的判断是对的：WHY 层是“文档级认知”到“专家级认知”的关键增量。

### 但工程上要分清两种 WHY

#### 类型 A：**显式 WHY**

来源中明确写了：
- because / in order to / to avoid / trade-off / chosen because
- ADR / design note / maintainer explanation / migration rationale

这类 WHY **可以被提取**。

#### 类型 B：**隐式 WHY**

需要从代码结构、历史演化、生态定位、交叉项目关系推断：
- “为什么要用这种反合理化设计？”
- “为什么 description 必须是触发器？”
- “为什么 Superpowers 与 Soul Extractor 是互补关系？”

这类 WHY **更接近研究判断**，不能轻易冒充“自动提取事实”。

### 工程意义

Soul Extractor 适合先做：

> **显式 WHY 提取 + 保守标注 derived WHY**

而不是一开始就承诺“自动还原专家洞察”。

来源：`[L1][S4]`；置信度：**高**

---

## 4.2 WHY 知识的来源分析

### 当前 prepare-repo / 本地 repo 能拿到的

1. **README / docs / architecture 文档**
2. **CHANGELOG / migration guide**
3. **`git log` commit message**
4. **代码注释 / docstring / header comments**
5. **仓库内 ADR / decisions 文档**
   - 如 `docs/adr/`, `docs/decisions/`, `architecture/`

### 需要额外采集的

6. **GitHub Discussions 里的设计讨论**
7. **Issue 中 `design` / `architecture` / `proposal` 标签内容**
8. **PR 描述与 review comments**（高价值，但采集成本也高）

### prepare-repo 当前做不到的

9. **博客文章 / 会议演讲 / 播客 / 外部文档**
   - 除非 repo 明确链接，且你们愿意额外抓外链

### 推荐分层

#### Tier 1：仓库内显式 rationale（P0/P1 可做）
- README
- docs
- ADR
- changelog
- commit message

#### Tier 2：平台内显式 rationale（P2）
- GitHub Discussions
- Design issues
- Important PR descriptions

#### Tier 3：仓库外推理性 rationale（研究模式）
- 博客 / 演讲
- 人类研究笔记
- 跨项目比较

### 关键判断

**WHY 层的核心难点不在卡片格式，而在信号来源和置信度分层。**

来源：`[L1][L4][S4]`；置信度：**高**

---

## 4.3 WHY 卡片设计：我建议用 `design_rationale_card`（DRC）

WHY 不建议塞进现有 `decision_rule_card`；它更接近 ADR / MADR。  
ADR/MADR 的核心思想也是：记录一个决策、上下文、理由、权衡与后果。  
来源：`[S4]`；置信度：**高**

### 推荐 frontmatter

```yaml
---
card_type: design_rationale_card
card_id: DRC-001
repo: superpowers
title: "Descriptions are triggers, not summaries"
rationale_type: DESIGN_DECISION
confidence: high
explicitness: explicit
status: accepted
sources:
  - "README.md:120-156"
  - "docs/adr/0003-description-as-trigger.md:1-42"
  - "GitHub Discussion #57"
related_cards:
  - "CC-001"
  - "DR-001"
---
```

### 推荐正文模板

```markdown
## Context
这个决策要解决什么问题？

## Decision
项目明确选择了什么做法？

## Why
为什么这样做？核心理由是什么？

## Alternatives Considered
考虑过什么替代方案？为什么没选？

## Consequences
这样做带来的收益、代价、边界是什么？

## Evidence
- 摘要证据 1
- 摘要证据 2

## Injection Hint
当 AI 遇到什么场景时，这条 WHY 应该被注入？
```

### 为什么要加 `explicitness`

因为 WHY 很容易“推断过度”。推荐三档：

- `explicit`：来源明确说了 why
- `derived`：从多个显式信号归纳出来
- `speculative`：只能推断，**不进入生产注入包**

### 为什么要加 `Injection Hint`

WHY 层不是每次都该注入。很多 WHY 只在这些场景有价值：
- 做架构改造
- 试图重构核心机制
- 质疑某个看似奇怪设计时

来源：`[S4]` + 工程推理；置信度：**高**

---

## 4.4 如何在工程上实现 WHY 抽取

### 推荐新增一个独立阶段

不要把 WHY 混进 Stage 3 规则卡提取里。  
建议新增：

> **Stage 2.5 — Rationale Extraction**

### 输入

- `00-project-essence.md`
- `packed_compressed.xml`
- `community_signals.md` 中 design / architecture / migration 相关信号
- repo 文档中被脚本挑出的 rationale snippets
- `git log` 中被脚本挑出的设计变更 commit

### 新增脚本建议

1. **新增** `scripts/collect-rationale-signals.py`
   - 或扩展 `collect-community-signals.py`
2. **新增** `stages/STAGE-2.5-rationale.md`

### 为什么不建议直接让模型从全 repo 猜 WHY

- 代码更多告诉你“怎么做”，不是“为什么这么做”
- 缺少显式信号时，弱模型会把“合理猜测”写成“事实”
- 这类 hallucination 比普通字段缺失更危险，因为读起来最像专家意见

### 推荐脚本预处理

脚本先抽出带 rationale cue 的片段：

```python
RATIONALE_MARKERS = [
    "because", "so that", "to avoid", "trade-off", "chosen", "decided",
    "design", "rationale", "motivation", "why", "instead of", "prefer"
]
```

#### 伪代码

```python
def collect_rationale_signals(repo_path):
    snippets = []

    snippets += grep_docs(repo_path, patterns=RATIONALE_MARKERS)
    snippets += grep_adr_files(repo_path)
    snippets += grep_readme_sections(repo_path, ["Architecture", "Design", "Rationale", "Trade-offs"])
    snippets += grep_git_log(repo_path, ["because", "avoid", "decide", "trade-off", "motivation"])
    snippets += grep_discussions_cache(repo_path, labels=["design", "architecture"])

    return rank_and_trim(snippets, max_items=30)
```

然后 Stage 2.5 只基于这些片段做抽取，不让模型“在整片海里猜”。

---

## 4.5 弱模型能提取 WHY 吗？

### 结论

**能做“显式 WHY 提取”，不适合做“隐式 WHY 推理”。**

### MiniMax-M2.5 适合的部分

- 从 README / ADR / maintainer comment 中抽取明确 rationale
- 把一个设计决策写成结构化 DRC
- 在 `sources` 足够清楚时进行摘要和组织

### MiniMax-M2.5 不适合的部分

- 从代码结构强行推断设计哲学
- 归纳跨项目互补关系
- 从零重建“方法论背后的方法论”

### 因此推荐的产品策略

#### 生产模式（默认）
- 只产出 `explicit` / `derived` 的 WHY 卡
- `derived` 卡必须至少两条独立来源支撑
- `speculative` 不输出到注入文件

#### 研究模式（增强）
- 允许强模型或人工审查产生更深层 WHY
- 输出到 `human/`，不直接进 `.cursorrules`

### Prompt 设计建议

#### 不要这样问

> “请分析这个项目为什么会这样设计。”

这太宽，容易触发脑补。

#### 建议这样问

> “以下片段中，哪些明确说明了设计决策的原因？只抽取来源中有明确信号支持的理由；若只是推断，请标为 derived；若证据不足，不要输出。”

#### 再配合结构化输出

如果用支持 schema 的模型，优先结构化输出；如果不用，也至少用脚本二次校验字段完整性。  
来源：`[S1]`；置信度：**高**

---

## 4.6 WHY 方向的最小可行实现（MVP）

### 建议的 MVP 范围

只做：
- repo 内显式 WHY
- DRC 2–5 张
- 不碰外部博客 / 演讲
- 不承诺“专家级战略洞察自动提取”

### 我会改的文件

1. **新增** `skills/soul-extractor/stages/STAGE-2.5-rationale.md`
2. **新增** `skills/soul-extractor/scripts/collect-rationale-signals.py`
3. **修改** `skills/soul-extractor/scripts/prepare-repo.sh`
4. **修改** `skills/soul-extractor/scripts/assemble-output.sh`
5. **修改** `skills/soul-extractor/SKILL.md`

### 工作量评估

- **2–4 天**（显式 WHY 版）
- **5 个文件左右**
- 若接 GitHub Discussions，再加 **1–2 天**

### 风险

1. 弱模型把“合理猜测”写成事实
2. 很多项目根本没有显式 WHY 来源，容易产出很少
3. WHY 卡如果无节制注入，会压缩真正高频实用规则的上下文空间

### 关键建议

先把 WHY 当成：

> **“高价值、低覆盖”的增强层**

而不是基础燃料层。

---

## 五、方向 3：拆解 / 定向注入（我建议排在 P1）

## 5.1 问题域拆解 vs 代码模块拆解：我的判断

### 结论

**正确主轴是问题域拆解，不是代码模块拆解。**  
但工程上不能只靠模型“理解问题域”；更稳的方法是：

> **问题域为主，模块为证据映射。**

也就是说：
- 对用户暴露的是问题域
- 对系统内部保存的是“问题域 ↔ 模块 / 文件 / 卡片”的映射

### 为什么不是纯模块拆解

- 用户不会说“我只关心 `parser.py`”
- 用户会说“我只关心配置加载 / 多环境变量覆盖 / CLI 修改”
- AI 注入的价值来自任务相关性，而不是代码目录结构

### 为什么又不能完全忽略模块

- 最终注入要落到证据和规则上
- 卡片与文件引用、workflow、API surface 都还是模块化存在

### 推荐中间层：`domain_map.yaml`

```yaml
repo: python-dotenv
problem_domains:
  - domain_id: PD-001
    name: "配置加载"
    user_intents:
      - "从 .env 读取变量"
      - "控制 override 行为"
      - "在启动时加载配置"
    related_cards:
      - CC-001
      - WF-001
      - DR-001
      - DR-101
    related_files:
      - src/dotenv/main.py
      - src/dotenv/parser.py
    api_surface:
      - load_dotenv
      - dotenv_values
    confidence: high
```

这个文件是“问题域语言”和“代码结构语言”的桥。

来源：`[L1][L2]` + 工程推理；置信度：**高**

---

## 5.2 问题域拆解在工程上怎么实现？

### 推荐实现：模型辅助归纳，脚本固定结构

#### 第一步：候选问题域发现

来源：
- README 的任务导向标题
- 公共 API 名称
- CLI commands
- workflow card 标题
- 高频规则簇

#### 第二步：模型归纳问题域

输入不是整 repo，而是：
- essence
- concepts
- workflows
- rules
- public API list

让模型回答：
- 这个项目主要帮用户解决哪 3–6 类问题？
- 每类问题和哪些 API / file / cards 对应？

#### 第三步：脚本做结构化规范

输出固定 `domain_map.yaml`：
- domain_id
- name
- user intents
- related_cards
- related_files
- related_api
- confidence

### 为什么这是可行的

- 问题域是“对已有知识的重组”，不是完全新抽取
- 它复用现有卡片成果，风险低于 WHY
- 它把“问题空间”显式化，为定向注入铺路

---

## 5.3 定向 AI 燃料应该在提取阶段做，还是组装阶段做？

### 结论

**MVP 一定要在组装阶段做。不要先碰“只提取相关部分”。**

### 推荐方案：全量提取，按域组装

#### 原因 1：复用最大

现有 pipeline 已经能提取全量知识。  
如果改成“只提取某域”，你要重新设计：
- prepare 输入
- stage prompt
- 卡片编号
- coverage 校验
- 组装逻辑

#### 原因 2：可缓存

一次 full extract 后：
- 可以生成多个 domain slice
- 用户二次选择不需要重跑 Stage 1–3

#### 原因 3：更容易验证

组装阶段过滤是确定性的；提取阶段裁剪会把问题复杂度推回模型侧。

### 推荐架构

```text
full extraction
  -> canonical knowledge pack
  -> domain_map.yaml
  -> assembler --domain PD-001
  -> inject/domain-PD-001/.cursorrules
```

### 什么时候再考虑提取阶段裁剪

只在下面两个条件同时满足时：
1. full extract 成本过高
2. 你们已经拥有稳定的 domain discovery 与 coverage 评测

在现在这个阶段，不建议。

来源：`[L1][L2][L7]`；置信度：**高**

---

## 5.4 产品交互设计：用户怎么表达关注的问题域？

### 我推荐的顺序

#### MVP：提取后选择（推荐）

流程：

1. 用户先做完整提取
2. 系统展示问题域列表
3. 用户选择一个或多个问题域
4. 系统生成定向 `.cursorrules` / `CLAUDE.md`

### 为什么这是 MVP 最优解

- 不需要用户一开始就理解项目结构
- 不会因为用户选错域而漏提取关键信息
- 和“先全量建索引，再按需切片”的架构一致

#### 增强版：提取前指定（次优先）

例如：
- “只关注配置加载”
- “只关注 CLI”

推荐做法：
- 把它当成 **排序 hint**，不是 hard filter
- 提高该问题域在组装时的优先级
- 不要让它直接裁掉其他知识

#### 更后续：全自动推断（P3）

例如分析用户项目代码：
- 发现调用了 `load_dotenv()`
- 自动推荐“配置加载”领域知识包

这需要：
- 读取用户代码
- 做 symbol/use-site 分析
- 建 domain-to-API map

不是当前阶段该做的第一优先级。

---

## 5.5 拆解 / 定向注入方向的最小可行实现（MVP）

### 建议的 MVP 目标

- 生成 `domain_map.yaml`
- 在 assembly 阶段支持 `--domain <id>`
- 为每个 domain 生成一个裁剪版 `.cursorrules` / `CLAUDE.md`
- 默认仍保留 full pack

### 我会改的文件

1. **新增** `skills/soul-extractor/scripts/build_domain_map.py`
2. **修改** `skills/soul-extractor/scripts/assemble-output.sh`
3. **修改** `skills/soul-extractor/stages/STAGE-1-essence.md` 或 `STAGE-2-concepts.md`
4. **修改** `skills/soul-extractor/SKILL.md`
5. **可选新增** `skills/soul-extractor/stages/STAGE-2.8-domains.md`

### 工作量评估

- **2–3 天**（组装期裁剪版）
- **3–5 个文件**
- 风险 **中低**

### 风险

1. 问题域命名不稳，容易因模型 wording 波动而抖动
2. 相关卡片归属可能交叉，需要允许“一卡多域”
3. 如果没有验证阶段，低质量卡片会被“高精度裁剪”后更显眼

### 关键建议

Domain map 也要走验证：
- 每个 domain 至少关联 1 个 workflow 或 1 个 rule
- 每个 `related_card` 必须存在
- 每个 `api_surface` 必须能在 repo 或 docs 中找到对应符号

---

## 六、优先级验证：我是否同意“验证 P0 > WHY P1 > 拆解 P2”？

### 我的答案

**不同意。**

我的排序是：

> **验证 P0 > 拆解 P1 > WHY P2**

### 详细理由

#### 1. 验证必须排第一

这点我完全同意。  
因为没有验证，就没有：
- 质量基线
- 回归检测
- 功能扩展前后的比较框架

#### 2. 拆解应排第二

从工程 ROI 看，它比 WHY 更适合作为下一步：

- **复用现有成果**：直接复用 WHAT/HOW/IF
- **实现路径短**：主要发生在组装层
- **用户价值直接**：马上提升注入相关性
- **验证容易**：可以比较 full pack vs domain pack 的答题得分 / token 密度

#### 3. WHY 应排第三

WHY 的战略价值很大，我同意这点。  
但它在工程上同时具有三重难度：

- **来源难**：很多 why 不在 repo 内
- **验证难**：比 `file:line` 真伪难多了
- **模型难**：弱模型更容易把推断写成事实

### 我给出的执行建议

- **主线 roadmap**：`Validation -> Domain Slice -> Explicit WHY`
- **研究支线**：并行小范围试 WHY，先在 Superpowers 这种 rich-text 项目上做 POC

这样既不拖慢产品主线，也不放弃 WHY 的差异化探索。

---

## 七、每个方向的 MVP 工作量与改动文件数

| 方向 | 建议优先级 | MVP 目标 | 预计工期 | 预计改动文件 |
|------|-----------|---------|---------|-------------|
| 验证闭环 | P0 | 加 `Stage 3.5`、硬校验、软审查 summary | 1–2 天 | 4–5 |
| 拆解 / 定向注入 | P1 | 生成 `domain_map.yaml`、assembly 支持 `--domain` | 2–3 天 | 3–5 |
| WHY 层提取 | P2 | 仅提 repo 内显式 WHY，生成 2–5 张 DRC | 2–4 天 | 5 左右 |

### 更细拆分

#### 验证闭环 MVP

- 脚本 hard validator：0.5–1 天
- Stage 3.5 reviewer prompt：0.5 天
- assemble 阶段接 gate：0.5 天

#### 拆解 MVP

- domain map 生成：1 天
- assembler filter：0.5–1 天
- prompt / output 说明：0.5 天

#### WHY MVP

- rationale signals 收集：1 天
- Stage 2.5 prompt：0.5–1 天
- assembly 集成：0.5 天
- 调试 hallucination / confidence：0.5–1 天

---

## 八、关键伪代码与实现建议

## 8.1 Validation Orchestrator

```python
def stage35_validate(output_dir, reviewer_model=None):
    report = run_hard_validator(output_dir)

    if report.hard_fail_count > 0:
        write_summary(report, output_dir)
        return {"status": "blocked", "report": report}

    review_results = []
    for card in load_cards(output_dir):
        review_results.append(review_single_card(card, reviewer_model))

    merged = merge_hard_and_soft_results(report, review_results)
    write_summary(merged, output_dir)
    return {"status": "pass_with_warnings" if merged.soft_warns else "pass", "report": merged}
```

## 8.2 DRC Extraction

```python
def extract_why_cards(rationale_signals, essence, model):
    prompt = build_prompt(
        task="extract explicit design rationale only",
        constraints=[
            "Do not infer unsupported rationale",
            "Mark explicitness as explicit or derived",
            "Speculative cards are forbidden",
        ],
        inputs=[rationale_signals, essence],
        schema=DESIGN_RATIONALE_CARD_SCHEMA,
    )
    return call_model(model, prompt)
```

## 8.3 Domain Slice Assembly

```python
def assemble_domain_pack(output_dir, domain_id):
    pack = load_knowledge_pack(output_dir)
    domain_map = load_yaml(f"{output_dir}/soul/domain_map.yaml")
    domain = find_domain(domain_map, domain_id)

    selected_cards = [card for card in pack.cards if card.id in domain.related_cards]
    selected_rules = rerank_rules(selected_cards, domain.user_intents)

    render_cursorrules(selected_cards, selected_rules, path=f"{output_dir}/inject/{domain_id}/.cursorrules")
    render_claude_md(selected_cards, selected_rules, path=f"{output_dir}/inject/{domain_id}/CLAUDE.md")
```

---

## 九、风险评估总表

| 方向 | 主要风险 | 严重度 | 缓解策略 |
|------|---------|-------|---------|
| 验证闭环 | hard gate 过严导致流程经常中断 | 中 | 先把错误分级，逐步抬阈值 |
| 验证闭环 | reviewer 一次吃太多上下文，弱模型误判 | 中 | 单卡审查、固定 rubric、结构化输出 |
| WHY 层 | 模型把推断写成事实 | 高 | `explicitness` 字段 + 禁止 speculative 入生产 |
| WHY 层 | 来源覆盖不足导致卡片太少 | 中 | 先只承诺 explicit WHY；不足时宁缺毋滥 |
| 拆解 / 定向注入 | domain 边界模糊 | 中 | 允许一卡多域，domain_map 做可验证结构 |
| 拆解 / 定向注入 | 过度裁剪导致遗漏关键信息 | 中 | 默认保留 full pack；domain pack 仅作为增量产物 |

---

## 十、最终建议

### 我会怎么推进

#### 第 1 周前半：先补验证

- 加 `validate_extraction.py`
- 加 `Stage 3.5`
- 产出 `validation_report.json`
- 建立 4 个核心指标：格式合规、证据可追溯、社区信号利用、规则具体性

#### 第 1 周后半：再做 domain slice

- 生成 `domain_map.yaml`
- 组装层支持 `--domain`
- 做 full pack vs domain pack 对比

#### 第 2 周：再开 WHY POC

- 先挑有丰富文档的 repo（如 Superpowers）
- 只做 explicit WHY
- 强制 `explicitness` / `confidence` 字段
- 不把 speculative WHY 放进生产注入包

### 一句话总结

> **验证闭环让 Soul Extractor“可信”，问题域拆解让它“好用”，WHY 层让它“高端”。**  
> 正确顺序不是同时追三者，而是先把可信度立住，再用裁剪放大价值，最后再追求专家级认知增量。

---

## 参考来源

### 官方 / 外部

- `[S1]` OpenAI Structured Outputs  
  https://platform.openai.com/docs/guides/structured-outputs/supported-schemas
- `[S2]` OpenAI Evals Guide  
  https://platform.openai.com/docs/guides/evals
- `[S3]` OpenAI Graders Guide  
  https://platform.openai.com/docs/guides/graders/
- `[S4]` Architectural Decision Records / MADR  
  https://adr.github.io/  
  https://adr.github.io/madr/

### 本地

- `[L1]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_evolution_directions_task.md`
- `[L2]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_v06_plan.md`
- `[L3]` `Documents/vibecoding/allinone/skills/soul-extractor/stages/STAGE-3-rules.md`
- `[L4]` `Documents/vibecoding/allinone/skills/soul-extractor/scripts/collect-community-signals.py`
- `[L5]` `Documents/vibecoding/allinone/skills/soul-extractor/scripts/assemble-output.sh`
- `[L6]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_community_signals_report.md`
- `[L7]` `Documents/vibecoding/allinone/experiments/exp01-v04-minimax/research/20260309_codex_skill_engineering_report.md`
