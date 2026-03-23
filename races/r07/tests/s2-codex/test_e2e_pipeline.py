"""End-to-end tests for the R07 Doramagic bridge pipeline."""

from __future__ import annotations

import json
from pathlib import Path


def _parse_stdout_json(stdout: str) -> dict:
    payload = json.loads(stdout)
    assert isinstance(payload, dict)
    return payload


def test_pipeline_with_mock_data(run_pipeline, good_repo_path: Path) -> None:
    need = {
        "user_need": "calorie tracking app",
        "keywords": ["calorie", "nutrition"],
        "domain": "health",
    }
    repos = [
        {
            "name": "calorie-tracking",
            "path": str(good_repo_path),
            "stars": 42,
            "url": "https://github.com/example/calorie-tracking",
        }
    ]

    result = run_pipeline(need, repos)

    assert result.returncode == 0, result.stderr
    payload = _parse_stdout_json(result.stdout)
    assert payload["status"] == "success"
    assert payload["repos_extracted"] == 1
    assert payload["repos_failed"] == 0

    skill_path = Path(payload["delivery"]["SKILL.md"]["path"])
    provenance_path = Path(payload["delivery"]["PROVENANCE.md"]["path"])
    limitations_path = Path(payload["delivery"]["LIMITATIONS.md"]["path"])

    assert skill_path.exists()
    assert provenance_path.exists()
    assert limitations_path.exists()
    assert skill_path.stat().st_size >= 1024

    skill_text = skill_path.read_text(encoding="utf-8")
    assert "## Purpose" in skill_text
    assert "## Capabilities" in skill_text


def test_pipeline_handles_empty_repos(run_pipeline) -> None:
    need = {
        "user_need": "calorie tracking app",
        "keywords": ["calorie"],
        "domain": "health",
    }

    result = run_pipeline(need, [])

    assert result.returncode == 1
    payload = _parse_stdout_json(result.stdout)
    assert payload["status"] == "error"
    assert "empty" in payload["error"]


def test_pipeline_handles_bad_repo_path(run_pipeline, good_repo_path: Path) -> None:
    need = {
        "user_need": "calorie tracking app",
        "keywords": ["calorie", "nutrition"],
        "domain": "health",
    }
    repos = [
        {
            "name": "missing-repo",
            "path": str(good_repo_path.parent / "missing-repo"),
            "stars": 1,
            "url": "https://github.com/example/missing-repo",
        },
        {
            "name": "calorie-tracking",
            "path": str(good_repo_path),
            "stars": 42,
            "url": "https://github.com/example/calorie-tracking",
        },
    ]

    result = run_pipeline(need, repos)

    assert result.returncode == 0, result.stderr
    payload = _parse_stdout_json(result.stdout)
    assert payload["status"] == "success"
    assert payload["repos_extracted"] == 1
    assert payload["repos_failed"] == 1
    assert any("missing-repo" in warning for warning in payload["warnings"])
    assert Path(payload["delivery"]["SKILL.md"]["path"]).exists()
