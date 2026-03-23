#!/bin/bash
# Doramagic v1.0: Assemble final output — Soul + Module Map + Community Wisdom
# Usage: bash assemble-output.sh <output_dir>
set -euo pipefail

OUTPUT_DIR="${1:?Usage: assemble-output.sh <output_dir>}"
SOUL_DIR="$OUTPUT_DIR/soul"
INJECT_DIR="$OUTPUT_DIR/inject"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$INJECT_DIR"

REPO_NAME=$(basename "$OUTPUT_DIR")
NARRATIVE="$SOUL_DIR/expert_narrative.md"
MODULE_MAP="$SOUL_DIR/module-map.md"
COMMUNITY_WISDOM="$SOUL_DIR/community-wisdom.md"

echo "=== Doramagic: Assembling output for $REPO_NAME ==="

# --- Check validation gate (must PASS before assembly) ---
VALIDATION_REPORT="$SOUL_DIR/validation_report.json"
if [ -f "$VALIDATION_REPORT" ]; then
    if python3 -c "import json; r=json.load(open('$VALIDATION_REPORT')); exit(0 if r['summary']['overall_pass'] else 1)" 2>/dev/null; then
        echo "  Validation: PASS"
    else
        echo "  ERROR: Validation did not pass. Fix errors in Stage 3.5 before assembling."
        exit 1
    fi
else
    echo "  ERROR: No validation report found. Run Stage 3.5 first."
    exit 1
fi

# --- Check required files ---
if [ ! -f "$NARRATIVE" ]; then
    echo "ERROR: expert_narrative.md not found. Run Stage 4 first."
    exit 1
fi
if [ ! -f "$MODULE_MAP" ]; then
    echo "ERROR: module-map.md not found. Run Stage M first."
    exit 1
fi
if [ ! -f "$COMMUNITY_WISDOM" ]; then
    echo "ERROR: community-wisdom.md not found. Run Stage C first."
    exit 1
fi

# --- Build CRITICAL RULES section from cards (规则路 — script-generated) ---
RULES_SECTION=$(mktemp)
echo "## CRITICAL RULES" > "$RULES_SECTION"
echo "" >> "$RULES_SECTION"
echo "以下规则从代码分析和社区经验中提取，按严重度排序。" >> "$RULES_SECTION"
echo "" >> "$RULES_SECTION"

# Extract CRITICAL rules first, then HIGH
for severity in CRITICAL HIGH; do
    for card in "$SOUL_DIR"/cards/rules/DR-*.md; do
        [ -f "$card" ] || continue
        card_sev=$(grep -m1 'severity:' "$card" 2>/dev/null | sed 's/severity: *//;s/ *$//' | tr '[:lower:]' '[:upper:]')
        if [ "$card_sev" = "$severity" ]; then
            title=$(grep -m1 'title:' "$card" 2>/dev/null | sed 's/title: *"*//;s/"*$//')
            rule=$(python3 -c "
import sys, re
text = open('$card').read()
m = re.search(r'^rule:\s*\|?\s*\n((?:  .+\n?)*)', text, re.MULTILINE)
if m:
    lines = [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]
    print(' '.join(lines[:2]))
else:
    m2 = re.search(r'^rule:\s*(.+)', text, re.MULTILINE)
    print(m2.group(1).strip() if m2 else '')
" 2>/dev/null || echo "")
            echo "- **[$severity]** $title — $rule" >> "$RULES_SECTION"
        fi
    done
done
echo "" >> "$RULES_SECTION"

# --- Build QUICK REFERENCE table (速查路 — script-generated) ---
REFERENCE_SECTION=$(mktemp)
echo "## QUICK REFERENCE" >> "$REFERENCE_SECTION"
echo "" >> "$REFERENCE_SECTION"
echo "| 规则 | 严重度 |" >> "$REFERENCE_SECTION"
echo "|------|--------|" >> "$REFERENCE_SECTION"

for card in "$SOUL_DIR"/cards/rules/DR-*.md; do
    [ -f "$card" ] || continue
    title=$(grep -m1 'title:' "$card" 2>/dev/null | sed 's/title: *"*//;s/"*$//' || echo "$(basename $card .md)")
    sev=$(grep -m1 'severity:' "$card" 2>/dev/null | sed 's/severity: *//;s/ *$//' | tr '[:lower:]' '[:upper:]' || echo "-")
    echo "| $title | $sev |" >> "$REFERENCE_SECTION"
done
echo "" >> "$REFERENCE_SECTION"

# --- Build FEATURE INVENTORY section (from repo_facts.json) ---
INVENTORY_SECTION=$(mktemp)
REPO_FACTS="$OUTPUT_DIR/artifacts/repo_facts.json"
if [ -f "$REPO_FACTS" ]; then
    python3 - "$REPO_FACTS" << 'PYEOF' > "$INVENTORY_SECTION"
import json, sys
facts = json.load(open(sys.argv[1]))
skills = facts.get("skills", [])
commands = facts.get("commands", [])
config_keys = facts.get("config_keys", [])

lines = ["## FEATURE INVENTORY", ""]
if skills:
    lines.append("**Skills / Features:**")
    for s in skills:
        lines.append(f"- `{s}`")
    lines.append("")
if commands:
    lines.append("**Commands:**")
    for c in commands[:20]:  # cap at 20 to avoid bloat
        lines.append(f"- `{c}`")
    lines.append("")
if config_keys:
    lines.append("**Config Keys:**")
    for k in config_keys[:15]:
        lines.append(f"- `{k}`")
    lines.append("")
print("\n".join(lines))
PYEOF
else
    echo "" > "$INVENTORY_SECTION"
fi

# --- Build MODULE MAP section (from module-map.md) ---
MODULE_SECTION=$(mktemp)
echo "## MODULE MAP" > "$MODULE_SECTION"
echo "" >> "$MODULE_SECTION"
# Strip the H1 title from module-map.md since we provide our own H2 heading
tail -n +3 "$MODULE_MAP" >> "$MODULE_SECTION"
echo "" >> "$MODULE_SECTION"

# --- Build COMMUNITY WISDOM section (from community-wisdom.md) ---
COMMUNITY_SECTION=$(mktemp)
echo "## COMMUNITY WISDOM" > "$COMMUNITY_SECTION"
echo "" >> "$COMMUNITY_SECTION"
# Strip the H1 title from community-wisdom.md since we provide our own H2 heading
tail -n +3 "$COMMUNITY_WISDOM" >> "$COMMUNITY_SECTION"
echo "" >> "$COMMUNITY_SECTION"

# --- Assemble CLAUDE.md: rules + inventory + modules + narrative + community + reference ---
CLAUDE_MD="$INJECT_DIR/CLAUDE.md"
{
    echo "# $REPO_NAME — Doramagic AI Advisor Pack"
    echo "# Generated by Doramagic v1.0 | Three-module: Soul + Architecture + Community"
    echo "# Structure: CRITICAL RULES → FEATURE INVENTORY → MODULE MAP → EXPERT KNOWLEDGE → COMMUNITY WISDOM → QUICK REFERENCE"
    echo ""
    cat "$RULES_SECTION"
    cat "$INVENTORY_SECTION"
    cat "$MODULE_SECTION"
    echo "## EXPERT KNOWLEDGE"
    echo ""
    cat "$NARRATIVE"
    echo ""
    cat "$COMMUNITY_SECTION"
    cat "$REFERENCE_SECTION"
} > "$CLAUDE_MD"
echo "  -> $CLAUDE_MD"

# --- Generate .cursorrules (same content) ---
CURSORRULES="$INJECT_DIR/.cursorrules"
cp "$CLAUDE_MD" "$CURSORRULES"
echo "  -> $CURSORRULES"

# --- Generate advisor-brief.md (non-technical user brief) ---
ADVISOR_BRIEF="$INJECT_DIR/advisor-brief.md"
python3 - "$SOUL_DIR" "$REPO_NAME" "$ADVISOR_BRIEF" << 'PYEOF'
import os, re, sys

soul_dir = sys.argv[1]
repo_name = sys.argv[2]
output_path = sys.argv[3]

# Read soul essence (Q3/Q4/Q5 = core promise)
soul_path = os.path.join(soul_dir, "00-soul.md")
soul_content = ""
if os.path.exists(soul_path):
    with open(soul_path, encoding="utf-8") as f:
        soul_content = f.read()

# Extract core promise (Q3)
promise_match = re.search(r'(?:核心承诺|Core Promise|3\.|Q3)[^\n]*\n+(.*?)(?=\n##|\n\d\.|\Z)', soul_content, re.DOTALL)
promise = promise_match.group(1).strip()[:200] if promise_match else ""

# Extract one-liner (Q5)
oneliner_match = re.search(r'(?:一句话总结|One.liner|5\.|Q5)[^\n]*\n+(.*?)(?=\n##|\n\d\.|\Z)', soul_content, re.DOTALL)
oneliner = oneliner_match.group(1).strip()[:200] if oneliner_match else ""

# Count modules from module-map.md
module_map_path = os.path.join(soul_dir, "module-map.md")
module_count = 0
module_names = []
if os.path.exists(module_map_path):
    with open(module_map_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'^### (M-\d+：.+)', line)
            if m:
                module_count += 1
                module_names.append(m.group(1).replace("M-", "").split("：", 1)[-1].strip())

# Count CRITICAL rules
rules_dir = os.path.join(soul_dir, "cards", "rules")
critical_rules = []
high_rules = []
if os.path.isdir(rules_dir):
    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(rules_dir, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        sev_match = re.search(r'^severity:\s*(\w+)', content, re.MULTILINE)
        title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
        if sev_match and title_match:
            sev = sev_match.group(1).upper()
            title = title_match.group(1)
            if sev == "CRITICAL":
                critical_rules.append(title)
            elif sev == "HIGH":
                high_rules.append(title)

# Count community signals
community_path = os.path.join(soul_dir, "community-wisdom.md")
pain_count = 0
if os.path.exists(community_path):
    with open(community_path, encoding="utf-8") as f:
        pain_count = len(re.findall(r'^### 痛点', f.read(), re.MULTILINE))

lines = [
    f"# {repo_name} — AI 顾问简介",
    "",
    f"> 由 Doramagic 从 {repo_name} 开源项目中提取，注入AI，生成专属顾问。",
    "",
    "## 这位顾问能帮你做什么",
    "",
]

if oneliner:
    lines.append(f"**一句话**：{oneliner}")
    lines.append("")
if promise:
    lines.append(f"**核心承诺**：{promise}")
    lines.append("")

lines += [
    "这位 AI 顾问掌握了：",
    f"- 项目的设计哲学和心智模型（知道\"为什么\"，不只是\"怎么用\"）",
    f"- {module_count} 个核心模块的边界和接口（知道各部分如何协作）" if module_count else "",
    f"- {len(critical_rules)} 个最高风险陷阱（遇到前主动提醒你）" if critical_rules else "",
    f"- {pain_count} 个社区反复踩坑的模式（真实项目经验，不是文档理论）" if pain_count else "",
    "",
]
lines = [l for l in lines if l is not None]  # remove None

if module_names:
    lines += [
        "## 项目模块",
        "",
        "| 模块 |",
        "|------|",
    ]
    for name in module_names:
        lines.append(f"| {name} |")
    lines.append("")

if critical_rules:
    lines += [
        "## 最高风险警告（CRITICAL）",
        "",
    ]
    for rule in critical_rules[:5]:
        lines.append(f"- {rule}")
    lines.append("")

lines += [
    "## 适合问这位顾问的问题",
    "",
    '- \u201c我应该用 [A 方案] 还是 [B 方案]？\u201d',
    '- \u201c我遇到了 [报错]，这是什么问题，怎么排查？\u201d',
    '- \u201c[某功能] 有什么限制或注意事项？\u201d',
    '- \u201c我想做 [X]，这个项目支持吗？最佳做法是什么？\u201d',
    "",
    "---",
    f"*由 Doramagic v1.0 自动生成*",
]

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"  -> {output_path}")
PYEOF

# --- Generate project_soul.md (full soul with card index) ---
SOUL_SUMMARY="$SOUL_DIR/project_soul.md"
{
    cat "$CLAUDE_MD"
    echo ""
    echo "---"
    echo ""
    echo "## 知识卡片索引"
    echo ""
    echo "| ID | 类型 | 标题 | 严重度 |"
    echo "|----|------|------|--------|"
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
        echo "| $id | $type | $title | $sev |"
    done
    echo ""
    echo "---"
    echo "*Generated by Doramagic v1.0 $(date +%Y-%m-%d)*"
} > "$SOUL_SUMMARY"
echo "  -> $SOUL_SUMMARY"

# --- Cleanup temp files ---
rm -f "$RULES_SECTION" "$INVENTORY_SECTION" "$REFERENCE_SECTION" "$MODULE_SECTION" "$COMMUNITY_SECTION"

# --- Run output validation ---
echo ""
echo "=== Validating output ==="
VALIDATE_SCRIPT="$SCRIPT_DIR/validate_output.py"
if [ -f "$VALIDATE_SCRIPT" ]; then
    python3 "$VALIDATE_SCRIPT" --file "$CLAUDE_MD"
    VALIDATE_EXIT=$?
    if [ $VALIDATE_EXIT -ne 0 ]; then
        echo "ERROR: Output validation failed. See above for details."
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
echo "=== DORAMAGIC ASSEMBLY COMPLETE ==="
echo "repo=$REPO_NAME"
echo "output_size=$CLAUDE_SIZE bytes"
echo "concepts=$CC_COUNT"
echo "workflows=$WF_COUNT"
echo "rules=$DR_COUNT"
echo "inject=$INJECT_DIR"
echo ""
echo "Files for user:"
echo "  CLAUDE.md       — Claude Code AI advisor injection"
echo "  .cursorrules    — Cursor AI advisor injection"
echo "  advisor-brief.md — Non-technical user brief"
echo "  project_soul.md — Full soul with card index"
