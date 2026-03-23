#!/usr/bin/env python3
"""
Soul Extractor v0.9: Benchmark Judge
Sends answers to Gemini CLI for cross-model evaluation.

Usage:
    python3 run_judge.py <group>

    group: A, B, or C
"""

import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "..", "results")

# Questions
QUESTIONS = {
    "Q01": "Superpowers 框架为什么把 TDD（测试驱动开发）设计为 Iron Law（不可违反的铁律），而不是可选的最佳实践？背后的设计理由是什么？",
    "Q02": "Superpowers 有 14 个 skill，它们不是按固定顺序执行的线性 pipeline，而是根据触发条件动态激活。为什么这样设计？",
    "Q03": "在 subagent-driven development 中，Superpowers 要求每个 task 完成后做两轮审查：先 spec compliance review，再 code quality review。为什么要分两阶段？一次审查不行吗？",
    "Q04": "假设我已经安装了 Superpowers，我想给我的项目加一个'用户认证'功能。从提出需求到代码合并，Superpowers 规定的完整流程是什么？列出每一步和对应的 skill。",
    "Q05": 'Brainstorming skill 的流程中规定"一次只问一个问题"，不能一条消息问多个问题。为什么这样限制？另外，如果我的需求非常简单（比如改一个配置值），可以跳过 brainstorming 吗？',
    "Q06": 'Writing-plans skill 要求计划任务是"bite-sized"的。什么叫 bite-sized？给我一个好的和差的例子对比。',
    "Q07": "我安装了 Superpowers，但在对话中发现 AI agent 完全忽略了 skills——不做 brainstorming，不做 TDD，直接写代码。可能是什么问题？怎么解决？",
    "Q08": '我在 debugging 一个问题，试了几个修复方法都没用，然后 AI 说"这个问题可能是 X 导致的"就开始改代码了。在 Superpowers 的 systematic-debugging 框架下，这样做对吗？正确的做法是什么？',
    "Q09": "我听说 Superpowers 有一个 auto-fix 功能，可以自动扫描代码中的问题并提供修复建议，类似 ESLint 的 --fix。请问怎么启用这个功能？",
    "Q10": "我在 Superpowers 文档里看到 skill 可以用 @ 语法引用其他 skill。那我可以在 brainstorming 的设计文档里写 @test-driven-development 来自动触发 TDD skill 吗？",
}

KEY_POINTS = {
    "Q01": "KP1: AI容易作弊——先写代码再补测试，测试只验证代码做了什么而非应该做什么。KP2: 先写测试迫使AI承认无知，打破自信幻觉。KP3: tests-after会立即通过证明不了东西；tests-first先失败(RED)证明测试有检测力。",
    "Q02": "KP1: 软件开发不是线性的，可能需要在实现中途回去brainstorming。KP2: Skill是可组合模块形成有向无环图。KP3: 每个skill有触发条件，agent根据上下文判断激活。",
    "Q03": "KP1: spec compliance和code quality是正交维度，代码可以优雅但不符需求。KP2: 顺序必须spec先quality后。KP3: 每轮有review loop——发现问题→修复→重新审查。",
    "Q04": "KP1: 第一步brainstorming（探索需求、问问题、提方案、获批准、写设计文档），设计批准前不能写代码。KP2: 第二步writing-plans（2-5分钟粒度、具体文件路径和代码）。KP3: 第三步执行用TDD和双阶段审查。KP4: 最后finishing-a-development-branch。",
    "Q05": "KP1: 一次一个问题防止用户被压倒，尽量用选择题。KP2: 不能跳过brainstorming，是Hard Gate，明确的anti-pattern。KP3: 简单项目设计可以短但必须呈现并获批准。",
    "Q06": "KP1: 每步2-5分钟，一个动作。写测试和运行测试是两个步骤。KP2: 必须含确切文件路径、完整代码片段、运行命令和预期输出。KP3: 差例子：实现用户认证模块（太大）。好例子分多步：写测试→运行→实现→运行→commit。",
    "Q07": "KP1: 最可能是using-superpowers skill没正确加载，它建立1% Rule。KP2: 检查安装：marketplace配置→plugin install→SessionStart hook。KP3: AI有12种合理化借口跳过skill，using-superpowers的Red Flags表格列出了这些。",
    "Q08": "KP1: 违反Iron Law: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST。可能是X是猜测不是验证的根因。KP2: 正确四阶段：根因调查→模式分析→假设测试→预防。KP3: 越时间紧迫越不能跳过——rushing guarantees rework。",
    "Q09": "KP1: Superpowers没有auto-fix功能，不是代码分析/修复工具，而是通过skill约束AI工作流程。KP2: 核心机制是skills（提示词/工作流规范），不是代码扫描或自动修复。",
    "Q10": "KP1: @语法只是文档引用标记，不是运行时自动触发机制。KP2: Skill调用必须通过Skill tool显式调用。KP3: Skill衔接通过末尾的下一步指示，由agent手动调用。",
}

ANTI_POINTS = {
    "Q01": "AP1: 只说TDD是为了代码质量或减少bug（太泛）。AP2: 说有例外情况可以跳过TDD。",
    "Q02": "AP1: 说skills会自动激活或被系统自动调用。AP2: 编造不存在的skill名称。",
    "Q03": "AP1: 说顺序可以颠倒。AP2: 说自审可以替代正式审查。",
    "Q04": "AP1: 跳过brainstorming直接写代码或计划。AP2: TDD说成可选。AP3: 遗漏worktree隔离。",
    "Q05": "AP1: 说简单任务可以跳过brainstorming。AP2: 说可以一次问多个问题。",
    "Q06": "AP1: 说15-30分钟也算bite-sized。AP2: 说代码片段可省略或用伪代码。",
    "Q07": "AP1: 建议修改AI的system prompt。AP2: 说需要手动每次提醒AI。",
    "Q08": "AP1: 说AI做法可以接受。AP2: 说debugging流程是建议性非强制的。",
    "Q09": "AP1: 描述如何启用auto-fix。AP2: 把其他工具功能误认为Superpowers的。",
    "Q10": "AP1: 说@mention会自动触发skill。AP2: 说有skill chaining API或配置。",
}

QUESTION_TYPES = {
    "Q01": "设计理解", "Q02": "设计理解", "Q03": "设计理解",
    "Q04": "正确使用", "Q05": "正确使用", "Q06": "正确使用",
    "Q07": "避坑判断", "Q08": "避坑判断",
    "Q09": "陷阱题", "Q10": "陷阱题",
}


def run_gemini_judge(question, key_points, anti_points, answer, max_retries=3):
    """Send evaluation prompt to Gemini CLI and parse JSON response."""
    answer_truncated = answer[:2000]
    last_error = None
    for attempt in range(1, max_retries + 1):
        timeout = 180 + (attempt - 1) * 30
        eval_prompt = f"""你是一个严格的考试阅卷员。只根据标准答案评判，不要加入自己的知识。

### 题目
{question}

### 标准答案要点
{key_points}

### 反面要点（提到则扣分）
{anti_points}

### 被评判的回答
{answer_truncated}

### 评分规则
- factual (0-1): 回答中是否有与标准答案矛盾的错误？1=无错误 0=有错误
- coverage (0-1): 标准答案要点覆盖了一半以上？1=是 0=否
- no_hallucination (0-1): 没有提到反面要点或编造不存在的东西？1=无幻觉 0=有幻觉

只输出JSON:
{{"factual": 0或1, "coverage": 0或1, "no_hallucination": 0或1, "total": 总分, "reasoning": "一句话"}}"""

        try:
            result = subprocess.run(
                ["gemini", "-p", eval_prompt],
                capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            # Strip markdown code block wrapping if present
            output = output.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(output)
            if attempt > 1:
                print(f"  (succeeded on attempt {attempt})")
            return parsed
        except subprocess.TimeoutExpired as e:
            last_error = e
            print(f"  WARNING: TIMEOUT after {timeout}s (attempt {attempt}/{max_retries})")
        except json.JSONDecodeError as e:
            last_error = e
            print(f"  WARNING: PARSE_ERROR (attempt {attempt}/{max_retries})")
        except Exception as e:
            last_error = e
            print(f"  WARNING: CLI_ERROR (attempt {attempt}/{max_retries}): {e}")

    return {"factual": 0, "coverage": 0, "no_hallucination": 0, "total": 0, "reasoning": f"EVAL_FAILED: {last_error}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_judge.py <group A|B|C>")
        sys.exit(1)

    group = sys.argv[1].upper()
    if group not in ("A", "B", "C"):
        print("ERROR: group must be A, B, or C")
        sys.exit(1)

    answer_dir = os.path.join(RESULTS_DIR, f"group_{group}_answers")
    eval_dir = os.path.join(RESULTS_DIR, f"group_{group}_eval")
    os.makedirs(eval_dir, exist_ok=True)

    if not os.path.isdir(answer_dir):
        print(f"ERROR: Answer directory not found: {answer_dir}")
        print("Run run_eval.sh first to collect answers.")
        sys.exit(1)

    print(f"=== Running Gemini evaluation for Group {group} ===")
    print()

    results = []
    grand_total = 0

    for q_id in sorted(QUESTIONS.keys()):
        answer_file = os.path.join(answer_dir, f"{q_id}_answer.txt")
        eval_file = os.path.join(eval_dir, f"{q_id}_eval.json")

        if not os.path.isfile(answer_file):
            print(f"  WARNING: {answer_file} not found, skipping")
            continue

        with open(answer_file, "r", encoding="utf-8") as f:
            answer = f.read()

        print(f"--- Evaluating {q_id} ({QUESTION_TYPES[q_id]}) ---")

        eval_result = run_gemini_judge(
            QUESTIONS[q_id], KEY_POINTS[q_id], ANTI_POINTS[q_id], answer
        )

        # Save individual eval
        with open(eval_file, "w", encoding="utf-8") as f:
            json.dump(eval_result, f, indent=2, ensure_ascii=False)

        total = eval_result.get("total", 0)
        if isinstance(total, (int, float)):
            grand_total += int(total)

        results.append({
            "q_id": q_id,
            "type": QUESTION_TYPES[q_id],
            **eval_result
        })

        print(f"  Score: {total}/3 — {eval_result.get('reasoning', '?')}")

    # Summary
    print()
    print(f"=== Group {group} Summary ===")
    print()
    print(f"| Q# | 类型 | factual | coverage | no_hall | total | reasoning |")
    print(f"|----|------|---------|----------|---------|-------|-----------|")
    for r in results:
        print(f"| {r['q_id']} | {r['type']} | {r.get('factual','?')} | {r.get('coverage','?')} | {r.get('no_hallucination','?')} | {r.get('total','?')} | {r.get('reasoning','?')} |")

    print()
    print(f"Grand Total: {grand_total} / 30")
    print(f"Pass Rate: {grand_total/30:.0%}")

    # Save summary
    summary_file = os.path.join(RESULTS_DIR, f"group_{group}_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "group": group,
            "grand_total": grand_total,
            "max_score": 30,
            "pass_rate": round(grand_total / 30, 3),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSaved: {summary_file}")


if __name__ == "__main__":
    main()
