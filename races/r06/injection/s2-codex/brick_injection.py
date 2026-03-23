"""Deterministic brick injection for Doramagic Stage 1/2/3 prompts."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


def _bootstrap_contracts_path() -> None:
    """Make `doramagic_contracts` importable when this file runs standalone."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        contracts_dir = parent / "packages" / "contracts"
        if contracts_dir.is_dir():
            contracts_str = str(contracts_dir)
            if contracts_str not in sys.path:
                sys.path.insert(0, contracts_str)
            return
    raise ImportError("Could not locate packages/contracts from brick_injection.py")


_bootstrap_contracts_path()

from doramagic_contracts.domain_graph import DomainBrick  # noqa: E402


_FRAMEWORK_TO_BRICK_FILE: dict[str, str] = {
    "django": "django",
    "react": "react",
    "fastapi": "fastapi_flask",
    "flask": "fastapi_flask",
    "python": "python_general",
    "go": "go_general",
    "go module": "go_general",
    "go modules": "go_general",
    "home assistant": "home_assistant",
    "obsidian": "obsidian_logseq",
    "logseq": "obsidian_logseq",
    "obsidian/logseq": "obsidian_logseq",
    "finance": "domain_finance",
    "health": "domain_health",
    "pkm": "domain_pkm",
    "private cloud": "domain_private_cloud",
    "self-hosted": "domain_private_cloud",
    "info ingestion": "domain_info_ingestion",
}

_FRAMEWORK_SUBSTRING_MAP: tuple[tuple[str, str], ...] = (
    ("django", "django"),
    ("react", "react"),
    ("fastapi", "fastapi_flask"),
    ("flask", "fastapi_flask"),
    ("python", "python_general"),
    ("go", "go_general"),
    ("home assistant", "home_assistant"),
    ("home_assistant", "home_assistant"),
    ("obsidian", "obsidian_logseq"),
    ("logseq", "obsidian_logseq"),
)

_DOMAIN_LABELS: dict[str, str] = {
    "django": "Django",
    "react": "React",
    "fastapi-flask": "FastAPI/Flask",
    "python-general": "Python",
    "go-general": "Go",
    "home-assistant": "Home Assistant",
    "obsidian-logseq": "Obsidian/Logseq",
    "domain-finance": "Finance",
    "domain-health": "Health",
    "domain-info-ingestion": "Info Ingestion",
    "domain-pkm": "PKM",
    "domain-private-cloud": "Private Cloud",
}

_INJECTION_HEADER = "你已经知道以下框架基线知识（来自 Doramagic 积木库）："
_INJECTION_FOOTER = "你的任务是发现这个具体项目在基线之上的独特做法。不要重复以上知识。"
_STATEMENT_LIMIT = 220


@dataclass(frozen=True)
class BrickInjectionResult:
    bricks_loaded: int
    frameworks_matched: list[str]
    frameworks_not_matched: list[str]
    injection_text: str
    bricks_path: Optional[str]
    raw_bricks: list[dict]


def _normalize_framework_name(framework: str) -> str:
    cleaned = re.sub(r"\s+", " ", framework.strip().lower())
    return cleaned


def _slugify_framework_name(framework: str) -> str:
    normalized = _normalize_framework_name(framework)
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def _resolve_brick_filename(framework: str) -> str:
    normalized = _normalize_framework_name(framework)
    mapped = _FRAMEWORK_TO_BRICK_FILE.get(normalized)
    if mapped:
        return mapped

    for needle, filename in _FRAMEWORK_SUBSTRING_MAP:
        if needle in normalized:
            return filename

    return _slugify_framework_name(framework)


def _normalize_domain_id(domain_id: str) -> str:
    return domain_id.strip().lower().replace("_", "-")


def _format_domain_label(domain_id: str) -> str:
    normalized = _normalize_domain_id(domain_id)
    if normalized in _DOMAIN_LABELS:
        return _DOMAIN_LABELS[normalized]

    tokens = [token for token in normalized.split("-") if token and token != "domain"]
    return " ".join(token.upper() if len(token) <= 3 else token.title() for token in tokens) or "Unknown"


def _condense_statement(statement: str) -> str:
    condensed = re.sub(r"\s+", " ", statement).strip()
    if len(condensed) <= _STATEMENT_LIMIT:
        return condensed
    return condensed[: _STATEMENT_LIMIT - 3].rstrip() + "..."


def _load_bricks_from_file(jsonl_path: Path) -> list[DomainBrick]:
    if not jsonl_path.is_file():
        return []

    bricks: list[DomainBrick] = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                bricks.append(DomainBrick.model_validate_json(line))
            except (ValueError, TypeError):
                continue
    return bricks


def _serialize_bricks(bricks: Iterable[DomainBrick]) -> list[dict]:
    return [brick.model_dump() for brick in bricks]


def _generate_injection_text(bricks: list[DomainBrick]) -> str:
    if not bricks:
        return ""

    lines = [_INJECTION_HEADER, ""]
    for brick in bricks:
        label = _format_domain_label(brick.domain_id)
        statement = _condense_statement(brick.statement)
        lines.append(f"[{label}] {statement}")

    lines.extend(["", _INJECTION_FOOTER])
    return "\n".join(lines)


def _write_merged_bricks(bricks: list[DomainBrick], output_dir: str) -> str:
    artifacts_dir = Path(output_dir).expanduser().resolve() / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    output_path = artifacts_dir / "domain_bricks.jsonl"
    if bricks:
        output_path.write_text(
            "".join(f"{brick.model_dump_json()}\n" for brick in bricks),
            encoding="utf-8",
        )
    else:
        output_path.write_text("", encoding="utf-8")
    return str(output_path)


def load_and_inject_bricks(
    frameworks: list[str],
    bricks_dir: str = "bricks/",
    output_dir: Optional[str] = None,
) -> BrickInjectionResult:
    """Match frameworks, load curated bricks, persist artifacts, render prompt text."""

    bricks_root = Path(bricks_dir).expanduser().resolve()

    loaded_files: set[Path] = set()
    frameworks_matched: list[str] = []
    frameworks_not_matched: list[str] = []
    all_bricks: list[DomainBrick] = []

    for framework in frameworks:
        filename = _resolve_brick_filename(framework)
        brick_file = bricks_root / f"{filename}.jsonl"

        if brick_file in loaded_files:
            if brick_file.is_file():
                frameworks_matched.append(framework)
            else:
                frameworks_not_matched.append(framework)
            continue

        bricks = _load_bricks_from_file(brick_file)
        if bricks:
            loaded_files.add(brick_file)
            frameworks_matched.append(framework)
            all_bricks.extend(bricks)
            continue

        frameworks_not_matched.append(framework)

    injection_text = _generate_injection_text(all_bricks)
    bricks_path = _write_merged_bricks(all_bricks, output_dir) if output_dir else None

    return BrickInjectionResult(
        bricks_loaded=len(all_bricks),
        frameworks_matched=frameworks_matched,
        frameworks_not_matched=frameworks_not_matched,
        injection_text=injection_text,
        bricks_path=bricks_path,
        raw_bricks=_serialize_bricks(all_bricks),
    )


__all__ = [
    "BrickInjectionResult",
    "_format_domain_label",
    "_generate_injection_text",
    "_load_bricks_from_file",
    "_normalize_framework_name",
    "_resolve_brick_filename",
    "_write_merged_bricks",
    "load_and_inject_bricks",
]
