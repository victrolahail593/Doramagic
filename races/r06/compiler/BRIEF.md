# Race Brief: Knowledge Compiler (Stage 4.5)

> **Race ID**: r06-compiler
> **赛道**: C
> **选手**: 四路赛马
> **评审权重**: Token 效率 25% + 可读性 25% + 代码质量 20% + 测试 15% + DECISIONS.md 15%

---

## 任务

实现 Stage-level Knowledge Compiler：将提取的知识卡片按类型编译为不同格式的输出段落，生成 `compiled_knowledge.md`。

这是**纯确定性逻辑**，无 LLM 调用。输入是卡片文件 + 00-soul.md + repo_facts.json，输出是格式优化的 CLAUDE.md 内容。

---

## 输入

1. `<output>/soul/cards/concepts/CC-*.md` — 概念卡（YAML frontmatter + body）
2. `<output>/soul/cards/workflows/WF-*.md` — 工作流卡
3. `<output>/soul/cards/rules/DR-*.md` — 规则卡（DR-001~ 代码规则，DR-100~ 社区陷阱）
4. `<output>/soul/00-soul.md` — Q6 设计哲学 + Q7 心智模型
5. `<output>/artifacts/repo_facts.json` — 确定性事实（commands, skills, config_keys）

## 输出

`<output>/soul/compiled_knowledge.md` — 替代 expert_narrative.md 作为 CLAUDE.md 的主内容。

---

## 编译规则（9 段，U 型排序）

| # | 段 | 来源 | 编译格式 | Token 占比 |
|---|---|------|---------|-----------|
| 1 | CRITICAL RULES | DR-* (CRITICAL/HIGH) | `[SEVERITY] title — IF/THEN rule` | ~15% |
| 2 | CONCEPTS | CC-* | `**Name**: definition. Is: X. IsNot: Y.` | ~10% |
| 3 | WORKFLOWS | WF-* | `Step 1 → Step 2 → Step 3` (每条一行) | ~10% |
| 4 | FEATURE INVENTORY | repo_facts.json | 结构化列表 | ~10% |
| 5 | DESIGN PHILOSOPHY | Q6 from 00-soul.md | 2-3 段叙事 | ~15% |
| 6 | MENTAL MODEL | Q7 from 00-soul.md | 1 段类比叙事 | ~5% |
| 7 | WHY CHAINS | DR-* 中 rationale 最丰富的 top 3 | 叙事 "为什么这样设计" | ~15% |
| 8 | TRAPS | DR-100+ 社区陷阱 | ⚠️ 警告格式 + Issue# | ~15% |
| 9 | QUICK REFERENCE | 所有 DR-* | 表格: 规则 \| 严重度 | ~5% |

## 排序逻辑（U 型）

1. 最危险的先（CRITICAL RULES）
2. 最有用的中（CONCEPTS → WORKFLOWS → FEATURE INVENTORY）
3. 最深的后（DESIGN PHILOSOPHY → MENTAL MODEL → WHY CHAINS → TRAPS）
4. 速查末（QUICK REFERENCE）

## Token 预算

总计 **1500-2000 tokens**。超预算时：
- 先砍 MEDIUM/LOW 规则（只保留 CRITICAL/HIGH）
- 再砍 QUICK REFERENCE（只保留 CRITICAL/HIGH 行）
- 哲学/心智模型/陷阱不砍（核心价值）

## 置信度过滤

- `verdict == REJECTED` 的卡片不进入编译
- `verdict == WEAK` 的卡片加 `[推测]` 标注
- 无 verdict 字段的卡片正常处理（向后兼容）

## 适用域处理

- `is_exception_path == true` 的社区陷阱排在同 severity 的后面
- `applicable_versions` 存在时，在规则后附加 `(适用: >=2.0)` 标注

---

## 模型无关

纯确定性 Python。不调用任何 LLM。不需要 LLMAdapter。

## Deliverables

| # | 文件 | 说明 |
|---|------|------|
| 1 | `knowledge_compiler.py` | 主实现 |
| 2 | `tests/test_knowledge_compiler.py` | 测试（含 python-dotenv fixture） |
| 3 | `DECISIONS.md` | 设计决策 |

## 输出路径

```
races/r06/compiler/{your-racer-id}/
├── knowledge_compiler.py
├── tests/test_knowledge_compiler.py
└── DECISIONS.md
```

## 设计自由区

- 每段的具体格式细节（如何压缩概念卡到一行？）
- Token 估算方法（字符/4？tiktoken？简单计数？）
- 超预算时的裁剪策略细节
- YAML frontmatter 解析方式
- WHY CHAINS 的 "top 3 rationale" 选择算法
