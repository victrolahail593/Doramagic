# 知识供应链 + 知识通胀 — 三方研究综合报告

> 日期：2026-03-15（Codex 补交后更新）
> 三方：Claude Opus（知识工程+产品架构）/ Gemini（产品+市场+UX）/ Codex（工程实现+算法）

---

## 一、五项全票共识

### 共识 1：供应链 V1 = 显式来源追踪 + 回声校正，不是全链路重建

- **Claude**：V2+（图谱 GA）才做完整追踪，P0 预留字段
- **Codex**：V1 只做四件事——显式来源提取 / 同源聚类 / adjusted independence / 弱通胀校正。"不要做知识取证学"
- **Gemini**：Beta 引入溯源标签

**结论**：三方一致——V1 是"知识来路账本"，不是"知识传播史"。Codex 的"NEVER 硬判定唯一源头"是关键约束。

### 共识 2：STALE / DRIFTED / INFLATED 三种衰变模式

- **Claude**：精确区分三者
- **Codex**：同意，补充通胀四阶段（frontier → emerging consensus → infrastructure → commodity），区分 adoption（只是更多人知道）vs verification（被独立验证）
- **Gemini**：通胀 = "零独创性"标记

**结论**：三种检测逻辑完全不同，不可混为一谈。Codex 的 adoption vs verification 区分是重要补充。

### 共识 3：溯源必须基于硬证据

- **Claude**：显式引用优先
- **Codex**：三层置信度——explicit_confirmed(0.90-0.98) / inferred_high_precision(0.60-0.80) / inferred_speculative(0.35-0.60)。V1 只信显式。
- **Gemini**：基于 Git Commit + AST

**结论**："代码说事实"原则的直接推论。V1 只做显式引用提取。

### 共识 4：通胀检测比供应链追踪优先级更高

- **Claude**：通胀 = 核心引擎升级（V1.1），供应链 = 高级消费层（V2+）
- **Codex**：通胀检测标 LATER（需更大图谱），但弱通胀校正标 NOW-LITE
- **Gemini**：Phase 2 开启通胀监测

**结论**：弱通胀校正（likely_inflated 标记）可以 NOW，完整通胀检测需要图谱规模。

### 共识 5：这是升级，不是新系统

- **Claude**：能力升级，本质不变
- **Codex**："对 Doramagic 而言，这不是新系统，而是 evidence chain + support_independence + domain map history 的升级版"
- **Gemini**：（虽然用了"数字资产管理系统"，但本质认同升级路线）

**结论**：不重做，在已有体系上叠加。

---

## 二、各方独有最佳贡献

### Claude 独有：理论框架 + 体系整合

1. **6 种传播变形模式**（从 4 个 SEO 项目归纳）：范围扩大化 / 去上下文化 / 时间冻结 / 对立面合并 / 权威借用 / 零扭曲传播

2. **5 种上游源头分类**（按确定性递减）：平台官方 > 学术实证 > 行业分析 > 社区经验 > 个人推断

3. **通胀度量模型**：`InflationIndex = penetration_rate(now) / penetration_rate(first_seen)`，四阶段生命周期

4. **"二阶知识通胀"**（最重要新洞察）：一阶通胀但深度理解仍稀缺

5. **normative_force 作为零成本扭曲预测器**：描述性知识零扭曲，规范性知识扭曲大

6. **5 条案例的完整传播链追踪**

7. **supply_independence 升级方案**（provenance_independence + upstream_authority + interpretation_variance）

### Codex 独有：工程深度（补交）

1. **NOW/LATER/NEVER 判断框架**：
   | 能力 | 判断 |
   |------|------|
   | 显式来源提取 | **NOW** |
   | provenance clustering + adjusted independence | **NOW** |
   | 槽位扭曲检测 | **NOW-LITE** |
   | 推断式来源恢复 | LATER |
   | 完整通胀检测 | LATER |
   | inflation-adjusted ORIGINAL | NOW-LITE / LATER-FULL |
   | 硬判定唯一源头 | **NEVER** |

2. **完整数据结构**（5 个 JSON Schema）：
   - `SourceRef`：结构化来源元数据（URL / publisher / published_at / extraction_mode / confidence）
   - `AtomOccurrence`：知识在项目中的出现位置（含 slots + source_refs）
   - `ProvenanceEdge`：引用关系（from_node → to_node + confidence + mode）
   - `PropagationEdge`：项目间传播关系（含 lexical_similarity + slot_match）
   - `ProvenanceCluster`：同源聚类

3. **覆盖率估算**：
   - 整体 atom 级显式来源覆盖率约 **15-35%**
   - 但最关键的 20%（高影响规则、高传播数据点）可覆盖
   - "不需要为所有 atom 找来源，先覆盖最关键的 20% 就有产品价值"

4. **三层推断置信度**：explicit_confirmed / inferred_high_precision / inferred_speculative

5. **精度/召回现实预期**：
   | 模式 | 精度 | 召回 |
   |------|------|------|
   | 显式来源 | 0.90-0.98 | 0.15-0.35 |
   | 高精度推断 | 0.60-0.80 | 0.30-0.50 |
   | 激进推断 | 0.35-0.60 | 0.50-0.70 |

6. **provenance clustering 核心算法**：识别多个项目引用同一上游 → 聚类 → 修正 independence

7. **detect_distortion() 槽位检测**：按 subject/relation/object/scope/conditions/normative_force/time_anchor 比对上下游原子的偏移

8. **adjusted_independence() 算法**：在现有 independence 基础上，按 provenance cluster 降权同源支持

9. **ORIGINAL 校正位置建议**：在 signal 层做，不在 matching 层。"matching 层的精度比 signal 层更关键，不应引入额外不确定性"

10. **关键工程原则**："宁可少报不要误报——一旦上游链条错了，independence / distortion / inflation 全部一起错"

11. **存储估算**：~50-200MB，适合现有管线

12. **分阶段 MVP 路径**：Phase 1 来源提取+聚类 → Phase 2 扭曲检测 → Phase 3 通胀趋势 → Phase 4 推断来源

### Gemini 独有：产品定位 + 商业价值

1. **用户故事矩阵**（架构师/创业者/投资人）
2. **竞品差异化**（Scholar=论文引用 / 审计=代码漏洞 / Doramagic=逻辑实现+思维陈旧度）
3. **"创新窗口预警"商业概念**
4. **定价分层**：Beta 溯源标签 / GA 通胀月报

---

## 三、分歧与决策建议

### 分歧 1：供应链 V1 的范围

- **Claude**：P0 只预留字段，P2 才做供应链
- **Codex**：显式来源提取 + provenance clustering 标 **NOW**

**决策建议（更新）：采 Codex 立场。** Codex 证明了显式来源提取和同源聚类的工程成本低、精度高（0.90-0.98），且直接修正 independence 的假独立问题。不需要等到 GA。**P1 就做。**

### 分歧 2：Gemini 的"数字资产管理系统"定位

**决策不变：采 Claude 立场。** 能力升级，本质不变。

### 分歧 3：通胀检测时机

- **Claude**：P1 立即做 likely_inflated 标记
- **Codex**：完整通胀标 LATER，弱校正标 NOW-LITE

**决策建议：两者兼容。** P1 做 NOW-LITE 弱校正（保守标记），完整通胀等图谱规模。

---

## 四、直接采纳清单（更新）

| 来源 | 采纳内容 | 优先级 |
|------|---------|--------|
| Claude | atom schema 预留 `upstream_references[]` | **P0（立即）** |
| Claude | independence 加入 normative_force 调节因子 | **P0（立即）** |
| Codex | 显式来源提取（URL/注释/commit/引用模式） | **P1** |
| Codex | provenance clustering + adjusted independence | **P1** |
| Codex | SourceRef / AtomOccurrence / ProvenanceEdge 数据结构 | **P1** |
| Codex | 三层推断置信度体系 | **P1** |
| Codex | detect_distortion() 槽位检测 | **P1-LITE** |
| Claude | ORIGINAL 增加 `likely_inflated` 标记 | **P1** |
| Codex | ORIGINAL 校正在 signal 层做 | **P1** |
| Claude | STALE/DRIFTED/INFLATED 精确区分 | P1 |
| Claude | 6 种变形模式 + 5 种上游分类 | 知识储备 |
| Claude | 二阶知识通胀 | 知识储备（V2+） |
| Codex | 推断式来源恢复 | **P2（图谱 ≥ 15 项目）** |
| Codex | 完整通胀趋势检测 | **P2** |
| Gemini | 竞品差异化 + 用户故事 | 产品参考 |
| Gemini | 创新窗口预警 | 远期商业模型 |

---

## 五、实施路径（更新）

| 阶段 | 时间 | 内容 | 依赖 |
|------|------|------|------|
| **P0** | 0.5 天 | atom schema 预留 `upstream_references[]` | 无 |
| **P0** | 0.5 天 | independence 加入 normative_force 调节 | 无 |
| **P1-a** | 1-2 天 | 显式来源提取器（URL/注释/commit/引用模式） | P0 |
| **P1-b** | 1-2 天 | provenance clustering + adjusted_independence() | P1-a |
| **P1-c** | 1 天 | ORIGINAL likely_inflated 弱校正 + detect_distortion() LITE | Health Check V1 |
| **P2** | 3-5 天 | 推断来源 + 完整通胀趋势 | 图谱 ≥ 15 项目 |
| **P3** | TBD | 完整知识生命周期追踪 | P1 + P2 数据充足 |

**P1 总工时：3-5 天**（可与 Health Check V1 并行推进）

---

## 六、一句话总结

> 通胀检测是 Health Check 的校准器，供应链追踪是 independence 的校准器。**Codex 证明了显式来源提取 + 同源聚类成本低、精度高，P1 就能做。** 先校准两个仪表（P1，3-5 天），预留 X 光机接口（P0，1 天），等骨骼长好了再做全链路追踪（P2）。
