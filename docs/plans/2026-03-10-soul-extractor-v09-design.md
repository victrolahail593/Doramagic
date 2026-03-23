# Soul Extractor v0.9 设计文档

**日期**: 2026-03-10
**状态**: 已确认

---

## 指导原则

以终极价值链为导向：**提取知识 → 注入 AI → AI 变聪明 → 让 AI 站在开源项目的肩膀上提供服务**

不是"提取做得好不好"，而是"整条链跑通后，AI 服务用户的能力提升了多少"。提取只有在服务于这个终极目标时才有意义。

## 成功标准

**评测不回退 + pipeline 从黑盒变白盒**

- v0.9 注入后 AI 做任务的成绩 ≥ v0.8 注入后的成绩
- pipeline 有了脚本化硬指标，可以客观衡量每次运行的产出质量

## 约束

| 项 | 决定 | 理由 |
|---|---|---|
| 评测仓库 | obra/superpowers | 足够复杂，有 v0.6/v0.7/v0.8 历史数据 |
| 评判者 | 不同模型交叉评判 | 打破"AI 评 AI"的同模型循环 |
| 改进范围 | 全部 P0 | Stage 3.5 真阻断 + 产出结构固化 + 脚本硬指标 |
| 方案 | 评测先行 | 先建评测 → 跑基线 → 改 pipeline → 对比验证 |

---

## 三步走

### Step 1：评测框架 + v0.8 基线

#### 题目设计

为 obra/superpowers 设计 10 道题，覆盖四类场景：

| 类型 | 题数 | 测什么 | 示例 |
|------|------|--------|------|
| 设计理解 | 3 | AI 是否理解项目的 WHY | "Superpowers 为什么强制 TDD 而不是可选？" |
| 正确使用 | 3 | AI 能否指导用户正确操作 | "我想给项目加一个新 skill，完整流程是什么？" |
| 避坑判断 | 2 | AI 能否拦截常见错误 | "我装了 superpowers 但 /brainstorm 报错，怎么排查？" |
| 陷阱题 | 2 | AI 是否会编造不存在的功能 | "Superpowers 的 hot-reload 功能怎么用？"（不存在） |

#### 评测流程

1. 同一道题分别给三个 AI session：
   - A组：无注入（纯模型知识）
   - B组：注入 v0.8 CLAUDE.md
   - C组：注入 v0.9 CLAUDE.md（Step 3 才跑）

2. 每组回答由不同模型评判：
   - Claude 的回答 → Gemini 评分（或反过来）

3. 评分维度（每题 0-3 分）：
   - 事实正确性：有没有说错的？（0-1）
   - 关键覆盖：关键点提到了几个？（0-1）
   - 无幻觉：有没有编造不存在的东西？（0-1）

4. 汇总：每组总分 / 30 = 通过率

#### 评分客观性保障

- 每道题预先写好标准答案要点（3-5 个 key points）
- 评判 prompt 明确要求："只根据标准答案判断，不要加入自己的知识"
- 评判模型看不到被评判模型的身份，只看回答内容

### Step 2：Pipeline P0 改进

#### 改动 1：Stage 3.5 真阻断

**现状**：validate_extraction.py 只检查格式（YAML 字段、severity 枚举、数量），软审查由 AI 做但实际无效（v0.6=v0.7 产出完全相同）。

**改为**：

validate_extraction.py 新增内容检查：
- 每张规则卡的 rule 字段必须包含 IF/THEN 或条件语句
- CRITICAL/HIGH 规则卡必须有代码示例（do 列表中含代码块）
- 社区陷阱卡的 sources 必须引用具体 Issue 编号

验证失败时：
- 输出 structured_feedback.json（哪张卡、什么问题、修改建议）
- STAGE-3.5-review.md 指示 AI 读取 feedback → 修改对应卡片 → 重跑验证
- 最多重试 2 次，仍失败则终止并报告

**删除软审查**：当前 AI 做的"具体性/真实性/可执行性"三维审查从未产生过实际修改，删掉。硬校验够用。

#### 改动 2：产出结构固化

**现状**：Stage 4 生成 expert_narrative.md，Stage 5 直接拼成 CLAUDE.md。规则被叙事吞掉（v0.8 CRITICAL 规则丢失）。

**改为**：

CLAUDE.md 强制结构（由 assemble-output.sh 模板控制，不依赖 AI）：

```
## CRITICAL RULES（规则路 — 直接从规则卡提取，脚本拼接）
  所有 CRITICAL/HIGH 规则卡 → 转为 IF/THEN 一行规则 + 严重度
  这部分不经过 Stage 4 的叙事加工

## EXPERT KNOWLEDGE（叙事路 — 来自 Stage 4 expert_narrative.md）
  设计哲学、心智模型、因果链、踩坑故事
  保持 v0.8 的叙事质量

## QUICK REFERENCE（速查 — 脚本从规则卡生成）
  全部规则的一行摘要表格
```

**关键设计决策**：规则路由 assemble-output.sh 脚本生成，不经过 AI 的 Stage 4。确保 CRITICAL 规则不会被叙事"平滑"掉。

#### 改动 3：脚本化硬指标

新增 `validate_output.py`（检查最终产出，区别于 validate_extraction.py 检查中间卡片）：

检查 CLAUDE.md 最终文件：
- CRITICAL 规则数量 ≥ 3（从卡片中 severity=CRITICAL 的数量决定）
- HIGH 规则数量 ≥ 5
- CRITICAL RULES 区块占总文件 ≥ 30%
- 每条规则含 IF/THEN 结构
- 不通过 → 终止，报告哪项不达标

在 assemble-output.sh 末尾调用，组装完成后自动验证。

### Step 3：对比验证

- 用 v0.9 pipeline 重新提取 obra/superpowers
- 同一 benchmark 题集跑评测
- 对比 v0.8 基线，判断是否回退

---

## 文件变更清单

### 新建

| 文件 | 用途 |
|------|------|
| `scripts/validate_output.py` | 最终产出硬指标检查 |
| `experiments/exp06-v09-superpowers/benchmark/questions.md` | 10 道评测题 + 标准答案 |
| `experiments/exp06-v09-superpowers/benchmark/eval_prompt.md` | 评判模型的评分 prompt |
| `experiments/exp06-v09-superpowers/benchmark/run_eval.sh` | 评测执行脚本 |
| `experiments/exp06-v09-superpowers/results/` | 各组评测结果存放 |

### 修改

| 文件 | 改什么 |
|------|--------|
| `scripts/validate_extraction.py` | 新增内容检查 + structured_feedback.json 输出 |
| `stages/STAGE-3.5-review.md` | 删除软审查，改为 feedback → 修卡片 → 重跑验证（最多2次） |
| `stages/STAGE-4-synthesis.md` | 明确叙事路职责：只负责哲学/模型/因果链/故事，不含速查规则 |
| `scripts/assemble-output.sh` | 重写：三路分离（规则路/叙事路/速查）+ 调用 validate_output.py |
| `SKILL.md` | 版本 0.8.0 → 0.9.0 |

### 不改

| 文件 | 为什么 v0.9 不改 |
|------|-----------------|
| `STAGE-1-essence.md` | 不知道是否有问题。benchmark 会告诉我们。 |
| `STAGE-2-concepts.md` | 不知道是否有问题。概念卡质量从未用下游任务验证过。 |
| `STAGE-3-rules.md` | 可能有问题（P1 建议绑定源码证据），但 v0.9 scope 只做 P0。 |
| `prepare-repo.sh` | 确定性脚本，大概率没问题。 |

---

*设计经 brainstorming 讨论确认，2026-03-10*
