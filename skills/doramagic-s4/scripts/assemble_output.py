#!/usr/bin/env python3
"""Assemble Output — 从知识卡片编译最终 Skill 输出。

用法：
    python3 assemble_output.py --cards-dir /tmp/doramagic/cards/ --output /tmp/doramagic/output/

输出：
    - SKILL.md（从卡片编译）
    - PROVENANCE.md（来源追溯）
    - LIMITATIONS.md（能力边界 + 暗雷评估）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load_cards(cards_dir: Path) -> dict[str, list[dict]]:
    """加载所有知识卡片。"""
    cards = defaultdict(list)

    for card_type in ["concept", "workflow", "decision", "trap", "signature"]:
        card_dir = cards_dir / card_type
        if card_dir.exists():
            for card_file in sorted(card_dir.glob("*.md")):
                content = card_file.read_text(encoding="utf-8")
                cards[card_type].append({
                    "file": card_file.name,
                    "content": content,
                    "path": str(card_file)
                })

    return dict(cards)


def parse_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter。"""
    if not content.strip().startswith("---"):
        return {}

    parts = content.split("---")
    if len(parts) < 3:
        return {}

    frontmatter_text = parts[1].strip()
    result = {}

    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")

    return result


def extract_section(content: str, section_name: str) -> str:
    """提取指定章节内容。"""
    pattern = rf"##\s*{section_name}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def compile_skill_md(cards: dict, metadata: dict) -> str:
    """从卡片编译 SKILL.md。"""

    sections = []

    # Frontmatter
    frontmatter = f"""---
name: {metadata.get('skill_name', 'extracted-skill')}
description: >
  {metadata.get('description', '从开源项目提取的知识技能')}
version: 1.0.0
user-invocable: true
allowed-tools: [exec, read, write]
tags: [doramagic, extracted]
metadata:
  openclaw:
    skillKey: {metadata.get('skill_key', 'auto')}
    category: builder
    sources: {json.dumps(metadata.get('sources', []))}
    extracted_at: {datetime.now().isoformat()}
---
"""
    sections.append(frontmatter)

    # Title
    sections.append(f"\n# {metadata.get('skill_name', 'Extracted Skill')}\n")

    # WHY Section
    why_content = metadata.get("why", "待补充设计理念")
    why_recoverability = metadata.get("why_recoverability", "未评估")

    sections.append(f"""## WHY（设计理念）

**WHY 可恢复性**: {why_recoverability}

{why_content}

""")

    # UNSAID Section
    unsaid_items = []
    if "trap" in cards:
        for card in cards["trap"]:
            fm = parse_frontmatter(card["content"])
            desc = extract_section(card["content"], "Description")
            how = extract_section(card["content"], "How to Avoid")
            unsaid_items.append(f"- **{fm.get('title', '未知陷阱')}** ({fm.get('severity', 'MEDIUM')})\n  {desc[:200]}..." if len(desc) > 200 else f"- **{fm.get('title', '未知陷阱')}** ({fm.get('severity', 'MEDIUM')})\n  {desc}")

    sections.append(f"""## UNSAID（注意事项）

{chr(10).join(unsaid_items) if unsaid_items else "暂无已知陷阱"}

""")

    # Capabilities Section（来自概念卡）
    if "concept" in cards:
        sections.append("## Capabilities\n\n")
        for card in cards["concept"]:
            fm = parse_frontmatter(card["content"])
            identity = extract_section(card["content"], "Identity")
            sections.append(f"### {fm.get('title', '概念')}\n\n{identity}\n\n")

    # Workflow Section（来自工作流卡）
    if "workflow" in cards:
        sections.append("## Workflow\n\n")
        for card in cards["workflow"]:
            fm = parse_frontmatter(card["content"])
            steps = extract_section(card["content"], "Steps")
            sections.append(f"### {fm.get('title', '工作流')}\n\n{steps}\n\n")

    # Decision Rules Section（来自决策卡）
    if "decision" in cards:
        sections.append("## Decision Rules\n\n")
        for card in cards["decision"]:
            fm = parse_frontmatter(card["content"])
            rule = extract_section(card["content"], "Rule")
            context = extract_section(card["content"], "Context")
            sections.append(f"""### {fm.get('title', '决策')}

**规则**: {rule}

**上下文**: {context}

""")

    return "\n".join(sections)


def compile_provenance_md(cards: dict, metadata: dict) -> str:
    """编译 PROVENANCE.md（来源追溯）。"""

    lines = [
        "# Provenance（来源追溯）",
        "",
        f"提取时间: {datetime.now().isoformat()}",
        f"来源项目: {', '.join(metadata.get('sources', ['未知']))}",
        "",
        "## 知识卡片清单",
        ""
    ]

    for card_type, card_list in cards.items():
        lines.append(f"### {card_type.upper()} Cards ({len(card_list)})")
        lines.append("")
        for card in card_list:
            fm = parse_frontmatter(card["content"])
            card_id = fm.get("card_id", "N/A")
            title = fm.get("title", "未命名")
            repo = fm.get("repo", "未知来源")
            evidence = extract_section(card["content"], "Evidence")

            lines.append(f"- **{card_id}**: {title}")
            lines.append(f"  - 来源: {repo}")
            lines.append(f"  - 文件: {card['file']}")
            if evidence:
                lines.append(f"  - 证据: {evidence[:100]}...")
            lines.append("")

    # WHY 可恢复性记录
    lines.extend([
        "## WHY 可恢复性记录",
        "",
        f"评估结果: {metadata.get('why_recoverability', '未评估')}",
        "",
        "证据来源:",
        f"- README: {'有' if metadata.get('has_readme_why') else '无'}",
        f"- ADR: {'有' if metadata.get('has_adr') else '无'}",
        f"- Issue 讨论: {'有' if metadata.get('has_issue_discussion') else '无'}",
        f"- CHANGELOG 边界: {'有' if metadata.get('has_changelog_boundary') else '无'}",
        ""
    ])

    return "\n".join(lines)


def compile_limitations_md(cards: dict, metadata: dict) -> str:
    """编译 LIMITATIONS.md（能力边界 + 暗雷评估）。"""

    dark_signals = metadata.get("dark_trap_signals", [])

    lines = [
        "# Limitations（能力边界）",
        "",
        "## 覆盖范围",
        "",
        f"- 概念卡: {len(cards.get('concept', []))} 张",
        f"- 工作流卡: {len(cards.get('workflow', []))} 张",
        f"- 决策卡: {len(cards.get('decision', []))} 张",
        f"- 陷阱卡: {len(cards.get('trap', []))} 张",
        "",
        "## 能力边界",
        "",
        "### 能做什么",
        "- 提供概念理解和最佳实践",
        "- 给出决策规则和建议",
        "- 标注已知陷阱和风险",
        "",
        "### 不能做什么",
        "- 替代专业判断",
        "- 保证在所有场景下适用",
        "- 覆盖所有边缘情况",
        "",
        "## 暗雷评估",
        ""
    ]

    if dark_signals:
        for signal in dark_signals:
            risk_emoji = "🔴" if signal.get("risk") == "HIGH" else "🟡" if signal.get("risk") == "MEDIUM" else "🟢"
            lines.append(f"### {risk_emoji} {signal.get('indicator', '未知指标')}")
            lines.append("")
            lines.append(f"- **风险等级**: {signal.get('risk', 'UNKNOWN')}")
            if "value" in signal:
                lines.append(f"- **指标值**: {signal['value']}")
            lines.append(f"- **说明**: {signal.get('description', '无描述')}")
            lines.append("")
    else:
        lines.append("暂未检测到高风险暗雷信号。")
        lines.append("")

    # 跨项目综合标注
    if metadata.get("cross_project_synthesis"):
        lines.extend([
            "## 跨项目综合",
            "",
            f"- **共识**: {len(metadata.get('consensus', []))} 项",
            f"- **冲突**: {len(metadata.get('conflicts', []))} 项",
            f"- **独有**: {len(metadata.get('unique', []))} 项",
            ""
        ])

        if metadata.get("conflicts"):
            lines.append("### 冲突项（需用户决策）")
            lines.append("")
            for conflict in metadata["conflicts"]:
                lines.append(f"- {conflict}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Assemble Doramagic output from knowledge cards")
    parser.add_argument("--cards-dir", required=True, help="Knowledge cards directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--metadata", help="Optional metadata JSON file")

    args = parser.parse_args()

    cards_dir = Path(args.cards_dir)
    output_dir = Path(args.output)

    if not cards_dir.exists():
        print(f"Error: Cards directory {cards_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载卡片
    print(f"Loading cards from {cards_dir}...")
    cards = load_cards(cards_dir)

    total_cards = sum(len(v) for v in cards.values())
    print(f"Found {total_cards} cards: {dict((k, len(v)) for k, v in cards.items())}")

    # 加载元数据
    metadata = {
        "skill_name": "wifi-password-manager",
        "skill_key": "wifi-pwd",
        "sources": [],
        "why": "待从卡片提取",
        "why_recoverability": "未评估"
    }

    if args.metadata:
        metadata_path = Path(args.metadata)
        if metadata_path.exists():
            metadata.update(json.loads(metadata_path.read_text(encoding="utf-8")))

    # 编译输出
    print("\nCompiling SKILL.md...")
    skill_md = compile_skill_md(cards, metadata)
    (output_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    print("Compiling PROVENANCE.md...")
    provenance_md = compile_provenance_md(cards, metadata)
    (output_dir / "PROVENANCE.md").write_text(provenance_md, encoding="utf-8")

    print("Compiling LIMITATIONS.md...")
    limitations_md = compile_limitations_md(cards, metadata)
    (output_dir / "LIMITATIONS.md").write_text(limitations_md, encoding="utf-8")

    # 复制卡片到输出
    cards_output = output_dir / "cards"
    for card_type, card_list in cards.items():
        type_dir = cards_output / card_type
        type_dir.mkdir(parents=True, exist_ok=True)
        for card in card_list:
            src = Path(card["path"])
            dst = type_dir / src.name
            dst.write_text(card["content"], encoding="utf-8")

    print(f"\n✓ Output assembled to {output_dir}")
    print(f"  - SKILL.md")
    print(f"  - PROVENANCE.md")
    print(f"  - LIMITATIONS.md")
    print(f"  - cards/ ({total_cards} cards)")


if __name__ == "__main__":
    main()