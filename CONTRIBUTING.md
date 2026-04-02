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
make check   # lint + typecheck + tests (491 tests)
make test    # tests only
make lint    # ruff check
make format  # ruff format
make typecheck  # mypy on contracts
```

## Project Structure

- `packages/` — Core Python engine (15 modular packages)
- `knowledge/bricks/` — 10,030 knowledge bricks across 50 domains (JSONL)
- `skills/doramagic/` — OpenClaw skill bundle (SKILL.md + references)
- `tests/` — Unit and E2E smoke tests
- `scripts/` — Release and development tools
- `data/fixtures/` — Test fixture data

## Architecture

Doramagic uses a **conditional DAG** (not a linear pipeline):

- `packages/controller/` — FlowController with conditional edge FSM
- `packages/executors/` — Phase executors (NeedProfileBuilder, WorkerSupervisor, etc.)
- `packages/extraction/` — Soul extraction pipeline (runs inside each RepoWorker)
- `packages/contracts/` — Pydantic schemas shared across all packages

## Adding Knowledge Bricks

Bricks are JSONL files in `knowledge/bricks/`. Each line is a JSON object:

```json
{
  "brick_id": "framework-l1-name",
  "domain_id": "framework",
  "knowledge_type": "rationale|capability|constraint|failure|pattern|assembly_pattern",
  "statement": "The knowledge claim (max 200 words)",
  "confidence": "high",
  "tags": ["framework", "topic", "l1"]
}
```

Requirements:
- At least 15% of bricks per file should be `knowledge_type: "failure"`
- Every brick needs a real documentation URL in `evidence_refs`
- L1 bricks (foundational) tagged with `"l1"` in tags

## Commit Messages

All commits use **English** with conventional commit format:

```
<type>: <description>

type: feat | fix | refactor | test | docs | chore
```

Examples:
- `feat: add spaced repetition to education bricks`
- `fix: resolve path traversal in SKILL_KEY validation`
- `chore: update dependencies`

AI-assisted commits include co-author attribution:
```
Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

## Pull Requests

1. Create a feature branch (`feat/<name>`, `fix/<name>`)
2. Run `make check` (must pass)
3. Describe **why** the change is needed (not just what changed)
4. PR must pass AI code review before merge

## Release Checklist

```bash
bash scripts/publish_preflight.sh          # pre-flight checks
bash scripts/release/publish_to_github.sh vX.Y.Z --dry-run  # dry run
bash scripts/release/publish_to_github.sh vX.Y.Z            # publish
```

See `scripts/release/README.md` for the complete 8-step release process.

## License

MIT
