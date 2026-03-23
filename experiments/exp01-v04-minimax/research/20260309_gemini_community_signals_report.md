# 社区信号对 AI 燃料价值与信息设计的研究报告 (v0.1)

## 1. 社区信号对 "AI 燃料" 质量的真实影响 (Q1 分析)

**核心结论：社区信号将 AI 从“懂代码的机器人”提升为“有经验的专家”。**

*   **行为改变的本质**：
    *   **代码分析规则**（静态知识）：告诉 AI “怎么写能跑通”。AI 会生成符合语法的代码，但可能触发性能瓶颈或已知 Bug。
    *   **社区经验规则**（条件知识）：告诉 AI “怎么写不踩坑”。AI 在生成代码时，会感知到特定的上下文（如多行字符串处理），从而主动选择绕过已知 Issue 的写法（如自动添加转义符）。
*   **具体规则 vs 抽象规则**：
    *   **具体规则（带 Issue 证据）更有效**。LLM（特别是弱模型）在面对“不要做 X”这种指令时，容易因缺乏上下文而忘记执行。但如果指令包含“Issue #89 报告了 29 人遇到过此问题，原因是解析器不支持...”，模型会将其理解为高权重的“故障预防逻辑”，在生成代码时具备更强的确定性。
*   **噪声风险管理**：
    *   风险确实存在。如果采集中包含大量“环境配置失败”或“已在两年前修复”的 Issue，会稀释规则库的密度。
    *   **对策**：必须引入**热度（Reactions）**和**时效（Last Updated）**作为首层过滤器。

## 2. 社区信号的信息价值分层 (Q2 分析)

针对不同信号源的价值密度评估（Tier List）：

| 来源 | 价值评分 | 优先级 | 核心理由 |
|------|----------|--------|----------|
| **CHANGELOG (breaking changes)** | ⭐⭐⭐⭐⭐ | P0 | 确定性最高，是 AI 防止代码在中大型重构中崩溃的“救命稻草”。 |
| **GitHub Issues (高赞 bug)** | ⭐⭐⭐⭐⭐ | P0 | 代表了真实世界的通用痛点。20+ Reactions 的 Bug 通常对应着代码层难以察觉的边界情况。 |
| **README FAQ / Troubleshooting** | ⭐⭐⭐⭐ | P1 | 开发者亲手总结的高频误区，信息密度极高，无需模型二次过滤。 |
| **GitHub Issues (question 标签)** | ⭐⭐⭐ | P2 | 价值在于发现“API 易用性设计缺陷”，可转化为编程助手中的最佳实践建议。 |
| **git log fix: commits** | ⭐⭐⭐ | P2 | 数据量巨大，适合挖掘那些没有显式 Issue 但频繁出现的 Bugfix 模式。 |
| **Stack Overflow 高票问答** | ⭐⭐⭐⭐ | P3 | 价值极高但采集成本（反爬、关联性）过高，暂列 P3。 |

## 3. community_signals.md 的信息设计 (Q3 分析)

**3.1 Tokens 权衡与摘要策略**
*   **Token 预算**：建议控制在 20K-30K Tokens（约占弱模型上下文的 20%）。
*   **策略**：不推荐给模型原始数据。脚本层应进行**结构化预处理**：仅保留 Issue Title、Top 3 Comments 摘要、Reactions 计数。

**3.2 面向弱模型 (MiniMax-M2.5) 的格式建议**
推荐使用带有 **XML 标签的 Markdown 列表**：
```markdown
<signal_item id="ISU-89" type="bug" heat="29">
  <title>Multiline strings truncated in parser</title>
  <context>Happens when using unquoted values with # comments</context>
  <impact>Data corruption or silent failure during parsing</impact>
</signal_item>
```
这种格式比 YAML 更能抗模型幻觉，且 `id` 方便后续追溯。

**3.3 去重与关联逻辑**
*   **语义聚类**：脚本层应对 Title 进行简单的关键词匹配（如 `multiline`, `parser`, `#`）。如果多个信号指向同一根因，在文件中进行物理合并，标注 `Shared by Issue #89, #102`。

## 4. DR-100~ 社区陷阱卡的产品形态 (Q4 分析)

*   **Source 引用**：使用 `community:issue#89` 或 `community:changelog:v1.0.0`。这增加了 AI 给出建议时的置信度（Confidence）。
*   **Severity 评估逻辑**：
    *   **CRITICAL**: 导致生产事故、数据丢失（对应 CHANGELOG Breaking Change 或 50+ Reactions Bug）。
    *   **HIGH**: 导致功能不可用（20+ Reactions）。
    *   **MEDIUM**: 导致易用性问题、性能轻微下降。
*   **融合策略**：如果一个问题既有代码证据又有社区证据，应**合并为一张卡**。代码分析提供“原理证明”，社区信号提供“威力评估”。

## 5. 用户感知价值 (Q5 分析)

*   **差异化卖点**：这是 Soul Extractor 的**核心护城河**。市面上的工具大多在做代码分析，但“能够预知 29 人踩过的坑”能带给开发者极大的心理安全感。
*   **总结页面建议**：在 `project_soul.md` 中增加 **“避坑指南 (Pitfall Alerts)”** 章节，直接列出受社区关注度最高的前 5 个陷阱。这比技术架构图更能打动 CEO 和一线开发者。

## 6. 竞品分析 (Q6)

*   **Repomix**: 纯代码打包工具，无社区数据支持。
*   **Cursor @docs**: 依赖用户提供的文档 URL，不具备主动挖掘 Issues 陷阱的能力。
*   **GitHub Copilot**: 虽然其底层训练数据包含代码库，但无法针对**当前特定版本**的特定已知 Bug 给出实时的规则限制。
*   **结论**：这是一个巨大的**垂直领域机会**。目前的工具多在解决“怎么写”，而没有解决“基于当前版本状况，别怎么写”。

## 7. 推荐的信息架构模板 (community_signals.md)

```markdown
# Community Intelligence Signals for [RepoName]

## Tier 1: Critical Breaking Changes (From CHANGELOG)
- [v1.2.0] Removal of `legacy_parser`. Use `new_parser` instead. (Impact: HIGH)

## Tier 2: High-Frequency Pitfalls (From Issues > 10 reactions)
### [SIGNAL-001] Multiline strings parsing error
- **Source**: Issue #89 (29 reactions), Issue #102
- **Symptoms**: Values starting with # are treated as comments even if multiline.
- **Workaround**: Use explicit quotes for all multiline values.

## Tier 3: FAQ & Common Questions (From README/Discussions)
- Q: Why is my .env not loading in Docker?
- A: Ensure the working directory is set correctly; load_dotenv() is path-sensitive.
```

## 8. 行动计划

1.  **Phase 1 (短期/验证)**:
    *   修改 `prepare-repo.sh`，利用 GitHub CLI (`gh issue list --sort reactions --limit 30`) 快速采集 top issues。
    *   手动测试：将采集到的信号注入 `STAGE-3`，观察 MiniMax 是否能产出 DR-100 系列卡片。
2.  **Phase 2 (中期/工程化)**:
    *   优化 `community_signals.md` 的信息压缩算法（摘要化）。
    *   在 `project_soul.md` 中增加“社区避坑”可视化模块。
3.  **Phase 3 (长期/闭环)**:
    *   引入版本号匹配逻辑，确保提取的“社区陷阱”适用于用户当前的库版本。

---
**战略建议**：社区信号是让 Soul Extractor 从“工具”进化为“服务”的关键。**重度投入**。这不仅是燃料质量的提升，更是产品溢价的核心来源。
