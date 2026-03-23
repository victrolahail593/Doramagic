# Race Brief: 置信度体系 + DSD (Stage 3.5 增强)

> **Race ID**: r06-confidence
> **赛道**: D
> **选手**: 四路赛马
> **评审权重**: 误报率 25% + 检出率 25% + 代码质量 20% + 测试 15% + DECISIONS.md 15%

---

## 任务

实现两个子系统，都集成到 Stage 3.5 验证流程中：

### 子系统 1: Evidence-Chain Tagging + Deterministic Verdict

对每张卡片的每个 evidence_ref 自动标注证据类型，然后基于证据组合确定性裁定 verdict。

### 子系统 2: Deceptive Source Detection (DSD)

8 项确定性检查，检测"证据是否在欺骗你"。输出 WARNING（不 BLOCKING）。

---

## 子系统 1: 置信度体系

### 证据标注规则（确定性，基于路径匹配）

| evidence_ref.kind | evidence_ref.path 包含 | 标注 |
|---|---|---|
| file_line | 任何 | CODE |
| artifact_ref | readme/doc/guide/contributing | DOC |
| artifact_ref | 其他 | CODE |
| community_ref | 任何 | COMMUNITY |
| 无 evidence_ref | — | INFERENCE |

### Verdict 裁定规则（确定性布尔代数）

| 证据组合 | Verdict | PolicyAction |
|---------|---------|-------------|
| CODE + DOC | SUPPORTED | ALLOW_CORE |
| CODE + COMMUNITY | SUPPORTED | ALLOW_CORE |
| DOC + COMMUNITY | SUPPORTED | ALLOW_STORY |
| CODE only | SUPPORTED | ALLOW_CORE |
| COMMUNITY only (NOT DOC, NOT CODE) | CONTESTED | ALLOW_STORY |
| INFERENCE + 任何 1 项佐证 | WEAK | ALLOW_STORY |
| INFERENCE only | REJECTED | QUARANTINE |
| 互相矛盾的证据 | CONTESTED | ALLOW_STORY |

### 输出

修改卡片 YAML frontmatter，新增字段：
```yaml
evidence_tags: [CODE, COMMUNITY]
verdict: SUPPORTED
policy_action: ALLOW_CORE
```

---

## 子系统 2: DSD (8 项检查)

每项检查输出 score (0-1) + triggered (bool) + detail (str)。

| # | 检查项 | 方法 | 阈值 |
|---|--------|------|------|
| 1 | Rationale Support Ratio | WHY 卡片中有 CODE/DOC/COMMUNITY 佐证的占比 | < 0.3 → WARNING |
| 2 | Temporal Conflict Score | 同一 subject 的卡片引用不同时代证据 | 跨 2+ major versions → WARNING |
| 3 | Exception Dominance Ratio | community_signals 中 workaround/edge case 占比 | > 0.6 → WARNING |
| 4 | Support-Desk Share | maintainer 回复占总回复比例 | > 0.8 → WARNING |
| 5 | Public Context Completeness | 卡片中 inferred/推测 等词占比 | > 0.4 → WARNING |
| 6 | Persona Divergence Score | 不同 sources 的环境假设是否矛盾 | 检测矛盾 → WARNING |
| 7 | Dependency Dominance Index | 核心功能依赖外部闭源服务的比例 | > 0.5 → WARNING |
| 8 | Narrative-Evidence Tension | 叙事断言是否都有卡片支撑 | 未匹配断言 > 30% → WARNING |

### DSD 输出

```python
class DSDReport(BaseModel):
    checks: list[DSDCheck]
    overall_status: Literal["CLEAN", "WARNING", "SUSPICIOUS"]
    # CLEAN = 0 checks triggered
    # WARNING = 1-3 checks triggered
    # SUSPICIOUS = 4+ checks triggered
```

DSD 结果是 **WARNING 不是 BLOCKING**。标注到 validation_report.json 中。

---

## 集成接口

```python
# 在 validate_extraction.py 调用链中新增
def run_evidence_tagging(cards: list[dict]) -> list[dict]:
    """为每张卡片标注 evidence_tags + verdict + policy_action。返回修改后的卡片。"""

def run_dsd_checks(cards: list[dict], repo_facts: dict, community_signals: str) -> DSDReport:
    """8 项 DSD 检查。"""
```

## 模型无关

纯确定性 Python。不调用任何 LLM。

## Deliverables

| # | 文件 | 说明 |
|---|------|------|
| 1 | `confidence_system.py` | 证据标注 + verdict 裁定 |
| 2 | `deceptive_source_detection.py` | 8 项 DSD 检查 |
| 3 | `tests/test_confidence_system.py` | 置信度测试 |
| 4 | `tests/test_dsd.py` | DSD 测试（含已知好项目 + 已知暗雷项目 fixture） |
| 5 | `DECISIONS.md` | 设计决策 |

## 输出路径

```
races/r06/confidence/{your-racer-id}/
├── confidence_system.py
├── deceptive_source_detection.py
├── tests/
│   ├── test_confidence_system.py
│   └── test_dsd.py
└── DECISIONS.md
```

## 设计自由区

- 证据标注的路径匹配细节（哪些路径算 DOC？）
- DSD 阈值校准策略（如何设定初始阈值？）
- DSD 检查项之间是否有权重？
- 矛盾证据的判定方法
- community_signals 的解析方式
