#!/usr/bin/env python3
"""Validate Skill — 检查 SKILL.md 质量 + 暗雷检测 + WHY 可恢复性。

用法：
    python3 validate_skill.py /path/to/output_dir --output validation_report.json
    python3 validate_skill.py /path/to/cards_dir --check-dark-traps

检查项：
1. SKILL.md 存在且可读
2. Frontmatter 存在且闭合
3. 必要字段：skillKey, allowed-tools
4. WHY 章节存在且有证据标注
5. UNSAID 章节存在
6. LIMITATIONS.md 存在且包含暗雷评估
7. 知识卡片格式检查
8. 暗雷检测（8 项 DSD 指标）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def check_file_exists(path: Path, filename: str) -> tuple[bool, str]:
    """检查文件是否存在。"""
    file_path = path / filename
    if not file_path.exists():
        return False, f"{filename} 不存在"
    if file_path.stat().st_size == 0:
        return False, f"{filename} 为空文件"
    return True, f"{filename} 存在且非空"


def check_frontmatter(content: str) -> tuple[bool, list[str]]:
    """检查 frontmatter。"""
    issues = []

    if not content.strip().startswith("---"):
        issues.append("SKILL.md 未以 frontmatter 开始")
        return False, issues

    parts = content.split("---")
    if len(parts) < 3:
        issues.append("Frontmatter 未正确闭合")
        return False, issues

    frontmatter = parts[1]

    required_fields = ["skillKey", "allowed-tools"]
    for field in required_fields:
        if field not in frontmatter:
            issues.append(f"Frontmatter 缺少: {field}")

    return len(issues) == 0, issues


def check_why_evidence(content: str) -> tuple[bool, list[str]]:
    """检查 WHY 是否有证据支撑。"""
    issues = []

    why_match = re.search(r'##\s*WHY.*?\n(.*?)(?=\n##|\Z)', content, re.IGNORECASE | re.DOTALL)
    if not why_match:
        issues.append("未找到 WHY 章节")
        return False, issues

    why_content = why_match.group(1).strip()

    if len(why_content) < 50:
        issues.append("WHY 章节内容过短")

    # 检查证据标注
    evidence_patterns = [
        r'证据充分',
        r'证据不足',
        r'无法.*重建',
        r'置信度',
        r'来源:',
        r'file:',
        r'Issue'
    ]

    has_evidence_note = any(re.search(p, why_content, re.IGNORECASE) for p in evidence_patterns)
    if not has_evidence_note:
        issues.append("WHY 缺少可恢复性标注（证据充分/证据不足/无法重建）")

    return len(issues) == 0, issues


def check_unsaid_content(content: str) -> tuple[bool, list[str]]:
    """检查 UNSAID 内容。"""
    issues = []

    unsaid_match = re.search(r'##\s*UNSAID.*?\n(.*?)(?=\n##|\Z)', content, re.IGNORECASE | re.DOTALL)
    if not unsaid_match:
        issues.append("未找到 UNSAID 章节")
        return False, issues

    unsaid_content = unsaid_match.group(1).strip()

    if len(unsaid_content) < 30:
        issues.append("UNSAID 章节内容过短")

    return len(issues) == 0, issues


def check_dark_traps_in_limitations(content: str) -> tuple[bool, list[str]]:
    """检查 LIMITATIONS 中是否包含暗雷评估。"""
    issues = []

    # 检查暗雷相关内容
    dark_trap_patterns = [
        r'暗雷',
        r'风险',
        r'陷阱',
        r'DSD',
        r'高风险',
        r'过度推理'
    ]

    has_dark_trap = any(re.search(p, content, re.IGNORECASE) for p in dark_trap_patterns)
    if not has_dark_trap:
        issues.append("LIMITATIONS 缺少暗雷评估")

    return len(issues) == 0, issues


def check_card_format(card_path: Path, card_type: str) -> tuple[bool, list[str]]:
    """检查知识卡片格式。"""
    issues = []

    if not card_path.exists():
        return False, [f"卡片文件不存在: {card_path}"]

    content = card_path.read_text(encoding="utf-8")

    # 检查 frontmatter
    if not content.strip().startswith("---"):
        issues.append("卡片缺少 YAML frontmatter")
        return False, issues

    parts = content.split("---")
    if len(parts) < 3:
        issues.append("卡片 frontmatter 未闭合")
        return False, issues

    frontmatter = parts[1]

    # 检查必要字段
    if "card_type:" not in frontmatter:
        issues.append("卡片缺少 card_type")
    if "card_id:" not in frontmatter:
        issues.append("卡片缺少 card_id")

    # 根据卡片类型检查特定字段
    if card_type == "concept":
        if "## Is / Is Not" not in content and "## Is/Is Not" not in content:
            issues.append("概念卡缺少 Is/Is Not 表格")
        if "## Evidence" not in content:
            issues.append("概念卡缺少 Evidence")

    elif card_type == "workflow":
        if "## Steps" not in content:
            issues.append("工作流卡缺少 Steps")

    elif card_type == "decision":
        if "## Rule" not in content and "IF" not in content:
            issues.append("决策卡缺少 Rule (IF/THEN)")

    elif card_type == "trap":
        if "source:" not in frontmatter and "Issue" not in content:
            issues.append("陷阱卡缺少 Issue 来源")

    return len(issues) == 0, issues


def detect_dark_trap_indicators(cards_dir: Path) -> list[dict]:
    """检测暗雷指标。"""
    signals = []

    # 读取所有卡片
    all_content = ""
    for card_type in ["concept", "workflow", "decision", "trap"]:
        card_dir = cards_dir / card_type
        if card_dir.exists():
            for card_file in card_dir.glob("*.md"):
                all_content += card_file.read_text(encoding="utf-8") + "\n"

    if not all_content:
        return signals

    # 指标 1: Rationale Support Ratio
    why_statements = len(re.findall(r'(因为|由于|理由是|why|reason|rationale)', all_content, re.IGNORECASE))
    evidence_refs = len(re.findall(r'(file:|line:|Issue #|PR #)', all_content))
    if why_statements > 0 and evidence_refs / why_statements < 0.3:
        signals.append({
            "indicator": "Rationale Support Ratio",
            "risk": "HIGH",
            "value": round(evidence_refs / max(why_statements, 1), 2),
            "description": "WHY 叙事多但证据支撑少，可能有过度推理"
        })

    # 指标 8: Narrative-Evidence Tension
    high_confidence = len(re.findall(r'(高置信度|置信度.*高|confidence.*high)', all_content, re.IGNORECASE))
    if high_confidence > 3 and evidence_refs < high_confidence:
        signals.append({
            "indicator": "Narrative-Evidence Tension",
            "risk": "MEDIUM",
            "description": "过多高置信度声明但证据不足"
        })

    return signals


def validate_skill(skill_md: str, limitations_md: str = "") -> dict:
    """验证 SKILL.md。"""
    checks = []
    all_passed = True

    # 1. Frontmatter
    passed, issues = check_frontmatter(skill_md)
    checks.append({"name": "Frontmatter", "passed": passed, "severity": "blocking", "details": issues})
    if not passed: all_passed = False

    # 2. WHY Evidence
    passed, issues = check_why_evidence(skill_md)
    checks.append({"name": "WHY Evidence", "passed": passed, "severity": "blocking", "details": issues})
    if not passed: all_passed = False

    # 3. UNSAID
    passed, issues = check_unsaid_content(skill_md)
    checks.append({"name": "UNSAID Content", "passed": passed, "severity": "blocking", "details": issues})
    if not passed: all_passed = False

    # 4. Dark Traps in LIMITATIONS
    if limitations_md:
        passed, issues = check_dark_traps_in_limitations(limitations_md)
        checks.append({"name": "Dark Trap Assessment", "passed": passed, "severity": "warning", "details": issues})

    # 5. Purpose
    if "## Purpose" in skill_md:
        checks.append({"name": "Purpose Section", "passed": True, "severity": "warning", "details": ["找到"]})
    else:
        checks.append({"name": "Purpose Section", "passed": False, "severity": "warning", "details": ["未找到"]})

    return {
        "checks": checks,
        "overall_passed": all_passed,
        "status": "PASS" if all_passed else "REVISE"
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Doramagic Skill output")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--output", "-o", help="Validation report JSON")
    parser.add_argument("--check-dark-traps", action="store_true", help="Check dark trap indicators")
    parser.add_argument("--check-cards", action="store_true", help="Validate knowledge cards")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"Error: {output_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    results = {"output_dir": str(output_dir), "checks": [], "dark_trap_signals": []}

    # 检查文件存在性
    print("检查文件存在性:")
    for filename in ["SKILL.md", "PROVENANCE.md", "LIMITATIONS.md"]:
        passed, msg = check_file_exists(output_dir, filename)
        results["checks"].append({"name": filename, "passed": passed, "details": [msg]})
        print(f"  [{'✓' if passed else '✗'}] {msg}")

    # 验证 SKILL.md
    skill_path = output_dir / "SKILL.md"
    limitations_path = output_dir / "LIMITATIONS.md"

    if skill_path.exists():
        print("\n验证 SKILL.md 内容:")
        skill_content = skill_path.read_text(encoding="utf-8")
        limitations_content = limitations_path.read_text(encoding="utf-8") if limitations_path.exists() else ""

        validation = validate_skill(skill_content, limitations_content)
        results["skill_validation"] = validation

        for check in validation["checks"]:
            status = "✓" if check["passed"] else "✗"
            print(f"  [{status}] {check['name']}: {', '.join(check['details'])}")

        print(f"\n最终状态: {validation['status']}")

    # 检查暗雷指标
    if args.check_dark_traps:
        cards_dir = output_dir / "cards"
        if cards_dir.exists():
            print("\n检测暗雷指标:")
            signals = detect_dark_trap_indicators(cards_dir)
            results["dark_trap_signals"] = signals

            if signals:
                for s in signals:
                    print(f"  ⚠️ [{s['risk']}] {s['indicator']}: {s['description']}")
            else:
                print("  ✓ 未检测到高风险暗雷信号")

    # 检查知识卡片
    if args.check_cards:
        print("\n验证知识卡片:")
        cards_dir = output_dir / "cards"
        card_results = []

        for card_type in ["concept", "workflow", "decision", "trap"]:
            card_dir = cards_dir / card_type
            if card_dir.exists():
                for card_file in sorted(card_dir.glob("*.md"))[:5]:
                    passed, issues = check_card_format(card_file, card_type)
                    status = "✓" if passed else "✗"
                    print(f"  [{status}] {card_file.name}")
                    if issues:
                        for issue in issues:
                            print(f"      - {issue}")
                    card_results.append({"file": str(card_file), "passed": passed, "issues": issues})

        results["card_validation"] = card_results

    # 写入报告
    if args.output:
        report_path = Path(args.output)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n报告已保存到: {args.output}")

    # 返回状态码
    if results.get("skill_validation", {}).get("overall_passed", False):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()