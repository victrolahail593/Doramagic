from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


TESTS_DIR = Path(__file__).resolve().parent
MODULE_DIR = TESTS_DIR.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from brick_injection import (  # noqa: E402
    BrickInjectionResult,
    _format_domain_label,
    _generate_injection_text,
    _load_bricks_from_file,
    _normalize_framework_name,
    _resolve_brick_filename,
    _write_merged_bricks,
    load_and_inject_bricks,
)


def _write_jsonl(path: Path, rows: list[dict | str]) -> None:
    rendered: list[str] = []
    for row in rows:
        if isinstance(row, str):
            rendered.append(row)
        else:
            rendered.append(json.dumps(row, ensure_ascii=False))
    path.write_text("\n".join(rendered) + "\n", encoding="utf-8")


@pytest.fixture()
def tmp_bricks_dir(tmp_path: Path) -> Path:
    bricks_dir = tmp_path / "bricks"
    bricks_dir.mkdir()

    django_rows = [
        {
            "brick_id": "django-l1-orm",
            "domain_id": "django",
            "knowledge_type": "rationale",
            "statement": "Django ORM is lazy and querysets defer SQL execution.",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
            "support_count": 1,
        },
        {
            "brick_id": "django-l2-n-plus-1",
            "domain_id": "django",
            "knowledge_type": "failure",
            "statement": "N+1 queries usually require select_related or prefetch_related.",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
            "support_count": 1,
        },
    ]
    react_rows = [
        {
            "brick_id": "react-l1-hooks",
            "domain_id": "react",
            "knowledge_type": "constraint",
            "statement": "Hooks must be called at the top level of a component.",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
            "support_count": 1,
        }
    ]
    fastapi_flask_rows = [
        {
            "brick_id": "fastapi-l1-depends",
            "domain_id": "fastapi-flask",
            "knowledge_type": "capability",
            "statement": "FastAPI dependency injection is built around Depends().",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
            "support_count": 1,
        }
    ]
    broken_rows = [
        {
            "brick_id": "bad-1",
            "domain_id": "django",
            "knowledge_type": "rationale",
            "statement": "Missing support_count should fail validation.",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
        },
        "NOT JSON",
    ]

    _write_jsonl(bricks_dir / "django.jsonl", django_rows)
    _write_jsonl(bricks_dir / "react.jsonl", react_rows)
    _write_jsonl(bricks_dir / "fastapi_flask.jsonl", fastapi_flask_rows)
    _write_jsonl(bricks_dir / "broken.jsonl", broken_rows)
    return bricks_dir


@pytest.fixture()
def real_bricks_dir() -> Path:
    for parent in MODULE_DIR.parents:
        candidate = parent / "bricks"
        if candidate.is_dir() and list(candidate.glob("*.jsonl")):
            return candidate
    pytest.skip("real bricks directory not found")


def test_normalize_framework_name() -> None:
    assert _normalize_framework_name("  Django  ") == "django"
    assert _normalize_framework_name("FastAPI") == "fastapi"


def test_resolve_brick_filename_exact_and_substring() -> None:
    assert _resolve_brick_filename("Django") == "django"
    assert _resolve_brick_filename("Django REST Framework") == "django"
    assert _resolve_brick_filename("Go module") == "go_general"


def test_format_domain_label() -> None:
    assert _format_domain_label("domain-private-cloud") == "Private Cloud"
    assert _format_domain_label("python_general") == "Python"


def test_load_bricks_from_file_validates_schema(tmp_bricks_dir: Path) -> None:
    bricks = _load_bricks_from_file(tmp_bricks_dir / "broken.jsonl")
    assert bricks == []


def test_generate_injection_text_has_expected_shape(tmp_bricks_dir: Path) -> None:
    bricks = _load_bricks_from_file(tmp_bricks_dir / "django.jsonl")
    text = _generate_injection_text(bricks)
    assert text.startswith("你已经知道以下框架基线知识")
    assert "[Django]" in text
    assert text.endswith("不要重复以上知识。")


def test_generate_injection_text_truncates_long_statement() -> None:
    from brick_injection import DomainBrick  # noqa: E402

    brick = DomainBrick.model_validate(
        {
            "brick_id": "long-1",
            "domain_id": "django",
            "knowledge_type": "rationale",
            "statement": "x" * 400,
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["test"],
            "support_count": 1,
        }
    )
    line = next(
        line for line in _generate_injection_text([brick]).splitlines() if line.startswith("[Django]")
    )
    assert len(line) < 260
    assert line.endswith("...")


def test_write_merged_bricks_creates_artifacts_dir(tmp_bricks_dir: Path, tmp_path: Path) -> None:
    bricks = _load_bricks_from_file(tmp_bricks_dir / "django.jsonl")
    path = _write_merged_bricks(bricks, str(tmp_path))
    assert Path(path).exists()
    assert Path(path).parent.name == "artifacts"


def test_load_and_inject_bricks_single_framework(tmp_bricks_dir: Path) -> None:
    result = load_and_inject_bricks(["Django"], bricks_dir=str(tmp_bricks_dir))
    assert isinstance(result, BrickInjectionResult)
    assert result.bricks_loaded == 2
    assert result.frameworks_matched == ["Django"]
    assert result.frameworks_not_matched == []
    assert len(result.raw_bricks) == 2


def test_load_and_inject_bricks_multiple_frameworks(tmp_bricks_dir: Path) -> None:
    result = load_and_inject_bricks(["Django", "React"], bricks_dir=str(tmp_bricks_dir))
    assert result.bricks_loaded == 3
    assert result.frameworks_matched == ["Django", "React"]


def test_load_and_inject_bricks_deduplicates_shared_file(tmp_bricks_dir: Path) -> None:
    result = load_and_inject_bricks(["FastAPI", "Flask"], bricks_dir=str(tmp_bricks_dir))
    assert result.bricks_loaded == 1
    assert result.frameworks_matched == ["FastAPI", "Flask"]


def test_load_and_inject_bricks_marks_unknown_framework(tmp_bricks_dir: Path) -> None:
    result = load_and_inject_bricks(["Unknown"], bricks_dir=str(tmp_bricks_dir))
    assert result.bricks_loaded == 0
    assert result.frameworks_not_matched == ["Unknown"]
    assert result.injection_text == ""


def test_load_and_inject_bricks_writes_output_when_requested(tmp_bricks_dir: Path, tmp_path: Path) -> None:
    result = load_and_inject_bricks(
        ["Django", "React"],
        bricks_dir=str(tmp_bricks_dir),
        output_dir=str(tmp_path / "out"),
    )
    assert result.bricks_path is not None
    output_path = Path(result.bricks_path)
    lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == result.bricks_loaded


def test_load_and_inject_bricks_writes_empty_file_for_empty_selection(tmp_bricks_dir: Path, tmp_path: Path) -> None:
    result = load_and_inject_bricks(
        [],
        bricks_dir=str(tmp_bricks_dir),
        output_dir=str(tmp_path / "out"),
    )
    assert result.bricks_loaded == 0
    assert result.bricks_path is not None
    assert Path(result.bricks_path).read_text(encoding="utf-8") == ""


def test_real_bricks_are_loadable(real_bricks_dir: Path) -> None:
    django_path = real_bricks_dir / "django.jsonl"
    bricks = _load_bricks_from_file(django_path)
    assert bricks
    assert all(brick.brick_id for brick in bricks)


def test_real_bricks_integration(real_bricks_dir: Path, tmp_path: Path) -> None:
    result = load_and_inject_bricks(
        ["Django", "React", "FastAPI"],
        bricks_dir=str(real_bricks_dir),
        output_dir=str(tmp_path / "out"),
    )
    assert result.bricks_loaded > 0
    assert result.frameworks_matched == ["Django", "React", "FastAPI"]
    assert Path(result.bricks_path).exists()
