#!/bin/bash
# Collect answers only (no judging). Judging is done by run_judge.py
# Usage: bash run_answers.sh <group> [inject_file]
set -euo pipefail

GROUP="${1:?Usage: run_answers.sh <group A|B|C> [inject_file]}"
INJECT_FILE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/../results"
mkdir -p "$RESULTS_DIR"

if [[ "$GROUP" != "A" && "$GROUP" != "B" && "$GROUP" != "C" ]]; then
    echo "ERROR: group must be A, B, or C"; exit 1
fi
if [[ "$GROUP" != "A" && -z "$INJECT_FILE" ]]; then
    echo "ERROR: inject_file required for group $GROUP"; exit 1
fi
if [[ -n "$INJECT_FILE" && ! -f "$INJECT_FILE" ]]; then
    echo "ERROR: inject file not found: $INJECT_FILE"; exit 1
fi

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
假设我已经安装了 Superpowers，我想给我的项目加一个用户认证功能。从提出需求到代码合并，Superpowers 规定的完整流程是什么？列出每一步和对应的 skill。
EOF
cat > "$QUESTIONS_DIR/Q05.txt" << 'EOF'
Brainstorming skill 的流程中规定一次只问一个问题，不能一条消息问多个问题。为什么这样限制？另外，如果我的需求非常简单（比如改一个配置值），可以跳过 brainstorming 吗？
EOF
cat > "$QUESTIONS_DIR/Q06.txt" << 'EOF'
Writing-plans skill 要求计划任务是 bite-sized 的。什么叫 bite-sized？给我一个好的和差的例子对比。
EOF
cat > "$QUESTIONS_DIR/Q07.txt" << 'EOF'
我安装了 Superpowers，但在对话中发现 AI agent 完全忽略了 skills——不做 brainstorming，不做 TDD，直接写代码。可能是什么问题？怎么解决？
EOF
cat > "$QUESTIONS_DIR/Q08.txt" << 'EOF'
我在 debugging 一个问题，试了几个修复方法都没用，然后 AI 说这个问题可能是 X 导致的就开始改代码了。在 Superpowers 的 systematic-debugging 框架下，这样做对吗？正确的做法是什么？
EOF
cat > "$QUESTIONS_DIR/Q09.txt" << 'EOF'
我听说 Superpowers 有一个 auto-fix 功能，可以自动扫描代码中的问题并提供修复建议，类似 ESLint 的 --fix。请问怎么启用这个功能？
EOF
cat > "$QUESTIONS_DIR/Q10.txt" << 'EOF'
我在 Superpowers 文档里看到 skill 可以用 @ 语法引用其他 skill。那我可以在 brainstorming 的设计文档里写 @test-driven-development 来自动触发 TDD skill 吗？
EOF

ANSWER_DIR="$RESULTS_DIR/group_${GROUP}_answers"
mkdir -p "$ANSWER_DIR"

echo "=== Collecting Group $GROUP answers ==="
echo "Inject file: ${INJECT_FILE:-none}"
echo ""

for q_file in "$QUESTIONS_DIR"/Q*.txt; do
    q_num=$(basename "$q_file" .txt)
    question=$(cat "$q_file")
    answer_file="$ANSWER_DIR/${q_num}_answer.txt"

    echo -n "--- $q_num --- "

    if [[ "$GROUP" == "A" ]]; then
        prompt="$question"
    else
        inject_content=$(cat "$INJECT_FILE")
        prompt="以下是关于 Superpowers 项目的知识注入文件，请基于这些知识回答后面的问题。

--- 知识注入开始 ---
$inject_content
--- 知识注入结束 ---

问题：$question"
    fi

    echo "$prompt" | CLAUDECODE="" claude -p --model sonnet --no-session-persistence --disable-slash-commands --allowedTools "" 2>/dev/null > "$answer_file" || {
        echo "RETRY..."
        echo "$prompt" | CLAUDECODE="" claude -p --model sonnet --no-session-persistence --disable-slash-commands --allowedTools "" 2>/dev/null > "$answer_file" || {
            echo "FAILED"
            echo "FAILED" > "$answer_file"
        }
    }

    answer_len=$(wc -c < "$answer_file" | tr -d ' ')
    echo "${answer_len} bytes"
done

echo ""
echo "=== Done. Answers in $ANSWER_DIR ==="
echo "Next: python3 run_judge.py $GROUP"
