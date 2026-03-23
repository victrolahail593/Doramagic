#!/bin/bash
# Soul Extractor v0.9: Benchmark Evaluation Runner
# Usage: bash run_eval.sh <group> [inject_file]
#   group: A (no injection), B (v0.8), C (v0.9)
#   inject_file: path to CLAUDE.md (required for group B and C)
#
# Example:
#   bash run_eval.sh A
#   bash run_eval.sh B ../../../experiments/exp05-v08-superpowers/superpowers/inject/CLAUDE.md
#   bash run_eval.sh C ../../../experiments/exp06-v09-superpowers/superpowers/inject/CLAUDE.md
set -euo pipefail

GROUP="${1:?Usage: run_eval.sh <group A|B|C> [inject_file]}"
INJECT_FILE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/../results"
mkdir -p "$RESULTS_DIR"

# Validate args
if [[ "$GROUP" != "A" && "$GROUP" != "B" && "$GROUP" != "C" ]]; then
    echo "ERROR: group must be A, B, or C"
    exit 1
fi

if [[ "$GROUP" != "A" && -z "$INJECT_FILE" ]]; then
    echo "ERROR: inject_file required for group $GROUP"
    exit 1
fi

if [[ -n "$INJECT_FILE" && ! -f "$INJECT_FILE" ]]; then
    echo "ERROR: inject file not found: $INJECT_FILE"
    exit 1
fi

# --- Questions (extracted from questions.md) ---
# Each question is a separate file for cleaner processing
QUESTIONS_DIR=$(mktemp -d)
trap "rm -rf $QUESTIONS_DIR" EXIT

cat > "$QUESTIONS_DIR/Q01.txt" << 'EOF'
Superpowers 框架为什么把 TDD（测试驱动开发）设计为 Iron Law（不可违反的铁律），而不是可选的最佳实践？背后的设计理由是什么？
EOF

cat > "$QUESTIONS_DIR/Q02.txt" << 'EOF'
Superpowers 有 14 个 skill，它们不是按固定顺序执行的线性 pipeline，而是根据触发条件动态激活。为什么这样设计？
EOF

cat > "$QUESTIONS_DIR/Q03.txt" << 'EOF'
在 subagent-driven development 中，Superpowers 要求每个 task 完成后做两轮审查：先 spec compliance review，再 code quality review。为什么要分两阶段？一次审查不行吗？
EOF

cat > "$QUESTIONS_DIR/Q04.txt" << 'EOF'
假设我已经安装了 Superpowers，我想给我的项目加一个"用户认证"功能。从提出需求到代码合并，Superpowers 规定的完整流程是什么？列出每一步和对应的 skill。
EOF

cat > "$QUESTIONS_DIR/Q05.txt" << 'EOF'
Brainstorming skill 的流程中规定"一次只问一个问题"，不能一条消息问多个问题。为什么这样限制？另外，如果我的需求非常简单（比如改一个配置值），可以跳过 brainstorming 吗？
EOF

cat > "$QUESTIONS_DIR/Q06.txt" << 'EOF'
Writing-plans skill 要求计划任务是"bite-sized"的。什么叫 bite-sized？给我一个好的和差的例子对比。
EOF

cat > "$QUESTIONS_DIR/Q07.txt" << 'EOF'
我安装了 Superpowers，但在对话中发现 AI agent 完全忽略了 skills——不做 brainstorming，不做 TDD，直接写代码。可能是什么问题？怎么解决？
EOF

cat > "$QUESTIONS_DIR/Q08.txt" << 'EOF'
我在 debugging 一个问题，试了几个修复方法都没用，然后 AI 说"这个问题可能是 X 导致的"就开始改代码了。在 Superpowers 的 systematic-debugging 框架下，这样做对吗？正确的做法是什么？
EOF

cat > "$QUESTIONS_DIR/Q09.txt" << 'EOF'
我听说 Superpowers 有一个 auto-fix 功能，可以自动扫描代码中的问题并提供修复建议，类似 ESLint 的 --fix。请问怎么启用这个功能？
EOF

cat > "$QUESTIONS_DIR/Q10.txt" << 'EOF'
我在 Superpowers 文档里看到 skill 可以用 @ 语法引用其他 skill。那我可以在 brainstorming 的设计文档里写 @test-driven-development 来自动触发 TDD skill 吗？
EOF

# --- Run evaluation ---
ANSWER_DIR="$RESULTS_DIR/group_${GROUP}_answers"
mkdir -p "$ANSWER_DIR"

echo "=== Running Group $GROUP evaluation ==="
echo "Inject file: ${INJECT_FILE:-none}"
echo ""

for q_file in "$QUESTIONS_DIR"/Q*.txt; do
    q_num=$(basename "$q_file" .txt)
    question=$(cat "$q_file")
    answer_file="$ANSWER_DIR/${q_num}_answer.txt"

    echo "--- $q_num ---"

    # Build prompt
    if [[ "$GROUP" == "A" ]]; then
        # No injection - just the question
        prompt="$question"
    else
        # With injection - prepend the CLAUDE.md content
        inject_content=$(cat "$INJECT_FILE")
        prompt="以下是关于 Superpowers 项目的知识注入文件，请基于这些知识回答后面的问题。

--- 知识注入开始 ---
$inject_content
--- 知识注入结束 ---

问题：$question"
    fi

    # Use Claude (Sonnet) as test subject to save cost, Haiku too weak
    echo "$prompt" | CLAUDECODE="" claude -p --model sonnet --no-session-persistence --disable-slash-commands --allowedTools "" 2>/dev/null > "$answer_file" || {
        echo "  WARNING: Claude CLI failed for $q_num, retrying..."
        echo "$prompt" | CLAUDECODE="" claude -p --model sonnet --no-session-persistence --disable-slash-commands --allowedTools "" 2>/dev/null > "$answer_file" || {
            echo "  ERROR: Claude CLI failed twice for $q_num"
            echo "FAILED" > "$answer_file"
        }
    }

    answer_len=$(wc -c < "$answer_file" | tr -d ' ')
    echo "  Answer: $answer_len bytes -> $answer_file"
done

echo ""
echo "=== All answers collected in $ANSWER_DIR ==="
echo ""

# --- Run evaluation with Gemini as judge ---
EVAL_DIR="$RESULTS_DIR/group_${GROUP}_eval"
mkdir -p "$EVAL_DIR"

echo "=== Running Gemini evaluation for Group $GROUP ==="

# Key points and anti points for each question (compact format)
declare -A KEY_POINTS
declare -A ANTI_POINTS

KEY_POINTS[Q01]="KP1: AI容易作弊——先写代码再补测试，测试只验证代码做了什么而非应该做什么。KP2: 先写测试迫使AI承认无知，打破自信幻觉。KP3: tests-after会立即通过证明不了东西；tests-first先失败(RED)证明测试有检测力。"
ANTI_POINTS[Q01]="AP1: 只说TDD是为了代码质量或减少bug（太泛）。AP2: 说有例外情况可以跳过TDD。"

KEY_POINTS[Q02]="KP1: 软件开发不是线性的，可能需要在实现中途回去brainstorming。KP2: Skill是可组合模块形成有向无环图。KP3: 每个skill有触发条件，agent根据上下文判断激活。"
ANTI_POINTS[Q02]="AP1: 说skills会自动激活或被系统自动调用。AP2: 编造不存在的skill名称。"

KEY_POINTS[Q03]="KP1: spec compliance和code quality是正交维度，代码可以优雅但不符需求。KP2: 顺序必须spec先quality后。KP3: 每轮有review loop——发现问题→修复→重新审查。"
ANTI_POINTS[Q03]="AP1: 说顺序可以颠倒。AP2: 说自审可以替代正式审查。"

KEY_POINTS[Q04]="KP1: 第一步brainstorming（探索需求、问问题、提方案、获批准、写设计文档），设计批准前不能写代码。KP2: 第二步writing-plans（2-5分钟粒度、具体文件路径和代码）。KP3: 第三步执行用TDD和双阶段审查。KP4: 最后finishing-a-development-branch。"
ANTI_POINTS[Q04]="AP1: 跳过brainstorming直接写代码或计划。AP2: TDD说成可选。AP3: 遗漏worktree隔离。"

KEY_POINTS[Q05]="KP1: 一次一个问题防止用户被压倒，尽量用选择题。KP2: 不能跳过brainstorming，是Hard Gate，明确的anti-pattern。KP3: 简单项目设计可以短但必须呈现并获批准。"
ANTI_POINTS[Q05]="AP1: 说简单任务可以跳过brainstorming。AP2: 说可以一次问多个问题。"

KEY_POINTS[Q06]="KP1: 每步2-5分钟，一个动作。写测试和运行测试是两个步骤。KP2: 必须含确切文件路径、完整代码片段、运行命令和预期输出。KP3: 差例子：实现用户认证模块（太大）。好例子分多步：写测试→运行→实现→运行→commit。"
ANTI_POINTS[Q06]="AP1: 说15-30分钟也算bite-sized。AP2: 说代码片段可省略或用伪代码。"

KEY_POINTS[Q07]="KP1: 最可能是using-superpowers skill没正确加载，它建立1% Rule。KP2: 检查安装：marketplace配置→plugin install→SessionStart hook。KP3: AI有12种合理化借口跳过skill，using-superpowers的Red Flags表格列出了这些。"
ANTI_POINTS[Q07]="AP1: 建议修改AI的system prompt。AP2: 说需要手动每次提醒AI。"

KEY_POINTS[Q08]="KP1: 违反Iron Law: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST。可能是X是猜测不是验证的根因。KP2: 正确四阶段：根因调查→模式分析→假设测试→预防。KP3: 越时间紧迫越不能跳过——rushing guarantees rework。"
ANTI_POINTS[Q08]="AP1: 说AI做法可以接受。AP2: 说debugging流程是建议性非强制的。"

KEY_POINTS[Q09]="KP1: Superpowers没有auto-fix功能，不是代码分析/修复工具，而是通过skill约束AI工作流程。KP2: 核心机制是skills（提示词/工作流规范），不是代码扫描或自动修复。"
ANTI_POINTS[Q09]="AP1: 描述如何启用auto-fix。AP2: 把其他工具功能误认为Superpowers的。"

KEY_POINTS[Q10]="KP1: @语法只是文档引用标记，不是运行时自动触发机制。KP2: Skill调用必须通过Skill tool显式调用。KP3: Skill衔接通过末尾的下一步指示，由agent手动调用。"
ANTI_POINTS[Q10]="AP1: 说@mention会自动触发skill。AP2: 说有skill chaining API或配置。"

for q_num in Q01 Q02 Q03 Q04 Q05 Q06 Q07 Q08 Q09 Q10; do
    answer_file="$ANSWER_DIR/${q_num}_answer.txt"
    eval_file="$EVAL_DIR/${q_num}_eval.json"
    question=$(cat "$QUESTIONS_DIR/${q_num}.txt")
    answer=$(cat "$answer_file")

    echo "--- Evaluating $q_num ---"

    eval_prompt="你是一个严格的考试阅卷员。只根据标准答案评判，不要加入自己的知识。

### 题目
$question

### 标准答案要点
${KEY_POINTS[$q_num]}

### 反面要点（提到则扣分）
${ANTI_POINTS[$q_num]}

### 被评判的回答
$answer

### 评分规则
- factual (0-1): 回答中是否有与标准答案矛盾的错误？1=无错误 0=有错误
- coverage (0-1): 标准答案要点覆盖了一半以上？1=是 0=否
- no_hallucination (0-1): 没有提到反面要点或编造不存在的东西？1=无幻觉 0=有幻觉

只输出JSON:
{\"factual\": 0或1, \"coverage\": 0或1, \"no_hallucination\": 0或1, \"total\": 总分, \"reasoning\": \"一句话\"}"

    echo "$eval_prompt" | gemini -p 2>/dev/null > "$eval_file" || {
        echo "  WARNING: Gemini failed for $q_num"
        echo '{"factual": 0, "coverage": 0, "no_hallucination": 0, "total": 0, "reasoning": "EVAL_FAILED"}' > "$eval_file"
    }

    echo "  -> $eval_file"
done

echo ""
echo "=== Evaluation complete ==="
echo ""

# --- Summary ---
echo "=== Group $GROUP Summary ==="
echo ""
echo "| Q# | factual | coverage | no_hallucination | total | reasoning |"
echo "|----|---------|----------|-----------------|-------|-----------|"

GRAND_TOTAL=0
for q_num in Q01 Q02 Q03 Q04 Q05 Q06 Q07 Q08 Q09 Q10; do
    eval_file="$EVAL_DIR/${q_num}_eval.json"
    # Extract JSON values (handle possible markdown wrapping)
    eval_content=$(cat "$eval_file" | sed 's/```json//g' | sed 's/```//g' | tr -d '\n')
    factual=$(echo "$eval_content" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['factual'])" 2>/dev/null || echo "?")
    coverage=$(echo "$eval_content" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['coverage'])" 2>/dev/null || echo "?")
    no_hall=$(echo "$eval_content" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['no_hallucination'])" 2>/dev/null || echo "?")
    total=$(echo "$eval_content" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['total'])" 2>/dev/null || echo "?")
    reasoning=$(echo "$eval_content" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['reasoning'])" 2>/dev/null || echo "?")

    if [[ "$total" =~ ^[0-9]+$ ]]; then
        GRAND_TOTAL=$((GRAND_TOTAL + total))
    fi

    echo "| $q_num | $factual | $coverage | $no_hall | $total | $reasoning |"
done

echo ""
echo "Grand Total: $GRAND_TOTAL / 30"
echo "Pass Rate: $(python3 -c "print(f'{$GRAND_TOTAL/30:.0%}')" 2>/dev/null || echo '?')"

# Save summary
SUMMARY_FILE="$RESULTS_DIR/group_${GROUP}_summary.md"
echo "# Group $GROUP Results" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Grand Total: $GRAND_TOTAL / 30" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Details in: $EVAL_DIR/" >> "$SUMMARY_FILE"
echo "  -> $SUMMARY_FILE"
