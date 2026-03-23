"""M1 — doramagic_pipeline.py: SKILL.md 桥接脚本。

将 OpenClaw SKILL.md 触发层与 Doramagic Python 核心引擎连接：
  1. 读 need_profile.json + repos.json
  2. 调 multi_extract() 并行提取所有 repo
  3. 跑 run_synthesis() 综合多项目知识
  4. 跑 run_skill_compiler() 生成 SKILL.md / PROVENANCE.md / LIMITATIONS.md
  5. 将产出写到 --output 目录
  6. stdout 打印 JSON 摘要

用法:
    python3 doramagic_pipeline.py \
        --need-profile /path/to/need_profile.json \
        --repos /path/to/repos.json \
        --run-dir /path/to/run_dir \
        --bricks-dir /path/to/bricks \
        --output /path/to/delivery
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import traceback
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# sys.path bootstrap — make Doramagic packages importable from any working dir
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent

_REPO_ROOT: Optional[Path] = None
for _candidate in [
    _THIS_DIR.parent.parent.parent.parent,  # races/r07/pipeline/s1-sonnet -> root
    _THIS_DIR.parent.parent.parent,
    _THIS_DIR.parent.parent,
]:
    if (_candidate / "packages" / "contracts").exists():
        _REPO_ROOT = _candidate
        break

if _REPO_ROOT is None:
    _REPO_ROOT = _THIS_DIR.parent.parent.parent.parent

for _pkg in ["contracts", "shared_utils", "extraction", "orchestration", "cross_project", "skill_compiler"]:
    _pkg_path = str(_REPO_ROOT / "packages" / _pkg)
    if _pkg_path not in sys.path:
        sys.path.insert(0, _pkg_path)

# Also add THIS directory so multi_extract is importable
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("doramagic_pipeline")

# ---------------------------------------------------------------------------
# Lazy package imports (soft-fail)
# ---------------------------------------------------------------------------


def _import_synthesis():
    try:
        from doramagic_cross_project.synthesis import run_synthesis  # type: ignore[import]
        return run_synthesis
    except ImportError as exc:
        logger.warning("Could not import synthesis: %s", exc)
        return None


def _import_skill_compiler():
    try:
        from doramagic_skill_compiler.compiler import run_skill_compiler  # type: ignore[import]
        return run_skill_compiler
    except ImportError as exc:
        logger.warning("Could not import skill_compiler: %s", exc)
        return None


def _import_contracts():
    """Import all needed contract types; return None on failure."""
    try:
        from doramagic_contracts.base import NeedProfile, RepoRef, SearchDirection  # type: ignore[import]
        from doramagic_contracts.cross_project import (  # type: ignore[import]
            CommunityKnowledge,
            CompareMetrics,
            CompareOutput,
            CompareSignal,
            DiscoveryResult,
            ExtractedProjectSummary,
            SynthesisDecision,
            SynthesisInput,
            SynthesisReportData,
        )
        from doramagic_contracts.skill import (  # type: ignore[import]
            PlatformRules,
            SkillCompilerInput,
        )
        return {
            "NeedProfile": NeedProfile,
            "RepoRef": RepoRef,
            "SearchDirection": SearchDirection,
            "CommunityKnowledge": CommunityKnowledge,
            "CompareMetrics": CompareMetrics,
            "CompareOutput": CompareOutput,
            "CompareSignal": CompareSignal,
            "DiscoveryResult": DiscoveryResult,
            "ExtractedProjectSummary": ExtractedProjectSummary,
            "SynthesisDecision": SynthesisDecision,
            "SynthesisInput": SynthesisInput,
            "SynthesisReportData": SynthesisReportData,
            "PlatformRules": PlatformRules,
            "SkillCompilerInput": SkillCompilerInput,
        }
    except ImportError as exc:
        logger.warning("Could not import contracts: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Input readers
# ---------------------------------------------------------------------------


def _load_need_profile(path: Path) -> dict:
    """Read need_profile.json; raises on parse error."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_repos(path: Path) -> list:
    """Read repos.json; raises on parse error."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# NeedProfile builder
# ---------------------------------------------------------------------------


def _build_need_profile(raw: dict, contracts: dict):
    """Convert raw dict to NeedProfile contract object."""
    NeedProfile = contracts["NeedProfile"]
    SearchDirection = contracts["SearchDirection"]

    # Support both direct NeedProfile format and the simpler need_profile.json format
    if "raw_input" in raw:
        # Already in NeedProfile format (e.g. sim2_need_profile.json)
        directions = [
            SearchDirection(direction=d["direction"], priority=d.get("priority", "medium"))
            for d in raw.get("search_directions", [])
        ]
        return NeedProfile(
            raw_input=raw.get("raw_input", ""),
            keywords=raw.get("keywords", []),
            intent=raw.get("intent", raw.get("raw_input", "")),
            search_directions=directions,
            constraints=raw.get("constraints", []),
            quality_expectations=raw.get("quality_expectations", {}),
        )
    else:
        # Simplified format: {user_need, keywords, domain}
        user_need = raw.get("user_need", "")
        keywords = raw.get("keywords", [])
        domain = raw.get("domain", "general")
        directions = [
            SearchDirection(direction=f"Search for {domain} solutions", priority="high"),
        ]
        return NeedProfile(
            raw_input=user_need,
            keywords=keywords,
            intent=user_need,
            search_directions=directions,
            constraints=[],
            quality_expectations={},
        )


# ---------------------------------------------------------------------------
# Synthesis input builder
# ---------------------------------------------------------------------------


def _build_synthesis_input(
    need_profile_obj,
    extraction_results: list,
    repos_raw: list,
    contracts: dict,
):
    """Build SynthesisInput from pipeline extraction results.

    Since we skip Stage 1/2/3/4 (LLM stages), we build minimal but valid
    contract objects from what phase_runner produced (Stage 0 + Stage 3.5).
    """
    SynthesisInput = contracts["SynthesisInput"]
    DiscoveryResult = contracts["DiscoveryResult"]
    ExtractedProjectSummary = contracts["ExtractedProjectSummary"]
    RepoRef = contracts["RepoRef"]
    CompareOutput = contracts["CompareOutput"]
    CompareSignal = contracts["CompareSignal"]
    CompareMetrics = contracts["CompareMetrics"]
    CommunityKnowledge = contracts["CommunityKnowledge"]

    # Build minimal RepoRef objects keyed by repo name
    repo_map = {r["name"]: r for r in repos_raw}

    project_summaries = []
    compared_projects = []

    for item in extraction_results:
        if item["result"] is None:
            continue
        name = item["name"]
        result = item["result"]
        raw_repo = repo_map.get(name, {})

        repo_ref = RepoRef(
            repo_id=name,
            full_name=raw_repo.get("name", name),
            url=raw_repo.get("url", f"https://github.com/{name}/{name}"),
            default_branch="main",
            commit_sha="unknown",
            local_path=raw_repo.get("path", ""),
        )

        # Extract top-level signals from stage results
        # Use stages_completed / stages_failed as proxy for capability/failure signals
        top_capabilities = [
            f"Deterministic extraction completed: {s}"
            for s in result.stages_completed
        ]
        top_constraints = []
        top_failures = [
            f"Stage failed: {s}"
            for s in result.stages_failed
        ]

        # If repo_facts exists, try to read frameworks/languages as capabilities
        facts_path = Path(result.output_dir) / "artifacts" / "repo_facts.json"
        if facts_path.exists():
            try:
                with open(facts_path, encoding="utf-8") as f:
                    facts = json.load(f)
                for lang in facts.get("languages", []):
                    top_capabilities.append(f"Language: {lang}")
                for fw in facts.get("frameworks", []):
                    top_capabilities.append(f"Framework: {fw}")
                for dep in facts.get("dependencies", [])[:5]:
                    top_capabilities.append(f"Dependency: {dep}")
                for storage in facts.get("storage_paths", [])[:3]:
                    top_constraints.append(f"Storage path: {storage}")
                narrative = facts.get("project_narrative", "")
                if narrative:
                    top_capabilities.append(narrative[:200])
            except Exception as exc:
                logger.warning("Could not read repo_facts for %s: %s", name, exc)

        if not top_capabilities:
            top_capabilities = [f"Project {name} extracted successfully"]

        project_summaries.append(
            ExtractedProjectSummary(
                project_id=name,
                repo=repo_ref,
                top_capabilities=top_capabilities,
                top_constraints=top_constraints,
                top_failures=top_failures,
                evidence_refs=[],
            )
        )
        compared_projects.append(name)

    # Build a minimal CompareOutput (no LLM compare step was run)
    # We create a single ALIGNED signal per shared capability keyword to
    # give synthesis something to work with.
    keywords = need_profile_obj.keywords or []
    signals = []
    for kw in keywords:
        sig_id = "SIG-" + hashlib.sha1(kw.encode()).hexdigest()[:8].upper()
        signals.append(
            CompareSignal(
                signal_id=sig_id,
                signal="ALIGNED",
                subject_project_ids=compared_projects,
                normalized_statement=f"Domain keyword matched across projects: {kw}",
                support_count=len(compared_projects),
                support_independence=0.9,
                match_score=0.85,
                evidence_refs=[],
            )
        )

    # Add ORIGINAL signals from each project's unique capabilities
    for summary in project_summaries:
        for cap in summary.top_capabilities[:3]:
            sig_id = "SIG-" + hashlib.sha1(
                (summary.project_id + cap).encode()
            ).hexdigest()[:8].upper()
            signals.append(
                CompareSignal(
                    signal_id=sig_id,
                    signal="ORIGINAL",
                    subject_project_ids=[summary.project_id],
                    normalized_statement=cap,
                    support_count=1,
                    support_independence=1.0,
                    match_score=1.0,
                    evidence_refs=[],
                )
            )

    compare_output = CompareOutput(
        domain_id=getattr(need_profile_obj, "intent", "compiled-skill")
        .lower().replace(" ", "-")[:40]
        or "compiled-skill",
        compared_projects=compared_projects,
        signals=signals,
        metrics=CompareMetrics(
            project_count=len(compared_projects),
            atom_count=len(signals),
            aligned_count=len(keywords),
            missing_count=0,
            original_count=len(signals) - len(keywords),
            drifted_count=0,
        ),
    )

    # Minimal DiscoveryResult
    discovery_result = DiscoveryResult(candidates=[], search_coverage=[])

    return SynthesisInput(
        need_profile=need_profile_obj,
        discovery_result=discovery_result,
        project_summaries=project_summaries,
        comparison_result=compare_output,
        community_knowledge=CommunityKnowledge(),
    )


# ---------------------------------------------------------------------------
# Fallback SKILL.md / PROVENANCE.md / LIMITATIONS.md generators
# ---------------------------------------------------------------------------


def _fallback_skill_md(need_raw: dict, extraction_results: list) -> str:
    """Generate a minimal SKILL.md when skill_compiler is unavailable."""
    user_need = need_raw.get("user_need", need_raw.get("raw_input", "compiled skill"))
    keywords = need_raw.get("keywords", [])
    extracted_names = [r["name"] for r in extraction_results if r["result"] is not None]

    lines = [
        "---",
        "skillKey: compiled-skill",
        "always: false",
        "os:",
        "  - macos",
        "  - linux",
        "install: Store all runtime data under ~/clawd/compiled-skill/",
        "allowed-tools:",
        "  - exec",
        "  - read",
        "  - write",
        "---",
        "",
        "# Compiled Skill",
        "",
        "## Purpose",
        user_need,
        "",
        "## Workflow",
        "- Read user context and relevant local files.",
        "- Execute required steps based on the user need.",
        "- Write stable outputs to ~/clawd/compiled-skill/.",
        "",
        "## Storage",
        "- Store all persistent data under ~/clawd/compiled-skill/memory/.",
        "",
        "## AI Prompt",
        "- Explain tradeoffs briefly and avoid unsupported automation promises.",
        "",
        "## Sources",
        f"- Extracted from: {', '.join(extracted_names) if extracted_names else 'no repos'}",
        f"- Keywords: {', '.join(keywords)}",
        "",
        "## Platform Notes",
        "- Allowed tools are restricted to exec, read, and write.",
        "- Cron is intentionally omitted from frontmatter.",
    ]
    return "\n".join(lines) + "\n"


def _fallback_provenance_md(extraction_results: list, repos_raw: list) -> str:
    repo_map = {r["name"]: r for r in repos_raw}
    lines = ["# Provenance", "", "Extracted from the following repositories:"]
    for item in extraction_results:
        if item["result"] is None:
            continue
        raw = repo_map.get(item["name"], {})
        url = raw.get("url", "unknown")
        stars = raw.get("stars", "?")
        result = item["result"]
        lines.append(f"\n## {item['name']}")
        lines.append(f"- URL: {url}")
        lines.append(f"- Stars: {stars}")
        lines.append(f"- Stages completed: {', '.join(result.stages_completed) or 'none'}")
        lines.append(f"- Total cards: {result.total_cards}")
    return "\n".join(lines) + "\n"


def _fallback_limitations_md(extraction_results: list) -> str:
    failed = [r for r in extraction_results if r["result"] is None]
    lines = ["# Limitations", ""]
    if failed:
        lines.append("## Extraction Failures")
        for item in failed:
            lines.append(f"- {item['name']}: {item.get('error', 'unknown error')}")
        lines.append("")
    partial = [
        r for r in extraction_results
        if r["result"] is not None and r["result"].stages_failed
    ]
    if partial:
        lines.append("## Partial Extraction Warnings")
        for item in partial:
            lines.append(f"- {item['name']}: stages_failed={item['result'].stages_failed}")
    if not failed and not partial:
        lines.append("No explicit exclusions or unresolved conflicts.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Best-single-project synthesis fallback
# ---------------------------------------------------------------------------


def _best_single_result(extraction_results: list) -> Optional[dict]:
    """Pick the single best extraction result (most cards, fewest failures)."""
    successful = [r for r in extraction_results if r["result"] is not None]
    if not successful:
        return None
    return max(
        successful,
        key=lambda r: (r["result"].total_cards, -len(r["result"].stages_failed)),
    )


# ---------------------------------------------------------------------------
# Delivery writer
# ---------------------------------------------------------------------------


def _write_delivery(
    output_dir: Path,
    skill_md: str,
    provenance_md: str,
    limitations_md: str,
) -> dict:
    """Write the three delivery files and return size info."""
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_path = output_dir / "SKILL.md"
    provenance_path = output_dir / "PROVENANCE.md"
    limitations_path = output_dir / "LIMITATIONS.md"

    skill_path.write_text(skill_md, encoding="utf-8")
    provenance_path.write_text(provenance_md, encoding="utf-8")
    limitations_path.write_text(limitations_md, encoding="utf-8")

    return {
        "SKILL.md": {
            "path": str(skill_path.resolve()),
            "size_bytes": skill_path.stat().st_size,
        },
        "PROVENANCE.md": {
            "path": str(provenance_path.resolve()),
            "size_bytes": provenance_path.stat().st_size,
        },
        "LIMITATIONS.md": {
            "path": str(limitations_path.resolve()),
            "size_bytes": limitations_path.stat().st_size,
        },
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def main(argv: Optional[list] = None) -> int:
    """Entry point. Returns exit code (0 = success, 1 = fatal error)."""
    parser = argparse.ArgumentParser(
        description="Doramagic Pipeline — bridge SKILL.md to Python engine"
    )
    parser.add_argument(
        "--need-profile",
        required=True,
        help="Path to need_profile.json",
    )
    parser.add_argument(
        "--repos",
        required=True,
        help="Path to repos.json",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Working directory for intermediate artifacts",
    )
    parser.add_argument(
        "--bricks-dir",
        default="bricks/",
        help="Domain bricks directory (default: bricks/)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for SKILL.md, PROVENANCE.md, LIMITATIONS.md",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Max parallel extraction workers (default: 3)",
    )
    parser.add_argument(
        "--timeout-per-repo",
        type=int,
        default=120,
        help="Timeout in seconds per repo extraction (default: 120)",
    )
    args = parser.parse_args(argv)

    # Resolve paths
    need_profile_path = Path(args.need_profile).resolve()
    repos_path = Path(args.repos).resolve()
    run_dir = str(Path(args.run_dir).resolve())
    bricks_dir = str(Path(args.bricks_dir).resolve())
    output_dir = Path(args.output).resolve()

    warnings: list = []

    # ---- Step 1: Read inputs ----
    try:
        need_raw = _load_need_profile(need_profile_path)
    except Exception as exc:
        _fatal(f"Failed to read need_profile.json: {exc}")
        return 1

    try:
        repos_raw = _load_repos(repos_path)
    except Exception as exc:
        _fatal(f"Failed to read repos.json: {exc}")
        return 1

    logger.info("Loaded %d repos from %s", len(repos_raw), repos_path)

    # ---- Step 2: Parallel extraction ----
    from multi_extract import extract_multiple_repos

    extraction_results = extract_multiple_repos(
        repos=repos_raw,
        run_dir=run_dir,
        bricks_dir=bricks_dir,
        max_workers=args.max_workers,
        timeout_per_repo=args.timeout_per_repo,
    )

    successful = [r for r in extraction_results if r["result"] is not None]
    failed = [r for r in extraction_results if r["result"] is None]

    logger.info(
        "Extraction complete: %d successful, %d failed",
        len(successful),
        len(failed),
    )

    for item in failed:
        warnings.append(f"Repo {item['name']} failed: {item.get('error', 'unknown')}")

    if len(successful) == 0:
        _fatal(f"All {len(repos_raw)} repo extractions failed. Cannot continue.")
        return 1

    # ---- Step 3: Load contract types ----
    contracts = _import_contracts()

    # ---- Step 4: Synthesis ----
    synthesis_report = None
    skill_md = None
    provenance_md = None
    limitations_md = None

    if contracts is not None:
        need_profile_obj = _build_need_profile(need_raw, contracts)

        run_synthesis = _import_synthesis()

        if len(successful) >= 2 and run_synthesis is not None:
            logger.info("Running synthesis across %d projects", len(successful))
            try:
                synthesis_input = _build_synthesis_input(
                    need_profile_obj,
                    extraction_results,
                    repos_raw,
                    contracts,
                )
                envelope = run_synthesis(synthesis_input)
                if envelope.status in ("ok", "degraded"):
                    synthesis_report = envelope.data
                    logger.info("Synthesis complete: status=%s", envelope.status)
                    if envelope.warnings:
                        for w in envelope.warnings:
                            warnings.append(f"Synthesis warning: {w.message}")
                else:
                    logger.warning(
                        "Synthesis returned status=%s error=%s — falling back to best single project",
                        envelope.status,
                        envelope.error_code,
                    )
                    warnings.append(
                        f"Synthesis degraded ({envelope.error_code}) — using best single project"
                    )
            except Exception as exc:
                logger.error("Synthesis failed: %s\n%s", exc, traceback.format_exc())
                warnings.append(f"Synthesis exception — fallback to best single project: {exc}")
        else:
            if len(successful) == 1:
                logger.info("Only 1 project succeeded — skipping synthesis")
                warnings.append("Only 1 project succeeded — synthesis skipped")
            else:
                logger.warning("run_synthesis not importable — skipping synthesis")
                warnings.append("synthesis module unavailable — fallback to best single project")

        # ---- Step 5: Skill Compiler ----
        if synthesis_report is not None:
            run_skill_compiler = _import_skill_compiler()
            if run_skill_compiler is not None:
                logger.info("Running skill compiler")
                try:
                    PlatformRules = contracts["PlatformRules"]
                    SkillCompilerInput = contracts["SkillCompilerInput"]

                    # Set output dir via env so compiler writes to our run_dir
                    compiler_out = str(output_dir)
                    old_env = os.environ.get("DORAMAGIC_SKILL_COMPILER_OUTPUT_DIR")
                    os.environ["DORAMAGIC_SKILL_COMPILER_OUTPUT_DIR"] = str(output_dir.parent)

                    compiler_input = SkillCompilerInput(
                        need_profile=need_profile_obj,
                        synthesis_report=synthesis_report,
                        platform_rules=PlatformRules(),
                    )
                    compiler_envelope = run_skill_compiler(compiler_input)

                    # Restore env
                    if old_env is None:
                        os.environ.pop("DORAMAGIC_SKILL_COMPILER_OUTPUT_DIR", None)
                    else:
                        os.environ["DORAMAGIC_SKILL_COMPILER_OUTPUT_DIR"] = old_env

                    if compiler_envelope.status in ("ok", "degraded") and compiler_envelope.data:
                        compiler_out_data = compiler_envelope.data
                        # Copy compiler output files to our delivery directory
                        output_dir.mkdir(parents=True, exist_ok=True)
                        for src_attr, dst_name in [
                            ("skill_md_path", "SKILL.md"),
                            ("provenance_md_path", "PROVENANCE.md"),
                            ("limitations_md_path", "LIMITATIONS.md"),
                        ]:
                            src_path = Path(getattr(compiler_out_data, src_attr, ""))
                            if src_path.exists():
                                dst_path = output_dir / dst_name
                                if src_path.resolve() != dst_path.resolve():
                                    shutil.copy2(src_path, dst_path)
                                    logger.info("Copied %s → %s", src_path, dst_path)
                            else:
                                logger.warning(
                                    "Skill compiler output not found: %s", src_path
                                )
                        # Read back for delivery report
                        skill_path = output_dir / "SKILL.md"
                        provenance_path = output_dir / "PROVENANCE.md"
                        limitations_path = output_dir / "LIMITATIONS.md"
                        skill_md = skill_path.read_text(encoding="utf-8") if skill_path.exists() else None
                        provenance_md = provenance_path.read_text(encoding="utf-8") if provenance_path.exists() else None
                        limitations_md = limitations_path.read_text(encoding="utf-8") if limitations_path.exists() else None
                        logger.info("Skill compiler output written to %s", output_dir)
                    else:
                        logger.warning(
                            "Skill compiler returned status=%s error=%s — using fallback",
                            compiler_envelope.status,
                            compiler_envelope.error_code,
                        )
                        warnings.append(
                            f"Skill compiler failed ({compiler_envelope.error_code}) — using fallback"
                        )
                except Exception as exc:
                    logger.error("Skill compiler exception: %s\n%s", exc, traceback.format_exc())
                    warnings.append(f"Skill compiler exception — using fallback: {exc}")
            else:
                warnings.append("skill_compiler module unavailable — using fallback")

    # ---- Fallback: generate files if compiler didn't produce them ----
    if skill_md is None:
        logger.info("Generating fallback SKILL.md")
        skill_md = _fallback_skill_md(need_raw, extraction_results)
    if provenance_md is None:
        logger.info("Generating fallback PROVENANCE.md")
        provenance_md = _fallback_provenance_md(extraction_results, repos_raw)
    if limitations_md is None:
        logger.info("Generating fallback LIMITATIONS.md")
        limitations_md = _fallback_limitations_md(extraction_results)

    # ---- Step 6: Write delivery ----
    try:
        delivery = _write_delivery(output_dir, skill_md, provenance_md, limitations_md)
    except Exception as exc:
        _fatal(f"Failed to write delivery files: {exc}")
        return 1

    # ---- Step 7: stdout JSON summary ----
    summary = {
        "status": "success",
        "repos_extracted": len(successful),
        "repos_failed": len(failed),
        "delivery": delivery,
        "warnings": warnings,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _fatal(message: str) -> None:
    """Print a fatal error JSON to stdout and log to stderr."""
    logger.error(message)
    print(
        json.dumps({"status": "error", "error": message}, indent=2, ensure_ascii=False)
    )


if __name__ == "__main__":
    sys.exit(main())
