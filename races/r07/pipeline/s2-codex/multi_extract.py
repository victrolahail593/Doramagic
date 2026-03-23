"""Parallel extraction helpers for the R07 Doramagic bridge pipeline."""

from __future__ import annotations

import logging
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

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

for package_name in ("contracts", "shared_utils", "extraction", "orchestration"):
    package_path = str(_REPO_ROOT / "packages" / package_name)
    if package_path not in sys.path:
        sys.path.insert(0, package_path)

for helper_path in (
    _REPO_ROOT / "skills" / "soul-extractor" / "scripts",
    _REPO_ROOT / "races" / "r06" / "injection" / "s1-sonnet",
):
    helper_path_str = str(helper_path)
    if helper_path.exists() and helper_path_str not in sys.path:
        sys.path.insert(0, helper_path_str)


def _import_phase_runner():
    try:
        from doramagic_orchestration.phase_runner import PipelineConfig, run_single_project_pipeline

        return run_single_project_pipeline, PipelineConfig
    except ImportError as exc:
        logger.warning("Could not import phase runner: %s", exc)
        return None, None


def _sanitize_repo_name(name: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("-", "_", ".") else "-" for char in name)
    safe = safe.strip("-._")
    return safe or "repo"


def _repo_output_dir(run_dir: Path, repo_name: str) -> Path:
    return run_dir / "extractions" / _sanitize_repo_name(repo_name)


def _extract_repo_facts_script() -> Optional[str]:
    script_path = _REPO_ROOT / "skills" / "soul-extractor" / "scripts" / "extract_repo_facts.py"
    if script_path.exists():
        return str(script_path)
    return None


def _extract_single_repo(repo: Dict[str, Any], run_dir: Path, bricks_dir: Path) -> Dict[str, Any]:
    name = str(repo.get("name") or "unknown")
    repo_path = Path(str(repo.get("path") or "")).expanduser()

    run_single_project_pipeline, pipeline_config_cls = _import_phase_runner()
    if run_single_project_pipeline is None or pipeline_config_cls is None:
        return {
            "name": name,
            "result": None,
            "error": "phase_runner import failed",
        }

    if not repo_path.exists():
        return {
            "name": name,
            "result": None,
            "error": "repo path does not exist: {0}".format(repo_path),
        }

    if not repo_path.is_dir():
        return {
            "name": name,
            "result": None,
            "error": "repo path is not a directory: {0}".format(repo_path),
        }

    output_dir = _repo_output_dir(run_dir, name)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        config = pipeline_config_cls(
            enable_stage15=False,
            enable_bricks=True,
            enable_dsd=True,
            bricks_dir=str(bricks_dir),
            skip_assembly=False,
            extract_repo_facts_script=_extract_repo_facts_script(),
        )
        result = run_single_project_pipeline(
            repo_path=str(repo_path.resolve()),
            output_dir=str(output_dir),
            adapter=None,
            router=None,
            config=config,
        )
        return {
            "name": name,
            "result": result,
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive branch
        logger.error("Extraction failed for %s: %s\n%s", name, exc, traceback.format_exc())
        return {
            "name": name,
            "result": None,
            "error": str(exc),
        }


def extract_multiple_repos(
    repos: List[Dict[str, Any]],
    run_dir: str,
    bricks_dir: str,
    max_workers: int = 3,
    timeout_per_repo: int = 120,
) -> List[Dict[str, Any]]:
    """Extract multiple repositories concurrently.

    Returns:
        [{"name": str, "result": PipelineResult|None, "error": str|None}]
    """
    if not repos:
        return []

    resolved_run_dir = Path(run_dir).expanduser().resolve()
    resolved_bricks_dir = Path(bricks_dir).expanduser().resolve()
    resolved_run_dir.mkdir(parents=True, exist_ok=True)

    results_by_index: Dict[int, Dict[str, Any]] = {}
    futures: List[Tuple[int, Any]] = []
    worker_count = max(1, min(int(max_workers or 1), len(repos)))

    executor = ThreadPoolExecutor(max_workers=worker_count)
    try:
        for index, repo in enumerate(repos):
            future = executor.submit(_extract_single_repo, repo, resolved_run_dir, resolved_bricks_dir)
            futures.append((index, future))

        for index, future in futures:
            repo_name = str(repos[index].get("name") or "unknown")
            try:
                results_by_index[index] = future.result(timeout=timeout_per_repo)
            except TimeoutError:
                logger.error("Extraction timed out for %s after %ss", repo_name, timeout_per_repo)
                results_by_index[index] = {
                    "name": repo_name,
                    "result": None,
                    "error": "timeout after {0}s".format(timeout_per_repo),
                }
            except Exception as exc:  # pragma: no cover - defensive branch
                logger.error("Unexpected extraction error for %s: %s", repo_name, exc)
                results_by_index[index] = {
                    "name": repo_name,
                    "result": None,
                    "error": str(exc),
                }
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    return [results_by_index[index] for index in range(len(repos))]
