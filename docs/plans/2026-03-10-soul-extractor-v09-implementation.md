# Soul Extractor v0.9 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立评测框架跑 v0.8 基线，实现三项 P0 pipeline 改进，对比验证不回退。

**Architecture:** 三步走——Step 1 评测框架(Opus)，Step 2 Pipeline 改进(Sonnet)，Step 3 对比验证(Opus)。评测框架用跨模型交叉评判打破 AI 自评循环。Pipeline 改进将规则路与叙事路分离，确保 CRITICAL 规则不被叙事吞掉。

**Tech Stack:** Python 3 脚本, Bash, Markdown prompt 文件, Claude API / Gemini API (评测用)

**设计文档:** `docs/plans/2026-03-10-soul-extractor-v09-design.md`

**模型调度约定:**
- Step 1 (Task 1-3): Opus — 出题和评测设计需要深度理解
- Step 2 (Task 4-8): Sonnet — 确定性脚本和 prompt 修改
- Step 3 (Task 9-10): Opus — 跑评测和分析结果

---

## Step 1: 评测框架 + v0.8 基线 [Opus]

### Task 1: 出 benchmark 题集

**Files:**
- Create: `experiments/exp06-v09-superpowers/benchmark/questions.md`

**Step 1: 研读 obra/superpowers 仓库**

读取 v0.8 提取产出，理解 superpowers 项目的真实设计：
- `experiments/exp05-v08-superpowers/superpowers/soul/00-soul.md`
- `experiments/exp05-v08-superpowers/superpowers/soul/expert_narrative.md`
- `experiments/exp05-v08-superpowers/superpowers/soul/cards/rules/DR-*.md`
- `experiments/exp05-v08-superpowers/superpowers/soul/cards/concepts/CC-*.md`

同时读取我们对 superpowers 的人工研究（比 AI 提取更深入）：
- `experiments/exp05-v08-superpowers/research_agent_best_practices.md`
- 以及远程 Mac mini 上 superpowers 仓库的源码（如需要）

**Step 2: 写 10 道题 + 标准答案**

每道题格式：

```markdown
## Q1: [题目标题]
**类型**: 设计理解 | 正确使用 | 避坑判断 | 陷阱题
**问题**: [给 AI 的完整问题文本]
**标准答案要点** (评判用，不给被测 AI):
- Key Point 1: [必须提到的内容]
- Key Point 2: [必须提到的内容]
- Key Point 3: [必须提到的内容]
**反面要点** (提到则扣分):
- Anti Point 1: [如果 AI 编造了这个，说明幻觉]
```

题目分布：
- 设计理解 ×3: 测 WHY 层理解（为什么 TDD、为什么 skill 架构、为什么双阶段 review）
- 正确使用 ×3: 测 HOW 层（创建 skill、执行 brainstorming、配置 subagent）
- 避坑判断 ×2: 测 IF 层（安装报错排查、skill 触发失败）
- 陷阱题 ×2: 测幻觉抵抗（不存在的功能、错误的配置项）

**Step 3: 自检题目质量**

对每道题检查：
- 标准答案要点是否有明确的来源证据（代码/文档/Issue）？
- 一个真正的 superpowers 专家能否毫不犹豫地给出全部要点？
- 陷阱题的"正确答案"是否确实是"这个功能不存在"？

**Step 4: 写入文件**

将 10 道题写入 `experiments/exp06-v09-superpowers/benchmark/questions.md`

---

### Task 2: 设计评判 prompt

**Files:**
- Create: `experiments/exp06-v09-superpowers/benchmark/eval_prompt.md`

**Step 1: 写评判 prompt**

评判模型收到的输入格式：

```markdown
## 评判任务

你是一个严格的考试阅卷员。请根据标准答案评判以下回答。

### 题目
[问题文本]

### 标准答案要点
[Key Points 列表]

### 反面要点
[Anti Points 列表]

### 被评判的回答
[AI 的回答文本]

### 评分规则
- 事实正确性 (0-1): 回答中是否有与标准答案矛盾的错误陈述？0=有错误, 1=无错误
- 关键覆盖 (0-1): 标准答案要点覆盖了几个？0=不到一半, 1=一半以上
- 无幻觉 (0-1): 是否提到了反面要点中的内容，或编造了不存在的功能/配置？0=有幻觉, 1=无幻觉

请只输出 JSON:
{"factual": 0或1, "coverage": 0或1, "no_hallucination": 0或1, "reasoning": "一句话解释"}
```

**Step 2: 用一道样题测试 prompt**

手动模拟：写一个好回答和一个差回答，检查评判 prompt 是否能正确区分。

**Step 3: 写入文件**

将评判 prompt 模板写入 `experiments/exp06-v09-superpowers/benchmark/eval_prompt.md`

---

### Task 3: 跑 v0.8 基线

**Files:**
- Create: `experiments/exp06-v09-superpowers/benchmark/run_eval.sh`
- Create: `experiments/exp06-v09-superpowers/results/v08_baseline.md`

**Step 1: 写评测执行脚本**

`run_eval.sh` 的逻辑：

```bash
# 输入: questions.md, eval_prompt.md, inject_file (可选)
# 流程:
# 1. 逐题向被测模型提问（带或不带注入文件）
# 2. 收集回答
# 3. 逐题向评判模型发送 eval_prompt + 回答
# 4. 收集评分 JSON
# 5. 汇总分数
```

注意：具体的 API 调用方式取决于可用的工具。可以用 Claude API + Gemini API，或通过 CLI 工具。如果 API 不便直接调用，可以改为手动流程（逐题在不同 session 中提问，收集回答，再统一评判）。

**Step 2: 跑 A 组（无注入）**

10 道题，无注入文件，记录回答和评分。

**Step 3: 跑 B 组（v0.8 注入）**

10 道题，注入 `experiments/exp05-v08-superpowers/superpowers/inject/CLAUDE.md`，记录回答和评分。

**Step 4: 汇总基线结果**

写入 `results/v08_baseline.md`:

```markdown
# v0.8 Baseline Results

| 题号 | 类型 | A组(无注入) | B组(v0.8) |
|------|------|------------|-----------|
| Q1   | 设计理解 | X/3 | Y/3 |
| ...  | ... | ... | ... |
| 总分 | - | XX/30 | YY/30 |
| 通过率 | - | XX% | YY% |
```

---

## Step 2: Pipeline P0 改进 [Sonnet]

### Task 4: validate_extraction.py 新增内容检查

**Files:**
- Modify: `skills/soul-extractor/scripts/validate_extraction.py`

**Step 1: 添加内容检查函数**

在现有 validators 区域后新增三个检查函数：

```python
def check_rule_has_condition(meta):
    """Check that rule field contains IF/THEN or conditional language."""
    rule = str(meta.get("rule", ""))
    condition_patterns = [
        r'\bif\b', r'\bwhen\b', r'\bthen\b', r'\bunless\b',
        r'\bbefore\b', r'\bafter\b', r'\bmust\b', r'\bnever\b'
    ]
    has_condition = any(re.search(p, rule, re.IGNORECASE) for p in condition_patterns)
    if not has_condition:
        return ["Rule field lacks conditional language (IF/THEN/WHEN/MUST/NEVER)"]
    return []


def check_critical_has_code_example(meta):
    """Check that CRITICAL/HIGH cards have code examples in do list."""
    sev = str(meta.get("severity", "")).upper()
    if sev not in ("CRITICAL", "HIGH"):
        return []
    do_list = meta.get("do", [])
    do_text = " ".join(str(d) for d in do_list) if isinstance(do_list, list) else str(do_list)
    if '`' not in do_text and 'code' not in do_text.lower():
        return [f"CRITICAL/HIGH card lacks code example in do list"]
    return []


def check_community_has_issue_ref(meta):
    """Check that community gotcha cards reference specific Issue numbers."""
    card_id = str(meta.get("card_id", ""))
    if not re.match(r"DR-1\d{2}", card_id):
        return []
    sources = meta.get("sources", [])
    sources_text = " ".join(str(s) for s in sources)
    if not re.search(r"#\d+|Issue\s*\d+", sources_text, re.IGNORECASE):
        return ["Community gotcha card lacks specific Issue # reference"]
    return []
```

**Step 2: 在验证循环中调用新检查**

在 `validate_all()` 函数中，对 decision_rule_card 类型卡片新增调用：

```python
if card_type == "decision_rule_card":
    errors.extend(check_rule_has_condition(meta))
    errors.extend(check_critical_has_code_example(meta))
    errors.extend(check_community_has_issue_ref(meta))
```

**Step 3: 添加 structured_feedback.json 输出**

在 `write_report()` 函数中新增：

```python
# Structured feedback for Stage 3 retry
feedback_path = os.path.join(soul_dir, "structured_feedback.json")
feedback_items = []
for card in report["cards"]:
    if card["errors"]:
        feedback_items.append({
            "card_id": card.get("card_id", card["file"]),
            "file": card["file"],
            "errors": card["errors"],
            "suggestion": "Fix the listed errors and rerun validation"
        })
if feedback_items:
    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedback_items, f, indent=2, ensure_ascii=False)
```

**Step 4: 用 v0.8 产出验证改动**

```bash
python3 skills/soul-extractor/scripts/validate_extraction.py \
  --output-dir experiments/exp05-v08-superpowers/superpowers
```

检查：新增的内容检查是否合理（v0.8 产出可能触发一些新 error，这正是预期的）。

---

### Task 5: 重写 STAGE-3.5-review.md

**Files:**
- Modify: `skills/soul-extractor/stages/STAGE-3.5-review.md`

**Step 1: 重写文件**

删除现有软审查内容，替换为：

```markdown
# Stage 3.5: 验证与硬阻断

## 前置条件
Stage 3 规则卡提取已完成。

## 步骤 1: 运行硬校验

运行验证脚本：

\```bash
python3 {baseDir}/scripts/validate_extraction.py --output-dir "<output>"
\```

### 如果 RESULT: PASS
继续下一步。

### 如果 RESULT: BLOCKED（第一次）

1. 读取 `<output>/soul/structured_feedback.json`
2. 逐条修复：
   - rule 缺条件语句 → 改写 rule 为 IF/THEN 格式
   - CRITICAL/HIGH 缺代码示例 → 在 do 列表中添加具体命令或代码
   - 社区卡缺 Issue 引用 → 核实 community_signals.md 补上 Issue #
   - 其他错误 → 按错误信息修复对应卡片文件
3. 修复后**重新运行验证脚本**

### 如果 RESULT: BLOCKED（第二次）

1. 再次读取 structured_feedback.json
2. 修复剩余问题
3. 重新运行验证脚本

### 如果 RESULT: BLOCKED（第三次）

停止。告诉用户："验证 3 次未通过，剩余问题：[列出]。请人工检查。"
不要继续后续阶段。

## ⛔ Hard Gate
- 验证必须 PASS 才能继续
- 最多重试 2 次（共 3 次运行）
- 第三次仍失败则终止流程

## 完成后
告诉用户："验证通过，X/Y 张卡片合格。正在合成专家叙事..."

**下一步：读取并执行 STAGE-4-synthesis.md 中的专家叙事合成指令。**
```

---

### Task 6: 修改 STAGE-4-synthesis.md

**Files:**
- Modify: `skills/soul-extractor/stages/STAGE-4-synthesis.md`

**Step 1: 修改产出结构说明**

将"速查"部分从 Stage 4 职责中移除。修改产出结构模板：

原来的结构有 5 个部分（设计哲学、心智模型、为什么这样设计、踩坑故事、速查），改为 4 个部分：

```markdown
## 产出结构（必须严格遵循）

\```markdown
# [项目名] — 专家知识

## 设计哲学
[直接从 00-soul.md 的 Q6 取。像创造者在对你说话。]

## 心智模型
[直接从 00-soul.md 的 Q7 取。一个类比或一句话。]

## 为什么这样设计
[2-3 个核心设计决策的因果链。]

## 你一定会踩的坑
[3 个最重要的叙事体故事，附 Issue 编号。]
\```

注意：**不要写速查规则表**。规则速查由组装脚本自动从卡片生成，不需要你写。
你的职责是写好叙事——设计哲学、心智模型、因果链、踩坑故事。
```

**Step 2: 在约束中强调**

在约束部分添加：

```markdown
- 不要在叙事中重复规则卡的 DO/DON'T 列表——规则路由组装脚本处理
- 叙事聚焦于"为什么"和"踩过什么坑"，不要写"怎么做"的指令
```

---

### Task 7: 重写 assemble-output.sh

**Files:**
- Modify: `skills/soul-extractor/scripts/assemble-output.sh`

**Step 1: 重写组装逻辑**

核心变化：三路分离（规则路 / 叙事路 / 速查路）

```bash
#!/bin/bash
# Soul Extractor v0.9: Assemble final output with rules/narrative/reference separation
set -euo pipefail

OUTPUT_DIR="${1:?Usage: assemble-output.sh <output_dir>}"
SOUL_DIR="$OUTPUT_DIR/soul"
INJECT_DIR="$OUTPUT_DIR/inject"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$INJECT_DIR"

REPO_NAME=$(basename "$OUTPUT_DIR")
NARRATIVE="$SOUL_DIR/expert_narrative.md"

echo "=== Assembling output for $REPO_NAME ==="

# --- Check validation gate ---
VALIDATION_REPORT="$SOUL_DIR/validation_report.json"
if [ -f "$VALIDATION_REPORT" ]; then
    if python3 -c "import json; r=json.load(open('$VALIDATION_REPORT')); exit(0 if r['summary']['overall_pass'] else 1)" 2>/dev/null; then
        echo "  Validation: PASS"
    else
        echo "  ERROR: Validation did not pass. Cannot assemble."
        exit 1
    fi
else
    echo "  ERROR: No validation report found. Run Stage 3.5 first."
    exit 1
fi

# --- Check expert narrative exists ---
if [ ! -f "$NARRATIVE" ]; then
    echo "ERROR: expert_narrative.md not found. Stage 4 synthesis must complete first."
    exit 1
fi

# --- Build CRITICAL RULES section from cards (规则路) ---
RULES_SECTION=$(mktemp)
echo "## CRITICAL RULES" > "$RULES_SECTION"
echo "" >> "$RULES_SECTION"
echo "以下规则从代码分析和社区经验中提取，按严重度排序。违反 CRITICAL 规则可能导致严重问题。" >> "$RULES_SECTION"
echo "" >> "$RULES_SECTION"

# Extract CRITICAL rules first, then HIGH
for severity in CRITICAL HIGH; do
    for card in "$SOUL_DIR"/cards/rules/DR-*.md; do
        [ -f "$card" ] || continue
        card_sev=$(grep -m1 'severity:' "$card" 2>/dev/null | sed 's/severity: *//;s/ *$//' | tr '[:lower:]' '[:upper:]')
        if [ "$card_sev" = "$severity" ]; then
            title=$(grep -m1 'title:' "$card" 2>/dev/null | sed 's/title: *"*//;s/"*$//')
            rule=$(sed -n '/^rule:/,/^[a-z_]*:/{ /^rule:/d; /^[a-z_]*:/d; p; }' "$card" 2>/dev/null | head -3 | sed 's/^  //' | tr '\n' ' ')
            echo "- **[$severity]** $title — $rule" >> "$RULES_SECTION"
        fi
    done
done
echo "" >> "$RULES_SECTION"

# --- Build QUICK REFERENCE table from all rules (速查路) ---
REFERENCE_SECTION=$(mktemp)
echo "## QUICK REFERENCE" >> "$REFERENCE_SECTION"
echo "" >> "$REFERENCE_SECTION"
echo "| 规则 | 严重度 |" >> "$REFERENCE_SECTION"
echo "|------|--------|" >> "$REFERENCE_SECTION"

for card in "$SOUL_DIR"/cards/rules/DR-*.md; do
    [ -f "$card" ] || continue
    title=$(grep -m1 'title:' "$card" 2>/dev/null | sed 's/title: *"*//;s/"*$//')
    sev=$(grep -m1 'severity:' "$card" 2>/dev/null | sed 's/severity: *//;s/ *$//' | tr '[:lower:]' '[:upper:]')
    echo "| $title | $sev |" >> "$REFERENCE_SECTION"
done
echo "" >> "$REFERENCE_SECTION"

# --- Assemble CLAUDE.md ---
CLAUDE_MD="$INJECT_DIR/CLAUDE.md"
cat > "$CLAUDE_MD" << HEADER
# $REPO_NAME — AI Knowledge Pack
# Auto-generated by Soul Extractor v0.9
# Structure: CRITICAL RULES → EXPERT KNOWLEDGE → QUICK REFERENCE

HEADER

cat "$RULES_SECTION" >> "$CLAUDE_MD"
echo "" >> "$CLAUDE_MD"
echo "## EXPERT KNOWLEDGE" >> "$CLAUDE_MD"
echo "" >> "$CLAUDE_MD"
cat "$NARRATIVE" >> "$CLAUDE_MD"
echo "" >> "$CLAUDE_MD"
cat "$REFERENCE_SECTION" >> "$CLAUDE_MD"

echo "  -> $CLAUDE_MD"

# --- Generate .cursorrules (same content) ---
CURSORRULES="$INJECT_DIR/.cursorrules"
cp "$CLAUDE_MD" "$CURSORRULES"
echo "  -> $CURSORRULES"

# --- Generate project_soul.md ---
SOUL_SUMMARY="$SOUL_DIR/project_soul.md"
cp "$CLAUDE_MD" "$SOUL_SUMMARY"

# Add card index
echo "" >> "$SOUL_SUMMARY"
echo "---" >> "$SOUL_SUMMARY"
echo "" >> "$SOUL_SUMMARY"
echo "## 知识卡片索引" >> "$SOUL_SUMMARY"
echo "" >> "$SOUL_SUMMARY"
echo "| ID | 类型 | 标题 | 严重度 |" >> "$SOUL_SUMMARY"
echo "|----|------|------|--------|" >> "$SOUL_SUMMARY"

for card in "$SOUL_DIR"/cards/concepts/CC-*.md "$SOUL_DIR"/cards/workflows/WF-*.md "$SOUL_DIR"/cards/rules/DR-*.md; do
    [ -f "$card" ] || continue
    id=$(basename "$card" .md)
    type_prefix=$(echo "$id" | cut -d'-' -f1)
    case "$type_prefix" in
        CC) type="概念" ;;
        WF) type="工作流" ;;
        DR) type="规则" ;;
        *) type="其他" ;;
    esac
    title=$(grep -m1 'title:' "$card" 2>/dev/null | sed 's/title: *"*//;s/"*$//' || echo "$id")
    sev=$(grep -m1 'severity:' "$card" 2>/dev/null | sed 's/severity: *//;s/ *$//' || echo "-")
    echo "| $id | $type | $title | $sev |" >> "$SOUL_SUMMARY"
done

echo "" >> "$SOUL_SUMMARY"
echo "---" >> "$SOUL_SUMMARY"
echo "*Generated by Soul Extractor v0.9 $(date +%Y-%m-%d)*" >> "$SOUL_SUMMARY"
echo "  -> $SOUL_SUMMARY"

# --- Cleanup temp files ---
rm -f "$RULES_SECTION" "$REFERENCE_SECTION"

# --- Run output validation ---
echo ""
echo "=== Validating output ==="
if [ -f "$SCRIPT_DIR/validate_output.py" ]; then
    python3 "$SCRIPT_DIR/validate_output.py" --file "$CLAUDE_MD"
    VALIDATE_EXIT=$?
    if [ $VALIDATE_EXIT -ne 0 ]; then
        echo "ERROR: Output validation failed. Check output above."
        exit 1
    fi
else
    echo "WARNING: validate_output.py not found, skipping output validation"
fi

# --- Stats ---
CC_COUNT=$(ls "$SOUL_DIR"/cards/concepts/CC-*.md 2>/dev/null | wc -l | tr -d ' ')
WF_COUNT=$(ls "$SOUL_DIR"/cards/workflows/WF-*.md 2>/dev/null | wc -l | tr -d ' ')
DR_COUNT=$(ls "$SOUL_DIR"/cards/rules/DR-*.md 2>/dev/null | wc -l | tr -d ' ')
CLAUDE_SIZE=$(wc -c < "$CLAUDE_MD" 2>/dev/null | tr -d ' ' || echo "0")

echo ""
echo "=== ASSEMBLY COMPLETE ==="
echo "repo=$REPO_NAME"
echo "output_size=$CLAUDE_SIZE bytes"
echo "concepts=$CC_COUNT"
echo "workflows=$WF_COUNT"
echo "rules=$DR_COUNT"
echo "inject=$INJECT_DIR"
```

---

### Task 8: 创建 validate_output.py

**Files:**
- Create: `skills/soul-extractor/scripts/validate_output.py`

**Step 1: 写脚本**

```python
#!/usr/bin/env python3
"""
Soul Extractor v0.9: Output Validation
Validates the final CLAUDE.md for structural compliance.

Usage:
    python3 validate_output.py --file <path_to_CLAUDE.md>

Exit codes:
    0 = all checks pass
    1 = validation failures found
"""

import argparse
import re
import sys


def validate_output(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    total_len = len(content)
    errors = []
    metrics = {}

    # Check CRITICAL RULES section exists
    cr_match = re.search(r'^## CRITICAL RULES\b', content, re.MULTILINE)
    if not cr_match:
        errors.append("Missing '## CRITICAL RULES' section")
        metrics["critical_rules_section"] = False
    else:
        metrics["critical_rules_section"] = True

    # Check EXPERT KNOWLEDGE section exists
    ek_match = re.search(r'^## EXPERT KNOWLEDGE\b', content, re.MULTILINE)
    if not ek_match:
        errors.append("Missing '## EXPERT KNOWLEDGE' section")

    # Check QUICK REFERENCE section exists
    qr_match = re.search(r'^## QUICK REFERENCE\b', content, re.MULTILINE)
    if not qr_match:
        errors.append("Missing '## QUICK REFERENCE' section")

    # Count CRITICAL rules
    critical_count = len(re.findall(r'\[CRITICAL\]', content))
    metrics["critical_count"] = critical_count
    if critical_count < 1:
        errors.append(f"Only {critical_count} CRITICAL rules (minimum 1)")

    # Count HIGH rules
    high_count = len(re.findall(r'\[HIGH\]', content))
    metrics["high_count"] = high_count

    # Total rules in CRITICAL RULES section
    total_rules = critical_count + high_count
    metrics["total_rules"] = total_rules
    if total_rules < 3:
        errors.append(f"Only {total_rules} rules in CRITICAL RULES section (minimum 3)")

    # Check CRITICAL RULES section proportion
    if cr_match and ek_match:
        cr_section_len = ek_match.start() - cr_match.start()
        cr_proportion = cr_section_len / total_len if total_len > 0 else 0
        metrics["critical_rules_proportion"] = round(cr_proportion, 3)
        if cr_proportion < 0.15:
            errors.append(f"CRITICAL RULES section is {cr_proportion:.1%} of file (minimum 15%)")

    # Check rules have conditional language
    rule_lines = re.findall(r'\*\*\[(?:CRITICAL|HIGH)\]\*\*.*?—\s*(.*)', content)
    rules_with_condition = 0
    condition_patterns = [r'\bif\b', r'\bwhen\b', r'\bthen\b', r'\bmust\b',
                          r'\bnever\b', r'\bbefore\b', r'\bafter\b', r'\bunless\b']
    for rule_text in rule_lines:
        if any(re.search(p, rule_text, re.IGNORECASE) for p in condition_patterns):
            rules_with_condition += 1
    metrics["rules_with_condition"] = rules_with_condition

    # Print results
    print(f"Output validation: {filepath}")
    print(f"  File size: {total_len} bytes")
    print(f"  CRITICAL rules: {critical_count}")
    print(f"  HIGH rules: {high_count}")
    if "critical_rules_proportion" in metrics:
        print(f"  Rules section proportion: {metrics['critical_rules_proportion']:.1%}")
    print(f"  Rules with conditions: {rules_with_condition}/{len(rule_lines)}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print(f"\nPASSED — all checks OK")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate Soul Extractor output")
    parser.add_argument("--file", required=True, help="Path to CLAUDE.md")
    args = parser.parse_args()

    if not validate_output(args.file):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 2: 用 v0.8 产出测试**

```bash
python3 skills/soul-extractor/scripts/validate_output.py \
  --file experiments/exp05-v08-superpowers/superpowers/inject/CLAUDE.md
```

预期结果：FAILED（v0.8 产出没有 CRITICAL RULES 分区，这正是 v0.9 要解决的问题）。

---

### Task 8.5: 更新 SKILL.md 版本号

**Files:**
- Modify: `skills/soul-extractor/SKILL.md`

**Step 1: 版本号 0.8.0 → 0.9.0**

修改 frontmatter 中的 `version: 0.8.0` 为 `version: 0.9.0`。

---

## Step 3: 对比验证 [Opus]

### Task 9: 用 v0.9 pipeline 重新提取

**Step 1: 部署 v0.9 到远程 Mac mini**

```bash
scp -r skills/soul-extractor/ tangsir@192.168.0.251:~/.openclaw/skills/soul-extractor/
```

**Step 2: 在远程运行提取**

对 obra/superpowers 运行 v0.9 pipeline，产出到新目录。

**Step 3: 拷贝产出到本地**

```bash
scp -r tangsir@192.168.0.251:~/soul-output/superpowers \
  experiments/exp06-v09-superpowers/superpowers/
```

---

### Task 10: 跑 v0.9 评测并对比

**Step 1: 跑 C 组（v0.9 注入）**

用 v0.9 产出的 CLAUDE.md，同一 10 道题，同一评判 prompt。

**Step 2: 汇总对比**

写入 `experiments/exp06-v09-superpowers/results/comparison.md`:

```markdown
# v0.8 vs v0.9 Comparison

| 题号 | 类型 | A组(无注入) | B组(v0.8) | C组(v0.9) |
|------|------|------------|-----------|-----------|
| Q1   | ... | X/3 | Y/3 | Z/3 |
| ...  | ... | ... | ... | ... |
| 总分 | - | XX/30 | YY/30 | ZZ/30 |

## Pipeline 可观测性指标 (v0.9 新增)

| 指标 | 值 |
|------|-----|
| CRITICAL 规则数 | N |
| HIGH 规则数 | N |
| 规则区块占比 | N% |
| validate_extraction 通过率 | N/N |
| validate_output 通过/失败 | PASS/FAIL |
```

**Step 3: 判定结论**

- C组 ≥ B组 → v0.9 成功（不回退）
- C组 < B组 → 分析哪些题退步了，回查 pipeline 改动
- 无论结果如何，pipeline 可观测性指标本身就是 v0.9 的增量价值

---

*Plan created 2026-03-10*
