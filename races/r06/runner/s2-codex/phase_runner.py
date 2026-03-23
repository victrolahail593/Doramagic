"""Single-project orchestration for the deterministic parts of Doramagic."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _discover_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "packages" / "contracts").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root for phase_runner.py")


_REPO_ROOT = _discover_repo_root()
for package_dir in (
    _REPO_ROOT / "packages" / "contracts",
    _REPO_ROOT / "packages" / "shared_utils",
    _REPO_ROOT / "packages" / "extraction",
):
    package_str = str(package_dir)
    if package_dir.is_dir() and package_str not in sys.path:
        sys.path.insert(0, package_str)

_SKILLS_SCRIPTS_DIR = _REPO_ROOT / "skills" / "soul-extractor" / "scripts"
_INJECTION_DIR = _REPO_ROOT / "races" / "r06" / "injection" / "s2-codex"
if str(_INJECTION_DIR) not in sys.path:
    sys.path.insert(0, str(_INJECTION_DIR))

_ALL_STAGE1_QUESTIONS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
_STAGE1_OUTPUT_CANDIDATES = (
    "artifacts/stage1_scan_output.json",
    "artifacts/stage1_output.json",
    "artifacts/stage1-scan-output.json",
    "stage1_scan_output.json",
    "stage1_output.json",
)
_STAGE1_FINDINGS_CANDIDATES = (
    "artifacts/stage1_findings.json",
    "stage1_findings.json",
)
_STAGE1_HYPOTHESES_CANDIDATES = (
    "artifacts/hypothesis_list.json",
    "hypothesis_list.json",
)


class PipelineConfig(BaseModel):
    enable_stage15: bool = True
    enable_bricks: bool = True
    enable_dsd: bool = True
    bricks_dir: str = "bricks/"
    knowledge_budget: int = 1800
    skip_assembly: bool = False
    extract_repo_facts_script: Optional[str] = None


class PipelineResult(BaseModel):
    stages_completed: list[str]
    stages_skipped: list[str]
    stages_failed: list[str]
    output_dir: str
    inject_dir: Optional[str]
    dsd_report: Optional[dict]
    total_cards: int
    total_bricks_loaded: int


def _mark(stage_list: list[str], stage: str) -> None:
    if stage not in stage_list:
        stage_list.append(stage)


def _load_json(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _merge_unique(*iterables: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for iterable in iterables:
        for item in iterable:
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged


def _repo_facts_path(output_dir: str) -> Path:
    return Path(output_dir).expanduser().resolve() / "artifacts" / "repo_facts.json"


def _load_repo_facts(output_dir: str) -> Optional[dict]:
    return _load_json(_repo_facts_path(output_dir))


def _load_community_signals(output_dir: str) -> Optional[str]:
    path = Path(output_dir).expanduser().resolve() / "artifacts" / "community_signals.md"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _find_extract_script(config: PipelineConfig) -> Optional[str]:
    if config.extract_repo_facts_script:
        return config.extract_repo_facts_script
    candidate = _SKILLS_SCRIPTS_DIR / "extract_repo_facts.py"
    return str(candidate) if candidate.is_file() else None


def _import_validate() -> tuple[Optional[Callable[..., dict]], Optional[Callable[..., None]]]:
    if str(_SKILLS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SKILLS_SCRIPTS_DIR))
    try:
        from validate_extraction import validate_all, write_report  # type: ignore[import]

        return validate_all, write_report
    except ImportError as exc:
        logger.warning("Could not import validate_extraction: %s", exc)
        return None, None


def _import_assemble() -> Optional[Callable[[str], bool]]:
    if str(_SKILLS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SKILLS_SCRIPTS_DIR))
    try:
        from assemble_output import assemble  # type: ignore[import]

        return assemble
    except ImportError as exc:
        logger.warning("Could not import assemble_output: %s", exc)
        return None


def _import_brick_injector() -> Optional[Callable[..., Any]]:
    try:
        from brick_injection import load_and_inject_bricks  # type: ignore[import]

        return load_and_inject_bricks
    except ImportError as exc:
        logger.warning("Could not import brick_injection: %s", exc)
        return None


def _import_confidence_tools() -> tuple[Optional[Callable[[list[dict]], list[dict]]], Optional[Callable[[str, dict], str]]]:
    try:
        from doramagic_extraction.confidence_system import (
            inject_verdict_into_frontmatter,
            run_evidence_tagging,
        )

        return run_evidence_tagging, inject_verdict_into_frontmatter
    except ImportError as exc:
        logger.warning("Could not import confidence tools: %s", exc)
        return None, None


def _import_dsd_runner() -> Optional[Callable[..., Any]]:
    try:
        from doramagic_extraction.deceptive_source_detection import run_dsd_checks

        return run_dsd_checks
    except ImportError as exc:
        logger.warning("Could not import DSD runner: %s", exc)
        return None


def _import_knowledge_compiler() -> Optional[Callable[[str, int], bool]]:
    try:
        from doramagic_extraction.knowledge_compiler import compile_knowledge

        return compile_knowledge
    except ImportError as exc:
        logger.warning("Could not import knowledge compiler: %s", exc)
        return None


def _import_stage15_runner() -> Optional[Callable[..., Any]]:
    try:
        from doramagic_extraction.stage15_agentic import run_stage15_agentic

        return run_stage15_agentic
    except ImportError as exc:
        logger.warning("Could not import stage15 runner: %s", exc)
        return None


def _import_stage0_extractor() -> Optional[Callable[[str], Any]]:
    try:
        from doramagic_extraction.stage0 import extract_repo_facts

        return extract_repo_facts
    except ImportError as exc:
        logger.warning("Could not import stage0 extractor: %s", exc)
        return None


def _parse_frontmatter(text: str) -> dict:
    import re

    meta: dict = {}
    if not text.startswith("---"):
        return meta

    end = text.find("---", 3)
    if end == -1:
        return meta

    current_key: Optional[str] = None
    for line in text[3:end].strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and current_key is not None:
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(stripped[2:].strip().strip('"').strip("'"))
            continue

        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if not match:
            continue

        current_key = match.group(1)
        raw_value = match.group(2).strip()
        if raw_value == "":
            meta[current_key] = []
        elif raw_value != "|":
            meta[current_key] = raw_value.strip('"').strip("'")
    return meta


def _load_cards_as_dicts(output_dir: str) -> list[dict]:
    cards_dir = Path(output_dir).expanduser().resolve() / "soul" / "cards"
    cards: list[dict] = []
    for subdir in ("concepts", "workflows", "rules"):
        bucket = cards_dir / subdir
        if not bucket.is_dir():
            continue
        for path in sorted(bucket.glob("*.md")):
            meta = _parse_frontmatter(path.read_text(encoding="utf-8"))
            meta["_filename"] = path.name
            meta["_subdir"] = subdir
            meta["_path"] = str(path)
            meta.setdefault("evidence_refs", [])
            cards.append(meta)
    return cards


def _write_validation_report(output_dir: str, report: dict) -> None:
    path = Path(output_dir).expanduser().resolve() / "soul" / "validation_report.json"
    _write_json(path, report)


def _write_dsd_report(output_dir: str, dsd_dict: dict) -> None:
    path = Path(output_dir).expanduser().resolve() / "artifacts" / "dsd_report.json"
    _write_json(path, dsd_dict)


def _fallback_inject_confidence(frontmatter_text: str, card: dict) -> str:
    lines = frontmatter_text.splitlines()
    filtered = [
        line
        for line in lines
        if not line.startswith("evidence_tags:")
        and not line.startswith("verdict:")
        and not line.startswith("policy_action:")
    ]

    close_index: Optional[int] = None
    markers_seen = 0
    for index, line in enumerate(filtered):
        if line.strip() == "---":
            markers_seen += 1
            if markers_seen == 2:
                close_index = index
                break

    injection = [
        f"evidence_tags: [{', '.join(card.get('evidence_tags', []))}]",
        f"verdict: {card.get('verdict')}",
        f"policy_action: {card.get('policy_action')}",
    ]

    if close_index is None:
        filtered.extend(injection)
    else:
        for offset, line in enumerate(injection):
            filtered.insert(close_index + offset, line)

    return "\n".join(filtered)


def _persist_tagged_cards(
    tagged_cards: list[dict],
    injector: Optional[Callable[[str, dict], str]],
) -> None:
    for card in tagged_cards:
        card_path = card.get("_path")
        if not card_path:
            continue
        path = Path(card_path)
        original = path.read_text(encoding="utf-8")
        updated = injector(original, card) if injector is not None else _fallback_inject_confidence(original, card)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def _repo_facts_from_stage0_output(repo_path: str, output: Any) -> dict:
    payload = output.model_dump() if hasattr(output, "model_dump") else dict(output)
    repo_payload = payload.get("repo", {})
    return {
        "repo": repo_payload,
        "repo_path": repo_path,
        "project_narrative": payload.get("project_narrative") or payload.get("repo_summary", ""),
        "repo_summary": payload.get("repo_summary", ""),
        "languages": payload.get("languages", []),
        "frameworks": payload.get("frameworks", []),
        "entrypoints": payload.get("entrypoints", []),
        "commands": payload.get("commands", []),
        "storage_paths": payload.get("storage_paths", []),
        "dependencies": payload.get("dependencies", []),
        "skills": [],
        "files": [],
        "config_keys": [],
    }


def _ensure_repo_facts_compat(repo_path: str, output_dir: str) -> Optional[dict]:
    repo_path = str(Path(repo_path).expanduser().resolve())
    facts_path = _repo_facts_path(output_dir)
    raw_facts = _load_json(facts_path)
    if raw_facts is None:
        return None

    extractor = _import_stage0_extractor()
    if extractor is None:
        return raw_facts

    needs_enrichment = any(
        field not in raw_facts
        for field in ("languages", "frameworks", "entrypoints", "storage_paths", "dependencies", "repo_summary")
    )

    if not needs_enrichment:
        return raw_facts

    try:
        stage0_facts = extractor(repo_path)
    except Exception as exc:
        logger.warning("Could not enrich repo_facts via stage0 extractor: %s", exc)
        return raw_facts

    stage0_payload = _repo_facts_from_stage0_output(repo_path, stage0_facts)
    enriched = dict(raw_facts)
    enriched["repo_path"] = raw_facts.get("repo_path", repo_path)
    enriched["project_narrative"] = raw_facts.get("project_narrative") or stage0_payload["project_narrative"]
    enriched["repo_summary"] = raw_facts.get("repo_summary") or stage0_payload["repo_summary"]
    enriched["languages"] = raw_facts.get("languages") or stage0_payload["languages"]
    enriched["frameworks"] = raw_facts.get("frameworks") or stage0_payload["frameworks"]
    enriched["entrypoints"] = raw_facts.get("entrypoints") or stage0_payload["entrypoints"]
    enriched["storage_paths"] = raw_facts.get("storage_paths") or stage0_payload["storage_paths"]
    enriched["dependencies"] = raw_facts.get("dependencies") or stage0_payload["dependencies"]
    enriched["commands"] = _merge_unique(raw_facts.get("commands", []), stage0_payload["commands"])
    enriched["skills"] = raw_facts.get("skills", [])
    enriched["files"] = raw_facts.get("files", [])
    enriched["config_keys"] = raw_facts.get("config_keys", [])
    if not raw_facts.get("repo") and stage0_payload.get("repo"):
        enriched["repo"] = stage0_payload["repo"]

    if enriched != raw_facts:
        _write_json(facts_path, enriched)
    return enriched


def _run_stage0(
    repo_path: str,
    output_dir: str,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> bool:
    facts_path = _repo_facts_path(output_dir)
    if facts_path.is_file():
        _ensure_repo_facts_compat(repo_path, output_dir)
        _mark(stages_completed, "stage0")
        return True

    script = _find_extract_script(config)
    if script is not None:
        try:
            completed = subprocess.run(
                [sys.executable, script, "--repo-path", repo_path, "--output-dir", output_dir],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if completed.returncode == 0:
                _ensure_repo_facts_compat(repo_path, output_dir)
                _mark(stages_completed, "stage0")
                return True
            logger.error("Stage 0 CLI failed: %s", completed.stderr.strip())
        except subprocess.TimeoutExpired:
            logger.error("Stage 0 CLI timed out for %s", repo_path)
        except Exception:
            logger.error("Stage 0 CLI raised:\n%s", traceback.format_exc())

    extractor = _import_stage0_extractor()
    if extractor is None:
        _mark(stages_failed, "stage0")
        return False

    try:
        stage0_facts = extractor(repo_path)
        _write_json(facts_path, _repo_facts_from_stage0_output(repo_path, stage0_facts))
        _mark(stages_completed, "stage0")
        return True
    except Exception:
        logger.error("Stage 0 fallback extractor raised:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage0")
        return False


def _run_brick_injection(
    output_dir: str,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> int:
    if not config.enable_bricks:
        _mark(stages_skipped, "brick_injection")
        return 0

    bricks_dir = Path(config.bricks_dir).expanduser().resolve()
    if not bricks_dir.is_dir():
        _mark(stages_skipped, "brick_injection")
        return 0

    load_and_inject_bricks = _import_brick_injector()
    if load_and_inject_bricks is None:
        _mark(stages_skipped, "brick_injection")
        return 0

    repo_facts = _load_repo_facts(output_dir)
    frameworks = (repo_facts or {}).get("frameworks", [])
    if not frameworks:
        _mark(stages_skipped, "brick_injection")
        return 0

    try:
        result = load_and_inject_bricks(frameworks=frameworks, bricks_dir=str(bricks_dir), output_dir=output_dir)
        _mark(stages_completed, "brick_injection")
        return int(result.bricks_loaded)
    except Exception:
        logger.error("Brick injection raised:\n%s", traceback.format_exc())
        _mark(stages_failed, "brick_injection")
        return 0


def _build_stage15_repo_facts(repo_path: str, repo_facts_raw: dict):
    from doramagic_contracts.base import RepoRef
    from doramagic_contracts.extraction import RepoFacts

    repo_payload = dict(repo_facts_raw.get("repo") or {})
    repo_payload.setdefault("repo_id", Path(repo_path).name)
    repo_payload.setdefault("full_name", f"local/{Path(repo_path).name}")
    repo_payload.setdefault("url", f"https://localhost/local/{Path(repo_path).name}")
    repo_payload.setdefault("default_branch", "main")
    repo_payload.setdefault("commit_sha", "0" * 40)
    repo_payload.setdefault("local_path", repo_path)
    repo_ref = RepoRef.model_validate(repo_payload)

    return RepoFacts(
        repo=repo_ref,
        languages=repo_facts_raw.get("languages", []),
        frameworks=repo_facts_raw.get("frameworks", []),
        entrypoints=repo_facts_raw.get("entrypoints", []),
        commands=repo_facts_raw.get("commands", []),
        storage_paths=repo_facts_raw.get("storage_paths", []),
        dependencies=repo_facts_raw.get("dependencies", []),
        repo_summary=repo_facts_raw.get("repo_summary") or repo_facts_raw.get("project_narrative", ""),
        project_narrative=repo_facts_raw.get("project_narrative", ""),
    )


def _load_stage1_scan_output(output_dir: str, repo_ref) -> Optional[Any]:
    from doramagic_contracts.extraction import Hypothesis, Stage1Coverage, Stage1Finding, Stage1ScanOutput

    root = Path(output_dir).expanduser().resolve()

    for relative in _STAGE1_OUTPUT_CANDIDATES:
        path = root / relative
        payload = _load_json(path)
        if payload is not None:
            return Stage1ScanOutput.model_validate(payload)

    findings_payload: Optional[list[dict]] = None
    hypotheses_payload: Optional[list[dict]] = None

    for relative in _STAGE1_FINDINGS_CANDIDATES:
        path = root / relative
        payload = _load_json(path)
        if isinstance(payload, list):
            findings_payload = payload
            break

    for relative in _STAGE1_HYPOTHESES_CANDIDATES:
        path = root / relative
        payload = _load_json(path)
        if isinstance(payload, list):
            hypotheses_payload = payload
            break

    if findings_payload is None and hypotheses_payload is None:
        return None

    findings = [Stage1Finding.model_validate(item) for item in (findings_payload or [])]
    hypotheses = [Hypothesis.model_validate(item) for item in (hypotheses_payload or [])]
    answered = sorted({finding.question_key for finding in findings})
    uncovered = [question for question in _ALL_STAGE1_QUESTIONS if question not in answered]
    coverage = Stage1Coverage(
        answered_questions=answered,
        partial_questions=[],
        uncovered_questions=uncovered,
    )
    return Stage1ScanOutput(
        repo=repo_ref,
        findings=findings,
        hypotheses=hypotheses,
        coverage=coverage,
        recommended_for_stage15=bool(hypotheses),
    )


def _run_stage15(
    repo_path: str,
    output_dir: str,
    adapter,
    router,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> None:
    if not config.enable_stage15 or adapter is None:
        _mark(stages_skipped, "stage1.5")
        return

    runner = _import_stage15_runner()
    if runner is None:
        _mark(stages_skipped, "stage1.5")
        return

    repo_facts_raw = _load_repo_facts(output_dir)
    if not repo_facts_raw:
        _mark(stages_skipped, "stage1.5")
        return

    try:
        from doramagic_contracts.extraction import Stage15AgenticInput, Stage15Budget, Stage15Toolset
    except ImportError:
        logger.error("Stage 1.5 contracts import failed:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage1.5")
        return

    try:
        repo_facts = _build_stage15_repo_facts(repo_path, repo_facts_raw)
        stage1_output = _load_stage1_scan_output(output_dir, repo_facts.repo)
    except Exception:
        logger.error("Stage 1.5 input construction failed:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage1.5")
        return

    if stage1_output is None:
        _mark(stages_skipped, "stage1.5")
        return
    if not stage1_output.recommended_for_stage15 or not stage1_output.hypotheses:
        _mark(stages_skipped, "stage1.5")
        return

    try:
        input_data = Stage15AgenticInput(
            repo=repo_facts.repo,
            repo_facts=repo_facts,
            stage1_output=stage1_output,
            budget=Stage15Budget(),
            toolset=Stage15Toolset(),
        )
        envelope = runner(input_data, adapter=adapter, router=router)
    except Exception:
        logger.error("Stage 1.5 execution failed:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage1.5")
        return

    if envelope.status in ("ok", "degraded"):
        _mark(stages_completed, "stage1.5")
    elif envelope.status == "blocked" and getattr(envelope, "error_code", None) == "E_NO_HYPOTHESES":
        _mark(stages_skipped, "stage1.5")
    else:
        _mark(stages_failed, "stage1.5")


def _run_stage35(
    output_dir: str,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> tuple[bool, Optional[dict], list[dict]]:
    validate_all, write_report = _import_validate()
    run_evidence_tagging, inject_frontmatter = _import_confidence_tools()
    run_dsd_checks = _import_dsd_runner()

    validation_passed = False
    if validate_all is None:
        _mark(stages_failed, "stage3.5_validate")
    else:
        try:
            report = validate_all(output_dir)
            if write_report is not None:
                write_report(report, output_dir)
            else:
                _write_validation_report(output_dir, report)
            validation_passed = bool(report.get("summary", {}).get("overall_pass", False))
            if validation_passed:
                _mark(stages_completed, "stage3.5_validate")
            else:
                _mark(stages_failed, "stage3.5_validate")
        except Exception:
            logger.error("Validation failed:\n%s", traceback.format_exc())
            _mark(stages_failed, "stage3.5_validate")

    cards = _load_cards_as_dicts(output_dir)
    tagged_cards = cards
    if not cards:
        _mark(stages_skipped, "stage3.5_confidence")
    elif run_evidence_tagging is None:
        _mark(stages_failed, "stage3.5_confidence")
    else:
        try:
            tagged_cards = run_evidence_tagging(cards)
            _persist_tagged_cards(tagged_cards, inject_frontmatter)
            _mark(stages_completed, "stage3.5_confidence")
        except Exception:
            logger.error("Confidence tagging failed:\n%s", traceback.format_exc())
            _mark(stages_failed, "stage3.5_confidence")

    dsd_report_dict: Optional[dict] = None
    if not config.enable_dsd:
        _mark(stages_skipped, "stage3.5_dsd")
    elif run_dsd_checks is None:
        _mark(stages_skipped, "stage3.5_dsd")
    else:
        try:
            dsd_report = run_dsd_checks(
                cards=tagged_cards,
                repo_facts=_load_repo_facts(output_dir),
                community_signals=_load_community_signals(output_dir),
            )
            dsd_report_dict = dsd_report.to_dict()
            _write_dsd_report(output_dir, dsd_report_dict)
            _mark(stages_completed, "stage3.5_dsd")
        except Exception:
            logger.error("DSD failed:\n%s", traceback.format_exc())
            _mark(stages_failed, "stage3.5_dsd")

    return validation_passed, dsd_report_dict, tagged_cards


def _run_stage45(
    output_dir: str,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> bool:
    compile_knowledge = _import_knowledge_compiler()
    if compile_knowledge is None:
        _mark(stages_failed, "stage4.5")
        return False

    try:
        success = compile_knowledge(output_dir, budget=config.knowledge_budget)
    except Exception:
        logger.error("Knowledge compiler failed:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage4.5")
        return False

    if success:
        _mark(stages_completed, "stage4.5")
        return True

    _mark(stages_failed, "stage4.5")
    return False


def _run_stage5(
    output_dir: str,
    config: PipelineConfig,
    stages_completed: list[str],
    stages_skipped: list[str],
    stages_failed: list[str],
) -> Optional[str]:
    if config.skip_assembly:
        _mark(stages_skipped, "stage5")
        return None

    assemble = _import_assemble()
    if assemble is None:
        _mark(stages_failed, "stage5")
        return None

    try:
        success = assemble(output_dir)
    except Exception:
        logger.error("Assembly failed:\n%s", traceback.format_exc())
        _mark(stages_failed, "stage5")
        return None

    if not success:
        _mark(stages_failed, "stage5")
        return None

    inject_dir = str((Path(output_dir).expanduser().resolve() / "inject"))
    _mark(stages_completed, "stage5")
    return inject_dir if Path(inject_dir).is_dir() else None


def run_single_project_pipeline(
    repo_path: str,
    output_dir: str,
    adapter=None,
    router=None,
    config: Optional[PipelineConfig] = None,
) -> PipelineResult:
    config = config or PipelineConfig()
    repo_path = str(Path(repo_path).expanduser().resolve())
    output_dir = str(Path(output_dir).expanduser().resolve())
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    stages_completed: list[str] = []
    stages_skipped: list[str] = []
    stages_failed: list[str] = []

    _run_stage0(repo_path, output_dir, config, stages_completed, stages_skipped, stages_failed)
    _ensure_repo_facts_compat(repo_path, output_dir)

    bricks_loaded = _run_brick_injection(output_dir, config, stages_completed, stages_skipped, stages_failed)
    _run_stage15(repo_path, output_dir, adapter, router, config, stages_completed, stages_skipped, stages_failed)

    validation_passed, dsd_report_dict, tagged_cards = _run_stage35(
        output_dir, config, stages_completed, stages_skipped, stages_failed
    )

    inject_dir: Optional[str] = None
    if not validation_passed:
        _mark(stages_skipped, "stage4.5")
        _mark(stages_skipped, "stage5")
    else:
        _run_stage45(output_dir, config, stages_completed, stages_skipped, stages_failed)
        inject_dir = _run_stage5(output_dir, config, stages_completed, stages_skipped, stages_failed)

    return PipelineResult(
        stages_completed=stages_completed,
        stages_skipped=stages_skipped,
        stages_failed=stages_failed,
        output_dir=output_dir,
        inject_dir=inject_dir,
        dsd_report=dsd_report_dict,
        total_cards=len(tagged_cards),
        total_bricks_loaded=bricks_loaded,
    )


__all__ = [
    "PipelineConfig",
    "PipelineResult",
    "_ensure_repo_facts_compat",
    "_load_cards_as_dicts",
    "_load_repo_facts",
    "_load_stage1_scan_output",
    "run_single_project_pipeline",
]
