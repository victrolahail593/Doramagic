"""Bridge script from SKILL.md execution to the Doramagic Python pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import tempfile
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT: Optional[Path] = None

for candidate in (
    _THIS_DIR.parent.parent.parent.parent,
    _THIS_DIR.parent.parent.parent,
    _THIS_DIR.parent.parent,
):
    if (candidate / "packages" / "contracts").exists():
        _REPO_ROOT = candidate
        break

if _REPO_ROOT is None:
    _REPO_ROOT = _THIS_DIR.parent.parent.parent.parent

for package_name in (
    "contracts",
    "shared_utils",
    "extraction",
    "orchestration",
    "cross_project",
    "skill_compiler",
):
    package_path = str(_REPO_ROOT / "packages" / package_name)
    if package_path not in sys.path:
        sys.path.insert(0, package_path)

if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("doramagic_pipeline")


def _import_contracts() -> Dict[str, Any]:
    from doramagic_contracts.base import EvidenceRef, NeedProfile, RepoRef, SearchDirection
    from doramagic_contracts.cross_project import (
        CommunityKnowledge,
        CompareMetrics,
        CompareOutput,
        CompareSignal,
        DiscoveryResult,
        ExtractedProjectSummary,
        SynthesisConflict,
        SynthesisDecision,
        SynthesisInput,
        SynthesisReportData,
    )
    from doramagic_contracts.skill import PlatformRules, SkillCompilerInput

    return {
        "EvidenceRef": EvidenceRef,
        "NeedProfile": NeedProfile,
        "RepoRef": RepoRef,
        "SearchDirection": SearchDirection,
        "CommunityKnowledge": CommunityKnowledge,
        "CompareMetrics": CompareMetrics,
        "CompareOutput": CompareOutput,
        "CompareSignal": CompareSignal,
        "DiscoveryResult": DiscoveryResult,
        "ExtractedProjectSummary": ExtractedProjectSummary,
        "SynthesisConflict": SynthesisConflict,
        "SynthesisDecision": SynthesisDecision,
        "SynthesisInput": SynthesisInput,
        "SynthesisReportData": SynthesisReportData,
        "PlatformRules": PlatformRules,
        "SkillCompilerInput": SkillCompilerInput,
    }


def _import_synthesis():
    from doramagic_cross_project.synthesis import run_synthesis

    return run_synthesis


def _import_skill_compiler():
    from doramagic_skill_compiler.compiler import run_skill_compiler

    return run_skill_compiler


def _safe_model_dump(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return dict(model)


def _slugify(value: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "-" for char in value)
    normalized = "-".join(part for part in normalized.split("-") if part)
    return normalized or "compiled-skill"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fatal_json(message: str) -> str:
    return json.dumps({"status": "error", "error": message}, ensure_ascii=False, indent=2)


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(parts)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10].upper()
    return "{0}-{1}".format(prefix, digest)


def _load_platform_rules(contracts: Dict[str, Any]) -> Any:
    rules_path = _REPO_ROOT / "data" / "fixtures" / "platform_rules.json"
    platform_rules_cls = contracts["PlatformRules"]
    if rules_path.exists():
        return platform_rules_cls(**_read_json(rules_path))
    return platform_rules_cls()


def _build_need_profile(raw_need: Dict[str, Any], contracts: Dict[str, Any]) -> Any:
    need_profile_cls = contracts["NeedProfile"]
    search_direction_cls = contracts["SearchDirection"]

    if "raw_input" in raw_need:
        return need_profile_cls(
            raw_input=raw_need.get("raw_input", ""),
            keywords=list(raw_need.get("keywords", [])),
            intent=raw_need.get("intent", raw_need.get("raw_input", "")),
            search_directions=[
                search_direction_cls(
                    direction=item.get("direction", ""),
                    priority=item.get("priority", "medium"),
                )
                for item in raw_need.get("search_directions", [])
            ],
            constraints=list(raw_need.get("constraints", [])),
            quality_expectations=dict(raw_need.get("quality_expectations", {})),
        )

    user_need = str(raw_need.get("user_need", "")).strip()
    keywords = [str(item) for item in raw_need.get("keywords", [])]
    domain = str(raw_need.get("domain", "")).strip()
    directions = []
    if domain:
        directions.append(search_direction_cls(direction="Search for {0} implementations".format(domain), priority="high"))
    elif keywords:
        directions.append(search_direction_cls(direction="Search for implementations using {0}".format(", ".join(keywords[:3])), priority="high"))

    return need_profile_cls(
        raw_input=user_need,
        keywords=keywords,
        intent=user_need or domain or "Compiled Doramagic skill",
        search_directions=directions,
        constraints=[],
        quality_expectations={},
    )


def _repo_metadata_map(repos: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(repo.get("name") or "unknown"): repo for repo in repos}


def _repo_ref_from_raw(name: str, raw_repo: Dict[str, Any], contracts: Dict[str, Any]) -> Any:
    repo_ref_cls = contracts["RepoRef"]
    repo_url = str(raw_repo.get("url") or "https://github.com/example/{0}".format(name))
    local_path = str(raw_repo.get("path") or "")
    return repo_ref_cls(
        repo_id=name,
        full_name=str(raw_repo.get("name") or name),
        url=repo_url,
        default_branch="main",
        commit_sha=str(raw_repo.get("commit_sha") or "unknown"),
        local_path=local_path,
    )


def _load_repo_facts(result: Any) -> Dict[str, Any]:
    facts_path = Path(result.output_dir) / "artifacts" / "repo_facts.json"
    if facts_path.exists():
        try:
            payload = _read_json(facts_path)
            if isinstance(payload, dict):
                return payload
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.warning("Failed to read repo facts from %s: %s", facts_path, exc)
    return {}


def _evidence_ref(path_text: str, contracts: Dict[str, Any], source_url: Optional[str] = None) -> Any:
    evidence_ref_cls = contracts["EvidenceRef"]
    return evidence_ref_cls(
        kind="artifact_ref",
        path=path_text,
        artifact_name=Path(path_text).name,
        source_url=source_url,
    )


def _project_summary_from_result(
    item: Dict[str, Any],
    repo_meta: Dict[str, Any],
    contracts: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    extracted_summary_cls = contracts["ExtractedProjectSummary"]
    name = item["name"]
    result = item["result"]
    repo_ref = _repo_ref_from_raw(name, repo_meta, contracts)
    facts = _load_repo_facts(result)

    languages = [str(value) for value in facts.get("languages", []) if str(value).strip()]
    frameworks = [str(value) for value in facts.get("frameworks", []) if str(value).strip()]
    commands = [str(value) for value in facts.get("commands", []) if str(value).strip()]
    storage_paths = [str(value) for value in facts.get("storage_paths", []) if str(value).strip()]
    narrative = str(facts.get("project_narrative", "")).strip()
    project_files = [str(value) for value in facts.get("files", []) if str(value).strip()]

    top_capabilities: List[str] = []
    top_constraints: List[str] = []
    top_failures: List[str] = []
    evidence_refs: List[Any] = []
    repo_url = str(repo_meta.get("url") or "")

    for language in languages[:3]:
        top_capabilities.append("Implements the solution in {0}.".format(language))
    for framework in frameworks[:4]:
        top_capabilities.append("Uses {0} as part of the implementation stack.".format(framework))
    for command in commands[:4]:
        top_capabilities.append("Exposes runnable entrypoint `{0}` for local execution.".format(command))
    if narrative:
        top_capabilities.append(narrative.rstrip(".") + ".")
    if not top_capabilities:
        top_capabilities.append("Provides a deterministic repository snapshot that can be mined for portable implementation patterns.")

    for storage_path in storage_paths[:4]:
        top_constraints.append("Persists data under `{0}`.".format(storage_path))
    if result.total_bricks_loaded == 0:
        top_constraints.append("No domain bricks were injected during deterministic extraction.")
    if "stage3.5_validate" in result.stages_failed:
        top_constraints.append("Structured soul validation did not pass, so knowledge is inferred from deterministic repo facts only.")

    for failed_stage in result.stages_failed:
        top_failures.append("Pipeline stage `{0}` failed during extraction.".format(failed_stage))
    if not top_failures and result.total_cards == 0:
        top_failures.append("No extracted soul cards were available, so downstream synthesis relies on repo metadata and file layout.")

    if repo_url:
        evidence_refs.append(_evidence_ref(repo_url, contracts, source_url=repo_url))
    for rel_path in project_files[:4]:
        evidence_refs.append(_evidence_ref(rel_path, contracts, source_url=repo_url or None))
    if not evidence_refs:
        evidence_refs.append(_evidence_ref("artifacts/repo_facts.json", contracts, source_url=repo_url or None))

    summary = extracted_summary_cls(
        project_id=name,
        repo=repo_ref,
        top_capabilities=top_capabilities[:8],
        top_constraints=top_constraints[:6],
        top_failures=top_failures[:6],
        evidence_refs=evidence_refs[:6],
    )
    return summary, facts


def _keyword_signal(keyword: str, project_ids: Sequence[str], contracts: Dict[str, Any]) -> Any:
    compare_signal_cls = contracts["CompareSignal"]
    return compare_signal_cls(
        signal_id=_stable_id("SIG", "KW", keyword, ",".join(project_ids)),
        signal="ALIGNED",
        subject_project_ids=list(project_ids),
        normalized_statement="The solution should support `{0}` as part of the user need.".format(keyword),
        support_count=len(project_ids),
        support_independence=1.0 if len(project_ids) == 1 else 0.85,
        match_score=0.86,
        evidence_refs=[],
        notes="Synthetic alignment signal derived from the structured need profile.",
    )


def _signals_from_summaries(
    need_profile: Any,
    project_summaries: Sequence[Any],
    extraction_results: Sequence[Dict[str, Any]],
    contracts: Dict[str, Any],
) -> List[Any]:
    compare_signal_cls = contracts["CompareSignal"]
    signals: List[Any] = []
    project_ids = [summary.project_id for summary in project_summaries]

    if not project_ids:
        return signals

    for keyword in need_profile.keywords[:6]:
        signals.append(_keyword_signal(str(keyword), project_ids, contracts))

    statement_to_projects: Dict[str, List[str]] = {}
    for summary in project_summaries:
        for statement in summary.top_capabilities[:4]:
            statement_to_projects.setdefault(statement, []).append(summary.project_id)

    for statement, matched_projects in statement_to_projects.items():
        signal_kind = "ALIGNED" if len(matched_projects) > 1 else "ORIGINAL"
        signals.append(
            compare_signal_cls(
                signal_id=_stable_id("SIG", signal_kind, statement, ",".join(matched_projects)),
                signal=signal_kind,
                subject_project_ids=list(matched_projects),
                normalized_statement=statement,
                support_count=len(matched_projects),
                support_independence=1.0 if len(matched_projects) == 1 else 0.8,
                match_score=1.0 if len(matched_projects) == 1 else 0.84,
                evidence_refs=[],
                notes="Generated from deterministic extraction summaries.",
            )
        )

    storage_facts: Dict[str, List[str]] = {}
    for item in extraction_results:
        if item["result"] is None:
            continue
        facts = _load_repo_facts(item["result"])
        storage_list = [str(value) for value in facts.get("storage_paths", []) if str(value).strip()]
        if storage_list:
            storage_facts[item["name"]] = storage_list

    if len(storage_facts) >= 2:
        normalized_variants = {tuple(values[:2]) for values in storage_facts.values()}
        if len(normalized_variants) > 1:
            statements = []
            subject_ids = []
            for repo_name, values in sorted(storage_facts.items()):
                subject_ids.append(repo_name)
                statements.append("{0}: {1}".format(repo_name, ", ".join(values[:2])))
            signals.append(
                compare_signal_cls(
                    signal_id=_stable_id("SIG", "DIVERGENT", *statements),
                    signal="DIVERGENT",
                    subject_project_ids=subject_ids,
                    normalized_statement="Storage layout differs across extracted repositories.",
                    support_count=len(subject_ids),
                    support_independence=0.9,
                    match_score=0.4,
                    evidence_refs=[],
                    notes="; ".join(statements),
                )
            )

    return signals


def _build_synthesis_input(
    need_profile: Any,
    extraction_results: Sequence[Dict[str, Any]],
    repos: Sequence[Dict[str, Any]],
    contracts: Dict[str, Any],
) -> Tuple[Any, List[Any], Dict[str, Dict[str, Any]]]:
    synthesis_input_cls = contracts["SynthesisInput"]
    discovery_result_cls = contracts["DiscoveryResult"]
    compare_output_cls = contracts["CompareOutput"]
    compare_metrics_cls = contracts["CompareMetrics"]
    community_knowledge_cls = contracts["CommunityKnowledge"]

    repo_meta_map = _repo_metadata_map(repos)
    project_summaries: List[Any] = []
    repo_facts_map: Dict[str, Dict[str, Any]] = {}

    for item in extraction_results:
        if item["result"] is None:
            continue
        summary, facts = _project_summary_from_result(item, repo_meta_map.get(item["name"], {}), contracts)
        project_summaries.append(summary)
        repo_facts_map[item["name"]] = facts

    signals = _signals_from_summaries(need_profile, project_summaries, extraction_results, contracts)
    aligned_count = sum(1 for signal in signals if signal.signal == "ALIGNED")
    original_count = sum(1 for signal in signals if signal.signal == "ORIGINAL")
    drifted_count = sum(1 for signal in signals if signal.signal in ("DRIFTED", "DIVERGENT", "CONTESTED"))

    compare_output = compare_output_cls(
        domain_id=_slugify(getattr(need_profile, "intent", "") or getattr(need_profile, "raw_input", "")),
        compared_projects=[summary.project_id for summary in project_summaries],
        signals=signals,
        metrics=compare_metrics_cls(
            project_count=max(1, len(project_summaries)),
            atom_count=len(signals),
            aligned_count=aligned_count,
            missing_count=0,
            original_count=original_count,
            drifted_count=drifted_count,
        ),
    )

    discovery_result = discovery_result_cls(
        candidates=[],
        search_coverage=[],
        no_candidate_reason=None,
    )

    synthesis_input = synthesis_input_cls(
        need_profile=need_profile,
        discovery_result=discovery_result,
        project_summaries=project_summaries,
        comparison_result=compare_output,
        community_knowledge=community_knowledge_cls(),
    )
    return synthesis_input, project_summaries, repo_facts_map


def _best_single_result(extraction_results: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    successful = [item for item in extraction_results if item["result"] is not None]
    if not successful:
        return None
    return max(
        successful,
        key=lambda item: (item["result"].total_cards, len(item["result"].stages_completed), -len(item["result"].stages_failed)),
    )


def _single_project_report(
    need_profile: Any,
    extraction_results: Sequence[Dict[str, Any]],
    repos: Sequence[Dict[str, Any]],
    contracts: Dict[str, Any],
) -> Tuple[Any, List[Any]]:
    synthesis_report_cls = contracts["SynthesisReportData"]
    synthesis_decision_cls = contracts["SynthesisDecision"]
    synthesis_input, project_summaries, _repo_facts_map = _build_synthesis_input(
        need_profile,
        extraction_results,
        repos,
        contracts,
    )

    best_item = _best_single_result(extraction_results)
    if best_item is None:
        raise ValueError("No successful extraction result available for single-project fallback.")

    selected_project = next(
        summary for summary in project_summaries if summary.project_id == best_item["name"]
    )
    selected: List[Any] = []
    excluded: List[Any] = []

    ordered_statements = (
        list(selected_project.top_capabilities[:6])
        + list(selected_project.top_constraints[:4])
        + list(selected_project.top_failures[:3])
    )

    for index, statement in enumerate(ordered_statements):
        decision_type = "include" if index < 8 else "exclude"
        decision_cls = synthesis_decision_cls(
            decision_id=_stable_id("DEC", selected_project.project_id, statement, str(index)),
            statement=statement,
            decision=decision_type,
            rationale="Derived from deterministic extraction of `{0}` while synthesis was unavailable or intentionally bypassed.".format(selected_project.project_id),
            source_refs=[str(selected_project.repo.url), "project:{0}".format(selected_project.project_id)],
            demand_fit="high" if index < 4 else "medium",
        )
        if decision_type == "include":
            selected.append(decision_cls)
        else:
            excluded.append(decision_cls)

    report = synthesis_report_cls(
        consensus=[],
        conflicts=[],
        unique_knowledge=list(selected),
        selected_knowledge=list(selected),
        excluded_knowledge=list(excluded),
        open_questions=[
            "Only one repository was compiled into the final report, so cross-project consensus is unavailable."
        ],
    )
    return report, project_summaries


def _prepare_compile_ready_report(report: Any, contracts: Dict[str, Any]) -> Any:
    synthesis_report_cls = contracts["SynthesisReportData"]
    synthesis_decision_cls = contracts["SynthesisDecision"]

    selected = [decision for decision in report.selected_knowledge if decision.decision == "include"]
    if not selected:
        selected = [
            synthesis_decision_cls(
                decision_id=decision.decision_id,
                statement=decision.statement,
                decision="include",
                rationale=decision.rationale,
                source_refs=list(decision.source_refs),
                demand_fit=decision.demand_fit,
            )
            for decision in list(report.consensus)[:3] + list(report.unique_knowledge)[:3]
            if getattr(decision, "decision", "include") != "exclude"
        ]

    excluded = [decision for decision in report.excluded_knowledge if decision.decision == "exclude"]
    consensus = [decision for decision in report.consensus if decision.decision == "include"]
    unique = [decision for decision in report.unique_knowledge if decision.decision == "include"]

    return synthesis_report_cls(
        consensus=consensus,
        conflicts=[],
        unique_knowledge=unique,
        selected_knowledge=selected,
        excluded_knowledge=excluded,
        open_questions=list(report.open_questions),
    )


@contextmanager
def _temporary_environ(extra_env: Dict[str, str]):
    previous: Dict[str, Optional[str]] = {}
    try:
        for key, value in extra_env.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _render_skill_markdown(
    need_profile: Any,
    compile_ready_report: Any,
    extraction_results: Sequence[Dict[str, Any]],
    repos: Sequence[Dict[str, Any]],
) -> str:
    skill_key = _slugify(getattr(need_profile, "intent", "") or getattr(need_profile, "raw_input", "compiled-skill"))
    title = skill_key.replace("-", " ").title()
    repo_meta_map = _repo_metadata_map(repos)

    capability_lines = []
    workflow_lines = []
    storage_lines = []
    prompt_lines = []
    limitation_lines = []

    for decision in compile_ready_report.selected_knowledge[:12]:
        statement = decision.statement.strip()
        lowered = statement.lower()
        capability_lines.append("- {0}".format(statement))
        if any(token in lowered for token in ("store", "storage", "persist", "path", "directory")):
            storage_lines.append("- {0}".format(statement))
        elif any(token in lowered for token in ("prompt", "message", "explain", "ai", "model")):
            prompt_lines.append("- {0}".format(statement))
        else:
            workflow_lines.append("- {0}".format(statement))

    if not workflow_lines:
        workflow_lines.extend(
            [
                "- Read the user request and map it to the extracted repository patterns.",
                "- Execute deterministic local commands before proposing any generated structure.",
                "- Write reproducible artifacts so the skill can be re-run safely.",
            ]
        )
    if not storage_lines:
        storage_lines.extend(
            [
                "- Store runtime state under `~/clawd/{0}/memory/`.".format(skill_key),
                "- Keep imported reference material separate from user-generated state.",
            ]
        )
    if not prompt_lines:
        prompt_lines.extend(
            [
                "- Explain why each generated artifact exists and which repository evidence influenced it.",
                "- Call out uncertainty when extraction coverage is partial.",
            ]
        )

    for item in extraction_results:
        repo_name = item["name"]
        if item["result"] is None:
            limitation_lines.append("- `{0}` was skipped because extraction failed: {1}".format(repo_name, item.get("error", "unknown error")))
            continue
        result = item["result"]
        stars = repo_meta_map.get(repo_name, {}).get("stars")
        limitation_lines.append(
            "- `{0}` contributed {1} cards, completed {2} stages, failed {3} stages{4}.".format(
                repo_name,
                result.total_cards,
                len(result.stages_completed),
                len(result.stages_failed),
                " and has {0} GitHub stars".format(stars) if stars is not None else "",
            )
        )

    keywords_line = ", ".join(need_profile.keywords[:8]) or "none"
    purpose_lines = [
        getattr(need_profile, "intent", "") or getattr(need_profile, "raw_input", ""),
        "",
        "This bridge skill packages deterministic extraction outputs into a reusable OpenClaw workflow. It is designed to keep provenance visible, isolate unsupported automation, and preserve the strongest patterns found across the supplied repositories.",
    ]

    sections = [
        "---",
        "skillKey: {0}".format(skill_key),
        "always: false",
        "os:",
        "  - macos",
        "  - linux",
        "install: Store all runtime data under ~/clawd/{0}/".format(skill_key),
        "allowed-tools:",
        "  - exec",
        "  - read",
        "  - write",
        "---",
        "# {0}".format(title),
        "",
        "## Purpose",
        "\n".join(purpose_lines),
        "",
        "## Capabilities",
        "\n".join(capability_lines or ["- Convert structured user intent into a deterministic local workflow."]),
        "",
        "## Workflow",
        "\n".join(workflow_lines),
        "",
        "## Storage",
        "\n".join(storage_lines),
        "",
        "## AI Prompt",
        "\n".join(prompt_lines),
        "",
        "## Provenance Policy",
        "- Prefer statements backed by extracted repo facts, project summaries, and compiler-selected knowledge.",
        "- Keep user-facing outputs traceable to source repositories and generated synthesis decisions.",
        "- Treat cross-project conflicts as limitations unless explicitly resolved upstream.",
        "",
        "## Input Context",
        "- Need keywords: {0}".format(keywords_line),
        "- Repositories considered: {0}".format(", ".join(item["name"] for item in extraction_results) or "none"),
        "- Selected knowledge count: {0}".format(len(compile_ready_report.selected_knowledge)),
        "",
        "## Operational Notes",
        "- This pipeline runs without direct LLM API dependencies and relies on deterministic extraction first.",
        "- If only one repository succeeds, the skill compiles in best-single-project mode.",
        "- If the compiler blocks on unresolved conflicts, the bridge emits a simplified but usable skill bundle.",
        "",
        "## Limitations",
        "\n".join(limitation_lines or ["- No additional limitations were recorded."]),
        "",
    ]
    rendered = "\n".join(sections).strip() + "\n"
    if len(rendered.encode("utf-8")) < 1024:
        rendered += (
            "\n## Extended Guidance\n"
            "Use this skill as a deterministic synthesis layer between discovery results and installable artifacts. "
            "When repository coverage is weak, prefer explicit placeholders over invented implementation detail. "
            "When multiple repositories disagree, keep the safer, more portable pattern in the compiled workflow and push alternative designs into limitations or provenance notes.\n"
        )
    return rendered


def _render_provenance_markdown(
    compile_ready_report: Any,
    extraction_results: Sequence[Dict[str, Any]],
    repos: Sequence[Dict[str, Any]],
) -> str:
    repo_meta_map = _repo_metadata_map(repos)
    lines = [
        "# Provenance",
        "",
        "This bundle was assembled from deterministic extraction results and compile-ready synthesis decisions.",
        "",
        "## Repositories",
    ]

    for item in extraction_results:
        repo_name = item["name"]
        repo_meta = repo_meta_map.get(repo_name, {})
        lines.append("")
        lines.append("### {0}".format(repo_name))
        lines.append("- Path: `{0}`".format(repo_meta.get("path", "unknown")))
        lines.append("- URL: {0}".format(repo_meta.get("url", "unknown")))
        if "stars" in repo_meta:
            lines.append("- Stars: {0}".format(repo_meta.get("stars")))
        if item["result"] is None:
            lines.append("- Extraction status: failed")
            lines.append("- Error: {0}".format(item.get("error", "unknown error")))
            continue
        result = item["result"]
        lines.append("- Extraction status: success")
        lines.append("- Completed stages: {0}".format(", ".join(result.stages_completed) or "none"))
        lines.append("- Failed stages: {0}".format(", ".join(result.stages_failed) or "none"))
        lines.append("- Total cards: {0}".format(result.total_cards))
        lines.append("- Bricks loaded: {0}".format(result.total_bricks_loaded))

    lines.extend(["", "## Selected Knowledge"])
    for decision in compile_ready_report.selected_knowledge:
        lines.append("")
        lines.append("### {0}".format(decision.decision_id))
        lines.append("- Statement: {0}".format(decision.statement))
        lines.append("- Rationale: {0}".format(decision.rationale))
        lines.append("- Source refs: {0}".format(", ".join(decision.source_refs) or "none"))

    return "\n".join(lines).strip() + "\n"


def _render_limitations_markdown(
    report: Any,
    extraction_results: Sequence[Dict[str, Any]],
) -> str:
    lines = ["# Limitations", ""]
    failures = [item for item in extraction_results if item["result"] is None]
    partial = [item for item in extraction_results if item["result"] is not None and item["result"].stages_failed]

    if failures:
        lines.append("## Extraction Failures")
        for item in failures:
            lines.append("- `{0}`: {1}".format(item["name"], item.get("error", "unknown error")))
        lines.append("")

    if partial:
        lines.append("## Partial Extraction")
        for item in partial:
            lines.append("- `{0}` failed stages: {1}".format(item["name"], ", ".join(item["result"].stages_failed)))
        lines.append("")

    if getattr(report, "excluded_knowledge", None):
        lines.append("## Excluded Knowledge")
        for decision in report.excluded_knowledge:
            lines.append("- `{0}`: {1}".format(decision.decision_id, decision.statement))
            lines.append("  Reason: {0}".format(decision.rationale))
        lines.append("")

    if getattr(report, "conflicts", None):
        lines.append("## Conflicts")
        for conflict in report.conflicts:
            lines.append("- `{0}`: {1}".format(conflict.conflict_id, conflict.title))
            lines.append("  Recommendation: {0}".format(conflict.recommended_resolution))
        lines.append("")

    open_questions = list(getattr(report, "open_questions", []) or [])
    if open_questions:
        lines.append("## Open Questions")
        for question in open_questions:
            lines.append("- {0}".format(question))
        lines.append("")

    if len(lines) <= 2:
        lines.append("No explicit limitations were recorded.")
    return "\n".join(lines).strip() + "\n"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_delivery(output_dir: Path, files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: Dict[str, Dict[str, Any]] = {}
    for filename, content in files.items():
        destination = output_dir / filename
        _write_text(destination, content)
        summary[filename] = {
            "path": str(destination.resolve()),
            "size_bytes": destination.stat().st_size,
        }
    return summary


def _copy_compiler_outputs(compiler_data: Any, output_dir: Path) -> Dict[str, Optional[Path]]:
    copied: Dict[str, Optional[Path]] = {
        "SKILL.md": None,
        "PROVENANCE.md": None,
        "LIMITATIONS.md": None,
    }
    attr_map = {
        "SKILL.md": "skill_md_path",
        "PROVENANCE.md": "provenance_md_path",
        "LIMITATIONS.md": "limitations_md_path",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, attr_name in attr_map.items():
        source = Path(str(getattr(compiler_data, attr_name, "")))
        if not source.exists():
            continue
        destination = output_dir / filename
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        copied[filename] = destination
    return copied


def _run_skill_compiler_step(
    need_profile: Any,
    compile_ready_report: Any,
    output_dir: Path,
    contracts: Dict[str, Any],
) -> Tuple[Optional[Any], Optional[str]]:
    try:
        run_skill_compiler = _import_skill_compiler()
        skill_compiler_input_cls = contracts["SkillCompilerInput"]
        platform_rules = _load_platform_rules(contracts)
        compiler_parent = Path(tempfile.mkdtemp(prefix="doramagic-compiler-", dir=str(output_dir.parent)))

        with _temporary_environ({"DORAMAGIC_SKILL_COMPILER_OUTPUT_DIR": str(compiler_parent)}):
            envelope = run_skill_compiler(
                skill_compiler_input_cls(
                    need_profile=need_profile,
                    synthesis_report=compile_ready_report,
                    platform_rules=platform_rules,
                )
            )
        if envelope.status not in ("ok", "degraded") or envelope.data is None:
            return None, "skill compiler returned status={0} error={1}".format(envelope.status, envelope.error_code)
        return envelope.data, None
    except Exception as exc:
        logger.error("Skill compiler failed: %s\n%s", exc, traceback.format_exc())
        return None, str(exc)


def _run_synthesis_step(
    synthesis_input: Any,
) -> Tuple[Optional[Any], Optional[str], List[str]]:
    warnings: List[str] = []
    try:
        run_synthesis = _import_synthesis()
        envelope = run_synthesis(synthesis_input)
        for warning in getattr(envelope, "warnings", []) or []:
            message = getattr(warning, "message", str(warning))
            warnings.append(message)
        if envelope.status not in ("ok", "degraded") or envelope.data is None:
            return None, "synthesis returned status={0} error={1}".format(envelope.status, envelope.error_code), warnings
        return envelope.data, None, warnings
    except Exception as exc:
        logger.error("Synthesis failed: %s\n%s", exc, traceback.format_exc())
        return None, str(exc), warnings


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Doramagic bridge pipeline")
    parser.add_argument("--need-profile", required=True)
    parser.add_argument("--repos", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--bricks-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--timeout-per-repo", type=int, default=120)
    args = parser.parse_args(argv)

    need_profile_path = Path(args.need_profile).expanduser().resolve()
    repos_path = Path(args.repos).expanduser().resolve()
    run_dir = Path(args.run_dir).expanduser().resolve()
    bricks_dir = Path(args.bricks_dir).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    warnings: List[str] = []

    try:
        raw_need = _read_json(need_profile_path)
    except Exception as exc:
        print(_fatal_json("failed to read need profile: {0}".format(exc)))
        return 1

    try:
        raw_repos = _read_json(repos_path)
    except Exception as exc:
        print(_fatal_json("failed to read repos file: {0}".format(exc)))
        return 1

    if not isinstance(raw_repos, list):
        print(_fatal_json("repos.json must contain a JSON list"))
        return 1

    if not raw_repos:
        print(_fatal_json("repos.json is empty"))
        return 1

    contracts = _import_contracts()
    need_profile = _build_need_profile(raw_need, contracts)

    from multi_extract import extract_multiple_repos

    extraction_results = extract_multiple_repos(
        repos=list(raw_repos),
        run_dir=str(run_dir),
        bricks_dir=str(bricks_dir),
        max_workers=args.max_workers,
        timeout_per_repo=args.timeout_per_repo,
    )

    successful = [item for item in extraction_results if item["result"] is not None]
    failed = [item for item in extraction_results if item["result"] is None]

    for item in failed:
        warnings.append("repo '{0}' failed: {1}".format(item["name"], item.get("error", "unknown error")))

    if not successful:
        print(_fatal_json("all repo extractions failed"))
        return 1

    synthesis_input, project_summaries, _repo_facts_map = _build_synthesis_input(
        need_profile,
        successful,
        raw_repos,
        contracts,
    )

    synthesis_report = None
    if len(successful) >= 2:
        synthesis_report, synthesis_error, synthesis_warnings = _run_synthesis_step(synthesis_input)
        warnings.extend("synthesis warning: {0}".format(message) for message in synthesis_warnings)
        if synthesis_report is None and synthesis_error:
            warnings.append("synthesis failed, using best single project: {0}".format(synthesis_error))
    else:
        warnings.append("only one repository extracted successfully; synthesis skipped in favor of best single project mode")

    if synthesis_report is None:
        synthesis_report, project_summaries = _single_project_report(
            need_profile,
            successful,
            raw_repos,
            contracts,
        )

    compile_ready_report = _prepare_compile_ready_report(synthesis_report, contracts)

    compiler_data, compiler_error = _run_skill_compiler_step(
        need_profile,
        compile_ready_report,
        output_dir,
        contracts,
    )
    if compiler_error:
        warnings.append("skill compiler failed, using fallback documents: {0}".format(compiler_error))

    if compiler_data is not None:
        _copy_compiler_outputs(compiler_data, output_dir)

    delivery_files = {
        "SKILL.md": _render_skill_markdown(
            need_profile,
            compile_ready_report,
            extraction_results,
            raw_repos,
        ),
        "PROVENANCE.md": _render_provenance_markdown(
            compile_ready_report,
            extraction_results,
            raw_repos,
        ),
        "LIMITATIONS.md": _render_limitations_markdown(
            synthesis_report,
            extraction_results,
        ),
    }

    delivery_summary = _write_delivery(output_dir, delivery_files)
    print(
        json.dumps(
            {
                "status": "success",
                "repos_extracted": len(successful),
                "repos_failed": len(failed),
                "delivery": delivery_summary,
                "warnings": warnings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
