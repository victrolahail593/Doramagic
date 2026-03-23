# Race Brief: 积木制作 (Brick Forge)

> **Race ID**: r06-bricks
> **赛道**: B
> **选手**: S2-Codex vs S4-GLM5
> **预估**: 2-3 天
> **评审权重**: 积木数量×质量 25% + 领域覆盖 25% + 代码质量 20% + 测试 15% + DECISIONS.md 15%

---

## 任务

设计并实现积木制作流程，为 Doramagic 的 6 个预提取领域生产第一批框架级和领域级积木。

积木 = 框架/领域基线知识锚点。注入 Stage 1 后，LLM 知道基线知识，集中挖掘项目独特的 WHY/UNSAID。

---

## 输出契约（冻结，不可修改）

每块积木必须符合 `DomainBrick` schema:

```python
class DomainBrick(BaseModel):
    brick_id: str           # "L1-PYTHON-001" 或 "L2-HOMEASSISTANT-003"
    domain_id: str           # "python-general" 或 "smart-home"
    knowledge_type: KnowledgeType  # capability/rationale/constraint/interface/failure
    statement: str           # 积木内容（一段知识声明）
    confidence: Confidence   # high/medium/low
    signal: SignalKind       # ALIGNED（共识）为主
    source_project_ids: list[str]  # 来源项目
    support_count: int       # 支持此积木的证据数
    evidence_refs: list[EvidenceRef] = []  # 证据（文档URL、代码引用）
    tags: list[str] = []     # 标签
```

---

## 积木两层结构

### L1: 框架级（200-400 tokens/块）
全领域通用的框架基线知识。

| 优先级 | 框架/领域 | 覆盖 Doramagic 领域 | 目标数量 |
|--------|----------|---------------------|---------|
| **最高** | Python 通用 | 6/6 全覆盖 | ≥15 |
| 高 | FastAPI/Flask | 财务, 健康, 信息摄取 | ≥8 |
| 高 | Home Assistant | 智能家居 | ≥8 |
| 中 | Obsidian/Logseq 插件 | PKM | ≥6 |
| 中 | Go 通用 | 私有云, 信息摄取 | ≥6 |
| 中 | Django | 财务, 健康 | ≥6 |
| 中低 | React | 财务前端, PKM 前端 | ≥5 |

### L2: 模式级（400-800 tokens/块）
领域特定的最佳实践/反模式/社区共识。

| 领域 | 关键模式 | 目标数量 |
|------|---------|---------|
| 广义个人财务 | 多币种处理, 银行API对接, 隐私合规 | ≥5 |
| 笔记/PKM | 双向链接实现, 本地优先同步, 插件安全 | ≥5 |
| 私有云/自托管 | 反向代理配置, Let's Encrypt 自动化, Docker compose 模式 | ≥5 |
| 健康数据 | 异构设备数据对齐, FHIR 协议, 去噪 | ≥5 |
| 信息摄取 | RSS 解析陷阱, Anti-AI 过滤, OCR pipeline | ≥5 |
| 智能家居 | 自动化规则引擎, 设备集成协议, 场景联动 | ≥5 |

---

## 积木来源（你可以使用的信息源）

1. **框架官方文档** — 设计哲学页面、API 陷阱文档
2. **高频 Stack Overflow / GitHub Issues** — 社区反复踩的坑
3. **领域头部项目代码** — 如 Home Assistant core, Obsidian API
4. **已有研究资产** — `research/soul-lego-bricks/reports/synthesis-report.md`
5. **LLM 辅助提取**（通过 LLMAdapter）— 让 LLM 总结框架设计哲学

---

## Deliverables

| # | 文件 | 说明 |
|---|------|------|
| 1 | `brick_forge.py` | 积木制作脚本（可重复运行） |
| 2 | `bricks/python-general.jsonl` | Python 通用 L1 积木 |
| 3 | `bricks/fastapi.jsonl` | FastAPI L1 积木 |
| 4 | `bricks/homeassistant.jsonl` | Home Assistant L1+L2 积木 |
| 5 | `bricks/django.jsonl` | Django L1 积木 |
| 6 | `bricks/react.jsonl` | React L1 积木 |
| 7 | `bricks/domain-*.jsonl` | 6 个领域的 L2 积木（每领域一个文件） |
| 8 | `tests/test_brick_forge.py` | 测试（schema 合规、token 预算、evidence 覆盖） |
| 9 | `DECISIONS.md` | 设计决策（来源选择、分层策略、token 分配） |
| 10 | `BRICK_INVENTORY.md` | 积木清单（统计表：每个 domain × knowledge_type 的数量） |

---

## 模型无关约束（硬性）

- ❌ 禁止 `import anthropic` / `import openai` / `import google.generativeai`
- ✅ `brick_forge.py` 通过 `LLMAdapter` 调用 LLM 辅助提取
- ✅ 积木本身是确定性产物（JSONL 文件），一旦生成不依赖 LLM
- ✅ 如果 adapter=None，脚本应能从纯手工数据生成积木（不调 LLM）

---

## 质量标准

每块积木的质量检查：

- [ ] statement ≤ 400 tokens (L1) 或 ≤ 800 tokens (L2)
- [ ] knowledge_type 正确分类（不是所有都标 capability）
- [ ] 至少 1 个 evidence_ref（文档 URL 或代码引用）
- [ ] 反模式积木（knowledge_type=failure）占比 ≥ 15%
- [ ] brick_id 格式: `L{level}-{FRAMEWORK}-{NNN}`
- [ ] 无重复（同一 statement 不出现两次）

---

## 设计自由区（赛马空间）

- **知识提取策略**: 从文档提取？从代码分析？从 LLM 知识？混合？
- **L1/L2 边界**: 什么知识属于 L1（框架通用）vs L2（领域特定）？
- **反模式积木设计**: 如何系统性地发现反模式？
- **积木粒度**: 一块积木是一个独立知识点？还是一组相关知识？
- **证据质量**: 文档引用 vs 代码引用 vs 社区引用的权重？

---

## 输出路径

```
races/r06/bricks/{your-racer-id}/
├── brick_forge.py
├── bricks/
│   ├── python-general.jsonl
│   ├── fastapi.jsonl
│   ├── homeassistant.jsonl
│   ├── django.jsonl
│   ├── react.jsonl
│   ├── domain-finance.jsonl
│   ├── domain-pkm.jsonl
│   ├── domain-selfhosted.jsonl
│   ├── domain-health.jsonl
│   ├── domain-infoingest.jsonl
│   └── domain-smarthome.jsonl
├── tests/
│   └── test_brick_forge.py
├── DECISIONS.md
└── BRICK_INVENTORY.md
```
