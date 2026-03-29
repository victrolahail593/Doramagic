# Synthesis 因果推理升级
日期: 2026-03-29

## 背景与目标

Doramagic 从开源项目中提取知识，编译成 AI 技能包。但提取出的知识是**事实清单**而非**设计洞察**。

用户看到的是："Use explicit state transitions"（事实）
用户需要的是："Use explicit state transitions **because** failures become visible early and repairable, **as evidenced by** acme/ledger's migration from implicit to explicit states"（洞察）

根因：SynthesisRunner 在组装 SynthesisDecision 时丢弃了因果语境。

## 不在范围内

- 不做 LLM 额外调用来生成因果链（成本控制）
- 不改 SynthesisDecision schema（保持向后兼容）
- 不改 Knowledge Compiler 的 DR 卡片格式
- 不做 embedding 相似度匹配

## 方案设计

### 改动 1: SynthesisRunner — 保留因果链（synthesis_runner.py）

**现状：**
```python
# design_philosophy → statement（事实）
# mental_model → rationale（原因）
# 但 why_hypotheses 的 rationale 被覆写为 "Derived from X"
```

**改为：**
```python
# 主决策: statement = "X because Y"（合并事实+原因）
statement = f"{design_philosophy} — {mental_model}" if mental_model != "[NO_DATA]" else design_philosophy
rationale = f"Evidence from {repo_name}: {evidence_summary}"

# why_hypotheses: 解析 "because" 子句，保留原始因果
# 如果 item 包含 "because"，拆分为 statement + rationale
# 否则保留原文

# anti_patterns: 追加 "risk: {场景描述}" 到 rationale
```

### 改动 2: Iron Law 门禁（synthesis_runner.py）

在 LLM 质量过滤之后、组装 report 之前，检查：
```python
substantive_rationale = [d for d in decisions if len(d.rationale) > 30 and "Derived from" not in d.rationale]
if len(substantive_rationale) < 1:
    # 标记 compile_brief 中 "workflow" 为 ["WARNING: No causal reasoning extracted"]
    # 不触发熔断（仍然产出），但在 compile_brief 中标注质量风险
```

### 改动 3: compile_brief 注入因果链（synthesis_runner.py）

现在的 compile_brief["workflow"] 是硬编码的两行。改为从 decisions 中提取真实的因果链：
```python
workflow = []
for d in decisions[:5]:
    if "[TRAP]" not in d.statement:
        workflow.append(f"{d.statement}")
        if d.rationale and "Derived from" not in d.rationale:
            workflow.append(f"  Why: {d.rationale[:100]}")
```

### 改动 4: Knowledge Compiler — common_why 兜底（knowledge_compiler.py）

如果 DR 卡片构建的 WHY CHAINS 为空（常见于小 repo），用 synthesis 传递的 common_why 作为兜底：
```python
# compile_knowledge 接收 synthesis_report 参数
# 如果 build_why_chains 返回空，用 common_why 填充
```

## 验证标准

1. `make check` 全通过
2. 测试：构造包含 because 子句的 why_hypotheses fixture，验证 rationale 保留因果链
3. 测试：构造全 [NO_DATA] 的 envelope，验证 Iron Law 在 compile_brief 中标注警告
4. 测试：构造有 common_why 但无 DR 卡片的场景，验证 WHY CHAINS 非空

## 风险与权衡

- **不额外调用 LLM** — 因果链完全从已有数据中提取，零额外成本
- **向后兼容** — SynthesisDecision schema 不变，只是 rationale 字段内容更丰富
- **Iron Law 不熔断** — 标注警告但仍然产出，避免过度拒绝
