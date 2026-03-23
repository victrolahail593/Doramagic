#!/usr/bin/env python3
"""Assemble the Doramagic S2 output bundle from an analysis context."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


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

CATEGORY_ORDER = ["concept", "workflow", "decision", "trap", "signature"]
SOUL_CATEGORY_MAP = {
    "concept": "concepts",
    "workflow": "workflows",
    "decision": "rules",
    "trap": "rules",
    "signature": "signatures",
}


def _slugify(value: str, fallback: str = "doramagic-skill") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def _require(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError("missing required key: {0}".format(key))
    return mapping[key]


def _normalize_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        item = value.strip()
        return [item] if item else []
    if isinstance(value, list):
        items = []
        for item in value:
            if item is None:
                continue
            if isinstance(item, str):
                text = item.strip()
            else:
                text = str(item).strip()
            if text:
                items.append(text)
        return items
    text = str(value).strip()
    return [text] if text else []


def _normalize_mapping_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _bullet_list(items: list[str], fallback: str = "- none") -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    if not cleaned:
        return fallback
    return "\n".join("- {0}".format(item) for item in cleaned)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def _frontmatter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        if isinstance(value, list):
            lines.append("{0}:".format(key))
            if value:
                for item in value:
                    lines.append("  - {0}".format(_yaml_scalar(item)))
            else:
                lines.append("  []")
        else:
            lines.append("{0}: {1}".format(key, _yaml_scalar(value)))
    lines.append("---")
    return "\n".join(lines)


def _source_text(source: Any) -> str:
    if isinstance(source, str):
        return source.strip()
    if not isinstance(source, dict):
        return str(source).strip()

    path = str(source.get("path", "")).strip()
    start_line = source.get("start_line")
    end_line = source.get("end_line")
    source_url = str(source.get("source_url", "")).strip()
    artifact_name = str(source.get("artifact_name", "")).strip()
    snippet = str(source.get("snippet", "")).strip()

    location = path or artifact_name or source_url
    if path and start_line:
        if end_line and end_line != start_line:
            location = "{0}:{1}-{2}".format(path, start_line, end_line)
        else:
            location = "{0}:{1}".format(path, start_line)
    text = location
    if snippet:
        text = "{0} — {1}".format(text, snippet)
    return text.strip(" —")


def _normalize_sources(value: Any) -> list[str]:
    items = []
    if isinstance(value, list):
        candidates = value
    elif value is None:
        candidates = []
    else:
        candidates = [value]
    for item in candidates:
        text = _source_text(item)
        if text:
            items.append(text)
    return items


def _project_repo_field(projects: list[str]) -> str:
    return ", ".join(projects) if projects else "unknown"


def _normalize_stage1(stage1: Any, need_profile: dict[str, Any], analysis: dict[str, Any]) -> dict[str, str]:
    if isinstance(stage1, dict):
        result = {}
        for index in range(1, 8):
            key = "q{0}".format(index)
            alt_key = str(index)
            result[key] = str(stage1.get(key) or stage1.get(alt_key) or "").strip()
        return result

    if isinstance(stage1, list):
        result = {}
        for index in range(1, 8):
            value = stage1[index - 1] if index - 1 < len(stage1) else ""
            result["q{0}".format(index)] = str(value).strip()
        return result

    why = analysis.get("why", [])
    mental_model = analysis.get("mental_model", "")
    return {
        "q1": str(need_profile.get("intent", "")).strip(),
        "q2": ", ".join(_normalize_text_list(need_profile.get("constraints"))),
        "q3": str(analysis.get("summary", "")).strip(),
        "q4": ", ".join(_normalize_text_list(analysis.get("workflow_steps"))[:2]),
        "q5": str(analysis.get("summary", "")).strip(),
        "q6": " ".join(_normalize_text_list(why)),
        "q7": str(mental_model).strip(),
    }


def _normalize_domain_api(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"status": "unavailable", "message": "No preextract API assessment provided."}
    return {
        "status": str(value.get("status", "unavailable")).strip() or "unavailable",
        "domain_id": str(value.get("domain_id", "")).strip(),
        "matched_keywords": _normalize_text_list(value.get("matched_keywords")),
        "brick_titles": _normalize_text_list(value.get("brick_titles")),
        "message": str(value.get("message", "")).strip(),
    }


def _normalize_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for index, project in enumerate(projects, start=1):
        full_name = _require(project, "full_name")
        project_id = str(project.get("id") or "SRC-{0:03d}".format(index))
        why_recoverability = project.get("why_recoverability") or {}
        dsd = dict(project.get("deceptive_source_detection") or project.get("dsd_metrics") or {})

        direct_evidence_count = _coerce_int(
            why_recoverability.get("direct_evidence_count"),
            len(_normalize_text_list(project.get("why_evidence"))),
        )
        narrative_assertion_count = max(
            1,
            _coerce_int(
                why_recoverability.get("narrative_assertion_count"),
                len(_normalize_text_list(project.get("why_assertions"))) or len(_normalize_text_list(project.get("why"))),
            ),
        )
        rationale_support_ratio = _coerce_float(
            why_recoverability.get("rationale_support_ratio"),
            float(direct_evidence_count) / float(narrative_assertion_count),
        )
        if "rationale_support_ratio" not in dsd:
            dsd["rationale_support_ratio"] = round(rationale_support_ratio, 4)

        normalized_dsd = {}
        for key in DSD_METRIC_KEYS:
            normalized_dsd[key] = round(_coerce_float(dsd.get(key), 0.0), 4)

        status = str(why_recoverability.get("status", "")).strip().lower()
        if not status:
            if direct_evidence_count > 0:
                status = "evidence_sufficient"
            else:
                status = "unrecoverable"

        normalized.append(
            {
                "id": project_id,
                "full_name": full_name,
                "url": _require(project, "url"),
                "license": project.get("license", "unknown"),
                "relevance_reason": str(project.get("relevance_reason", "")).strip(),
                "facts_path": str(project.get("facts_path", "")).strip(),
                "community_json_path": str(project.get("community_json_path", "")).strip(),
                "community_md_path": str(project.get("community_md_path", "")).strip(),
                "why_evidence": _normalize_text_list(project.get("why_evidence")),
                "unsaid_evidence": _normalize_text_list(project.get("unsaid_evidence")),
                "issue_urls": _normalize_text_list(project.get("issue_urls")),
                "risk_flags": _normalize_text_list(project.get("risk_flags")),
                "project_focus": _normalize_text_list(project.get("project_focus")),
                "why_recoverability": {
                    "status": status,
                    "label": str(why_recoverability.get("label", "")).strip(),
                    "notes": _normalize_text_list(why_recoverability.get("notes")),
                    "direct_evidence_count": direct_evidence_count,
                    "narrative_assertion_count": narrative_assertion_count,
                    "rationale_support_ratio": round(rationale_support_ratio, 4),
                },
                "deceptive_source_detection": normalized_dsd,
                "risk_level": str(project.get("risk_level", "")).strip().lower() or "medium",
            }
        )
    return normalized


def _default_card_id(category: str, index: int) -> str:
    prefix_map = {
        "concept": "CC",
        "workflow": "WF",
        "decision": "DC",
        "trap": "TR",
        "signature": "SG",
    }
    return "{0}-{1:03d}".format(prefix_map[category], index)


def _normalize_card(category: str, item: dict[str, Any], index: int) -> dict[str, Any]:
    project_ids = _normalize_text_list(item.get("project_ids"))
    repo = str(item.get("repo", "")).strip()
    if repo and repo not in project_ids:
        project_ids.append(repo)

    normalized = {
        "category": category,
        "card_id": str(item.get("card_id") or _default_card_id(category, index)),
        "title": str(item.get("title") or item.get("name") or "{0} card {1}".format(category, index)).strip(),
        "project_ids": project_ids,
        "summary": str(item.get("summary", "")).strip(),
        "sources": _normalize_sources(item.get("sources") or item.get("evidence")),
        "evidence": _normalize_sources(item.get("evidence") or item.get("sources")),
        "why_link": _normalize_text_list(item.get("why_link")),
        "unsaid_link": _normalize_text_list(item.get("unsaid_link")),
        "body": str(item.get("body", "")).strip(),
    }

    if category == "concept":
        normalized.update(
            {
                "identity": str(item.get("identity", "")).strip(),
                "is_items": _normalize_text_list(item.get("is_items") or item.get("is")),
                "is_not_items": _normalize_text_list(item.get("is_not_items") or item.get("is_not")),
                "attributes": _normalize_mapping_list(item.get("attributes")),
                "boundaries": _normalize_text_list(item.get("boundaries")),
            }
        )
    elif category == "workflow":
        normalized.update(
            {
                "goal": str(item.get("goal", "")).strip(),
                "steps": _normalize_mapping_list(item.get("steps")),
                "mermaid": str(item.get("mermaid", "")).strip(),
                "failure_modes": _normalize_text_list(item.get("failure_modes")),
            }
        )
    elif category == "decision":
        normalized.update(
            {
                "rule": str(item.get("rule", "")).strip(),
                "context": str(item.get("context", "")).strip(),
                "severity": str(item.get("severity", "MEDIUM")).strip().upper(),
                "do": _normalize_text_list(item.get("do")),
                "dont": _normalize_text_list(item.get("dont")),
                "alternatives": _normalize_text_list(item.get("alternatives")),
                "confidence": round(_coerce_float(item.get("confidence"), 0.8), 2),
            }
        )
    elif category == "trap":
        normalized.update(
            {
                "trap": str(item.get("trap") or item.get("summary") or item.get("title", "")).strip(),
                "trigger": str(item.get("trigger", "")).strip(),
                "why_it_happens": str(item.get("why_it_happens", "")).strip(),
                "severity": str(item.get("severity", "HIGH")).strip().upper(),
                "avoidance": _normalize_text_list(item.get("avoidance") or item.get("do")),
                "impact_scope": _normalize_text_list(item.get("impact_scope")),
                "confidence": round(_coerce_float(item.get("confidence"), 0.9), 2),
            }
        )
    elif category == "signature":
        normalized.update(
            {
                "trait": str(item.get("trait") or item.get("summary") or item.get("title", "")).strip(),
                "why_it_matters": str(item.get("why_it_matters", "")).strip(),
            }
        )

    return normalized


def _normalize_cards(cards_block: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    normalized = {}
    source = cards_block if isinstance(cards_block, dict) else {}
    for category in CATEGORY_ORDER:
        raw_cards = source.get(category)
        if raw_cards is None:
            raw_cards = source.get("{0}s".format(category), [])
        if not isinstance(raw_cards, list):
            raw_cards = []
        normalized[category] = [
            _normalize_card(category, item, index)
            for index, item in enumerate(raw_cards, start=1)
            if isinstance(item, dict)
        ]
    return normalized


def _normalize_cross_project(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {"consensus": [], "conflicts": [], "unique": [], "non_independent": []}
    return {
        "consensus": _normalize_text_list(value.get("consensus")),
        "conflicts": _normalize_text_list(value.get("conflicts")),
        "unique": _normalize_text_list(value.get("unique")),
        "non_independent": _normalize_text_list(value.get("non_independent")),
    }


def _normalize_dark_traps(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"overall_risk": "medium", "compound_warnings": [], "notes": []}
    return {
        "overall_risk": str(value.get("overall_risk", "medium")).strip().lower() or "medium",
        "compound_warnings": _normalize_text_list(value.get("compound_warnings")),
        "notes": _normalize_text_list(value.get("notes")),
    }


def _project_lookup(projects: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup = {}
    for project in projects:
        lookup[project["id"]] = project
        lookup[project["full_name"]] = project
    return lookup


def _card_repo_names(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> list[str]:
    names = []
    for project_id in card.get("project_ids", []):
        project = project_lookup.get(project_id)
        if project is not None:
            names.append(project["full_name"])
        else:
            names.append(project_id)
    return names


def _render_concept_card(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    rows = []
    left = card.get("is_items", [])
    right = card.get("is_not_items", [])
    max_len = max(len(left), len(right), 1)
    for index in range(max_len):
        rows.append(
            "| {0} | {1} |".format(
                left[index] if index < len(left) else "",
                right[index] if index < len(right) else "",
            )
        )

    attribute_lines = ["| Attribute | Type | Purpose |", "|-----------|------|---------|"]
    attributes = card.get("attributes", [])
    if attributes:
        for item in attributes:
            attribute_lines.append(
                "| {0} | {1} | {2} |".format(
                    str(item.get("name", "")).strip(),
                    str(item.get("type", "")).strip(),
                    str(item.get("purpose", "")).strip(),
                )
            )
    else:
        attribute_lines.append("| n/a | n/a | n/a |")

    return "\n".join(
        [
            _frontmatter(
                {
                    "card_type": "concept_card",
                    "card_id": card["card_id"],
                    "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
                    "title": card["title"],
                }
            ),
            "",
            "## Identity",
            card.get("identity") or card.get("summary") or "Identity not provided.",
            "",
            "## Is / Is Not",
            "",
            "| IS | IS NOT |",
            "|----|--------|",
            *rows,
            "",
            "## Key Attributes",
            "",
            *attribute_lines,
            "",
            "## Boundaries",
            _bullet_list(card.get("boundaries", [])),
            "",
            "## Evidence",
            _bullet_list(card.get("evidence", [])),
            "",
        ]
    ).rstrip() + "\n"


def _render_workflow_steps(steps: list[dict[str, Any]]) -> list[str]:
    if not steps:
        return ["1. Workflow details not provided."]
    lines = []
    for index, step in enumerate(steps, start=1):
        title = str(step.get("title") or step.get("name") or "Step {0}".format(index)).strip()
        detail = str(step.get("detail") or step.get("description") or "").strip()
        evidence = _normalize_sources(step.get("evidence"))
        line = "{0}. {1}".format(index, title)
        if detail:
            line = "{0} — {1}".format(line, detail)
        lines.append(line)
        if evidence:
            lines.append("   Evidence: {0}".format("; ".join(evidence)))
    return lines


def _render_workflow_card(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    mermaid = card.get("mermaid") or "graph TD\n  A[Start] --> B[Inspect Repo]\n  B --> C[Produce Skill]"
    return "\n".join(
        [
            _frontmatter(
                {
                    "card_type": "workflow_card",
                    "card_id": card["card_id"],
                    "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
                    "title": card["title"],
                }
            ),
            "",
            "## Goal",
            card.get("goal") or card.get("summary") or "Workflow goal not provided.",
            "",
            "## Steps",
            * _render_workflow_steps(card.get("steps", [])),
            "",
            "## Mermaid",
            "```mermaid",
            mermaid,
            "```",
            "",
            "## Failure Modes",
            _bullet_list(card.get("failure_modes", [])),
            "",
            "## Evidence",
            _bullet_list(card.get("evidence", [])),
            "",
        ]
    ).rstrip() + "\n"


def _render_decision_card(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    return "\n".join(
        [
            _frontmatter(
                {
                    "card_type": "decision_card",
                    "card_id": card["card_id"],
                    "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
                    "title": card["title"],
                    "severity": card.get("severity", "MEDIUM"),
                    "confidence": card.get("confidence", 0.8),
                    "sources": card.get("sources", []) or card.get("evidence", []),
                }
            ),
            "",
            "## Rule",
            card.get("rule") or card.get("summary") or "Rule not provided.",
            "",
            "## Context",
            card.get("context") or "Context not provided.",
            "",
            "## Do",
            _bullet_list(card.get("do", [])),
            "",
            "## Don't",
            _bullet_list(card.get("dont", [])),
            "",
            "## Alternatives",
            _bullet_list(card.get("alternatives", [])),
            "",
            "## Evidence",
            _bullet_list(card.get("evidence", [])),
            "",
        ]
    ).rstrip() + "\n"


def _render_trap_card(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    return "\n".join(
        [
            _frontmatter(
                {
                    "card_type": "trap_card",
                    "card_id": card["card_id"],
                    "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
                    "title": card["title"],
                    "severity": card.get("severity", "HIGH"),
                    "confidence": card.get("confidence", 0.9),
                    "sources": card.get("sources", []),
                }
            ),
            "",
            "## Trap",
            card.get("trap") or card.get("summary") or "Trap summary not provided.",
            "",
            "## Trigger",
            card.get("trigger") or "Trigger not provided.",
            "",
            "## Why It Happens",
            card.get("why_it_happens") or "Cause not provided.",
            "",
            "## Avoidance",
            _bullet_list(card.get("avoidance", [])),
            "",
            "## Impact Scope",
            _bullet_list(card.get("impact_scope", [])),
            "",
            "## Sources",
            _bullet_list(card.get("sources", [])),
            "",
        ]
    ).rstrip() + "\n"


def _render_signature_card(card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    return "\n".join(
        [
            _frontmatter(
                {
                    "card_type": "signature_card",
                    "card_id": card["card_id"],
                    "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
                    "title": card["title"],
                }
            ),
            "",
            "## Trait",
            card.get("trait") or card.get("summary") or "Signature trait not provided.",
            "",
            "## Why It Matters",
            card.get("why_it_matters") or "Why it matters not provided.",
            "",
            "## Evidence",
            _bullet_list(card.get("evidence", [])),
            "",
        ]
    ).rstrip() + "\n"


def _render_card(category: str, card: dict[str, Any], project_lookup: dict[str, dict[str, Any]]) -> str:
    if category == "concept":
        return _render_concept_card(card, project_lookup)
    if category == "workflow":
        return _render_workflow_card(card, project_lookup)
    if category == "decision":
        return _render_decision_card(card, project_lookup)
    if category == "trap":
        return _render_trap_card(card, project_lookup)
    return _render_signature_card(card, project_lookup)


def _render_soul_rule_card(card: dict[str, Any], category: str, project_lookup: dict[str, dict[str, Any]], index: int) -> str:
    if category == "trap":
        card_id = "DR-{0:03d}".format(100 + index)
        title = card["title"]
        rule = "If {0}, then {1}.".format(
            (card.get("trigger") or "the documented boundary is crossed").rstrip("."),
            (card.get("trap") or "the workflow breaks in a non-obvious way").rstrip("."),
        )
        scenario = card.get("trap") or card.get("summary") or title
        impact_lines = card.get("impact_scope", [])
    else:
        card_id = "DR-{0:03d}".format(index)
        title = card["title"]
        rule = card.get("rule") or card.get("summary") or title
        scenario = card.get("context") or title
        impact_lines = card.get("alternatives", [])

    meta = {
        "card_type": "decision_rule_card",
        "card_id": card_id,
        "repo": _project_repo_field(_card_repo_names(card, project_lookup)),
        "type": "COMMUNITY_GOTCHA" if category == "trap" else "DEFAULT_BEHAVIOR",
        "title": title,
        "severity": card.get("severity", "MEDIUM"),
        "rule": rule,
        "do": card.get("avoidance") if category == "trap" else card.get("do", []),
        "dont": card.get("dont", []),
        "confidence": card.get("confidence", 0.8),
        "sources": card.get("sources", []) or card.get("evidence", []),
    }
    return "\n".join(
        [
            _frontmatter(meta),
            "",
            "## 真实场景",
            scenario or "Scenario not provided.",
            "",
            "## 影响范围",
            _bullet_list(impact_lines),
            "",
        ]
    ).rstrip() + "\n"


def _write_cards(
    output_dir: Path,
    cards: dict[str, list[dict[str, Any]]],
    project_lookup: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    index = {}
    cards_root = output_dir / "cards"
    soul_root = output_dir / "soul" / "cards"
    for category in CATEGORY_ORDER:
        target_dir = cards_root / category
        soul_dir = soul_root / SOUL_CATEGORY_MAP[category]
        target_dir.mkdir(parents=True, exist_ok=True)
        soul_dir.mkdir(parents=True, exist_ok=True)
        index[category] = []
        for item_index, card in enumerate(cards.get(category, []), start=1):
            filename = "{0}.md".format(card["card_id"])
            rendered = _render_card(category, card, project_lookup)
            (target_dir / filename).write_text(rendered, encoding="utf-8")
            index[category].append(str(Path("cards") / category / filename))

            if category in ("decision", "trap"):
                soul_rendered = _render_soul_rule_card(card, category, project_lookup, item_index)
            else:
                soul_rendered = rendered
            (soul_dir / filename).write_text(soul_rendered, encoding="utf-8")
    return index


def _build_soul_essence(stage1: dict[str, str], analysis: dict[str, Any]) -> str:
    title = _require(analysis, "skill_title")
    return "\n".join(
        [
            "# {0} — 灵魂".format(title),
            "",
            "## 1. 解决什么问题？",
            stage1.get("q1", "") or "Not provided.",
            "",
            "## 2. 没有它会怎样？",
            stage1.get("q2", "") or "Not provided.",
            "",
            "## 3. 核心承诺",
            stage1.get("q3", "") or "Not provided.",
            "",
            "## 4. 兑现方式",
            stage1.get("q4", "") or "Not provided.",
            "",
            "## 5. 一句话总结",
            stage1.get("q5", "") or "Not provided.",
            "",
            "## 6. 设计哲学",
            stage1.get("q6", "") or "Not provided.",
            "",
            "## 7. 心智模型",
            stage1.get("q7", "") or "Not provided.",
            "",
        ]
    ).rstrip() + "\n"


def _build_skill_md(
    need_profile: dict[str, Any],
    analysis: dict[str, Any],
    storage_root: str,
    projects: list[dict[str, Any]],
    cards: dict[str, list[dict[str, Any]]],
    cross_project: dict[str, list[str]],
    dark_traps: dict[str, Any],
    domain_api: dict[str, Any],
) -> str:
    skill_title = _require(analysis, "skill_title")
    skill_key = analysis.get("skill_key") or _slugify(skill_title)
    summary = _require(analysis, "summary")
    workflow_steps = _normalize_text_list(analysis.get("workflow_steps"))
    capabilities = _normalize_text_list(analysis.get("capabilities"))
    why = _normalize_text_list(analysis.get("why"))
    unsaid = _normalize_text_list(analysis.get("unsaid"))
    limitations = _normalize_text_list(analysis.get("limitations"))
    expert_narrative = str(analysis.get("expert_narrative", "")).strip()
    mental_model = str(analysis.get("mental_model", "")).strip()
    keywords = _normalize_text_list(need_profile.get("keywords"))

    lines = [
        "---",
        "skillKey: {0}".format(skill_key),
        "always: false",
        "os:",
        "  - macos",
        "install: Store runtime data under {0}".format(storage_root),
        "allowed-tools:",
        "  - exec",
        "  - read",
        "  - write",
        "---",
        "",
        "# {0}".format(skill_title),
        "",
        "## Purpose",
        summary,
        "",
        "Original request: {0}".format(need_profile.get("raw_input", "")),
        "Keywords: {0}".format(", ".join(keywords) if keywords else "n/a"),
        "",
        "## Source Portfolio",
    ]
    for project in projects:
        lines.append(
            "- {0} — {1} ({2})".format(project["id"], project["full_name"], project["url"])
        )
    if not projects:
        lines.append("- No source projects recorded.")

    lines.extend(["", "## Domain API"])
    status = domain_api.get("status", "unavailable")
    domain_line = "- Preextract API status: {0}".format(status)
    if domain_api.get("domain_id"):
        domain_line += " (domain_id={0})".format(domain_api["domain_id"])
    lines.append(domain_line)
    if domain_api.get("message"):
        lines.append("- Notes: {0}".format(domain_api["message"]))
    if domain_api.get("matched_keywords"):
        lines.append("- Matched keywords: {0}".format(", ".join(domain_api["matched_keywords"])))
    if domain_api.get("brick_titles"):
        lines.append("- Injected bricks: {0}".format(", ".join(domain_api["brick_titles"])))

    if expert_narrative:
        lines.extend(["", "## Expert Narrative", expert_narrative])

    lines.extend(["", "## WHY"])
    lines.append(_bullet_list(why, "- WHY not available."))

    if mental_model:
        lines.extend(["", "## Mental Model", mental_model])

    lines.extend(["", "## WHY Recoverability"])
    for project in projects:
        why_rec = project["why_recoverability"]
        ratio = why_rec["rationale_support_ratio"]
        status_text = why_rec.get("label") or why_rec["status"]
        lines.append(
            "- {0}: {1}; rationale_support_ratio={2}".format(
                project["full_name"],
                status_text,
                ratio,
            )
        )
        if why_rec["status"] == "unrecoverable":
            lines.append("  WHY 无法从公开证据可靠重建；任何 WHY 叙事都必须降为低置信推断。")
        for note in why_rec.get("notes", []):
            lines.append("  - {0}".format(note))

    lines.extend(["", "## UNSAID"])
    lines.append(_bullet_list(unsaid, "- UNSAID not available."))

    lines.extend(["", "## Knowledge Cards"])
    for category in CATEGORY_ORDER:
        heading = category.title()
        lines.append("### {0}".format(heading))
        category_cards = cards.get(category, [])
        if not category_cards:
            lines.append("- none")
            continue
        for card in category_cards:
            lines.append(
                "- {0}: {1}".format(card["card_id"], card["title"])
            )
            if card.get("summary"):
                lines.append("  - {0}".format(card["summary"]))

    lines.extend(["", "## Cross-Project Synthesis"])
    lines.append("### Consensus")
    lines.append(_bullet_list(cross_project.get("consensus", [])))
    lines.append("")
    lines.append("### Conflicts")
    lines.append(_bullet_list(cross_project.get("conflicts", [])))
    lines.append("")
    lines.append("### Unique")
    lines.append(_bullet_list(cross_project.get("unique", [])))
    lines.append("")
    lines.append("### Non-Independent Checks")
    lines.append(_bullet_list(cross_project.get("non_independent", [])))

    lines.extend(["", "## Deceptive Source Detection"])
    for project in projects:
        metrics = project["deceptive_source_detection"]
        lines.append(
            "- {0} ({1})".format(project["full_name"], project.get("risk_level", "medium"))
        )
        for key in DSD_METRIC_KEYS:
            lines.append("  - {0}: {1}".format(key, metrics.get(key, 0.0)))
        if project.get("risk_flags"):
            lines.append("  - risk_flags: {0}".format(", ".join(project["risk_flags"])))
    lines.append("- overall_risk: {0}".format(dark_traps.get("overall_risk", "medium")))
    for warning in dark_traps.get("compound_warnings", []):
        lines.append("- compound_warning: {0}".format(warning))

    lines.extend(["", "## Operating Steps"])
    lines.append(_bullet_list(workflow_steps, "- Workflow not provided."))

    lines.extend(["", "## Capabilities"])
    lines.append(_bullet_list(capabilities, "- No capabilities supplied."))

    lines.extend(["", "## Storage"])
    lines.append("- Store runtime data under {0}".format(storage_root))
    lines.append("- Persist generated cards under output/cards/")
    lines.append("- Persist stage mirrors under output/soul/")

    lines.extend(["", "## Limitations"])
    lines.append(_bullet_list(limitations, "- No explicit limitations supplied."))

    return "\n".join(lines).rstrip() + "\n"


def _build_provenance_md(
    analysis: dict[str, Any],
    projects: list[dict[str, Any]],
    cards: dict[str, list[dict[str, Any]]],
    project_lookup: dict[str, dict[str, Any]],
) -> str:
    lines = ["# Provenance", "", "## Project Assessments", ""]

    for project in projects:
        lines.append("### {0} — {1}".format(project["id"], project["full_name"]))
        lines.append("- Source URL: {0}".format(project["url"]))
        lines.append("- License: {0}".format(project["license"]))
        lines.append("- Relevance: {0}".format(project["relevance_reason"] or "n/a"))
        lines.append(
            "- WHY Recoverability: {0}".format(
                project["why_recoverability"].get("label") or project["why_recoverability"]["status"]
            )
        )
        lines.append(
            "- Rationale Support Ratio: {0} ({1})".format(
                project["why_recoverability"]["rationale_support_ratio"],
                "direct evidence" if project["why_recoverability"]["direct_evidence_count"] > 0 else "no evidence",
            )
        )
        if project["why_evidence"]:
            lines.append("- WHY Evidence:")
            for item in project["why_evidence"]:
                lines.append("  - {0}".format(item))
        if project["unsaid_evidence"]:
            lines.append("- UNSAID Evidence:")
            for item in project["unsaid_evidence"]:
                lines.append("  - {0}".format(item))
        if project["issue_urls"]:
            lines.append("- Issue URLs: {0}".format(", ".join(project["issue_urls"])))
        lines.append("- DSD Metrics:")
        for key in DSD_METRIC_KEYS:
            lines.append(
                "  - {0}: {1}".format(
                    key, project["deceptive_source_detection"].get(key, 0.0)
                )
            )
        lines.append("")

    lines.extend(["## Card Traceability", ""])
    for category in CATEGORY_ORDER:
        for card in cards.get(category, []):
            lines.append("### {0} — {1}".format(card["card_id"], card["title"]))
            lines.append("- Category: {0}".format(category))
            repo_names = _card_repo_names(card, project_lookup)
            lines.append("- Source Projects: {0}".format(", ".join(repo_names) or "n/a"))
            lines.append("- Sources:")
            sources = card.get("sources") or card.get("evidence")
            if sources:
                for source in sources:
                    lines.append("  - {0}".format(source))
            else:
                lines.append("  - n/a")
            if card.get("why_link"):
                lines.append("- WHY Links: {0}".format("; ".join(card["why_link"])))
            if card.get("unsaid_link"):
                lines.append("- UNSAID Links: {0}".format("; ".join(card["unsaid_link"])))
            lines.append("")

    decisions = _normalize_text_list(analysis.get("decisions"))
    if decisions:
        lines.extend(["## Selected Decisions"])
        for index, decision in enumerate(decisions, start=1):
            lines.append("- DEC-{0:03d}: {1}".format(index, decision))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _build_limitations_md(
    analysis: dict[str, Any],
    projects: list[dict[str, Any]],
    dark_traps: dict[str, Any],
    domain_api: dict[str, Any],
) -> str:
    lines = ["# Limitations", ""]
    limitations = _normalize_text_list(analysis.get("limitations"))
    if limitations:
        for item in limitations:
            lines.append("- {0}".format(item))
    else:
        lines.append("- No explicit limitations supplied.")

    if len(projects) < 2:
        lines.append("- Only one source repository was deeply analyzed; cross-project confidence is limited.")

    lines.extend(["", "## Dark Trap Assessment"])
    lines.append("- Overall risk: {0}".format(dark_traps.get("overall_risk", "medium")))
    for warning in dark_traps.get("compound_warnings", []):
        lines.append("- Compound warning: {0}".format(warning))
    for note in dark_traps.get("notes", []):
        lines.append("- Note: {0}".format(note))
    for project in projects:
        if project.get("risk_flags"):
            lines.append(
                "- {0}: {1}".format(project["full_name"], ", ".join(project["risk_flags"]))
            )

    lines.extend(["", "## Coverage"])
    if domain_api.get("status") != "hit":
        lines.append("- Preextract API was not a confirmed hit; extraction quality relied on live repository evidence only.")
    else:
        lines.append("- Preextract API domain bricks were used as hints, not as sole evidence.")
    for question in _normalize_text_list(analysis.get("open_questions")):
        lines.append("- Open question: {0}".format(question))

    return "\n".join(lines).rstrip() + "\n"


def _build_readme_md(need_profile: dict[str, Any], analysis: dict[str, Any], storage_root: str) -> str:
    skill_title = _require(analysis, "skill_title")
    return (
        "# {title}\n\n"
        "Generated by Doramagic S2 full integration flow.\n\n"
        "## Request\n"
        "- {request}\n\n"
        "## Runtime Layout\n"
        "- Storage root: {storage_root}\n"
        "- Final bundle: `output/`\n"
        "- Knowledge cards: `output/cards/`\n"
        "- Stage mirror: `output/soul/`\n"
        "- Research artifacts: `output/artifacts/`\n"
    ).format(
        title=skill_title,
        request=need_profile.get("raw_input", ""),
        storage_root=storage_root,
    )


def _normalize_synthesis_decision(item: Any, prefix: str, index: int, default_decision: str) -> dict[str, Any]:
    if isinstance(item, dict):
        return {
            "decision_id": str(item.get("decision_id") or "{0}-{1:03d}".format(prefix, index)),
            "statement": str(item.get("statement") or item.get("title") or "").strip(),
            "decision": str(item.get("decision") or default_decision),
            "rationale": str(item.get("rationale") or "Selected from repository evidence.").strip(),
            "source_refs": _normalize_text_list(item.get("source_refs")),
            "demand_fit": str(item.get("demand_fit") or "high"),
        }
    statement = str(item).strip()
    return {
        "decision_id": "{0}-{1:03d}".format(prefix, index),
        "statement": statement,
        "decision": default_decision,
        "rationale": "Selected from repository evidence.",
        "source_refs": [],
        "demand_fit": "high",
    }


def _normalize_synthesis_conflict(item: Any, index: int) -> dict[str, Any]:
    if isinstance(item, dict):
        return {
            "conflict_id": str(item.get("conflict_id") or "CF-{0:03d}".format(index)),
            "category": str(item.get("category") or "architecture"),
            "title": str(item.get("title") or item.get("statement") or "").strip(),
            "positions": _normalize_text_list(item.get("positions")),
            "recommended_resolution": str(item.get("recommended_resolution") or item.get("rationale") or "Keep as an explicit option.").strip(),
            "source_refs": _normalize_text_list(item.get("source_refs")),
        }
    statement = str(item).strip()
    return {
        "conflict_id": "CF-{0:03d}".format(index),
        "category": "architecture",
        "title": statement,
        "positions": [],
        "recommended_resolution": "Keep as an explicit option.",
        "source_refs": [],
    }


def _build_synthesis_report(
    analysis: dict[str, Any],
    projects: list[dict[str, Any]],
    cross_project: dict[str, list[str]],
) -> dict[str, Any]:
    source_refs = [project["url"] for project in projects]
    consensus = [
        _normalize_synthesis_decision(item, "CON", index, "include")
        for index, item in enumerate(cross_project.get("consensus", []), start=1)
    ]
    unique_knowledge = [
        _normalize_synthesis_decision(item, "UNI", index, "option")
        for index, item in enumerate(cross_project.get("unique", []), start=1)
    ]
    selected_knowledge = consensus + unique_knowledge
    if not selected_knowledge:
        decisions = _normalize_text_list(analysis.get("decisions") or analysis.get("capabilities"))
        selected_knowledge = [
            {
                "decision_id": "SEL-{0:03d}".format(index),
                "statement": item,
                "decision": "include",
                "rationale": "Selected from repository evidence.",
                "source_refs": source_refs,
                "demand_fit": "high",
            }
            for index, item in enumerate(decisions, start=1)
        ]

    for item in selected_knowledge:
        if not item["source_refs"]:
            item["source_refs"] = source_refs

    conflicts = [
        _normalize_synthesis_conflict(item, index)
        for index, item in enumerate(cross_project.get("conflicts", []), start=1)
    ]
    return {
        "schema_version": "dm.synthesis-report.v1",
        "consensus": consensus,
        "conflicts": conflicts,
        "unique_knowledge": unique_knowledge,
        "selected_knowledge": selected_knowledge,
        "excluded_knowledge": [],
        "open_questions": _normalize_text_list(analysis.get("open_questions")),
    }


def _bundle_manifest(
    skill_title: str,
    skill_key: str,
    storage_root: str,
    card_index: dict[str, list[str]],
) -> dict[str, Any]:
    output_files = [
        "SKILL.md",
        "PROVENANCE.md",
        "LIMITATIONS.md",
        "README.md",
        "artifacts/need_profile.json",
        "artifacts/synthesis_report.json",
        "artifacts/assembly_context.json",
        "artifacts/cards_index.json",
        "artifacts/bundle_manifest.json",
        "soul/00-soul.md",
        "soul/expert_narrative.md",
    ]
    for paths in card_index.values():
        output_files.extend(paths)
    return {
        "schema_version": "dm.s2.bundle-manifest.v2",
        "skill_title": skill_title,
        "skill_key": skill_key,
        "storage_root": storage_root,
        "output_files": output_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble Doramagic bundle from analysis context")
    parser.add_argument("--context", required=True, help="Path to assembly-context.json")
    parser.add_argument("--output-dir", required=True, help="Output directory for bundle files")
    args = parser.parse_args()

    context_path = Path(args.context).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    context = json.loads(context_path.read_text(encoding="utf-8"))

    need_profile = _require(context, "need_profile")
    analysis = _require(context, "analysis")
    skill_title = _require(analysis, "skill_title")
    skill_key = analysis.get("skill_key") or _slugify(skill_title)
    storage_root = analysis.get("storage_root") or "~/clawd/{0}/".format(skill_key)

    projects = _normalize_projects(analysis.get("selected_projects", []))
    if not projects:
        raise ValueError("analysis.selected_projects must contain at least one project")

    cards = _normalize_cards(analysis.get("cards") or {})
    project_lookup = _project_lookup(projects)
    cross_project = _normalize_cross_project(analysis.get("cross_project"))
    dark_traps = _normalize_dark_traps(analysis.get("dark_traps"))
    domain_api = _normalize_domain_api(analysis.get("domain_api"))
    stage1 = _normalize_stage1(analysis.get("stage1_answers"), need_profile, analysis)

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "soul").mkdir(parents=True, exist_ok=True)

    card_index = _write_cards(output_dir, cards, project_lookup)

    skill_md = _build_skill_md(
        need_profile,
        analysis,
        storage_root,
        projects,
        cards,
        cross_project,
        dark_traps,
        domain_api,
    )
    provenance_md = _build_provenance_md(analysis, projects, cards, project_lookup)
    limitations_md = _build_limitations_md(analysis, projects, dark_traps, domain_api)
    readme_md = _build_readme_md(need_profile, analysis, storage_root)
    synthesis_report = _build_synthesis_report(analysis, projects, cross_project)
    soul_essence = _build_soul_essence(stage1, analysis)
    expert_narrative = str(analysis.get("expert_narrative", "")).strip() or "Expert narrative not provided."

    (output_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (output_dir / "PROVENANCE.md").write_text(provenance_md, encoding="utf-8")
    (output_dir / "LIMITATIONS.md").write_text(limitations_md, encoding="utf-8")
    (output_dir / "README.md").write_text(readme_md, encoding="utf-8")
    (output_dir / "soul" / "00-soul.md").write_text(soul_essence, encoding="utf-8")
    (output_dir / "soul" / "expert_narrative.md").write_text(expert_narrative + "\n", encoding="utf-8")

    (artifacts_dir / "need_profile.json").write_text(
        json.dumps(need_profile, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (artifacts_dir / "synthesis_report.json").write_text(
        json.dumps(synthesis_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (artifacts_dir / "assembly_context.json").write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (artifacts_dir / "cards_index.json").write_text(
        json.dumps(card_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = _bundle_manifest(skill_title, skill_key, storage_root, card_index)
    (artifacts_dir / "bundle_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("bundle={0}".format(output_dir))
    print("skill_key={0}".format(skill_key))
    print("projects={0}".format(len(projects)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
