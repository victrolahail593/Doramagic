---
name: doramagic
description: >
  从开源世界找最好的作业，提取智慧（WHY + UNSAID），
  锻造开袋即食的 OpenClaw Skill。
  双引擎：Python 脚本负责确定性事实提取，AI 负责灵魂提取和跨项目综合。
  Triggers on: /dora, doramagic, 帮我做一个, 我想做一个, forge skill, 锻造 skill
version: 3.1.0
user-invocable: true
allowed-tools: [exec, read, write]
tags: [doramagic, knowledge-extraction, skill-generation, s1-sonnet]
metadata:
  openclaw:
    skillKey: dora
    category: builder
    requires:
      bins: [python3, curl, unzip]
    storage_root: ~/clawd/doramagic/s1-sonnet/
---

# Doramagic S1-Sonnet v3.1 — 双引擎版

> 不教用户做事，给他工具。——哆啦A梦式产品哲学
>
> 双引擎：Python 负责确定性提取（facts/frameworks），AI 负责灵魂提取（WHY/UNSAID/综合）。

## 触发方式

`/dora <需求>` | `doramagic <需求>` | `帮我做一个 XXX` | `forge skill <需求>`

收到后立即回复："收到！开始 Phase A..."，然后按顺序执行。

---

## 暗雷知识库（DSD — Phase B 过滤依据）

**Top 10 暗雷速查：**

| # | 暗雷 | 检测方式 |
|---|------|---------|
| 1 | **LLM 过度推理** | 代码无注释，WHY 置信度全高分 → 注释密度 < 5% |
| 2 | **隐性规模假设** | 大公司架构 + 小业务逻辑 → 基础设施复杂度倒挂 |
| 3 | **架构考古遗址** | CHANGELOG 出现 "rewrite/overhaul"，同时依赖新旧替代库 |
| 4 | **开源包闭源魂** | API wrapper 行数 > 业务逻辑行数，核心依赖闭源 SaaS |
| 5 | **Hidden Context** | "discussed offline/internal" 频繁出现 |
| 6 | **维护者独白社区** | 独立参与者 / Issue 数 < 2 |
| 7 | **Winner's History** | narrative 与早期 PR 历史不一致 |
| 8 | **Exception Bias** | 高互动线程异常/边缘场景占比 > 60% |
| 9 | **简历驱动开发** | 实体数量 << 抽象层数量 |
| 10 | **幽灵约束** | 为已修复旧 bug 做的反直觉设计 |

**DSD 8 项指标（深度扫描）：**

| # | 指标 | 风险阈值 |
|---|------|---------|
| 1 | Rationale Support Ratio | < 0.3（WHY 证据数 / 叙事断言数） |
| 2 | Temporal Conflict Score | CHANGELOG "rewrite/overhaul/migration" |
| 3 | Exception Dominance Ratio | > 60% 高互动线程是异常场景 |
| 4 | Support-Desk Share | > 70% 求助线程 |
| 5 | Public Context Completeness | "discussed offline/internal" 频繁 |
| 6 | Persona Divergence Score | 同一项目服务差异过大的用户群体 |
| 7 | Dependency Dominance Index | > 1（API wrapper 行数 / 业务逻辑行数） |
| 8 | Narrative-Evidence Tension | WHY 置信度全高 = 过度推理信号 |

**暗雷叠加：** 1 个→低风险标注；2 个→中危，LIMITATIONS 专节；3+→高危，建议替换项目。

---

## Phase A：需求理解（AI-native）

解析用户输入为 need_profile：`domain / keywords(3-5) / intent / constraints / anti_keywords / domain_id`

生成 `run_id`（`YYYYMMDD_HHMMSS`），写 `{storage_root}/runs/{run_id}/need_profile.json`。
向用户展示解析结果，说："Phase A 完成，开始发现作业..."

---

## Phase B：作业发现（AI + exec）

**B-0（可选）：** `exec curl -s --max-time 5 http://192.168.1.104:8420/domains/{domain_id}/bricks`
命中→注入先验知识；失败→跳过。

**B-1：GitHub 搜索：**
```bash
exec python3 {skill_dir}/scripts/github_search.py \
  "{kw1}" "{kw2}" "{kw3}" --top 8 \
  --output {run_dir}/discovery.json
```

**B-2：AI 筛选（3-5 个，必须 ≥ 2）：** stars > 50 优先，语义相关性，updated_at 较新。
每个候选检查至少 3 个 DSD 指标。触发 3+ 个暗雷的项目降级或替换。

**B-3：下载项目：**
```bash
exec python3 {skill_dir}/scripts/github_search.py \
  --download "owner/repo" --branch main --output {run_dir}/repos/
```
（每个选中的 repo 各执行一次）

写 `{run_dir}/repos.json`，告知用户已下载哪些项目。

---

## Phase C：逐 Repo 双引擎提取

对每个 repo 依次执行 C-1 和 C-2。

### C-1：确定性提取（exec）

```bash
exec python3 {skill_dir}/scripts/extract_facts.py \
  --repo-path {run_dir}/repos/{repo_name} \
  --output {run_dir}/extractions/{repo_name}/repo_facts.json \
  --repo-id {repo_name} \
  --repo-url {repo_url}
```

### C-2：AI 灵魂提取（你自己做，不是 exec）

**读取内容（只读关键文件，不要读整个 repo）：**
1. `README.md`（第一优先）
2. `{run_dir}/extractions/{repo_name}/repo_facts.json`（C-1 事实骨架）
3. 主入口（`main.py` / `index.ts` / `cmd/root.go`，≤ 300 行）
4. 核心模块（1-2 个，按 repo_facts.json top_files 字段选择）
5. `CHANGELOG.md` 前 100 行

**你必须回答以下 5 个问题，每条都要求有证据（file:line 或 Issue# 或 CHANGELOG 版本）：**

**Q1 — 设计信念（WHY it exists this way）**
这个项目的核心设计信念是什么？不是"做什么"，而是"为什么这样设计"。
像创造者对顶级工程师说话一样写，是信念宣言而非功能描述。

首先完成 **WHY 可恢复性判断**：
- ADR / `// because ...` 注释 / 设计文档 → 可恢复（confidence: high）
- README/CONTRIBUTING 有设计哲学段落 → 可恢复（confidence: high）
- Issues/PRs 有设计决策讨论 → 可恢复（confidence: medium，社区证据）
- 以上全无，但代码模式强烈暗示 → 可推断（confidence: low，必须标注）
- 核心逻辑在闭源服务 → 不可恢复（写明原因，仍提供推测版，标注 confidence: low）

**Q2 — 心智模型**
理解这个项目的正确心智模型是什么？用一个隐喻或类比。
"如果一个专家只能说一句话让你顿悟，那句话是什么？"

**Q3 — 关键设计决策（evidence-bound）**
有哪些关键的设计决策？为什么选 A 不选 B？
每条必须指向：`file:line` 或 README section 名称 或 `Issue #NNN`。
没有证据 → 标注 `confidence: low`，仍然写出来。

**Q4 — 文档盲区（UNSAID traps）**
文档没说但你会踩的坑有哪些？从以下推断：
- 代码中的边界条件和防御性写法（什么情况下会出问题）
- Issue 标题高频词（"not working when...", "breaks if..."）
- CHANGELOG 的 bugfix 条目（修了什么，说明之前会失败）
每条标注：`severity`（HIGH/MEDIUM/LOW）+ 来源引用。

**Q5 — 社区反复踩的坑**
从 Issues/CHANGELOG 中，社区反复遇到什么问题？
标注：`Issue #NNN（N reactions）`+ workaround（如何避免）。

**完成 5 个问题后，写 `{run_dir}/extractions/{repo_name}/soul.json`：**

```json
{
  "project_name": "repo_name",
  "why_recoverability": "recoverable | inferable | unrecoverable",
  "design_philosophy": "设计信念（Q1）",
  "mental_model": "心智模型隐喻（Q2）",
  "why_decisions": [
    {"decision": "为什么用 X 不用 Y", "evidence": "file:line 或 Issue #NNN", "confidence": "high|medium|low"}
  ],
  "unsaid_traps": [
    {"trap": "文档没说的坑", "evidence": "代码模式 或 Issue #NNN 或 CHANGELOG vX.Y", "severity": "HIGH|MEDIUM|LOW"}
  ],
  "capabilities": ["核心能力1", "核心能力2"],
  "community_traps": [
    {"trap": "社区反复的问题", "source": "Issue #NNN (N reactions)", "workaround": "如何避免"}
  ]
}
```

告知用户："[repo_name] 灵魂提取完成（WHY: N 条，UNSAID: N 条）。"

---

## Phase D：跨项目综合（AI 直接执行）

读取所有 `soul.json`，写 `{run_dir}/synthesis.json`：

```json
{
  "domain": "{domain}",
  "consensus": [{"insight": "...", "supported_by": ["repo1", "repo2"]}],
  "conflicts": [{"topic": "...", "positions": {"repo1": "...", "repo2": "..."}, "recommendation": "..."}],
  "unique_insights": [{"insight": "...", "from": "repo_name", "why_valuable": "..."}],
  "unified_mental_model": "结合所有项目的统一理解框架"
}
```

---

## Phase E-F：编译交付（AI 直接执行）

读取 `synthesis.json` + 所有 `soul.json`，写三个文件到 `{run_dir}/delivery/`。

**SKILL.md（≥ 5KB）必须包含：**
- 正确 OpenClaw frontmatter（skillKey, allowed-tools, install 路径）
- Purpose / Capabilities / **设计哲学（WHY）** / **已知陷阱（UNSAID）** / Workflow / Storage / LIMITATIONS

  WHY 每条注明来源 repo；UNSAID 每条引用 Issue# 或 file:line，标 severity。

**PROVENANCE.md：** 参考项目清单（URL/stars/license）+ 每个知识点来源追踪。

**LIMITATIONS.md：** 分析日期 + 覆盖项目数 + 未覆盖能力 + 冲突未解决 + confidence: low 的 WHY 清单 + 暗雷触发记录。

**Hard Gate：** SKILL.md 缺少"设计哲学"或"已知陷阱"章节 → 不合格，重新编译，不允许交付空壳。

---

## Phase 报告：向用户汇报（AI-native）

读 delivery/ 三个文件，汇报：
1. 提取概览（分析了哪些 repo，⭐数）
2. Skill 核心能力（一句话）
3. 设计哲学要点（2-3 条，含来源 repo）
4. 已知陷阱要点（2-3 条，含 Issue 编号）
5. 安装：delivery/SKILL.md 放到 OpenClaw skills/ 目录
6. 已知限制（覆盖项目数，confidence: low 数量）

最后说："这份 Skill 已就绪。如果陷阱描述不准确或 WHY 有误，告诉我，我来更新。"

---

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| GitHub API 限速（403/429） | 等待 10 秒重试一次，失败后继续其他项目 |
| 下载超时 | 尝试 master 分支，失败后跳过 |
| repo_facts.json 提取失败 | C-2 仍执行，仅基于读取的源代码 |
| Issues 获取失败 | Q5 标注"无社区数据"，LIMITATIONS 注明 |
| 只有 1 个项目成功 | 跳过 Phase D，降级交付，LIMITATIONS 注明 |
| SKILL.md 缺 WHY/UNSAID | Hard Gate 失败，重新编译 |
| discovery.json 为空 | 调整关键词重搜，或请用户补充描述 |
| 暗雷高危（3+） | LIMITATIONS 专节说明，建议替换项目 |

---

## 关键约束

1. **AI 主导，Python 辅助** — Python 只做确定性提取，WHY/UNSAID/综合全部 AI 执行
2. **WHY 必须有证据** — 每条指向文件/Issue/CHANGELOG，无证据标 confidence: low
3. **UNSAID 必须有来源** — 引用 Issue# 或代码模式或 CHANGELOG 条目
4. **只读关键文件** — README + 主入口 + 核心模块 + CHANGELOG，不读整个 repo
5. **≥ 2 个项目** — 至少 1 个成功可降级交付
6. **soul.json 是中间产物** — 用户看 SKILL.md，不看 soul.json
7. **OpenClaw 适配** — 存储路径只用 `~/clawd/`
8. **真实数据** — 不 mock，不 fallback 到虚构内容
