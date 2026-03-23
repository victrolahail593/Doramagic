# 错误共识检测（False Consensus Detection）— 三方研究综合报告

> 日期：2026-03-15
> 三方：Claude Opus（知识工程+理论框架）/ Gemini（产品+用户价值）/ Codex（工程实现+算法）

---

## 一、四项全票共识

### 共识 1：输出风险信号，不输出对错判断

- **Claude**：不说"这是错的"，说"这条知识有以下风险特征"
- **Codex**：计算 consensus_risk_score，不做硬判定
- **Gemini**：禁止"错误共识"措辞，用"高风险共识"或"认知脆弱性"

**结论**："不教用户做事"原则的直接推论。Doramagic 没有资格判断对错，只能标注风险信号。

### 共识 2：偏向漏报，不偏向误报

- **Claude**：误报（标记正确知识为"可疑"）的代价远高于漏报
- **Codex**：保守设计，高误报成本
- **Gemini**：如果标错了"正品牌损害有多大"→ 必须保守

**结论**：宁可放过错误共识，也不能冤枉正确共识。

### 共识 3：不需要新的信号类型，在现有体系上叠加

- **Claude**：不需要第 8 类信号，在 ALIGNED 上叠加 `consensus_risk` 标注
- **Codex**：cluster enrichment pass，不改 Health Check 信号分类
- **Gemini**：Tier-0 暗雷，复用 Stage 3.5 机制

**结论**：错误共识检测是风险叠加层，不是新分类。

### 共识 4：前置依赖是 provenance clustering + 显式来源提取

- **Claude**：LATER，在 Health Check V1 + 供应链 P1 完成后
- **Codex**：NOW-LITE，但承认"在 provenance clustering 之后做"
- **Gemini**：先嵌入探针（beta）

**结论**：错误共识检测建立在来源追踪之上。没有来源信息，大部分信号无法触发。

---

## 二、各方独有最佳贡献

### Claude 独有：理论分类 + 信号体系

1. **五种错误共识子类型**（认知科学角度）：
   - 共同认知偏差（相关性→因果性误读）
   - 过时共识（曾对现错，频率最高）
   - 数据源错误（原始研究有缺陷）
   - 正确数据+错误解读（数据对但解读错）
   - 幸存者偏差（只看到成功案例）

2. **六个代理信号 + 精度估算**：
   | 信号 | 精度 |
   |------|------|
   | Evidence-Assertion Gap（强断言弱证据）| ~0.5-0.6 |
   | Temporal Freeze（时间冻结）| ~0.6-0.7 |
   | Uniformity Anomaly（一致性异常）| ~0.4-0.5 |
   | Scope Absence（适用域缺失）| ~0.5-0.6 |
   | Contradicts Official（与官方矛盾）| ~0.7-0.8 |
   | Single-Study Dependency（单一研究依赖）| ~0.6-0.7 |

3. **信号组合规则**：1 信号=CONTEXT / 2 信号=SIGNAL / 3+=HIGH-SIGNAL

4. **完整案例分析表**：
   - "134-167 词" → HIGH-SIGNAL（4 信号命中）
   - "YouTube 0.737" → SIGNAL（3 信号）
   - "FAQPage 限制" → 无风险（官方来源+时间锚）
   - **风险率 ~4-6%**

5. **关键区分**：回声/扭曲是"传播层"问题，错误共识是"认知层"问题——知识流动正常，错在起点

6. **新洞察**：二维置信度升级（支持度 × 可靠性），学术 GRADE 评级体系可映射

### Codex 独有：工程实现

1. **七个风险信号**（比 Claude 多 2 个）：
   - S1-S6 与 Claude 大致对应
   - **S4 新增：Interpretation Escalation（解读升级/因果通胀）**：检测"相关性→因果性"的逻辑跳跃
   - **S7 新增：Implementation Gap（实现落差）**：代码中声称的功能未实际实现

2. **评分模型**：硬门控 + noisy-OR 组合（不是加权求和，不是决策树）

3. **`score_consensus_risk()` 完整伪代码**

4. **`consensus_risk_profile` JSON Schema**

5. **集成位置**：cluster enrichment pass，在 provenance clustering 之后、Health Check 之前

6. **判断：NOW-LITE**：
   - V1 先做 4 个关键信号（S1/S2/S5/S6），成本低
   - 后续扩展到 7 个
   - 10+ 项目才真正有效

7. **校准策略**：用已知正确共识（FAQPage/INP）和已知可疑共识（134-167 词）做回归校准

### Gemini 独有：产品定位

1. **错误共识 = Tier-0 暗雷**：系统级感染，不是单项目问题。在暗雷排序中应位于最高层

2. **术语设计**：禁止"错误共识"/"这是错的"，推荐"高风险共识"/"认知脆弱性"

3. **用户情感弧线**：震惊→验证→感激。"只要命中一次，用户就成死忠粉"

4. **企业级场景**：CTO 审计团队技术共识，高利润审计模块

5. **差异化定位**：发现整个技术生态的认知 Bug（Why 层），不只是代码 Bug（How 层）

6. **判断**：现在不做核心功能，嵌入探针（beta），需要 50+ 项目才有效

---

## 三、分歧与决策建议

### 分歧 1：时机

- **Claude**：LATER（Health Check V1 + 供应链 P1 完成后，1-2 天）
- **Codex**：NOW-LITE（4 个信号先做，成本低）
- **Gemini**：嵌入探针（beta），需 50+ 项目

**决策建议：采 Claude 的 LATER。** 理由：
1. 前置依赖（provenance clustering + 显式来源提取）是三方共识
2. 供应链 P1 还没做，错误共识检测没有数据基础
3. Codex 的 NOW-LITE 在技术上可行，但产品上过早——4 个项目的风险信号太少，误报风险高
4. Gemini 的 50+ 过于保守，10-15 项目就足够

**具体时机**：供应链 P1（显式来源 + provenance clustering）完成后，花 1-2 天做 MVP。

### 分歧 2：信号数量

- **Claude**：6 个信号
- **Codex**：7 个信号（多 Interpretation Escalation + Implementation Gap）

**决策建议：采 Codex 7 个。** Interpretation Escalation（相关性→因果性检测）直接对应"0.737"案例，价值明确。Implementation Gap 是额外的质量信号。但 MVP 先做 4 个（S1/S2/S5/S6），后续扩展。

### 分歧 3：评分方法

- **Claude**：组合规则（1/2/3+ 信号阈值）
- **Codex**：硬门控 + noisy-OR

**决策建议：MVP 用 Claude 的简单规则（易理解、易调试），V2 考虑 Codex 的 noisy-OR（更精确）。**

---

## 四、直接采纳清单

| 来源 | 采纳内容 | 优先级 |
|------|---------|--------|
| Claude | 5 种错误共识子类型分类 | 知识储备 |
| Claude | 6 个代理信号 + 精度估算 | MVP 设计基础 |
| Claude | 信号组合规则（1/2/3+ 阈值） | MVP 实现 |
| Claude | 风险率 ~4-6% 估算 | 预期管理 |
| Claude | 二维置信度（支持度×可靠性） | V2+ 升级方向 |
| Codex | S4 Interpretation Escalation 信号 | MVP 扩展 |
| Codex | S7 Implementation Gap 信号 | MVP 扩展 |
| Codex | consensus_risk_profile schema | MVP 实现 |
| Codex | 校准策略（已知正确+已知可疑做回归） | MVP 验证 |
| Codex | 集成位置：provenance clustering 之后 | 管线设计 |
| Gemini | Tier-0 暗雷定位 | 产品框架 |
| Gemini | 术语："高风险共识"不说"错误共识" | 渲染 prompt |
| Gemini | 企业级 CTO 审计场景 | 远期商业 |

---

## 五、实施路径

| 阶段 | 时间 | 内容 | 依赖 |
|------|------|------|------|
| **等待** | — | 供应链 P1 完成（显式来源 + provenance clustering） | P1 |
| **MVP** | 1-2 天 | 4 个核心信号（Evidence-Assertion Gap / Temporal Freeze / Contradicts Official / Single-Study Dependency） | 供应链 P1 |
| **V1.1** | 1 天 | 扩展到 7 个信号 + noisy-OR 评分 | MVP 校准完成 |
| **V2** | TBD | 二维置信度 + 企业审计模块 | 图谱 ≥ 15 项目 |

---

## 六、一句话总结

> 错误共识是假公约数的终极形态——来源独立、上游不同，但结论一样且都错了。**Doramagic 不能判断对错，但能标注风险信号。** 等供应链 P1 完成后，1-2 天做 MVP，4 个信号覆盖 ~4-6% 的风险共识。术语上用"高风险共识"，永远不说"这是错的"。
