#!/usr/bin/env python3
"""validate_skill.py — 检查生成的 Skill bundle 是否合格。扩展版：含暗雷检测 + WHY 可恢复性。

检查项：
1. Frontmatter 是否完整（name, description, allowed-tools, skillKey）
2. SKILL.md 是否包含 WHY 内容（设计哲学/WHY 关键词）
3. SKILL.md 是否包含 UNSAID/陷阱内容
4. LIMITATIONS.md 是否存在
5. PROVENANCE.md 是否包含来源 URL
6. 无冲突标记（<<<<<<, >>>>>>）
7. 存储路径使用 ~/clawd/ 前缀
8. 无安全暗雷（eval、sudo、rm -rf、硬编码密钥等）
9. [扩展] WHY 过度推理检查：Rationale Support Ratio < 0.3 告警
10. [扩展] Narrative-Evidence Tension：高置信度叙事但无证据锚点
11. [扩展] LIMITATIONS.md 包含暗雷评估结果
12. [扩展] PROVENANCE.md 按卡片 ID 组织溯源
13. [扩展] WHY 可恢复性标注

用法：
    python3 validate_skill.py <skill_dir> --output report.json
    python3 validate_skill.py /tmp/doramagic-test/output --output /tmp/report.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# 原有检查模式
# ---------------------------------------------------------------------------

URL_PATTERN = re.compile(r"https?://[^\s,)\"\']+")
CONFLICT_MARKER_PATTERN = re.compile(
    r"(<<<<<<|>>>>>>|======|UNRESOLVED)", re.IGNORECASE
)
DARK_TRAP_PATTERNS = [
    (re.compile(r"\bsudo\b", re.IGNORECASE), "sudo usage detected (privilege escalation risk)"),
    (re.compile(r"rm\s+-rf", re.IGNORECASE), "destructive rm -rf command detected"),
    (re.compile(r"\beval\s*\(", re.IGNORECASE), "eval() usage detected (code injection risk)"),
    (
        re.compile(r"\b(?:password|secret|token|api_key|apikey)\s*=\s*['\"]?\w{8,}", re.IGNORECASE),
        "potential hardcoded credential detected",
    ),
    (
        re.compile(r"\b(?:curl|wget)\b.*\|\s*(?:bash|sh)\b", re.IGNORECASE),
        "pipe-to-shell pattern detected (supply chain risk)",
    ),
]

WHY_KEYWORDS = re.compile(
    r"\b(why|设计哲学|design philosophy|WHY|核心信念|core belief|因为|原因|动机|motivation|trade.?off)\b",
    re.IGNORECASE,
)
UNSAID_KEYWORDS = re.compile(
    r"\b(unsaid|陷阱|pitfall|gotcha|caveat|注意|警告|warning|已知|limitation|已知陷阱|社区踩坑)\b",
    re.IGNORECASE,
)
LIMITATIONS_SECTION = re.compile(
    r"^#+\s*(limitation|局限|limitations|已知局限)", re.IGNORECASE | re.MULTILINE
)

# ---------------------------------------------------------------------------
# 扩展：WHY 过度推理 + DSD 指标
# ---------------------------------------------------------------------------

EVIDENCE_ANCHOR_PATTERN = re.compile(
    r"(Issue\s*#\d+|PR\s*#\d+|commit\s+[0-9a-f]{6,}|README|CHANGELOG|ADR|docs/|v\d+\.\d+|\bsource:\b|来源：)",
    re.IGNORECASE,
)
ASSERTION_WORDS = re.compile(
    r"\b(because|因为|therefore|所以|designed|设计|chose|选择|decided|决定|philosophy|哲学|belief|信念|principle|原则)\b",
    re.IGNORECASE,
)
HIGH_CONFIDENCE_SIGNAL = re.compile(
    r"(核心信念|设计哲学|根本原因|最重要|关键决策|显然|clearly|obviously|fundamentally)",
    re.IGNORECASE,
)
CARD_ID_PATTERN = re.compile(r"\b(CC|DC|TC|WF|SC)-[A-Z0-9]+-\d+\b")
WHY_UNRECOVERABLE_MARKER = re.compile(
    r"(WHY 无法|WHY 部分为推断|cannot be reliably reconstructed|置信度低|无法可靠重建)",
    re.IGNORECASE,
)
DSD_KEYWORDS = re.compile(
    r"(暗雷|dark trap|DSD|Rationale Support|Temporal Conflict|Exception Dominance|Support-Desk|Narrative-Evidence|风险等级|risk level)",
    re.IGNORECASE,
)


def _read(path: Path) -> tuple[Optional[str], Optional[str]]:
    if not path.exists():
        return None, f"File not found: {path}"
    try:
        return path.read_text(encoding="utf-8"), None
    except Exception as e:
        return None, f"Cannot read {path}: {e}"


def _parse_frontmatter(skill_md: str) -> tuple[str, str]:
    parts = skill_md.split("---", 2)
    if len(parts) >= 3:
        return parts[1], parts[2]
    return "", skill_md


def _check_frontmatter(frontmatter: str) -> dict:
    details = []
    required_keys = ["name", "description", "allowed-tools"]
    fm_lower = frontmatter.lower()
    for key in required_keys:
        if key not in fm_lower:
            details.append(f"Missing required frontmatter key: '{key}'")
    if "skillkey" not in fm_lower and "skill_key" not in fm_lower:
        details.append("Missing 'skillKey' in metadata.openclaw block")
    tools_match = re.search(r"allowed-tools[:\s\[]+([^\]]+)", frontmatter, re.IGNORECASE)
    if tools_match:
        tools_str = tools_match.group(1)
        valid_tools = {"exec", "read", "write"}
        found_tools = set(re.findall(r"\b(exec|read|write)\b", tools_str))
        if not found_tools:
            details.append("allowed-tools contains no valid values (exec/read/write)")
        invalid = set(re.findall(r"\b\w+\b", tools_str)) - valid_tools - {"[", "]", ","}
        invalid.discard("")
        if invalid:
            details.append(f"allowed-tools contains non-standard values: {invalid}")
    else:
        details.append("Cannot parse allowed-tools block")
    return {"name": "Frontmatter", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_why_content(body: str) -> dict:
    details = []
    if not WHY_KEYWORDS.search(body):
        details.append(
            "SKILL.md body contains no WHY content (missing: design philosophy, 设计哲学, why, etc.). "
            "A Skill without WHY is just a GitHub search result."
        )
    return {"name": "WHY Content", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_unsaid_content(body: str) -> dict:
    details = []
    if not UNSAID_KEYWORDS.search(body):
        details.append(
            "SKILL.md body contains no UNSAID/pitfall content (missing: 陷阱, pitfall, gotcha, caveat, etc.). "
            "Community trap knowledge is a core Doramagic value."
        )
    return {"name": "UNSAID Content", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_limitations_file(limitations_content: Optional[str], limitations_err: Optional[str]) -> dict:
    details = []
    if limitations_err:
        details.append(f"LIMITATIONS.md missing or unreadable: {limitations_err}")
    elif limitations_content and len(limitations_content.strip()) < 50:
        details.append("LIMITATIONS.md exists but is nearly empty (< 50 chars)")
    return {"name": "Limitations File", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_traceability(provenance_content: Optional[str], provenance_err: Optional[str]) -> dict:
    details = []
    if provenance_err:
        details.append(f"PROVENANCE.md missing or unreadable: {provenance_err}")
    elif provenance_content:
        urls = URL_PATTERN.findall(provenance_content)
        if not urls:
            details.append("PROVENANCE.md contains no source URLs (https://...) — knowledge is not traceable")
    return {"name": "Traceability", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_conflict_markers(skill_md: str) -> dict:
    details = []
    matches = CONFLICT_MARKER_PATTERN.findall(skill_md)
    if matches:
        details.append(f"SKILL.md contains unresolved conflict markers: {matches[:5]}")
    return {"name": "Conflict Resolution", "passed": len(details) == 0, "severity": "blocking", "details": details}


def _check_storage_paths(skill_md: str) -> dict:
    details = []
    paths = re.findall(r"~/\S+", skill_md)
    bad = [p for p in paths if not p.startswith("~/clawd/")]
    if bad:
        details.append(f"Storage paths not using ~/clawd/ prefix: {bad[:5]}")
    return {"name": "Storage Paths", "passed": len(details) == 0, "severity": "warning", "details": details}


def _check_dark_traps(skill_md: str) -> dict:
    details = []
    for pattern, description in DARK_TRAP_PATTERNS:
        if pattern.search(skill_md):
            details.append(f"Dark trap: {description}")
    return {"name": "Dark Trap Scan", "passed": len(details) == 0, "severity": "warning", "details": details}


def _check_limitations_in_skill(body: str) -> dict:
    details = []
    if not LIMITATIONS_SECTION.search(body):
        details.append(
            "SKILL.md body has no 'Limitations' / '局限性' section. "
            "Add a section listing what this skill does NOT cover."
        )
    return {"name": "Limitations Section", "passed": len(details) == 0, "severity": "blocking", "details": details}


# ---------------------------------------------------------------------------
# 扩展检查
# ---------------------------------------------------------------------------


def _check_why_over_reasoning(body: str) -> dict:
    """检查 WHY 过度推理：Rationale Support Ratio + Narrative-Evidence Tension。"""
    details = []

    why_section_pattern = re.compile(
        r"#{1,3}\s*(?:设计哲学|WHY|Design Philosophy|为什么这样设计|why).*?\n(.*?)(?=\n#{1,3}|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    why_match = why_section_pattern.search(body)
    why_text = why_match.group(1) if why_match else body

    assertion_count = len(ASSERTION_WORDS.findall(why_text))
    evidence_count = len(EVIDENCE_ANCHOR_PATTERN.findall(why_text))
    high_confidence_count = len(HIGH_CONFIDENCE_SIGNAL.findall(why_text))

    rsr = evidence_count / max(assertion_count, 1)

    if assertion_count >= 3 and rsr < 0.3:
        details.append(
            f"WHY 过度推理风险（Rationale Support Ratio={rsr:.2f}，阈值 0.3）："
            f"{assertion_count} 个断言仅 {evidence_count} 个证据锚点。"
            "在 PROVENANCE.md 为 WHY 内容标注具体来源（Issue #、README 段落、ADR）。"
        )

    if high_confidence_count >= 2 and evidence_count == 0:
        details.append(
            f"Narrative-Evidence Tension：{high_confidence_count} 个高置信度叙事信号但零个证据引用。"
            "如果 WHY 是推断，在 SKILL.md 中明确标注'以下为推断，置信度低'。"
        )

    return {
        "name": "WHY Over-Reasoning Check",
        "passed": len(details) == 0,
        "severity": "warning",
        "details": details,
        "metrics": {
            "assertion_count": assertion_count,
            "evidence_count": evidence_count,
            "rationale_support_ratio": round(rsr, 2),
            "high_confidence_signals": high_confidence_count,
        },
    }


def _check_provenance_card_ids(provenance_content: Optional[str]) -> dict:
    """检查 PROVENANCE.md 是否按卡片 ID 组织溯源。"""
    details = []
    if not provenance_content:
        return {
            "name": "Provenance Card Traceability",
            "passed": False,
            "severity": "warning",
            "details": ["PROVENANCE.md not available for card ID check"],
            "card_ids_found": [],
        }
    card_ids = CARD_ID_PATTERN.findall(provenance_content)
    if not card_ids:
        details.append(
            "PROVENANCE.md contains no knowledge card IDs (CC-xxx, DC-xxx, TC-xxx etc.). "
            "Full integration requires per-card provenance tracing."
        )
    return {
        "name": "Provenance Card Traceability",
        "passed": len(details) == 0,
        "severity": "warning",
        "details": details,
        "card_ids_found": list(set(card_ids)),
    }


def _check_dark_trap_evaluation_in_limitations(limitations_content: Optional[str]) -> dict:
    """检查 LIMITATIONS.md 是否包含 DSD 暗雷评估结果。"""
    details = []
    if not limitations_content:
        return {
            "name": "Dark Trap Evaluation in LIMITATIONS",
            "passed": False,
            "severity": "warning",
            "details": ["LIMITATIONS.md not available for dark trap check"],
        }
    if not DSD_KEYWORDS.search(limitations_content):
        details.append(
            "LIMITATIONS.md does not contain DSD dark trap evaluation. "
            "Add a '## 暗雷评估结果' section with per-indicator assessment."
        )
    return {
        "name": "Dark Trap Evaluation in LIMITATIONS",
        "passed": len(details) == 0,
        "severity": "warning",
        "details": details,
    }


def _check_why_recoverability_marker(body: str) -> dict:
    """检查 SKILL.md 是否对 WHY 可恢复性做了诚实标注。"""
    details = []
    why_present = WHY_KEYWORDS.search(body)
    if why_present:
        confidence_signal = re.compile(
            r"(置信度|confidence|证据充分|evidence|推断|inferred|based on|来源|source)",
            re.IGNORECASE,
        )
        if not confidence_signal.search(body):
            details.append(
                "WHY 可恢复性标注缺失：SKILL.md 包含 WHY 内容，但未标注证据来源或置信度等级。"
                "建议在 PROVENANCE.md 中对每条 WHY 标注 Rationale Support Ratio 和置信度。"
            )
    return {
        "name": "WHY Recoverability Annotation",
        "passed": len(details) == 0,
        "severity": "warning",
        "details": details,
    }


# ---------------------------------------------------------------------------
# Revise instructions
# ---------------------------------------------------------------------------


def _revise_instructions(checks: list[dict]) -> list[str]:
    instructions = []
    for check in checks:
        if not check["passed"] and check["severity"] == "blocking":
            name = check["name"]
            for detail in check["details"]:
                if name == "WHY Content":
                    instructions.append(
                        "Add a '## 设计哲学（WHY）' section to SKILL.md explaining the core design belief "
                        "extracted from the source project. This is mandatory — a Skill without WHY has no value."
                    )
                elif name == "UNSAID Content":
                    instructions.append(
                        "Add an '## 已知陷阱（UNSAID）' section to SKILL.md with community pitfalls "
                        "extracted from GitHub issues and README caveats."
                    )
                elif name == "Limitations Section":
                    instructions.append(
                        "Add a '## 局限性' section to SKILL.md listing scenarios this Skill does not cover."
                    )
                elif name == "Frontmatter":
                    instructions.append(f"Fix frontmatter issue: {detail}")
                elif name == "Traceability":
                    instructions.append(
                        "Add at least one GitHub URL (https://github.com/...) to PROVENANCE.md "
                        "for each knowledge item."
                    )
                elif name == "Limitations File":
                    instructions.append(
                        "Create LIMITATIONS.md with at least: known coverage gaps, "
                        "data freshness date, and non-applicable scenarios."
                    )
                elif name == "Conflict Resolution":
                    instructions.append("Resolve all conflict markers (<<<<<<, >>>>>>) before delivery.")
                else:
                    instructions.append(f"Fix {name}: {detail}")
    return instructions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def validate_skill_dir(skill_dir: str) -> dict:
    """Validate a skill bundle directory. Returns report dict."""
    base = Path(skill_dir).resolve()

    skill_content, skill_err = _read(base / "SKILL.md")
    provenance_content, provenance_err = _read(base / "PROVENANCE.md")
    limitations_content, limitations_err = _read(base / "LIMITATIONS.md")

    if skill_err:
        return {
            "status": "BLOCKED",
            "error": skill_err,
            "checks": [],
            "revise_instructions": [],
            "summary": "BLOCKED: SKILL.md not readable",
        }

    frontmatter, body = _parse_frontmatter(skill_content)

    checks = [
        # Original 9 checks
        _check_frontmatter(frontmatter),
        _check_why_content(body),
        _check_unsaid_content(body),
        _check_limitations_in_skill(body),
        _check_limitations_file(limitations_content, limitations_err),
        _check_traceability(provenance_content, provenance_err),
        _check_conflict_markers(skill_content),
        _check_storage_paths(skill_content),
        _check_dark_traps(skill_content),
        # Extended DSD checks (4 new)
        _check_why_over_reasoning(body),
        _check_provenance_card_ids(provenance_content),
        _check_dark_trap_evaluation_in_limitations(limitations_content),
        _check_why_recoverability_marker(body),
    ]

    blocking_failures = [c for c in checks if not c["passed"] and c["severity"] == "blocking"]
    status = "REVISE" if blocking_failures else "PASS"
    revise = _revise_instructions(checks)
    passed_count = sum(1 for c in checks if c["passed"])

    return {
        "status": status,
        "checks": checks,
        "revise_instructions": revise,
        "summary": f"{passed_count}/{len(checks)} checks passed",
        "extended_checks": {
            "why_over_reasoning": next(
                (c for c in checks if c["name"] == "WHY Over-Reasoning Check"), {}
            ),
            "card_traceability": next(
                (c for c in checks if c["name"] == "Provenance Card Traceability"), {}
            ),
            "dark_trap_evaluation": next(
                (c for c in checks if c["name"] == "Dark Trap Evaluation in LIMITATIONS"), {}
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Doramagic S1 validate_skill — 检查 Skill bundle 质量（扩展版含暗雷检测）"
    )
    parser.add_argument("skill_dir", help="包含 SKILL.md / PROVENANCE.md / LIMITATIONS.md 的目录")
    parser.add_argument("--output", required=True, help="输出 report.json 路径")
    args = parser.parse_args()

    started = time.time()
    report = validate_skill_dir(args.skill_dir)
    elapsed_ms = int((time.time() - started) * 1000)
    report["elapsed_ms"] = elapsed_ms

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    status = report["status"]
    summary = report["summary"]
    print(f"Validation result: {status} ({summary})")
    if report.get("revise_instructions"):
        print("\nRevise instructions:")
        for i, inst in enumerate(report["revise_instructions"], 1):
            print(f"  {i}. {inst}")

    ext = report.get("extended_checks", {})
    why_metrics = ext.get("why_over_reasoning", {}).get("metrics", {})
    if why_metrics:
        rsr = why_metrics.get("rationale_support_ratio", "N/A")
        print(f"\nExtended checks:")
        print(f"  Rationale Support Ratio: {rsr} (threshold: 0.3)")
        print(f"  Evidence anchors found: {why_metrics.get('evidence_count', 0)}")

    card_ids = ext.get("card_traceability", {}).get("card_ids_found", [])
    if card_ids:
        print(f"  Knowledge cards traced: {', '.join(card_ids[:8])}")

    print(f"\nReport saved to: {args.output}")

    if status == "PASS":
        sys.exit(0)
    elif status == "REVISE":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
