# Doramagic 全量研究集成开发 Brief

> 日期：2026-03-20
> 目标：将全部研究成果一次性集成到产品中，产出完整可用的 Doramagic Skill
> 前置必读：docs/supplementary-dev-brief.md（产品形态）、docs/product-design-adjustment.md（架构调整）

---

## 背景

Doramagic 经过 25+ 个 Session 的研究和实践，积累了大量已验证的方法论和实验结论。前几轮开发只用到了其中一小部分（7 问框架 + 确定性脚本 + validator）。本轮的目标是**把全部研究成果一次性变成产品能力**。

---

## 必须集成的 8 项研究成果

### 1. WHY 可恢复性判断

**研究结论**：不是每个项目都值得提取 WHY。如果项目缺少 rationale evidence（无 ADR、无 trade-off 文档、无维护者解释），强行提取 WHY 会导致 LLM 编造看似合理但虚假的设计哲学。

**落地要求**：
- Phase C 提取前，AI 先评估 WHY 可恢复性：
  - 是否有 README 的 "Why/Motivation/Philosophy" 段落？
  - 是否有 ADR (Architecture Decision Records) 文件？
  - 是否有 Issue/PR 中维护者的设计解释？
  - 是否有 CHANGELOG 中 "by design/won't implement" 的边界声明？
- 如果以上全无，输出：**"WHY 无法从公开证据可靠重建"**，在 SKILL.md 中标注"WHY 部分为推断，置信度低"
- 不允许在没有证据的情况下编造流畅的设计哲学

### 2. Deceptive Source Detection（8 项暗雷检测指标）

**研究结论**：最危险的项目不是明显差的，而是"看起来像好作业"但会误导提取的。8 个检测指标：

| # | 指标 | 检测什么 | 如何检测 |
|---|------|---------|---------|
| 1 | Rationale Support Ratio | WHY 证据数 / 叙事断言数 | 比值 < 0.3 为高风险 |
| 2 | Temporal Conflict Score | 跨版本冲突建议 | CHANGELOG 中 "rewrite/overhaul/migration" 关键词 |
| 3 | Exception Dominance Ratio | 高互动线程中异常/边缘场景占比 | > 60% 为高风险 |
| 4 | Support-Desk Share | 求助线程占全部线程比 | > 70% 说明项目门槛高 |
| 5 | Public Context Completeness | 公开讨论完整度 | "discussed offline/internal" 频繁出现为高风险 |
| 6 | Persona Divergence Score | 受众分叉度 | 同一项目服务差异过大的用户群体 |
| 7 | Dependency Dominance Index | 行为是否由上游库决定 | API wrapper 行数 > 业务逻辑行数为高风险 |
| 8 | Narrative-Evidence Tension | 叙事流畅但证据薄弱 | WHY 置信度全部高分 = 过度推理信号 |

**落地要求**：
- Phase B 筛选项目时，AI 对每个候选项目做暗雷快速扫描
- Phase G validate_skill.py 增加暗雷检测：检查产出的 SKILL.md 中 WHY 是否有过度推理迹象
- PROVENANCE.md 对每条 WHY 标注 Rationale Support Ratio（有直接证据 / 推断 / 无证据）

### 3. 暗雷叠加效应警告

**研究结论**：多个暗雷同时出现时风险指数增长。最危险的组合：
- 过度推理 + 架构考古 → LLM 用"优雅叙事"调和新旧矛盾
- 过度推理 + 文档代码脱节 → README 提供锚点，LLM 强行确认
- 隐性规模 + 项目人气高 → 系统性选择不适合目标用户的作业

**落地要求**：
- SKILL.md 中明确告知 AI：如果一个项目同时触发 2+ 个暗雷指标，整体风险等级升至"高危"，在 LIMITATIONS.md 中专门标注

### 4. Soul Extractor 完整提取流程（Stage 1-4）

**研究结论**：Soul Extractor 已验证的提取流程（42%→96% 提升）包含 7 个阶段。当前产品只用了 Stage 1（7 问），没有用 Stage 2-4。

**落地要求**：
- SKILL.md Phase C 必须引导 AI 按以下完整流程提取：

**Stage 1（广度扫描）**：回答 Q1-Q7，参考 `skills/soul-extractor/stages/STAGE-1-essence.md`
**Stage 2（概念提取）**：提取概念卡 + 工作流卡，参考 `skills/soul-extractor/stages/STAGE-2-concepts.md`
**Stage 3（规则提取）**：提取决策规则卡（含 UNSAID），参考 `skills/soul-extractor/stages/STAGE-3-rules.md`
**Stage 3.5（硬验证）**：事实检查 + 暗雷审查，参考 `skills/soul-extractor/stages/STAGE-3.5-review.md`
**Stage 4（叙事合成，可选）**：专家级知识合成，参考 `skills/soul-extractor/stages/STAGE-4-synthesis.md`

- AI 在执行每个 Stage 时，先 `read` 对应的 STAGE-*.md 文件获取详细指令

### 5. 知识卡片体系（5 类型）

**研究结论**：知识不是一篇文档，是一组可拼装的类型化对象。5 类卡片：

| 卡片类型 | 对应什么知识 | 格式要求 |
|---------|------------|---------|
| 概念卡 (Concept Card) | 核心概念的 Is/IsNot/属性/边界 | YAML frontmatter + 结构化字段 |
| 工作流卡 (Workflow Card) | 步骤 + Mermaid 流程图 + 失败模式 | YAML frontmatter + 步骤列表 |
| 决策卡 (Decision Card) | 架构决策 + 理由 + 替代方案 | YAML frontmatter + 规则/上下文/Do/Don't |
| 陷阱卡 (Trap Card) | UNSAID 社区踩坑经验 | YAML frontmatter + 陷阱描述/来源/严重度 |
| 特征卡 (Signature Card) | 项目独有特征 | YAML frontmatter + 特征描述 |

**落地要求**：
- Phase C 的提取输出不只是 Q1-Q7 文本，而是结构化的知识卡片
- 最终 SKILL.md 的内容从知识卡片编译而来（事实→结构化，哲学→叙事，踩坑→警告列表）
- PROVENANCE.md 按卡片 ID 追溯来源

### 6. 跨项目综合（真实多项目）

**研究结论**：跨项目比较能发现单项目看不到的共识、冲突和假公约数。`support_independence`（来源独立性）是防假公约数的生死线。

**落地要求**：
- Phase B 必须搜索并下载 **至少 2 个项目**（不是只下载 1 个）
- Phase C 对每个项目独立提取知识卡片
- Phase E 做跨项目综合：
  - 共识：多个项目做了相同选择 → 高置信度 brick
  - 冲突：不同项目做了不同选择 → 标注冲突，不替用户决策
  - 独有：只有一个项目有的知识 → 标注来源单一
  - 假公约数检测：多项目指向同一上游时标注"非独立验证"
- 可选：exec 调用 `packages/cross_project/doramagic_cross_project/compare.py` 做结构化对比

### 7. 社区信号自动采集

**研究结论**：社区经验（Issue/PR/CHANGELOG）是 UNSAID 的核心来源。已有脚本 `skills/soul-extractor/scripts/collect-community-signals.py` 可自动采集。

**落地要求**：
- Phase D 通过 exec 调用 GitHub API 获取 issues/PRs
- AI 从中提取：
  - 高频问题类型（出现 3 次以上）
  - 高评论 issues（社区有强烈感受的点）
  - "won't fix"/"by design" 回复（维护者边界声明 = 隐含 WHY）
  - bug 标签分布（反映真实使用中的痛点）
- 社区信号写入 陷阱卡（Trap Card），标注来源 issue 编号

### 8. 预提取领域 Domain Bricks 集成

**研究结论**：6 个首批预提取领域已确定。连接预提取 API 时获得 +20% 提取质量。

**落地要求**：
- Phase B 开始时，先尝试查询预提取 API（如果可用）：
  ```bash
  exec curl -s http://192.168.1.104:8420/domains/{domain_id}/bricks 2>/dev/null
  ```
- 如果 API 返回 domain bricks，注入到 Phase C 作为先验知识（提升提取质量）
- 如果 API 不可用，跳过，独立完成全流程（API 是加成不是依赖）
- 对本次验证场景，如果 domain 命中已预提取领域则展示加速效果

---

## 交付要求

### 文件结构

```
skills/doramagic-{选手}/
├── SKILL.md                     ← 集成全部 8 项研究成果的完整指令
├── scripts/
│   ├── github_search.py         ← 复用 skills/doramagic/scripts/github_search.py
│   ├── extract_facts.py         ← 确定性事实提取
│   ├── validate_skill.py        ← 质量检查 + 暗雷检测 + WHY 可恢复性
│   ├── assemble_output.py       ← 从知识卡片编译最终输出
│   └── community_signals.py     ← 社区信号采集（参考 collect-community-signals.py）
├── cards/                        ← 知识卡片输出目录
│   ├── concept/
│   ├── workflow/
│   ├── decision/
│   ├── trap/
│   └── signature/
└── README.md
```

### 验证方式

**必须同时满足以下全部条件：**

1. 输入 `/dora 我想做一个管理 WiFi 密码的工具`（不是菜谱，换个需求）
2. 真实调 GitHub API 搜索并下载 **至少 2 个** 项目
3. 对每个项目走 Stage 1-3.5 完整提取流程（读 STAGE-*.md）
4. 产出结构化知识卡片（至少 3 张概念卡 + 2 张决策卡 + 2 张陷阱卡）
5. 做 WHY 可恢复性评估（至少 1 个项目标注"WHY 证据充分"或"WHY 无法可靠重建"）
6. 做暗雷快扫（至少检查 3 个 DSD 指标）
7. 跨项目综合（标注共识/冲突/独有）
8. 最终 SKILL.md 包含 WHY + UNSAID + 知识卡片编译内容
9. PROVENANCE.md 按卡片 ID 追溯
10. LIMITATIONS.md 包含暗雷评估结果和覆盖范围
11. validator PASS 或合理的 REVISE 说明

---

## 参考资产（必须充分利用）

| 资产 | 位置 | 用法 |
|------|------|------|
| Soul Extractor 7 阶段提取指令 | `skills/soul-extractor/stages/STAGE-*.md` | AI 在 Phase C 读取并按指令执行 |
| GitHub 搜索脚本 | `skills/doramagic/scripts/github_search.py` | exec 调用搜索和下载 |
| 确定性事实提取 | `skills/doramagic/scripts/extract_facts.py` | exec 调用 |
| 社区信号采集参考 | `skills/soul-extractor/scripts/collect-community-signals.py` | 参考实现 |
| Validator | `skills/doramagic/scripts/validate_skill.py` | exec 调用，需扩展暗雷检测 |
| 跨项目比较 | `packages/cross_project/doramagic_cross_project/compare.py` | 可选 exec 调用 |
| 暗雷研究完整文档 | 见下方"Top 10 暗雷"章节 | AI 执行暗雷扫描时的参考知识 |

---

## Top 10 暗雷速查（嵌入 SKILL.md 供 AI 参考）

1. **LLM 过度推理**：代码简洁无注释，LLM 为技术选择编造 WHY → 检查注释密度 < 5%
2. **隐性规模假设**：大公司架构用于小团队 → 基础设施复杂度 vs 业务复杂度倒挂
3. **架构考古遗址**：新旧架构混合 → CHANGELOG "rewrite/overhaul" + 同时依赖替代库
4. **开源包闭源魂**：核心依赖闭源 SaaS → API wrapper 行数 > 业务逻辑行数
5. **Hidden Context**：决策在 Slack/内部发生 → "discussed offline/internal" 频繁
6. **维护者独白社区**：社区看似活跃但只有 1-2 人回复 → 独立参与者 / Issue 数 < 2
7. **Winner's History**：叙事是事后美化 → narrative 与早期 PR 历史不一致
8. **Exception Bias**：讨论集中在边缘场景 → 高互动线程异常占比 > 60%
9. **简历驱动开发**：过度工程化 → 实体数量 << 抽象层数量
10. **幽灵约束**：为已修复的旧 bug 做的反直觉设计 → 追溯引入年份

---

## 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 研究成果集成完整度 | 30% | 8 项是否全部落地 |
| WHY/UNSAID 提取质量 | 25% | 知识卡片质量、暗雷检测效果 |
| 真实数据端到端 | 20% | 多项目真实搜索/下载/提取/综合 |
| 产品形态正确性 | 15% | Skill 形态、AI 即 LLM、不绑 SDK |
| 已有资产复用 | 10% | STAGE-*.md、scripts、validator |
