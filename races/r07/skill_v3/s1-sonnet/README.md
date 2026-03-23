# SKILL.md v3.0 — 变更说明

**选手**: S1-Sonnet
**版本**: 3.0.0（从 2.0.0 升级）
**日期**: 2026-03-21

---

## 核心架构变化

### v2.0.0 的问题

| 问题 | 根因 |
|------|------|
| 只能处理 1 个项目 | Phase C 让 AI inline 读代码写卡片，上下文窗口限制 |
| 不调用 Python packages | Phase C→H 全部 AI inline，脚本空置 |
| 不调用积木注入 / Knowledge Compiler | Pipeline 绕过 |
| 产出质量薄（1647 bytes SKILL.md） | AI inline 无法做真正的跨项目综合 |
| SKILL.md 700 行太长 | Phase C→H 的详细指令全都写在 SKILL.md 里 |

### v3.0.0 的解法

**架构重心转移**：AI 负责"理解需求"和"筛选项目"（Phase A-B），Python pipeline 负责"提取知识"和"锻造 Skill"（Phase C→H）。

```
v2.0: Phase A→H 全部 AI inline（AI 读代码 → AI 写卡片 → AI 组装）
v3.0: Phase A-B AI-native + Phase C→H 一个 pipeline exec
```

---

## 变更明细

### 保留不变

- Frontmatter（name, description, tags, storage_root 等）
- 触发方式（/dora, 帮我做一个, 等）
- 暗雷知识库完整保留（DSD 8 指标 + Top 10 速查 + 叠加规则）
- Phase A 需求理解逻辑（domain/keywords/intent/constraints/anti_keywords/domain_id）
- Phase B-0 预提取 API 查询
- Phase B-1 GitHub 搜索调用
- Phase B-2 AI 筛选 + DSD 快扫逻辑
- Phase B-3 下载 + extract_facts.py
- 错误处理表

### 新增

- **Phase B-3 写 repos.json**：结构化输出供 pipeline 消费
  ```json
  [{"name": "xxx", "path": "/abs/path", "stars": 1234, "url": "https://..."}]
  ```
- **Phase C→H 替换为单一 pipeline exec**：
  ```bash
  exec python3 {skill_dir}/scripts/doramagic_pipeline.py \
    --need-profile ... --repos ... --run-dir ... --bricks-dir ... --output ...
  ```
- **Phase 报告**：AI 读 delivery/ 三个文件，向用户提供结构化摘要（6 个维度）

### 移除/精简

| 移除内容 | 原因 |
|----------|------|
| Phase C 全部 inline 指令（Stage 0.5-4）| 移入 pipeline，SKILL.md 不再需要 |
| Phase D 社区信号 inline 分析 | 移入 pipeline |
| Phase E 跨项目综合 inline 步骤 | 移入 pipeline |
| Phase F Skill 锻造 inline 写法 | 移入 pipeline |
| Phase G 质量门控 inline 逻辑 | 移入 pipeline |
| Phase H 交付 inline 展示 | 合并到"Phase 报告" |
| 存储结构的中间文件细节 | 精简为 delivery/ 最终产出结构 |

---

## 行数对比

| 版本 | 行数 | 核心原因 |
|------|------|----------|
| v2.0.0 | ~725 行 | Phase C→H 全部 inline 指令 |
| v3.0.0 | ~260 行 | Phase C→H 委派给 pipeline，SKILL.md 只保留 AI 需要的知识 |

行数减少 64%，同时能力不降反升（pipeline 可处理多项目并行）。

---

## 期望效果

- **多项目支持**：pipeline 不受上下文窗口限制，可并行分析 3-5 个项目
- **Python packages 激活**：phase_runner / synthesis / skill_compiler / knowledge_compiler 全部通过 pipeline 调用
- **积木注入生效**：pipeline 通过 `--bricks-dir` 参数注入现有积木
- **产出质量提升**：真正的跨项目综合，WHY/UNSAID 有证据支撑
- **SKILL.md 可维护**：260 行，结构清晰，AI 可快速理解和执行
