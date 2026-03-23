#!/usr/bin/env python3
"""Validate Doramagic S2 bundle quality and research coverage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "contracts"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "platform_openclaw"))

from doramagic_contracts.base import NeedProfile  # noqa: E402
from doramagic_contracts.cross_project import SynthesisReportData  # noqa: E402
from doramagic_contracts.skill import (  # noqa: E402
    PlatformRules,
    SkillBundlePaths,
    ValidationInput,
)
from doramagic_platform_openclaw.validator import run_validation  # noqa: E402


DSD_METRIC_KEYS = [
    "rationale_support_ratio",
    "temporal_conflict_score",
    "exception_dominance_ratio",
    "support_desk_share",
    "public_context_completeness",
    "persona_divergence_score",
    "dependency_dominance_index",
    "narrative_evidence_tension",
]

CARD_TYPE_BY_CATEGORY = {
    "concept": "concept_card",
    "workflow": "workflow_card",
    "decision": "decision_card",
    "trap": "trap_card",
    "signature": "signature_card",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_platform_rules() -> PlatformRules:
    fixture_path = PROJECT_ROOT / "data" / "fixtures" / "platform_rules.json"
    if fixture_path.exists():
        return PlatformRules(**_load_json(fixture_path))
    return PlatformRules()


def _serialize_model(model: object) -> str:
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=2)
    return model.json(indent=2, ensure_ascii=False)


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text

    raw_meta = text[4:end].splitlines()
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, Any] = {}
    current_key = None
    for line in raw_meta:
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key is not None:
            meta.setdefault(current_key, []).append(line[4:].strip().strip('"'))
            continue
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not match:
            continue
        current_key = match.group(1)
        value = match.group(2).strip()
        if value == "":
            meta[current_key] = []
        elif value.lower() in ("true", "false"):
            meta[current_key] = value.lower() == "true"
        else:
            try:
                number = float(value)
                if "." not in value:
                    number = int(number)
                meta[current_key] = number
            except ValueError:
                meta[current_key] = value.strip('"')
    return meta, body


def _collect_card_reports(skill_dir: Path) -> tuple[dict[str, list[dict[str, Any]]], list[str], list[str]]:
    cards_root = skill_dir / "cards"
    grouped: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []
    warnings: list[str] = []

    for category, expected_type in CARD_TYPE_BY_CATEGORY.items():
        category_dir = cards_root / category
        grouped[category] = []
        if not category_dir.exists():
            errors.append("Missing cards directory: {0}".format(category_dir))
            continue
        for card_path in sorted(category_dir.glob("*.md")):
            meta, body = _parse_frontmatter(card_path.read_text(encoding="utf-8"))
            card_id = str(meta.get("card_id", card_path.stem))
            card_type = str(meta.get("card_type", ""))
            if card_type != expected_type:
                errors.append(
                    "{0}: expected card_type={1}, got {2}".format(card_path.name, expected_type, card_type or "missing")
                )
            grouped[category].append(
                {
                    "path": card_path,
                    "card_id": card_id,
                    "card_type": card_type,
                    "meta": meta,
                    "body": body,
                }
            )
            if category == "concept":
                if "## Identity" not in body or "## Evidence" not in body:
                    warnings.append("{0}: concept card missing Identity/Evidence section".format(card_path.name))
            if category == "workflow":
                if "```mermaid" not in body:
                    warnings.append("{0}: workflow card missing mermaid diagram".format(card_path.name))
            if category in ("decision", "trap"):
                if not meta.get("sources"):
                    errors.append("{0}: missing sources in frontmatter".format(card_path.name))
    return grouped, errors, warnings


def _research_validation(
    skill_dir: Path,
    skill_md_text: str,
    provenance_text: str,
    limitations_text: str,
    assembly_context: dict[str, Any],
    grouped_cards: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    analysis = assembly_context.get("analysis", {})
    projects = analysis.get("selected_projects", [])
    dark_traps = analysis.get("dark_traps", {}) if isinstance(analysis.get("dark_traps"), dict) else {}

    if "## WHY" not in skill_md_text:
        issues.append("SKILL.md missing '## WHY' section")
    if "## UNSAID" not in skill_md_text:
        issues.append("SKILL.md missing '## UNSAID' section")

    if len(projects) < 2:
        issues.append("analysis.selected_projects has fewer than 2 projects")

    min_counts = {"concept": 3, "decision": 2, "trap": 2}
    for category, required in min_counts.items():
        actual = len(grouped_cards.get(category, []))
        if actual < required:
            issues.append("Only {0} {1} cards; minimum is {2}".format(actual, category, required))

    all_card_ids = set()
    for category_cards in grouped_cards.values():
        for card in category_cards:
            card_id = card["card_id"]
            if card_id in all_card_ids:
                issues.append("Duplicate card_id: {0}".format(card_id))
            all_card_ids.add(card_id)
            if card_id not in provenance_text:
                issues.append("PROVENANCE.md missing card reference: {0}".format(card_id))

    explicit_why_projects = 0
    dsd_projects_complete = 0
    compound_high_risk = False
    for project in projects:
        if not isinstance(project, dict):
            issues.append("selected_projects entry is not an object")
            continue
        why_rec = project.get("why_recoverability") or {}
        status = str(why_rec.get("status", "")).strip().lower()
        if status:
            explicit_why_projects += 1
        if status == "unrecoverable" and "WHY 无法从公开证据可靠重建" not in skill_md_text:
            issues.append(
                "{0}: unrecoverable WHY project not reflected in SKILL.md".format(project.get("full_name", "unknown"))
            )

        metrics = project.get("deceptive_source_detection") or project.get("dsd_metrics") or {}
        missing_metrics = [key for key in DSD_METRIC_KEYS if key not in metrics]
        if missing_metrics:
            issues.append(
                "{0}: missing DSD metrics {1}".format(
                    project.get("full_name", "unknown"),
                    ", ".join(missing_metrics),
                )
            )
        else:
            dsd_projects_complete += 1

        risk_flags = project.get("risk_flags") or []
        if isinstance(risk_flags, list) and len(risk_flags) >= 2:
            compound_high_risk = True

    if explicit_why_projects == 0:
        issues.append("No explicit why_recoverability assessment found")
    if dsd_projects_complete == 0:
        issues.append("No project contains the full 8 DSD metrics")

    if compound_high_risk or str(dark_traps.get("overall_risk", "")).lower() == "high":
        lower_limitations = limitations_text.lower()
        if "high risk" not in lower_limitations and "高危" not in limitations_text and "compound" not in lower_limitations:
            issues.append("LIMITATIONS.md does not call out high-risk compound dark traps")

    if "Rationale Support Ratio" not in provenance_text:
        issues.append("PROVENANCE.md missing Rationale Support Ratio annotations")

    if not (skill_dir / "soul" / "00-soul.md").exists():
        warnings.append("soul/00-soul.md not found")
    if not (skill_dir / "soul" / "expert_narrative.md").exists():
        warnings.append("soul/expert_narrative.md not found")

    return {
        "status": "PASS" if not issues else "REVISE",
        "issues": issues,
        "warnings": warnings,
        "metrics": {
            "project_count": len(projects),
            "concept_cards": len(grouped_cards.get("concept", [])),
            "workflow_cards": len(grouped_cards.get("workflow", [])),
            "decision_cards": len(grouped_cards.get("decision", [])),
            "trap_cards": len(grouped_cards.get("trap", [])),
            "signature_cards": len(grouped_cards.get("signature", [])),
            "projects_with_explicit_why_recoverability": explicit_why_projects,
            "projects_with_full_dsd": dsd_projects_complete,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an assembled Doramagic skill bundle")
    parser.add_argument("--skill-dir", required=True, help="Directory containing SKILL.md bundle files")
    parser.add_argument("--need-profile", required=True, help="Path to need_profile.json")
    parser.add_argument("--synthesis-report", required=True, help="Path to synthesis_report.json")
    parser.add_argument("--output", required=True, help="Validation report output path")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        print("skill dir not found: {0}".format(skill_dir), file=sys.stderr)
        return 1

    skill_md_path = skill_dir / "SKILL.md"
    provenance_path = skill_dir / "PROVENANCE.md"
    limitations_path = skill_dir / "LIMITATIONS.md"
    assembly_context_path = skill_dir / "artifacts" / "assembly_context.json"

    bundle = SkillBundlePaths(
        skill_md_path=str(skill_md_path),
        readme_md_path=str(skill_dir / "README.md"),
        provenance_md_path=str(provenance_path),
        limitations_md_path=str(limitations_path),
    )
    need_profile = NeedProfile(**_load_json(Path(args.need_profile).expanduser().resolve()))
    synthesis_report = SynthesisReportData(**_load_json(Path(args.synthesis_report).expanduser().resolve()))
    platform_rules = _load_platform_rules()

    base_result = run_validation(
        ValidationInput(
            need_profile=need_profile,
            synthesis_report=synthesis_report,
            skill_bundle=bundle,
            platform_rules=platform_rules,
        )
    )

    skill_md_text = skill_md_path.read_text(encoding="utf-8")
    provenance_text = provenance_path.read_text(encoding="utf-8")
    limitations_text = limitations_path.read_text(encoding="utf-8")
    grouped_cards, card_errors, card_warnings = _collect_card_reports(skill_dir)

    if assembly_context_path.exists():
        assembly_context = _load_json(assembly_context_path)
    else:
        assembly_context = {}
        card_errors.append("Missing assembly_context.json for research validation")

    research = _research_validation(
        skill_dir,
        skill_md_text,
        provenance_text,
        limitations_text,
        assembly_context,
        grouped_cards,
    )
    research["issues"] = card_errors + research["issues"]
    research["warnings"] = card_warnings + research["warnings"]
    if research["issues"]:
        research["status"] = "REVISE"

    base_payload = json.loads(_serialize_model(base_result))
    base_report_status = (
        base_result.data.status
        if base_result.status == "ok" and base_result.data is not None
        else "BLOCKED"
    )

    final_status = "PASS"
    if base_result.status != "ok" or base_result.data is None:
        final_status = "BLOCKED"
    elif base_report_status != "PASS":
        final_status = base_report_status
    elif research["status"] != "PASS":
        final_status = "REVISE"

    report = {
        "schema_version": "dm.s2.validation-report.v2",
        "final_status": final_status,
        "base_validation": base_payload,
        "research_validation": research,
    }

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("envelope_status={0}".format(base_result.status))
    print("base_report_status={0}".format(base_report_status))
    print("research_status={0}".format(research["status"]))
    print("final_status={0}".format(final_status))

    if final_status == "PASS":
        return 0
    if final_status == "REVISE":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
