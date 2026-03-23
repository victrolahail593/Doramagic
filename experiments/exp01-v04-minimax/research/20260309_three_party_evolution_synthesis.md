# Soul Extractor 三个进化方向：三方研究综合分析

> 日期：2026-03-09
> 参与方：Opus（战略洞察）、Codex（工程可行性）、Gemini（产品价值）
> 决策者：Tangsir

## 1. 优先级排序——分歧与决策

| 研究方 | P0 | P1 | P2 |
|--------|----|----|----|
| **Opus（战略）** | 验证闭环 | WHY 层 | 拆解 |
| **Gemini（产品）** | 验证闭环 | WHY 层 | 拆解 |
| **Codex（工程）** | 验证闭环 | 拆解 | WHY 层 |

### Codex 调序理由（拆解 > WHY）
- 拆解复用现有 WHAT/HOW/IF 成果，不需要新能力
- 实现路径短（主要在组装层），风险低
- 验证容易（full pack vs domain pack 对比）
- WHY 来源难、验证难、弱模型容易把推断写成事实

### Gemini 反对理由（WHY > 拆解）
- WHY 是护城河（Moat 阶段），拆解只是体验优化（Growth 阶段）
- 没有 WHY，产品只是"更全的文档"，缺乏差异化
- 拆解只是省 Token，不影响核心价值

### Tangsir 最终决策

> **验证闭环 P0 → WHY 层 P1 → 拆解 P2**

理由：拆解重要，但不应该排在 WHY 之前。WHY 层是"专家级认知"的分水岭，是产品从"能用"到"有灵魂"的跃迁。拆解可以稍后做，WHY 不能等。

## 2. 核心共识（三方一致，Tangsir 完全同意）

1. **验证闭环必须先做** — 没有验证，扩能力只会放大错误
2. **脚本做硬校验 + 模型做软审查** — 不要二选一
3. **WHY 分两种：显式 WHY 可做，隐式 WHY 危险** — 弱模型会把推断写成事实
4. **拆解按问题域，不按代码模块** — 但内部需要 domain↔module 映射
5. **全量提取 + 组装阶段裁剪** — 不要在提取阶段做裁剪

## 3. 各方独有贡献汇总

### Codex 工程贡献

| 贡献 | 内容 |
|------|------|
| **Stage 3.5 Validate** | 完整设计：hard fail（格式/引用）+ soft fail（内容质量），含伪代码 |
| **验证指标体系** | 13 项指标，分结构合规/证据追溯/内容利用/质量判断四类 |
| **Hard gate 阈值** | format_compliance ≥ 0.95, traceability = 1.00, community_utilization ≥ 0.30, 至少 3 张 DR-100~ |
| **domain_map.yaml** | 问题域↔卡片↔文件↔API 的结构化映射 |
| **DRC 卡片模板** | design_rationale_card，借鉴 ADR/MADR，含 explicitness 三档 |
| **community_signals.json** | Markdown 给人读 + JSON 给脚本验证，双轨并行 |
| **WHY prompt 设计** | "不要问'为什么这样设计'，要问'哪些片段明确说了原因'" |
| **Rationale markers** | because, so that, to avoid, trade-off, chosen, decided 等关键词预筛 |

### Gemini 产品贡献

| 贡献 | 内容 |
|------|------|
| **用户价值矩阵** | 5 类用户 × WHY 层价值（新手够用、高级开发者不足、架构师完全不够） |
| **产品阶段定位** | MVP→PMF 过渡期；验证=PMF，WHY=Moat，拆解=Growth |
| **竞品防御** | "做 AI 原生知识的专业供应商"，Cursor 官方只会做通用索引 |
| **交互模式推荐** | C 模式（全自动推断）+ B 模式（提取后选择）兜底 |
| **低置信度处理** | 不删除，标注"Experimental/Low Confidence" |
| **路线图** | v0.7 验证信任 → v0.8 哲学提取 → v1.0 规模化生态 |

### Opus 战略贡献

| 贡献 | 内容 |
|------|------|
| **知识层次模型** | WHAT(CC) → HOW(WF) → IF(DR) → WHY(❌空白) |
| **人类 vs 自动提取对比** | 5 项 WHY 层知识被人类发现但自动提取完全遗漏 |
| **Superpowers 设计模式** | 7 个可借鉴模式，5 个已落实到 v0.6 |
| **互补关系定位** | Superpowers=方法论注入，Soul Extractor=知识注入 |

## 4. 确认的产品路线图

| 版本 | 目标 | 核心改动 | 产品阶段 |
|------|------|---------|---------|
| **v0.7** | 验证闭环 | Stage 3.5 Validate（脚本硬校验 + 模型软审查） | PMF — 可信赖 |
| **v0.8** | WHY 层提取 | Stage 2.5 Rationale + DRC 卡片 + rationale signals 采集 | Moat — 专家级 |
| **v0.9** | 拆解/定向注入 | domain_map.yaml + assembler --domain | Growth — 规模化 |
| **v1.0** | 生态整合 | 多格式导出 + 全自动推断 + 跨项目知识 | 成熟产品 |

## 5. v0.7 实施计划（下一步）

### 目标
在不换模型、不重写链路的前提下，让 v0.6 产物"可挡、可量化、可回归"。

### 改动清单
1. **新增** `scripts/validate_extraction.py` — 硬校验脚本
2. **新增** `stages/STAGE-3.5-review.md` — 模型软审查 prompt
3. **修改** `stages/STAGE-3-rules.md` — 输出格式约束强化
4. **修改** `scripts/assemble-output.sh` — 接入验证 gate
5. **修改** `SKILL.md` — 版本号 + 流程更新

### 验证指标（MVP hard gate）
- format_compliance_rate ≥ 0.95
- traceability_rate = 1.00
- community_source_validity = 1.00
- community_utilization ≥ 0.30
- 至少 3 张 DR-100~

### 设计原则
- 脚本做硬校验（格式、引用、字段）— 确定性问题
- 模型做软审查（具体性、真实性、严重度匹配）— 语义问题
- 生成与审查分阶段、分输入
- 弱模型审查时：分卡审查、固定 rubric、结构化输出

## 6. 研究来源索引

- `20260309_codex_evolution_directions_report.md` — Codex 工程可行性报告（1211 行）
- `20260309_gemini_evolution_directions_report.md` — Gemini 产品价值报告（75 行）
- `20260309_codex_community_signals_report.md` — Codex 社区信号工程报告（前序）
- `20260309_gemini_community_signals_report.md` — Gemini 社区信号产品报告（前序）
