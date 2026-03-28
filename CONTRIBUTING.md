# Contributing to Doramagic

## Getting Started

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cd Doramagic
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running Tests

```bash
make test
```

Or manually:

```bash
PYTHONPATH=packages/contracts:packages/extraction:packages/shared_utils:packages/community:packages/cross_project:packages/skill_compiler:packages/orchestration:packages/platform_openclaw:packages/domain_graph:packages/controller:packages/executors:packages/racekit:packages/evals \
  .venv/bin/python -m pytest tests/ packages/ -v \
  --ignore=packages/preextract_api \
  --ignore=packages/doramagic_product
```

## Project Structure

- `packages/` -- Core Python engine (contracts, controller, executors, extraction, orchestration, etc.)
- `bricks/` -- 278 knowledge bricks across 34 frameworks/domains (JSONL format)
- `skills/doramagic/` -- Self-contained OpenClaw / Claude Code skill bundle
- `tests/` -- Unit and E2E smoke tests (26 tests)
- `scripts/` -- Utility and release scripts

## Architecture Overview

Doramagic v12.1.1 uses a **conditional DAG** (not a linear pipeline):

- `packages/controller/` -- FlowController with conditional edge FSM
- `packages/executors/` -- Phase executors (NeedProfileBuilder, WorkerSupervisor, DiscoveryRunner, etc.)
- `packages/extraction/` -- Stage 0-5 soul extraction pipeline (runs inside each RepoWorker)
- `packages/contracts/` -- Pydantic schemas shared across all packages

## Adding Knowledge Bricks

Bricks are JSONL files in `bricks/`. Each line is a JSON object:

```json
{
  "brick_id": "framework-l1-name",
  "domain_id": "framework",
  "knowledge_type": "rationale|capability|constraint|interface|failure|assembly_pattern",
  "statement": "The knowledge claim (max 200 words, focus on WHY/UNSAID)",
  "confidence": "high",
  "signal": "ALIGNED",
  "source_project_ids": ["hardcoded-expert-knowledge"],
  "support_count": 5,
  "evidence_refs": [{"kind": "community_ref", "path": "https://docs.example.com/...", "start_line": null, "end_line": null, "snippet": null, "artifact_name": null, "source_url": "https://docs.example.com/..."}],
  "tags": ["framework", "topic", "l1"]
}
```

Requirements:
- At least 15% of bricks per file should be `knowledge_type: "failure"` (anti-patterns)
- Every brick needs a real documentation URL in `evidence_refs`
- L1 bricks (framework philosophy) tagged with `"l1"` in tags

After adding bricks, update the framework mapping in `packages/extraction/doramagic_extraction/brick_injection.py`.

## Code Quality

```bash
make lint       # ruff check
make format     # ruff format
make typecheck  # mypy on contracts
make check      # all of the above + tests
```

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run `make check` (lint + typecheck + tests must pass)
5. Submit a PR with a clear description (explain **WHY**, not what)

## Pre-release Checklist

Before pushing to GitHub, run the preflight check:

```bash
bash scripts/publish_preflight.sh
```

This validates: community standard files, no hardcoded IPs/secrets/paths, no internal artifacts, version consistency, and lockfile tracking.

## License

MIT
