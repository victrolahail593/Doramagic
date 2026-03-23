from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


TESTS_DIR = Path(__file__).resolve().parent
MODULE_DIR = TESTS_DIR.parent
REPO_ROOT = next(
    parent
    for parent in MODULE_DIR.parents
    if (parent / "bricks").is_dir() and (parent / "packages" / "contracts").is_dir()
)
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from phase_runner import (  # noqa: E402
    PipelineConfig,
    _ensure_repo_facts_compat,
    _load_cards_as_dicts,
    _load_repo_facts,
    run_single_project_pipeline,
)


def _write_json(path: Path, payload: dict | list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_card(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _validation_report(overall_pass: bool = True) -> dict:
    return {
        "output_dir": "/tmp/out",
        "cards": [],
        "summary": {
            "overall_pass": overall_pass,
            "total_errors": 0 if overall_pass else 1,
        },
    }


class _MockDSDReport:
    def __init__(self, status: str) -> None:
        self.status = status

    def to_dict(self) -> dict:
        return {"checks": [], "overall_status": self.status}


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "manage.py").write_text("print('django')\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("django==5.0\n", encoding="utf-8")
    return repo


@pytest.fixture()
def temp_output(tmp_path: Path) -> Path:
    out = tmp_path / "output"
    (out / "artifacts").mkdir(parents=True)
    (out / "soul" / "cards" / "rules").mkdir(parents=True)
    (out / "soul" / "cards" / "concepts").mkdir(parents=True)
    (out / "soul").mkdir(exist_ok=True)
    return out


@pytest.fixture()
def old_repo_facts(temp_output: Path, temp_repo: Path) -> Path:
    path = temp_output / "artifacts" / "repo_facts.json"
    _write_json(
        path,
        {
            "repo_path": str(temp_repo),
            "commands": [],
            "skills": [],
            "files": ["manage.py", "requirements.txt"],
            "config_keys": [],
            "project_narrative": "legacy facts only",
        },
    )
    return path


@pytest.fixture()
def sample_rule_card(temp_output: Path) -> Path:
    card = temp_output / "soul" / "cards" / "rules" / "DR-001.md"
    _write_card(
        card,
        """---
card_type: decision_rule_card
card_id: DR-001
repo: demo
title: Guard transaction boundaries
type: ARCHITECTURE
severity: HIGH
rule: |
  When a write spans multiple steps, wrap it in a transaction.
do:
  - Use `transaction.atomic()`
dont:
  - Split the write across independent commits
confidence: 0.9
sources:
  - "repo/app.py:10"
---

## 真实场景

Atomic write.

## 影响范围

All payments.
""",
    )
    return card


def test_ensure_repo_facts_compat_enriches_old_payload(temp_repo: Path, temp_output: Path, old_repo_facts: Path) -> None:
    enriched = _ensure_repo_facts_compat(str(temp_repo), str(temp_output))
    assert enriched is not None
    assert "Django" in enriched["frameworks"]
    assert "Python" in enriched["languages"]
    stored = _load_repo_facts(str(temp_output))
    assert "frameworks" in stored


def test_load_cards_as_dicts_keeps_file_path(temp_output: Path, sample_rule_card: Path) -> None:
    cards = _load_cards_as_dicts(str(temp_output))
    assert len(cards) == 1
    assert cards[0]["_path"] == str(sample_rule_card)


def test_pipeline_enriches_old_repo_facts_and_runs_brick_injection(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
) -> None:
    config = PipelineConfig(
        enable_stage15=False,
        enable_dsd=False,
        skip_assembly=True,
        bricks_dir=str(REPO_ROOT / "bricks"),
    )
    with (
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=MagicMock(return_value=True)),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), config=config)

    assert "stage0" in result.stages_completed
    assert "brick_injection" in result.stages_completed
    assert result.total_bricks_loaded > 0
    assert "Django" in _load_repo_facts(str(temp_output))["frameworks"]


def test_stage15_skips_without_structured_stage1_output(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
) -> None:
    mock_stage15 = MagicMock()
    config = PipelineConfig(enable_stage15=True, enable_bricks=False, enable_dsd=False, skip_assembly=True)
    with (
        patch("phase_runner._import_stage15_runner", return_value=mock_stage15),
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=MagicMock(return_value=True)),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), adapter=object(), config=config)

    assert "stage1.5" in result.stages_skipped
    mock_stage15.assert_not_called()


def test_stage15_runs_with_structured_stage1_output(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
) -> None:
    fixture = json.loads((REPO_ROOT / "data" / "fixtures" / "sim2_stage1_output_calorie.json").read_text(encoding="utf-8"))
    fixture["repo"]["local_path"] = str(temp_repo)
    fixture["repo"]["repo_id"] = temp_repo.name
    fixture["repo"]["full_name"] = f"local/{temp_repo.name}"
    fixture["repo"]["url"] = f"https://localhost/local/{temp_repo.name}"
    _write_json(temp_output / "artifacts" / "stage1_scan_output.json", fixture)

    envelope = MagicMock(status="ok", data=MagicMock(promoted_claims=[]))
    stage15 = MagicMock(return_value=envelope)
    config = PipelineConfig(enable_stage15=True, enable_bricks=False, enable_dsd=False, skip_assembly=True)
    with (
        patch("phase_runner._import_stage15_runner", return_value=stage15),
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=MagicMock(return_value=True)),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), adapter=object(), config=config)

    assert "stage1.5" in result.stages_completed
    stage15.assert_called_once()


def test_stage35_persists_confidence_annotations_before_compiler(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
    sample_rule_card: Path,
) -> None:
    def fake_tag(cards: list[dict]) -> list[dict]:
        for card in cards:
            card["evidence_tags"] = ["CODE"]
            card["verdict"] = "SUPPORTED"
            card["policy_action"] = "ALLOW_CORE"
        return cards

    compiler = MagicMock(return_value=True)
    config = PipelineConfig(enable_stage15=False, enable_bricks=False, enable_dsd=False, skip_assembly=True)
    with (
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(fake_tag, None)),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=compiler),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), config=config)

    updated = sample_rule_card.read_text(encoding="utf-8")
    assert "evidence_tags: [CODE]" in updated
    assert "verdict: SUPPORTED" in updated
    assert "policy_action: ALLOW_CORE" in updated
    assert "stage3.5_confidence" in result.stages_completed
    compiler.assert_called_once()


def test_validation_failure_blocks_stage45_and_stage5(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
    sample_rule_card: Path,
) -> None:
    compiler = MagicMock(return_value=True)
    assemble = MagicMock(return_value=True)
    config = PipelineConfig(enable_stage15=False, enable_bricks=False, enable_dsd=False, skip_assembly=False)
    with (
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(False)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=compiler),
        patch("phase_runner._import_assemble", return_value=assemble),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), config=config)

    assert "stage3.5_validate" in result.stages_failed
    assert "stage4.5" in result.stages_skipped
    assert "stage5" in result.stages_skipped
    compiler.assert_not_called()
    assemble.assert_not_called()


def test_dsd_suspicious_is_reported_but_pipeline_continues(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
    sample_rule_card: Path,
) -> None:
    compiler = MagicMock(return_value=True)
    config = PipelineConfig(enable_stage15=False, enable_bricks=False, enable_dsd=True, skip_assembly=True)
    with (
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=MagicMock(return_value=_MockDSDReport("SUSPICIOUS"))),
        patch("phase_runner._import_knowledge_compiler", return_value=compiler),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), config=config)

    assert result.dsd_report == {"checks": [], "overall_status": "SUSPICIOUS"}
    assert "stage3.5_dsd" in result.stages_completed
    assert "stage4.5" in result.stages_completed


def test_assemble_failure_is_non_crashing(
    temp_repo: Path,
    temp_output: Path,
    old_repo_facts: Path,
    sample_rule_card: Path,
) -> None:
    config = PipelineConfig(enable_stage15=False, enable_bricks=False, enable_dsd=False, skip_assembly=False)
    with (
        patch("phase_runner._import_validate", return_value=(MagicMock(return_value=_validation_report(True)), MagicMock())),
        patch("phase_runner._import_confidence_tools", return_value=(MagicMock(side_effect=lambda cards: cards), MagicMock(side_effect=lambda text, card: text))),
        patch("phase_runner._import_dsd_runner", return_value=None),
        patch("phase_runner._import_knowledge_compiler", return_value=MagicMock(return_value=True)),
        patch("phase_runner._import_assemble", return_value=MagicMock(side_effect=RuntimeError("boom"))),
    ):
        result = run_single_project_pipeline(str(temp_repo), str(temp_output), config=config)

    assert "stage5" in result.stages_failed
    assert result.inject_dir is None
