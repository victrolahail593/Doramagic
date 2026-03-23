# SKILL.md v3.1 — 双引擎版

## 与 v3.0 的核心差异

| 方面 | v3.0（Pipeline 版） | v3.1（双引擎版） |
|------|-------------------|----------------|
| Phase C-H 执行者 | `python3 doramagic_pipeline.py`（一行） | AI 编排多个步骤 |
| WHY 提取 | Pipeline 用 `adapter=None` 跳过 → **0 张知识卡片** | AI 直接执行 C-2 灵魂提取 |
| UNSAID 提取 | 同上 → **0 条陷阱** | AI 从代码/Issues/CHANGELOG 推断 |
| 跨项目综合 | Pipeline 内部（实际未执行） | Phase D 由 AI 显式执行 |
| 产出保证 | 无法保证（pipeline 可静默跳过 LLM 阶段） | Hard Gate：SKILL.md 缺 WHY/UNSAID 不合格 |

## 根本原因修复

v3.0 失败的根本原因：WHY/UNSAID 提取只能由 LLM 做，Python 脚本无法读懂设计哲学。
v3.1 修复：Python 只负责确定性事实（repo_facts.json），AI 负责所有语义分析。

## 架构

```
Phase A  → AI：需求理解 → need_profile.json
Phase B  → AI + exec：GitHub 搜索 + 暗雷快扫 + 项目下载
Phase C  → 双引擎：
           C-1 exec：extract_facts.py → repo_facts.json（确定性）
           C-2 AI：灵魂提取 → soul.json（WHY/UNSAID/心智模型）
Phase D  → AI：跨项目综合 → synthesis.json
Phase E-F→ AI：编译交付 → delivery/SKILL.md + PROVENANCE.md + LIMITATIONS.md
报告     → AI：结构化摘要 → 向用户汇报
```

## soul.json 格式（C-2 产出）

```json
{
  "project_name": "repo_name",
  "why_recoverability": "recoverable | inferable | unrecoverable",
  "design_philosophy": "...",
  "mental_model": "...",
  "why_decisions": [{"decision": "...", "evidence": "file:line 或 Issue #NNN", "confidence": "high|medium|low"}],
  "unsaid_traps": [{"trap": "...", "evidence": "...", "severity": "HIGH|MEDIUM|LOW"}],
  "capabilities": ["..."],
  "community_traps": [{"trap": "...", "source": "Issue #NNN (N reactions)", "workaround": "..."}]
}
```

## 行数

SKILL.md：约 310 行（目标 350 行以内，Phase C 灵魂提取指令约 100 行）
